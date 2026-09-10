/**
 * useForm Hook - Comprehensive form handling with validation
 * Provides state management, validation, error handling, and submission
 */

'use client';

import { useState, useCallback, useRef } from 'react';
import type { MaybeAxiosError } from '@/lib/types/errors';
import {
  validateForm,
  FormValidationRules,
} from '@/lib/validation';

export interface UseFormOptions<T> {
  initialValues: T;
  onSubmit: (values: T) => Promise<void> | void;
  validationRules?: FormValidationRules;
  onError?: (error: Error) => void;
}

export interface UseFormReturn<T> {
  values: T;
  errors: Record<string, string>;
  touched: Record<string, boolean>;
  isDirty: boolean;
  isSubmitting: boolean;
  isValid: boolean;
  formError: string | null;
  handleChange: (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => void;
  handleBlur: (e: React.FocusEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => void;
  handleSubmit: (e: React.FormEvent) => Promise<void>;
  setFieldValue: (name: string, value: unknown) => void;
  setFieldError: (name: string, error: string) => void;
  resetForm: () => void;
  setFormError: (error: string | null) => void;
  clearFieldError: (name: string) => void;
}

/**
 * useForm hook for managing form state, validation, and submission
 */
export function useForm<T extends Record<string, unknown>>({
  initialValues,
  onSubmit,
  validationRules = {},
  onError,
}: UseFormOptions<T>): UseFormReturn<T> {
  const [values, setValues] = useState<T>(initialValues);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [touched, setTouched] = useState<Record<string, boolean>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  // A stable, one-time snapshot of the form's starting values, read during
  // render to compute isDirty - state (not a ref) so that read is safe
  // during render; it's captured once via the lazy initializer and never
  // updated, matching the ref's original "never changes" semantics.
  const [initialSnapshot] = useState(initialValues);
  const isDirtyRef = useRef(false);

  const isDirty = Object.keys(values).some(
    (key) => values[key as keyof T] !== initialSnapshot[key as keyof T]
  );

  const isValid = Object.keys(errors).length === 0 && isDirty;

  const resetForm = useCallback(() => {
    setValues(initialSnapshot);
    setErrors({});
    setTouched({});
    setFormError(null);
    isDirtyRef.current = false;
    // initialSnapshot is captured once via useState's lazy initializer and
    // never changes for the lifetime of this hook instance, so it's safe
    // to omit here.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
      const { name, value, type } = e.target;
      const processedValue =
        type === 'checkbox'
          ? (e.target as HTMLInputElement).checked
          : type === 'number'
          ? parseFloat(value) || ''
          : value;

      setValues((prev) => ({
        ...prev,
        [name]: processedValue,
      }));

      isDirtyRef.current = true;

      // Validate field if touched
      if (touched[name] && validationRules[name]) {
        const validation = validateForm(
          { ...values, [name]: processedValue },
          { [name]: validationRules[name] }
        );
        
        if (validation.errors[name]) {
          setErrors((prev) => ({
            ...prev,
            [name]: validation.errors[name],
          }));
        } else {
          setErrors((prev) => {
            const newErrors = { ...prev };
            delete newErrors[name];
            return newErrors;
          });
        }
      }
    },
    [touched, validationRules, values]
  );

  const handleBlur = useCallback(
    (e: React.FocusEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
      const { name } = e.target;

      setTouched((prev) => ({
        ...prev,
        [name]: true,
      }));

      // Validate field on blur
      if (validationRules[name]) {
        const validation = validateForm(values, { [name]: validationRules[name] });
        
        if (validation.errors[name]) {
          setErrors((prev) => ({
            ...prev,
            [name]: validation.errors[name],
          }));
        } else {
          setErrors((prev) => {
            const newErrors = { ...prev };
            delete newErrors[name];
            return newErrors;
          });
        }
      }
    },
    [validationRules, values]
  );

  const handleSubmit = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();
      setFormError(null);

      // Mark all fields as touched
      const allTouched = Object.keys(values).reduce(
        (acc, key) => ({ ...acc, [key]: true }),
        {}
      );
      setTouched(allTouched);

      // Validate entire form
      const validation = validateForm(values, validationRules);
      
      if (!validation.isValid) {
        setErrors(validation.errors);
        setFormError('Please fix the errors above');
        return;
      }

      setIsSubmitting(true);
      try {
        await onSubmit(values);
        // Reset form on successful submission
        resetForm();
      } catch (error: unknown) {
        const errorMessage = (error as MaybeAxiosError)?.message || 'An error occurred while submitting the form';
        setFormError(errorMessage);
        onError?.(error instanceof Error ? error : new Error(errorMessage));
      } finally {
        setIsSubmitting(false);
      }
    },
    [values, validationRules, onSubmit, onError, resetForm]
  );

  const setFieldValue = useCallback((name: string, value: unknown) => {
    setValues((prev) => ({
      ...prev,
      [name]: value,
    }));
    isDirtyRef.current = true;
  }, []);

  const setFieldError = useCallback((name: string, error: string) => {
    setErrors((prev) => ({
      ...prev,
      [name]: error,
    }));
  }, []);

  const clearFieldError = useCallback((name: string) => {
    setErrors((prev) => {
      const newErrors = { ...prev };
      delete newErrors[name];
      return newErrors;
    });
  }, []);

  return {
    values,
    errors,
    touched,
    isDirty,
    isSubmitting,
    isValid,
    formError,
    handleChange,
    handleBlur,
    handleSubmit,
    setFieldValue,
    setFieldError,
    resetForm,
    setFormError,
    clearFieldError,
  };
}

/**
 * Form Field Component Props Helper
 * Returns props to spread on form field elements
 */
export function getFieldProps(
  form: Partial<UseFormReturn<Record<string, unknown>>>,
  fieldName: string
) {
  return {
    name: fieldName,
    value: form.values?.[fieldName] ?? '',
    onChange: form.handleChange,
    onBlur: form.handleBlur,
    'aria-invalid': Boolean(form.errors?.[fieldName]),
    'aria-describedby': form.errors?.[fieldName]
      ? `${fieldName}-error`
      : undefined,
  };
}
