/**
 * API endpoint configuration for the admin app.
 * Deliberately a trimmed-down copy of frontend/lib/api-config.ts - this app
 * only ever talks to the CSRF endpoint (shared Django CSRF cookie) and the
 * saas-admin API, never any tenant-scoped endpoint.
 */

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000';
export const API_V1_BASE = `/api/v1`;

export const ENDPOINTS = {
  AUTH: {
    CSRF: `${API_V1_BASE}/users/auth/csrf/`,
  },

  SAAS_ADMIN: {
    AUTH_LOGIN: `${API_V1_BASE}/saas-admin/auth/login/`,
    AUTH_LOGOUT: `${API_V1_BASE}/saas-admin/auth/logout/`,
    AUTH_PROFILE: `${API_V1_BASE}/saas-admin/auth/profile/`,
    AUTH_TOKEN_REFRESH: `${API_V1_BASE}/saas-admin/auth/token/refresh/`,
    TENANTS: `${API_V1_BASE}/saas-admin/tenants/`,
    TENANT_DETAIL: (id: number | string) => `${API_V1_BASE}/saas-admin/tenants/${id}/`,
    TENANT_ACTIVATE: (id: number | string) => `${API_V1_BASE}/saas-admin/tenants/${id}/activate/`,
    TENANT_DEACTIVATE: (id: number | string) => `${API_V1_BASE}/saas-admin/tenants/${id}/deactivate/`,
    TENANT_SUPPORT_LOGIN: (id: number | string) => `${API_V1_BASE}/saas-admin/tenants/${id}/support-login/`,
    SHOPS: `${API_V1_BASE}/saas-admin/shops/`,
    SHOP_DETAIL: (id: number | string) => `${API_V1_BASE}/saas-admin/shops/${id}/`,
    SHOP_ACTIVATE: (id: number | string) => `${API_V1_BASE}/saas-admin/shops/${id}/activate/`,
    SHOP_DEACTIVATE: (id: number | string) => `${API_V1_BASE}/saas-admin/shops/${id}/deactivate/`,
    TENANT_STATS: `${API_V1_BASE}/saas-admin/tenant-stats/`,
    USERS_CREATE_ADMIN: `${API_V1_BASE}/saas-admin/users/create-admin/`,
    USERS_LIST: `${API_V1_BASE}/saas-admin/users/`,
    USERS_TOGGLE_STATUS: `${API_V1_BASE}/saas-admin/users/toggle-status/`,
    USERS_RESET_PASSWORD: `${API_V1_BASE}/saas-admin/users/reset-password/`,
    USERS_ASSIGN_SHOPS: `${API_V1_BASE}/saas-admin/users/assign-shops/`,
    IMPORT_TENANTS: `${API_V1_BASE}/saas-admin/import/tenants/`,
    IMPORT_ANALYZE: `${API_V1_BASE}/saas-admin/import/analyze/`,
    IMPORT_EXECUTE: `${API_V1_BASE}/saas-admin/import/execute/`,

    // Billing (platform-wide subscription/tier management)
    SUBSCRIPTION_PLANS: `${API_V1_BASE}/saas-admin/subscription-plans/`,
    SUBSCRIPTION_PLAN_DETAIL: (id: number | string) => `${API_V1_BASE}/saas-admin/subscription-plans/${id}/`,
    SUBSCRIPTIONS: `${API_V1_BASE}/saas-admin/subscriptions/`,
    SUBSCRIPTION_DETAIL: (id: number | string) => `${API_V1_BASE}/saas-admin/subscriptions/${id}/`,
    SUBSCRIPTION_OVERVIEW: `${API_V1_BASE}/saas-admin/subscriptions/overview/`,
    SUBSCRIPTION_CANCEL: (id: number | string) => `${API_V1_BASE}/saas-admin/subscriptions/${id}/cancel/`,
    SUBSCRIPTION_RENEW: (id: number | string) => `${API_V1_BASE}/saas-admin/subscriptions/${id}/renew/`,
    SUBSCRIPTION_CHANGE_PLAN: (id: number | string) => `${API_V1_BASE}/saas-admin/subscriptions/${id}/change_plan/`,
    SUBSCRIPTION_SUSPEND: (id: number | string) => `${API_V1_BASE}/saas-admin/subscriptions/${id}/suspend/`,
    SUBSCRIPTION_REACTIVATE: (id: number | string) => `${API_V1_BASE}/saas-admin/subscriptions/${id}/reactivate/`,
    SUBSCRIPTION_PAYMENTS: `${API_V1_BASE}/saas-admin/subscription-payments/`,
    SUBSCRIPTION_PAYMENT_PROCESS: (id: number | string) => `${API_V1_BASE}/saas-admin/subscription-payments/${id}/process/`,
    SUBSCRIPTION_PAYMENT_REFUND: (id: number | string) => `${API_V1_BASE}/saas-admin/subscription-payments/${id}/refund/`,

    // Audit log
    AUDIT_LOGS: `${API_V1_BASE}/saas-admin/audit-logs/`,

    // Provisioning health
    PROVISIONING_HEALTH: `${API_V1_BASE}/saas-admin/provisioning/`,
    RETRY_TENANT_PROVISIONING: (id: number | string) => `${API_V1_BASE}/saas-admin/provisioning/tenants/${id}/retry/`,
    RETRY_SHOP_PROVISIONING: (id: number | string) => `${API_V1_BASE}/saas-admin/provisioning/shops/${id}/retry/`,
  },

  USERS: {
    SUPERUSERS: `${API_V1_BASE}/users/auth/admin/superusers/`,
    SUPERUSER_DETAIL: (id: number | string) => `${API_V1_BASE}/users/auth/admin/superusers/${id}/`,
    SUPERUSER_SET_PASSWORD: (id: number | string) => `${API_V1_BASE}/users/auth/admin/superusers/${id}/set_password/`,
    SUPERUSER_TOGGLE_ACTIVE: (id: number | string) => `${API_V1_BASE}/users/auth/admin/superusers/${id}/toggle_active/`,
  },
} as const;
