'use client';

import { useEffect, useState } from 'react';
import { ShieldAlert } from 'lucide-react';
import { logout } from '@/lib/api';

/**
 * Persistent banner shown while the current tenant session was started via
 * the platform-owner's "Support Login" (see app/support-login/page.tsx).
 * The support_session_username cookie is deliberately non-httpOnly and
 * purely a client-side display hint - it carries no authority itself, the
 * real session is the httpOnly access_token/refresh_token cookies set
 * alongside it.
 */
function readCookie(name: string): string | null {
  if (typeof document === 'undefined') return null;
  for (let cookie of document.cookie.split(';')) {
    cookie = cookie.trim();
    if (cookie.startsWith(`${name}=`)) {
      return decodeURIComponent(cookie.substring(name.length + 1));
    }
  }
  return null;
}

function clearCookie(name: string) {
  document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/`;
}

export default function SupportSessionBanner() {
  const [supportUser, setSupportUser] = useState<string | null>(null);
  const [endingSession, setEndingSession] = useState(false);

  useEffect(() => {
    setSupportUser(readCookie('support_session_username'));
  }, []);

  if (!supportUser) return null;

  const handleEndSession = async () => {
    setEndingSession(true);
    try {
      await logout();
    } catch {
      // Continue anyway - cookies may already be cleared server-side.
    } finally {
      clearCookie('support_session_username');
      // eslint-disable-next-line @next/next/no-location-assign-relative-destination
      window.location.href = '/login';
    }
  };

  return (
    <div className="bg-amber-500 text-amber-950 px-4 py-2 text-sm flex items-center justify-between gap-3">
      <div className="flex items-center gap-2">
        <ShieldAlert className="h-4 w-4 shrink-0" />
        <span>
          Support session active - signed in by <strong>{supportUser}</strong>
        </span>
      </div>
      <button
        onClick={handleEndSession}
        disabled={endingSession}
        className="px-2.5 py-1 rounded-md bg-amber-950 text-amber-50 text-xs font-medium hover:bg-amber-900 transition disabled:opacity-50"
      >
        {endingSession ? 'Ending...' : 'End Session'}
      </button>
    </div>
  );
}
