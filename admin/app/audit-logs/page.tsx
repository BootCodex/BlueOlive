'use client';
import { Fragment, useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import { ArrowLeft, ChevronDown, ChevronUp, Search } from 'lucide-react';
import PlatformOwnerRoute from '@/components/PlatformOwnerRoute';
import {
  AuditLogEntry,
  AUDIT_ACTIONS,
  Tenant,
  fetchAuditLogs,
  fetchTenants,
} from '@/lib/platformApi';

function formatAction(action: string) {
  return action
    .toLowerCase()
    .split('_')
    .map((w) => w[0].toUpperCase() + w.slice(1))
    .join(' ');
}

function AuditLogsPage() {
  const [entries, setEntries] = useState<AuditLogEntry[]>([]);
  const [count, setCount] = useState(0);
  const [page, setPage] = useState(1);
  const [tenants, setTenants] = useState<Tenant[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [expanded, setExpanded] = useState<number | null>(null);

  const [action, setAction] = useState('');
  const [tenantId, setTenantId] = useState('');
  const [successFilter, setSuccessFilter] = useState('');
  const [search, setSearch] = useState('');

  const load = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const data = await fetchAuditLogs({
        page,
        action: action || undefined,
        tenant_id: tenantId ? Number(tenantId) : undefined,
        success: successFilter ? successFilter === 'true' : undefined,
        search: search || undefined,
      });
      setEntries(data.results);
      setCount(data.count);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to load audit log');
    } finally {
      setLoading(false);
    }
  }, [page, action, tenantId, successFilter, search]);

  useEffect(() => {
    load();
  }, [load]);

  useEffect(() => {
    fetchTenants().then(setTenants).catch(() => {});
  }, []);

  const pageSize = 10;
  const totalPages = Math.max(1, Math.ceil(count / pageSize));

  const handleFilterChange = (setter: (v: string) => void) => (v: string) => {
    setter(v);
    setPage(1);
  };

  return (
    <div className="max-w-6xl mx-auto px-6 py-8">
      <Link href="/" className="flex items-center gap-1.5 text-sm text-slate-400 hover:text-slate-100 mb-6 w-fit">
        <ArrowLeft className="h-4 w-4" /> Back to tenants
      </Link>

      <div className="mb-6">
        <h1 className="text-lg font-semibold">Audit Log</h1>
        <p className="text-xs text-slate-500">Logins, cross-tenant access attempts, role changes, and impersonation events</p>
      </div>

      <div className="flex flex-wrap gap-2 mb-4">
        <select
          value={action}
          onChange={(e) => handleFilterChange(setAction)(e.target.value)}
          className="px-3 py-1.5 bg-slate-900 border border-slate-800 rounded-md text-sm"
        >
          <option value="">All actions</option>
          {AUDIT_ACTIONS.map((a) => (
            <option key={a} value={a}>
              {formatAction(a)}
            </option>
          ))}
        </select>

        <select
          value={tenantId}
          onChange={(e) => handleFilterChange(setTenantId)(e.target.value)}
          className="px-3 py-1.5 bg-slate-900 border border-slate-800 rounded-md text-sm"
        >
          <option value="">All tenants</option>
          {tenants.map((t) => (
            <option key={t.id} value={t.id}>
              {t.name}
            </option>
          ))}
        </select>

        <select
          value={successFilter}
          onChange={(e) => handleFilterChange(setSuccessFilter)(e.target.value)}
          className="px-3 py-1.5 bg-slate-900 border border-slate-800 rounded-md text-sm"
        >
          <option value="">Success + Failed</option>
          <option value="true">Success only</option>
          <option value="false">Failed only</option>
        </select>

        <div className="relative">
          <Search className="h-3.5 w-3.5 text-slate-500 absolute left-2.5 top-1/2 -translate-y-1/2" />
          <input
            value={search}
            onChange={(e) => handleFilterChange(setSearch)(e.target.value)}
            placeholder="Search username / resource..."
            className="pl-8 pr-3 py-1.5 bg-slate-900 border border-slate-800 rounded-md text-sm w-56"
          />
        </div>
      </div>

      {error && (
        <div className="text-sm text-red-400 bg-red-950/50 border border-red-900 rounded px-3 py-2 mb-4">
          {error}
        </div>
      )}

      <div className="bg-slate-900 border border-slate-800 rounded-lg overflow-hidden overflow-x-auto">
        {loading ? (
          <div className="p-8 text-center text-slate-500 text-sm">Loading...</div>
        ) : entries.length === 0 ? (
          <div className="p-8 text-center text-slate-500 text-sm">No matching audit log entries.</div>
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-slate-800/50 text-slate-400 text-xs uppercase">
              <tr>
                <th className="text-left px-4 py-2.5 font-medium">Time</th>
                <th className="text-left px-4 py-2.5 font-medium">Action</th>
                <th className="text-left px-4 py-2.5 font-medium">User</th>
                <th className="text-left px-4 py-2.5 font-medium">Tenant</th>
                <th className="text-left px-4 py-2.5 font-medium">Resource</th>
                <th className="text-left px-4 py-2.5 font-medium">IP</th>
                <th className="text-left px-4 py-2.5 font-medium">Result</th>
                <th className="w-8"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {entries.map((entry) => (
                <Fragment key={entry.id}>
                  <tr
                    className="cursor-pointer hover:bg-slate-800/30"
                    onClick={() => setExpanded(expanded === entry.id ? null : entry.id)}
                  >
                    <td className="px-4 py-2.5 text-slate-400 whitespace-nowrap">
                      {new Date(entry.timestamp).toLocaleString()}
                    </td>
                    <td className="px-4 py-2.5">{entry.action_display}</td>
                    <td className="px-4 py-2.5 text-slate-400">{entry.username || '—'}</td>
                    <td className="px-4 py-2.5 text-slate-400">{entry.tenant_name || '—'}</td>
                    <td className="px-4 py-2.5 text-slate-400">
                      {entry.resource_type ? `${entry.resource_type} ${entry.resource_id}` : '—'}
                    </td>
                    <td className="px-4 py-2.5 text-slate-400">{entry.ip_address || '—'}</td>
                    <td className="px-4 py-2.5">
                      <span
                        className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs ${
                          entry.success ? 'bg-emerald-950 text-emerald-400' : 'bg-red-950 text-red-400'
                        }`}
                      >
                        {entry.success ? 'OK' : 'Failed'}
                      </span>
                    </td>
                    <td className="px-4 py-2.5 text-slate-500">
                      {expanded === entry.id ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                    </td>
                  </tr>
                  {expanded === entry.id && (
                    <tr className="bg-slate-950/50">
                      <td colSpan={8} className="px-4 py-3">
                        {entry.error_message && (
                          <div className="text-xs text-red-400 mb-2">{entry.error_message}</div>
                        )}
                        <pre className="text-xs text-slate-400 whitespace-pre-wrap break-all">
                          {JSON.stringify(entry.details, null, 2)}
                        </pre>
                      </td>
                    </tr>
                  )}
                </Fragment>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {count > pageSize && (
        <div className="flex items-center justify-between mt-4 text-sm text-slate-400">
          <span>
            Page {page} of {totalPages} ({count} entries)
          </span>
          <div className="flex gap-2">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page <= 1}
              className="px-3 py-1.5 rounded-md border border-slate-800 hover:bg-slate-800 transition disabled:opacity-50"
            >
              Previous
            </button>
            <button
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page >= totalPages}
              className="px-3 py-1.5 rounded-md border border-slate-800 hover:bg-slate-800 transition disabled:opacity-50"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default function OwnerAuditLogsPage() {
  return (
    <PlatformOwnerRoute>
      <AuditLogsPage />
    </PlatformOwnerRoute>
  );
}
