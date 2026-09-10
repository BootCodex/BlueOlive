'use client';
import { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import { ArrowLeft, PauseCircle, PlayCircle, RefreshCw, Settings2, X, XCircle } from 'lucide-react';
import PlatformOwnerRoute from '@/components/PlatformOwnerRoute';
import {
  BillingOverview,
  Subscription,
  SubscriptionPlan,
  Tenant,
  fetchBillingOverview,
  fetchSubscriptions,
  fetchSubscriptionPlans,
  fetchTenants,
  changeSubscriptionPlan,
  cancelSubscription,
  createSubscription,
  renewSubscription,
  suspendSubscription,
  reactivateSubscription,
} from '@/lib/platformApi';

const STATUS_STYLES: Record<Subscription['status'], string> = {
  TRIAL: 'bg-blue-950 text-blue-400',
  ACTIVE: 'bg-emerald-950 text-emerald-400',
  PAST_DUE: 'bg-amber-950 text-amber-400',
  CANCELLED: 'bg-slate-800 text-slate-400',
  EXPIRED: 'bg-red-950 text-red-400',
  SUSPENDED: 'bg-red-950 text-red-400',
};

function BillingDashboard() {
  const [overview, setOverview] = useState<BillingOverview | null>(null);
  const [subscriptions, setSubscriptions] = useState<Subscription[]>([]);
  const [plans, setPlans] = useState<SubscriptionPlan[]>([]);
  const [tenants, setTenants] = useState<Tenant[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [busyId, setBusyId] = useState<number | null>(null);
  const [changingPlanFor, setChangingPlanFor] = useState<Subscription | null>(null);
  const [assigningPlanFor, setAssigningPlanFor] = useState<Tenant | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const [overviewData, subsData, plansData, tenantsData] = await Promise.all([
        fetchBillingOverview(),
        fetchSubscriptions(),
        fetchSubscriptionPlans(),
        fetchTenants(),
      ]);
      setOverview(overviewData);
      setSubscriptions(subsData);
      setPlans(plansData);
      setTenants(tenantsData);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to load billing data');
    } finally {
      setLoading(false);
    }
  }, []);

  const unbilledTenants = tenants.filter(
    (tenant) => !subscriptions.some((sub) => sub.tenant === tenant.id)
  );

  useEffect(() => {
    load();
  }, [load]);

  const withBusy = async (id: number, action: () => Promise<unknown>) => {
    setBusyId(id);
    setError('');
    try {
      await action();
      await load();
    } catch (err: any) {
      setError(err?.response?.data?.error || err?.response?.data?.detail || 'Action failed');
    } finally {
      setBusyId(null);
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-6 py-8">
      <Link href="/" className="flex items-center gap-1.5 text-sm text-slate-400 hover:text-slate-100 mb-6 w-fit">
        <ArrowLeft className="h-4 w-4" /> Back to tenants
      </Link>

      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-lg font-semibold">Billing</h1>
          <p className="text-xs text-slate-500">Subscription tiers, tenant billing status, and payments</p>
        </div>
        <Link
          href="/billing/plans"
          className="flex items-center gap-1.5 text-sm bg-slate-100 text-slate-900 px-3 py-1.5 rounded-md hover:bg-white transition"
        >
          <Settings2 className="h-4 w-4" /> Manage Plans
        </Link>
      </div>

      {error && (
        <div className="text-sm text-red-400 bg-red-950/50 border border-red-900 rounded px-3 py-2 mb-4">
          {error}
        </div>
      )}

      {overview && (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 mb-8">
          <StatCard label="MRR" value={`R${Number(overview.mrr).toFixed(0)}`} />
          <StatCard label="Revenue (mo)" value={`R${Number(overview.revenue_this_month).toFixed(0)}`} />
          <StatCard label="Active" value={overview.status_counts.ACTIVE ?? 0} accent="text-emerald-400" />
          <StatCard label="Trial" value={overview.status_counts.TRIAL ?? 0} accent="text-blue-400" />
          <StatCard label="Suspended" value={overview.status_counts.SUSPENDED ?? 0} accent="text-red-400" />
          <StatCard label="Expiring ≤7d" value={overview.expiring_within_7_days} accent="text-amber-400" />
        </div>
      )}

      {!loading && unbilledTenants.length > 0 && (
        <div className="mb-8">
          <h2 className="text-sm font-medium text-slate-400 uppercase tracking-wide mb-3">
            Tenants Without a Plan
          </h2>
          <div className="bg-slate-900 border border-amber-900/50 rounded-lg overflow-hidden">
            <table className="w-full text-sm">
              <tbody className="divide-y divide-slate-800">
                {unbilledTenants.map((tenant) => (
                  <tr key={tenant.id}>
                    <td className="px-4 py-2.5">{tenant.name}</td>
                    <td className="px-4 py-2.5 text-slate-400">{tenant.subdomain}</td>
                    <td className="px-4 py-2.5 text-right">
                      <button
                        onClick={() => setAssigningPlanFor(tenant)}
                        className="inline-flex items-center gap-1 text-xs px-2.5 py-1 rounded-md border border-slate-700 text-slate-300 hover:bg-slate-800 transition"
                      >
                        <Settings2 className="h-3 w-3" /> Assign Plan
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      <h2 className="text-sm font-medium text-slate-400 uppercase tracking-wide mb-3">Subscriptions</h2>
      <div className="bg-slate-900 border border-slate-800 rounded-lg overflow-hidden overflow-x-auto">
        {loading ? (
          <div className="p-8 text-center text-slate-500 text-sm">Loading...</div>
        ) : subscriptions.length === 0 ? (
          <div className="p-8 text-center text-slate-500 text-sm">No subscriptions yet.</div>
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-slate-800/50 text-slate-400 text-xs uppercase">
              <tr>
                <th className="text-left px-4 py-2.5 font-medium">Tenant</th>
                <th className="text-left px-4 py-2.5 font-medium">Plan</th>
                <th className="text-left px-4 py-2.5 font-medium">Status</th>
                <th className="text-left px-4 py-2.5 font-medium">Days Left</th>
                <th className="text-left px-4 py-2.5 font-medium">Auto-renew</th>
                <th className="text-right px-4 py-2.5 font-medium">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {subscriptions.map((sub) => (
                <tr key={sub.id}>
                  <td className="px-4 py-2.5">{sub.tenant_name}</td>
                  <td className="px-4 py-2.5 text-slate-400">{sub.plan.name}</td>
                  <td className="px-4 py-2.5">
                    <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs ${STATUS_STYLES[sub.status]}`}>
                      {sub.status_display}
                    </span>
                  </td>
                  <td className="px-4 py-2.5 text-slate-400">{sub.days_remaining}</td>
                  <td className="px-4 py-2.5 text-slate-400">{sub.auto_renew ? 'Yes' : 'No'}</td>
                  <td className="px-4 py-2.5 text-right space-x-1.5 whitespace-nowrap">
                    <button
                      onClick={() => setChangingPlanFor(sub)}
                      disabled={busyId === sub.id}
                      className="inline-flex items-center gap-1 text-xs px-2.5 py-1 rounded-md border border-slate-700 text-slate-300 hover:bg-slate-800 transition disabled:opacity-50"
                    >
                      <Settings2 className="h-3 w-3" /> Change Plan
                    </button>
                    <button
                      onClick={() => withBusy(sub.id, () => renewSubscription(sub.id))}
                      disabled={busyId === sub.id}
                      className="inline-flex items-center gap-1 text-xs px-2.5 py-1 rounded-md border border-slate-700 text-slate-300 hover:bg-slate-800 transition disabled:opacity-50"
                    >
                      <RefreshCw className="h-3 w-3" /> Renew
                    </button>
                    {sub.status === 'SUSPENDED' ? (
                      <button
                        onClick={() => withBusy(sub.id, () => reactivateSubscription(sub.id))}
                        disabled={busyId === sub.id}
                        className="inline-flex items-center gap-1 text-xs px-2.5 py-1 rounded-md border border-emerald-900 text-emerald-400 hover:bg-emerald-950/50 transition disabled:opacity-50"
                      >
                        <PlayCircle className="h-3 w-3" /> Reactivate
                      </button>
                    ) : (
                      <button
                        onClick={() => withBusy(sub.id, () => suspendSubscription(sub.id))}
                        disabled={busyId === sub.id}
                        className="inline-flex items-center gap-1 text-xs px-2.5 py-1 rounded-md border border-amber-900 text-amber-400 hover:bg-amber-950/50 transition disabled:opacity-50"
                      >
                        <PauseCircle className="h-3 w-3" /> Suspend
                      </button>
                    )}
                    <button
                      onClick={() => {
                        if (window.confirm(`Cancel ${sub.tenant_name}'s subscription immediately?`)) {
                          withBusy(sub.id, () => cancelSubscription(sub.id, true));
                        }
                      }}
                      disabled={busyId === sub.id}
                      className="inline-flex items-center gap-1 text-xs px-2.5 py-1 rounded-md border border-red-900 text-red-400 hover:bg-red-950/50 transition disabled:opacity-50"
                    >
                      <XCircle className="h-3 w-3" /> Cancel
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {changingPlanFor && (
        <ChangePlanModal
          subscription={changingPlanFor}
          plans={plans}
          onClose={() => setChangingPlanFor(null)}
          onChanged={() => {
            setChangingPlanFor(null);
            load();
          }}
        />
      )}

      {assigningPlanFor && (
        <AssignPlanModal
          tenant={assigningPlanFor}
          plans={plans}
          onClose={() => setAssigningPlanFor(null)}
          onAssigned={() => {
            setAssigningPlanFor(null);
            load();
          }}
        />
      )}
    </div>
  );
}

function AssignPlanModal({
  tenant,
  plans,
  onClose,
  onAssigned,
}: {
  tenant: Tenant;
  plans: SubscriptionPlan[];
  onClose: () => void;
  onAssigned: () => void;
}) {
  const [planId, setPlanId] = useState(plans[0]?.id ?? 0);
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSaving(true);
    try {
      await createSubscription({ tenant: tenant.id, plan: planId });
      onAssigned();
    } catch (err: any) {
      const data = err?.response?.data;
      setError(
        typeof data === 'string'
          ? data
          : Object.values(data || {}).flat().join(' ') || 'Failed to assign plan'
      );
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 px-4">
      <div className="bg-slate-900 border border-slate-800 rounded-lg w-full max-w-md p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-semibold">Assign Plan — {tenant.name}</h3>
          <button onClick={onClose} className="text-slate-500 hover:text-slate-200">
            <X className="h-4 w-4" />
          </button>
        </div>
        <form onSubmit={handleSubmit} className="space-y-3">
          {error && (
            <div className="text-sm text-red-400 bg-red-950/50 border border-red-900 rounded px-3 py-2">{error}</div>
          )}
          {plans.length === 0 ? (
            <p className="text-sm text-slate-500">
              No plans exist yet. <Link href="/billing/plans" className="underline">Create one first.</Link>
            </p>
          ) : (
            <div>
              <label className="block text-sm text-slate-400 mb-1">Plan</label>
              <select
                value={planId}
                onChange={(e) => setPlanId(Number(e.target.value))}
                className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-slate-500"
              >
                {plans.map((plan) => (
                  <option key={plan.id} value={plan.id}>
                    {plan.name} — R{plan.price}/{plan.billing_period_display}
                  </option>
                ))}
              </select>
            </div>
          )}
          <button
            type="submit"
            disabled={saving || plans.length === 0}
            className="w-full bg-slate-100 text-slate-900 font-medium py-2 rounded-md text-sm hover:bg-white transition disabled:opacity-50 mt-2"
          >
            {saving ? 'Assigning...' : 'Assign Plan'}
          </button>
        </form>
      </div>
    </div>
  );
}

function ChangePlanModal({
  subscription,
  plans,
  onClose,
  onChanged,
}: {
  subscription: Subscription;
  plans: SubscriptionPlan[];
  onClose: () => void;
  onChanged: () => void;
}) {
  const [planId, setPlanId] = useState(subscription.plan.id);
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSaving(true);
    try {
      await changeSubscriptionPlan(subscription.id, planId);
      onChanged();
    } catch (err: any) {
      setError(err?.response?.data?.error || 'Failed to change plan');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 px-4">
      <div className="bg-slate-900 border border-slate-800 rounded-lg w-full max-w-md p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-semibold">Change Plan — {subscription.tenant_name}</h3>
          <button onClick={onClose} className="text-slate-500 hover:text-slate-200">
            <X className="h-4 w-4" />
          </button>
        </div>
        <form onSubmit={handleSubmit} className="space-y-3">
          {error && (
            <div className="text-sm text-red-400 bg-red-950/50 border border-red-900 rounded px-3 py-2">{error}</div>
          )}
          <div>
            <label className="block text-sm text-slate-400 mb-1">Plan</label>
            <select
              value={planId}
              onChange={(e) => setPlanId(Number(e.target.value))}
              className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-slate-500"
            >
              {plans.map((plan) => (
                <option key={plan.id} value={plan.id}>
                  {plan.name} — R{plan.price}/{plan.billing_period_display}
                </option>
              ))}
            </select>
          </div>
          <button
            type="submit"
            disabled={saving}
            className="w-full bg-slate-100 text-slate-900 font-medium py-2 rounded-md text-sm hover:bg-white transition disabled:opacity-50 mt-2"
          >
            {saving ? 'Saving...' : 'Change Plan'}
          </button>
        </form>
      </div>
    </div>
  );
}

function StatCard({ label, value, accent }: { label: string; value: string | number; accent?: string }) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-lg px-4 py-3">
      <div className={`text-xl font-semibold ${accent || 'text-slate-100'}`}>{value}</div>
      <div className="text-xs text-slate-500">{label}</div>
    </div>
  );
}

export default function OwnerBillingPage() {
  return (
    <PlatformOwnerRoute>
      <BillingDashboard />
    </PlatformOwnerRoute>
  );
}
