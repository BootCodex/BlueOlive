'use client';
import { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import { AlertTriangle, ArrowLeft, CheckCircle2, RefreshCw } from 'lucide-react';
import PlatformOwnerRoute from '@/components/PlatformOwnerRoute';
import {
  ProvisioningHealth,
  fetchProvisioningHealth,
  retryTenantProvisioning,
  retryShopProvisioning,
} from '@/lib/platformApi';

const STATUS_STYLES: Record<string, string> = {
  pending: 'bg-amber-950 text-amber-400',
  db_ready: 'bg-blue-950 text-blue-400',
  failed: 'bg-red-950 text-red-400',
};

function ProvisioningPage() {
  const [data, setData] = useState<ProvisioningHealth | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [busyKey, setBusyKey] = useState<string | null>(null);
  const [message, setMessage] = useState('');

  const load = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      setData(await fetchProvisioningHealth());
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to load provisioning health');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const handleRetryTenant = async (id: number, name: string) => {
    setBusyKey(`tenant-${id}`);
    setMessage('');
    try {
      const res = await retryTenantProvisioning(id);
      setMessage(res.message);
      await load();
    } catch (err: any) {
      setError(err?.response?.data?.error || `Failed to retry ${name}`);
    } finally {
      setBusyKey(null);
    }
  };

  const handleRetryShop = async (id: number, name: string) => {
    setBusyKey(`shop-${id}`);
    setMessage('');
    try {
      const res = await retryShopProvisioning(id);
      setMessage(res.message);
      await load();
    } catch (err: any) {
      setError(err?.response?.data?.error || `Failed to retry ${name}`);
    } finally {
      setBusyKey(null);
    }
  };

  const nothingStuck = data && data.tenants.length === 0 && data.shops.length === 0;

  return (
    <div className="max-w-5xl mx-auto px-6 py-8">
      <Link href="/" className="flex items-center gap-1.5 text-sm text-slate-400 hover:text-slate-100 mb-6 w-fit">
        <ArrowLeft className="h-4 w-4" /> Back to tenants
      </Link>

      <div className="mb-8">
        <h1 className="text-lg font-semibold">Provisioning Health</h1>
        <p className="text-xs text-slate-500">
          Tenants and shops not yet fully set up. Signup runs asynchronously - this surfaces anything stuck or failed.
        </p>
      </div>

      {error && (
        <div className="text-sm text-red-400 bg-red-950/50 border border-red-900 rounded px-3 py-2 mb-4">
          {error}
        </div>
      )}
      {message && (
        <div className="text-sm text-emerald-400 bg-emerald-950/50 border border-emerald-900 rounded px-3 py-2 mb-4">
          {message}
        </div>
      )}

      {loading ? (
        <div className="p-8 text-center text-slate-500 text-sm">Loading...</div>
      ) : nothingStuck ? (
        <div className="flex items-center gap-2 text-emerald-400 bg-emerald-950/30 border border-emerald-900 rounded-lg p-6 justify-center">
          <CheckCircle2 className="h-5 w-5" /> All tenants and shops are provisioned.
        </div>
      ) : (
        <>
          <section className="mb-10">
            <h2 className="text-sm font-medium text-slate-400 uppercase tracking-wide mb-3">
              Tenants ({data?.tenants.length ?? 0})
            </h2>
            {data && data.tenants.length === 0 ? (
              <div className="text-sm text-slate-500 px-1">No tenants stuck.</div>
            ) : (
              <div className="bg-slate-900 border border-slate-800 rounded-lg overflow-hidden overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="bg-slate-800/50 text-slate-400 text-xs uppercase">
                    <tr>
                      <th className="text-left px-4 py-2.5 font-medium">Tenant</th>
                      <th className="text-left px-4 py-2.5 font-medium">Status</th>
                      <th className="text-left px-4 py-2.5 font-medium">Age</th>
                      <th className="text-left px-4 py-2.5 font-medium">Error</th>
                      <th className="text-right px-4 py-2.5 font-medium">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800">
                    {data?.tenants.map((tenant) => (
                      <tr key={tenant.id}>
                        <td className="px-4 py-2.5">
                          <Link href={`/tenants/${tenant.id}`} className="hover:underline">
                            {tenant.name}
                          </Link>
                        </td>
                        <td className="px-4 py-2.5">
                          <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs ${STATUS_STYLES[tenant.setup_status] || ''}`}>
                            {tenant.setup_status}
                          </span>
                        </td>
                        <td className="px-4 py-2.5 text-slate-400">{tenant.minutes_since_created}m</td>
                        <td className="px-4 py-2.5 text-slate-400 max-w-xs truncate" title={tenant.setup_error}>
                          {tenant.setup_error || '—'}
                        </td>
                        <td className="px-4 py-2.5 text-right">
                          <button
                            onClick={() => handleRetryTenant(tenant.id, tenant.name)}
                            disabled={busyKey === `tenant-${tenant.id}`}
                            className="inline-flex items-center gap-1 text-xs px-2.5 py-1 rounded-md border border-slate-700 text-slate-300 hover:bg-slate-800 transition disabled:opacity-50"
                          >
                            <RefreshCw className="h-3 w-3" /> Retry DB Setup
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
            <p className="text-xs text-slate-600 mt-2 flex items-start gap-1.5">
              <AlertTriangle className="h-3.5 w-3.5 shrink-0 mt-0.5" />
              Retry only re-runs database provisioning. If a tenant's database is already ready but signup
              didn&apos;t finish (no shop/admin user), finish it manually from the tenant&apos;s detail page instead.
            </p>
          </section>

          <section>
            <h2 className="text-sm font-medium text-slate-400 uppercase tracking-wide mb-3">
              Shops ({data?.shops.length ?? 0})
            </h2>
            {data && data.shops.length === 0 ? (
              <div className="text-sm text-slate-500 px-1">No shops stuck.</div>
            ) : (
              <div className="bg-slate-900 border border-slate-800 rounded-lg overflow-hidden overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="bg-slate-800/50 text-slate-400 text-xs uppercase">
                    <tr>
                      <th className="text-left px-4 py-2.5 font-medium">Shop</th>
                      <th className="text-left px-4 py-2.5 font-medium">Tenant</th>
                      <th className="text-left px-4 py-2.5 font-medium">Status</th>
                      <th className="text-left px-4 py-2.5 font-medium">Age</th>
                      <th className="text-left px-4 py-2.5 font-medium">Error</th>
                      <th className="text-right px-4 py-2.5 font-medium">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800">
                    {data?.shops.map((shop) => (
                      <tr key={shop.id}>
                        <td className="px-4 py-2.5">{shop.name}</td>
                        <td className="px-4 py-2.5 text-slate-400">
                          <Link href={`/tenants/${shop.tenant_id}`} className="hover:underline">
                            {shop.tenant_name}
                          </Link>
                        </td>
                        <td className="px-4 py-2.5">
                          <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs ${STATUS_STYLES[shop.setup_status] || ''}`}>
                            {shop.setup_status}
                          </span>
                        </td>
                        <td className="px-4 py-2.5 text-slate-400">{shop.minutes_since_created}m</td>
                        <td className="px-4 py-2.5 text-slate-400 max-w-xs truncate" title={shop.setup_error}>
                          {shop.setup_error || '—'}
                        </td>
                        <td className="px-4 py-2.5 text-right">
                          <button
                            onClick={() => handleRetryShop(shop.id, shop.name)}
                            disabled={busyKey === `shop-${shop.id}`}
                            className="inline-flex items-center gap-1 text-xs px-2.5 py-1 rounded-md border border-slate-700 text-slate-300 hover:bg-slate-800 transition disabled:opacity-50"
                          >
                            <RefreshCw className="h-3 w-3" /> Retry
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>
        </>
      )}
    </div>
  );
}

export default function OwnerProvisioningPage() {
  return (
    <PlatformOwnerRoute>
      <ProvisioningPage />
    </PlatformOwnerRoute>
  );
}
