# BlueOlive Admin

Standalone Next.js app for the SaaS platform owner (real Django superuser) —
tenant CRUD, billing/subscription tiers, and platform owner accounts. This is
a separate deployment from `../frontend` (the tenant-facing app): it has its
own session (`po_access_token` / `po_refresh_token` cookies, `is_platform_owner`
JWT claim), its own login, and no link to or from the tenant dashboard.

## Development

```bash
npm install
npm run dev   # http://localhost:3001
```

The backend must allow this origin — `core.settings.CORS_ALLOWED_ORIGINS` and
`CSRF_TRUSTED_ORIGINS` include `http://localhost:3001` by default. If you
override those env vars in your own `.env`, add port 3001 there too.

Set `NEXT_PUBLIC_API_BASE` if the backend isn't at `http://localhost:8000`.

## Routes

| Path              | Purpose                                   |
|-------------------|--------------------------------------------|
| `/login`          | Platform owner sign-in                     |
| `/`               | Tenant list + stats                        |
| `/tenants/[id]`   | Tenant detail: addons, shops, users        |
| `/billing`        | Subscriptions overview, per-tenant actions |
| `/billing/plans`  | Subscription plan (tier) CRUD              |
| `/superusers`     | Manage other platform owner accounts       |

## Backend

All requests go to `/api/v1/saas-admin/*`, authenticated via
`PlatformOwnerJWTAuthentication` and gated by `IsPlatformSuperuser`
(`backend/core/apps/saas_admin/`). No endpoint here ever resolves a tenant
database — see that app's `permissions.py` and `subscription_views.py` for
why the tenant-facing `/api/v1/subscription/*` endpoints can't be reused
directly from this app.
