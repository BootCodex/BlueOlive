"""
Support Login — one-time codes for platform-owner "log in as tenant".

The platform-owner admin app (authenticated as a Django superuser, no tenant
context) can't set cookies on the tenant frontend's origin directly - cookies
are scoped per-origin, and the two apps run on different ports/domains. The
standard workaround: mint a short-lived, single-use, unguessable code on the
platform side, hand the tenant frontend a URL carrying that code, and let the
tenant frontend exchange it (from its own origin, so the resulting cookies
land in the right place) for a real tenant session.

Security properties:
- token_urlsafe(32) is 256 bits of entropy - infeasible to guess within the
  TTL even at high request rates (the exchange endpoint is throttled too).
- Single-use: consume_support_login_code() deletes the cache entry on read,
  so a code can't be replayed even if it leaks (browser history, logs).
- Short TTL: unused codes expire quickly, shrinking the window for a leaked
  URL to be replayed.
- Who/why is captured at mint time and audit-logged by the caller
  (TenantAuditLog.log_superuser_impersonation) - this module only handles
  the handoff mechanics, not the audit trail.
"""

import secrets

from django.core.cache import cache

SUPPORT_LOGIN_TTL_SECONDS = 60
_CACHE_KEY_PREFIX = "support_login:"


def generate_support_login_code(*, tenant_id, user_id, superuser_id, superuser_username, reason):
    """Mint a one-time code mapping to a specific tenant user. Returns the code."""
    code = secrets.token_urlsafe(32)
    cache.set(
        f"{_CACHE_KEY_PREFIX}{code}",
        {
            "tenant_id": tenant_id,
            "user_id": user_id,
            "superuser_id": superuser_id,
            "superuser_username": superuser_username,
            "reason": reason or "",
        },
        timeout=SUPPORT_LOGIN_TTL_SECONDS,
    )
    return code


def consume_support_login_code(code):
    """
    Look up and immediately invalidate a one-time code.
    Returns the payload dict, or None if the code is missing/expired/already used.
    """
    key = f"{_CACHE_KEY_PREFIX}{code}"
    payload = cache.get(key)
    if payload is not None:
        cache.delete(key)
    return payload
