'use client';

import { Suspense, useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import axios from 'axios';
import { ENDPOINTS, API_BASE_URL } from '@/lib/api-config';

/**
 * Landing page for the platform-owner's "Support Login" action (see
 * admin/app/tenants/[id]/page.tsx). Exchanges the one-time code in the URL
 * for a real tenant session, then hard-redirects into /dashboard so
 * AuthProvider re-bootstraps from scratch against the new cookies (see
 * lib/AuthContext.tsx's initial refetch() effect) - no client-side state
 * threading needed.
 *
 * A plain axios call (not the shared `api` instance from lib/api.ts):
 * that instance's interceptors assume an existing session (401 -> refresh
 * retry), which doesn't apply here - there is no session yet.
 */
function SupportLoginExchange() {
  const searchParams = useSearchParams();
  const [status, setStatus] = useState<'exchanging' | 'error'>('exchanging');
  const [error, setError] = useState('');

  useEffect(() => {
    const code = searchParams.get('code');
    if (!code) {
      setStatus('error');
      setError('Missing support login code.');
      return;
    }

    axios
      .post(
        `${API_BASE_URL}${ENDPOINTS.AUTH.SUPPORT_LOGIN_EXCHANGE}`,
        { code },
        { withCredentials: true }
      )
      .then(() => {
        // eslint-disable-next-line @next/next/no-location-assign-relative-destination
        window.location.href = '/dashboard';
      })
      .catch((err) => {
        setStatus('error');
        setError(err?.response?.data?.detail || 'This support login link is invalid or has expired.');
      });
  }, [searchParams]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="w-full max-w-sm text-center">
        {status === 'exchanging' ? (
          <>
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-400 mx-auto mb-4" />
            <p className="text-sm text-gray-600">Signing you in...</p>
          </>
        ) : (
          <>
            <p className="text-sm text-red-600 mb-4">{error}</p>
            <a href="/login" className="text-sm text-blue-600 hover:underline">
              Go to login
            </a>
          </>
        )}
      </div>
    </div>
  );
}

export default function SupportLoginPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-400" />
        </div>
      }
    >
      <SupportLoginExchange />
    </Suspense>
  );
}
