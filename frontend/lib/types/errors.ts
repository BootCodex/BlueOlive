/**
 * Minimal shape for a caught error of unknown origin that might be an axios
 * error (the overwhelmingly common case in this codebase's `catch` blocks).
 * Used to replace `catch (error: any)` with `catch (error: unknown)` plus a
 * narrow cast, instead of leaving the caught value typed `any`.
 */
export interface MaybeAxiosError {
  response?: {
    status?: number;
    data?: Record<string, unknown> & {
      detail?: string;
      message?: string;
      error?: string;
    };
  };
  message?: string;
  code?: string;
}
