'use client';
import { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import { ArrowLeft, Plus, X } from 'lucide-react';
import PlatformOwnerRoute from '@/components/PlatformOwnerRoute';
import {
  SubscriptionPlan,
  CreateSubscriptionPlanPayload,
  fetchSubscriptionPlans,
  createSubscriptionPlan,
  updateSubscriptionPlan,
} from '@/lib/platformApi';

const BILLING_PERIODS = [
  { value: 30, label: 'Monthly' },
  { value: 90, label: 'Quarterly' },
  { value: 365, label: 'Yearly' },
];

function PlansPage() {
  const [plans, setPlans] = useState<SubscriptionPlan[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showCreate, setShowCreate] = useState(false);
  const [editing, setEditing] = useState<SubscriptionPlan | null>(null);
  const [busyId, setBusyId] = useState<number | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      setPlans(await fetchSubscriptionPlans());
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to load plans');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const handleToggleActive = async (plan: SubscriptionPlan) => {
    setBusyId(plan.id);
    try {
      await updateSubscriptionPlan(plan.id, { is_active: !plan.is_active });
      await load();
    } catch (err: any) {
      setError(err?.response?.data?.error || 'Action failed');
    } finally {
      setBusyId(null);
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-6 py-8">
      <Link href="/billing" className="flex items-center gap-1.5 text-sm text-slate-400 hover:text-slate-100 mb-6 w-fit">
        <ArrowLeft className="h-4 w-4" /> Back to billing
      </Link>

      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-lg font-semibold">Subscription Plans</h1>
          <p className="text-xs text-slate-500">Pricing tiers offered to tenants</p>
        </div>
        <button
          onClick={() => setShowCreate(true)}
          className="flex items-center gap-1.5 text-sm bg-slate-100 text-slate-900 px-3 py-1.5 rounded-md hover:bg-white transition"
        >
          <Plus className="h-4 w-4" /> New Plan
        </button>
      </div>

      {error && (
        <div className="text-sm text-red-400 bg-red-950/50 border border-red-900 rounded px-3 py-2 mb-4">
          {error}
        </div>
      )}

      <div className="bg-slate-900 border border-slate-800 rounded-lg overflow-hidden overflow-x-auto">
        {loading ? (
          <div className="p-8 text-center text-slate-500 text-sm">Loading...</div>
        ) : plans.length === 0 ? (
          <div className="p-8 text-center text-slate-500 text-sm">No plans yet.</div>
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-slate-800/50 text-slate-400 text-xs uppercase">
              <tr>
                <th className="text-left px-4 py-2.5 font-medium">Name</th>
                <th className="text-left px-4 py-2.5 font-medium">Price</th>
                <th className="text-left px-4 py-2.5 font-medium">Billing</th>
                <th className="text-left px-4 py-2.5 font-medium">Limits</th>
                <th className="text-left px-4 py-2.5 font-medium">Status</th>
                <th className="text-right px-4 py-2.5 font-medium">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {plans.map((plan) => (
                <tr key={plan.id}>
                  <td className="px-4 py-2.5">
                    <button onClick={() => setEditing(plan)} className="hover:underline">
                      {plan.name}
                    </button>
                    {plan.is_trial && <span className="ml-2 text-xs text-blue-400">Trial</span>}
                  </td>
                  <td className="px-4 py-2.5 text-slate-400">R{plan.price}</td>
                  <td className="px-4 py-2.5 text-slate-400">{plan.billing_period_display}</td>
                  <td className="px-4 py-2.5 text-slate-400">
                    {plan.max_shops} shops &middot; {plan.max_users} users &middot; {plan.max_invoices_per_month}/mo invoices
                  </td>
                  <td className="px-4 py-2.5">
                    <span
                      className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs ${
                        plan.is_active ? 'bg-emerald-950 text-emerald-400' : 'bg-slate-800 text-slate-400'
                      }`}
                    >
                      {plan.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td className="px-4 py-2.5 text-right space-x-2">
                    <button
                      onClick={() => setEditing(plan)}
                      className="inline-flex items-center gap-1 text-xs px-2.5 py-1 rounded-md border border-slate-700 text-slate-300 hover:bg-slate-800 transition"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => handleToggleActive(plan)}
                      disabled={busyId === plan.id}
                      className={`inline-flex items-center gap-1 text-xs px-2.5 py-1 rounded-md border transition disabled:opacity-50 ${
                        plan.is_active
                          ? 'border-red-900 text-red-400 hover:bg-red-950/50'
                          : 'border-emerald-900 text-emerald-400 hover:bg-emerald-950/50'
                      }`}
                    >
                      {plan.is_active ? 'Deactivate' : 'Activate'}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {showCreate && (
        <PlanModal
          onClose={() => setShowCreate(false)}
          onSaved={() => {
            setShowCreate(false);
            load();
          }}
        />
      )}

      {editing && (
        <PlanModal
          plan={editing}
          onClose={() => setEditing(null)}
          onSaved={() => {
            setEditing(null);
            load();
          }}
        />
      )}
    </div>
  );
}

function PlanModal({
  plan,
  onClose,
  onSaved,
}: {
  plan?: SubscriptionPlan;
  onClose: () => void;
  onSaved: () => void;
}) {
  const [form, setForm] = useState<CreateSubscriptionPlanPayload>({
    name: plan?.name ?? '',
    slug: plan?.slug ?? '',
    description: plan?.description ?? '',
    price: plan?.price ?? '0',
    setup_fee: plan?.setup_fee ?? '0',
    billing_period_days: plan?.billing_period_days ?? 30,
    max_shops: plan?.max_shops ?? 1,
    max_users: plan?.max_users ?? 5,
    max_invoices_per_month: plan?.max_invoices_per_month ?? 100,
    is_trial: plan?.is_trial ?? false,
    sort_order: plan?.sort_order ?? 0,
  });
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSaving(true);
    try {
      if (plan) {
        await updateSubscriptionPlan(plan.id, form);
      } else {
        await createSubscriptionPlan(form);
      }
      onSaved();
    } catch (err: any) {
      const data = err?.response?.data;
      setError(
        typeof data === 'string'
          ? data
          : Object.values(data || {}).flat().join(' ') || 'Failed to save plan'
      );
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 px-4 overflow-y-auto py-8">
      <div className="bg-slate-900 border border-slate-800 rounded-lg w-full max-w-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-semibold">{plan ? 'Edit Plan' : 'New Plan'}</h3>
          <button onClick={onClose} className="text-slate-500 hover:text-slate-200">
            <X className="h-4 w-4" />
          </button>
        </div>
        <form onSubmit={handleSubmit} className="space-y-3">
          {error && (
            <div className="text-sm text-red-400 bg-red-950/50 border border-red-900 rounded px-3 py-2">{error}</div>
          )}
          <div className="grid grid-cols-2 gap-3">
            <Field label="Name" value={form.name || ''} onChange={(v) => setForm({ ...form, name: v })} required />
            <Field label="Slug" value={form.slug || ''} onChange={(v) => setForm({ ...form, slug: v })} required />
          </div>
          <Field
            label="Description"
            value={form.description || ''}
            onChange={(v) => setForm({ ...form, description: v })}
          />
          <div className="grid grid-cols-2 gap-3">
            <Field label="Price (ZAR)" value={String(form.price ?? '')} onChange={(v) => setForm({ ...form, price: v })} required />
            <Field label="Setup Fee (ZAR)" value={String(form.setup_fee ?? '')} onChange={(v) => setForm({ ...form, setup_fee: v })} />
          </div>
          <div>
            <label className="block text-sm text-slate-400 mb-1">Billing Period</label>
            <select
              value={form.billing_period_days}
              onChange={(e) => setForm({ ...form, billing_period_days: Number(e.target.value) as 30 | 90 | 365 })}
              className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-slate-500"
            >
              {BILLING_PERIODS.map((p) => (
                <option key={p.value} value={p.value}>
                  {p.label}
                </option>
              ))}
            </select>
          </div>
          <div className="grid grid-cols-3 gap-3">
            <Field
              label="Max Shops"
              type="number"
              value={String(form.max_shops ?? '')}
              onChange={(v) => setForm({ ...form, max_shops: Number(v) })}
            />
            <Field
              label="Max Users"
              type="number"
              value={String(form.max_users ?? '')}
              onChange={(v) => setForm({ ...form, max_users: Number(v) })}
            />
            <Field
              label="Max Invoices/mo"
              type="number"
              value={String(form.max_invoices_per_month ?? '')}
              onChange={(v) => setForm({ ...form, max_invoices_per_month: Number(v) })}
            />
          </div>
          <label className="flex items-center gap-2 text-sm text-slate-300">
            <input
              type="checkbox"
              checked={!!form.is_trial}
              onChange={(e) => setForm({ ...form, is_trial: e.target.checked })}
              className="h-4 w-4 rounded border-slate-700 bg-slate-800"
            />
            Trial plan (grants a 14-day trial period on signup)
          </label>
          <button
            type="submit"
            disabled={saving}
            className="w-full bg-slate-100 text-slate-900 font-medium py-2 rounded-md text-sm hover:bg-white transition disabled:opacity-50 mt-2"
          >
            {saving ? 'Saving...' : plan ? 'Save Changes' : 'Create Plan'}
          </button>
        </form>
      </div>
    </div>
  );
}

function Field({
  label,
  value,
  onChange,
  type = 'text',
  required = false,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  type?: string;
  required?: boolean;
}) {
  return (
    <div>
      <label className="block text-sm text-slate-400 mb-1">{label}</label>
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        required={required}
        className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-slate-500"
      />
    </div>
  );
}

export default function OwnerBillingPlansPage() {
  return (
    <PlatformOwnerRoute>
      <PlansPage />
    </PlatformOwnerRoute>
  );
}
