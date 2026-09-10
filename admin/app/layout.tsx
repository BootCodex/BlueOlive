import type { Metadata, Viewport } from 'next';
import './globals.css';
import { PlatformAuthProvider } from '@/lib/PlatformAuthContext';

/**
 * Root layout for the standalone admin app (formerly frontend's /owner/*
 * section). Kept as its own Next.js app - not a route group inside the
 * tenant-facing frontend - so the SaaS platform owner's code, auth session,
 * and deployment are fully isolated from tenant staff. See
 * lib/platformApi.ts for why the session itself (po_access_token cookie,
 * is_platform_owner JWT claim) is already independent of tenant auth.
 */
export const metadata: Metadata = {
  title: 'BlueOlive Admin',
  description: 'SaaS platform owner console for BlueOlive',
};

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 5,
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-slate-950 text-slate-100">
        <PlatformAuthProvider>{children}</PlatformAuthProvider>
      </body>
    </html>
  );
}
