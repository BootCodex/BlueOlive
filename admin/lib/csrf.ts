import axios from 'axios';
import { ENDPOINTS } from './api-config';

/**
 * Minimal CSRF helper, ported from frontend/lib/api.ts's fetchCSRFToken().
 * Django's CSRF cookie is set by any Django response, not saas-admin-
 * specific, so hitting the shared CSRF endpoint and reading the cookie back
 * works the same way here as it does in the tenant-facing app.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000';

let csrfToken: string | null = null;

function getCsrfTokenFromCookie(): string | null {
  const name = 'csrftoken';
  if (typeof document === 'undefined' || !document.cookie) return null;

  for (let cookie of document.cookie.split(';')) {
    cookie = cookie.trim();
    if (cookie.substring(0, name.length + 1) === `${name}=`) {
      return decodeURIComponent(cookie.substring(name.length + 1));
    }
  }
  return null;
}

export async function fetchCSRFToken(): Promise<string> {
  if (csrfToken) return csrfToken;

  try {
    await axios.get(`${API_BASE}${ENDPOINTS.AUTH.CSRF}`, { withCredentials: true });
    const cookieToken = getCsrfTokenFromCookie();
    if (cookieToken) {
      csrfToken = cookieToken;
      return cookieToken;
    }
  } catch {
    const cookieToken = getCsrfTokenFromCookie();
    if (cookieToken) {
      csrfToken = cookieToken;
      return cookieToken;
    }
  }

  return '';
}
