import axios, { AxiosInstance } from 'axios';
import { ENDPOINTS } from './api-config';
import { fetchCSRFToken } from './csrf';

/**
 * Platform-owner API client.
 *
 * Deliberately its own axios instance, separate from `lib/api.ts`'s `api`
 * export. The owner session lives in its own cookies (po_access_token /
 * po_refresh_token, set by the backend's saas-admin/auth/ views) and must
 * never be mixed with a tenant session's 401/refresh handling - reusing the
 * shared `api` instance would retry a platform-owner 401 against the
 * *tenant* token refresh endpoint, which has no idea about this session.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_BASE
  || (process.env.NODE_ENV === 'production' ? 'http://blueolive-backend:8000' : 'http://localhost:8000');

export const platformApi: AxiosInstance = axios.create({
  baseURL: API_BASE,
  withCredentials: true,
  timeout: 60000,
});

let isRefreshing = false;
let failedQueue: Array<{ resolve: () => void; reject: (err: unknown) => void }> = [];

function processQueue(error: unknown) {
  failedQueue.forEach(({ resolve, reject }) => (error ? reject(error) : resolve()));
  failedQueue = [];
}

platformApi.interceptors.request.use(async (config) => {
  if (config.method && ['post', 'put', 'patch', 'delete'].includes(config.method.toLowerCase())) {
    const token = await fetchCSRFToken();
    if (token) {
      config.headers['X-CSRFToken'] = token;
    }
  }
  return config;
});

platformApi.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    const isProfileCheck = (originalRequest?.url || '').includes(ENDPOINTS.SAAS_ADMIN.AUTH_PROFILE);

    if (error.response?.status === 401 && originalRequest && !originalRequest._retry && !isProfileCheck) {
      originalRequest._retry = true;

      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve: () => resolve(platformApi(originalRequest)), reject });
        });
      }

      isRefreshing = true;
      try {
        await platformApi.post(ENDPOINTS.SAAS_ADMIN.AUTH_TOKEN_REFRESH);
        isRefreshing = false;
        processQueue(null);
        return platformApi(originalRequest);
      } catch (refreshError) {
        isRefreshing = false;
        processQueue(refreshError);
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export interface PlatformOwner {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  is_superuser: true;
}

export interface Tenant {
  id: number;
  name: string;
  phone: string;
  email: string;
  slug: string;
  subdomain: string;
  company_name: string;
  company_address: string;
  vat_number: string;
  registration_number: string;
  currency_symbol: string;
  currency_code: string;
  setup_status: 'pending' | 'db_ready' | 'ready' | 'failed';
  is_active: boolean;
  enabled_addons: string[];
  created_at: string;
  shops?: { id: number; name: string; subdomain: string; is_head_office: boolean }[];
  user_count?: number;
}

export interface TenantStats {
  total_tenants: number;
  active_tenants: number;
  inactive_tenants: number;
  total_shops: number;
  active_shops: number;
}

export async function platformLogin(username: string, password: string) {
  const response = await platformApi.post(ENDPOINTS.SAAS_ADMIN.AUTH_LOGIN, { username, password });
  return response.data.user as PlatformOwner;
}

export async function platformLogout() {
  await platformApi.post(ENDPOINTS.SAAS_ADMIN.AUTH_LOGOUT);
}

export async function fetchPlatformProfile() {
  const response = await platformApi.get(ENDPOINTS.SAAS_ADMIN.AUTH_PROFILE);
  return response.data as PlatformOwner;
}

export async function fetchTenantStats() {
  const response = await platformApi.get(ENDPOINTS.SAAS_ADMIN.TENANT_STATS);
  return response.data as TenantStats;
}

export async function fetchTenants() {
  const response = await platformApi.get(ENDPOINTS.SAAS_ADMIN.TENANTS);
  const data = response.data;
  return (Array.isArray(data) ? data : data.results) as Tenant[];
}

export interface CreateTenantPayload {
  name: string;
  email: string;
  phone: string;
  password: string;
  company_name?: string;
}

export async function createTenant(payload: CreateTenantPayload) {
  const response = await platformApi.post(ENDPOINTS.SAAS_ADMIN.TENANTS, payload);
  return response.data as Tenant;
}

export async function fetchTenant(id: number) {
  const response = await platformApi.get(ENDPOINTS.SAAS_ADMIN.TENANT_DETAIL(id));
  return response.data as Tenant;
}

export async function updateTenantAddons(id: number, enabledAddons: string[]) {
  const response = await platformApi.patch(ENDPOINTS.SAAS_ADMIN.TENANT_DETAIL(id), {
    enabled_addons: enabledAddons,
  });
  return response.data as Tenant;
}

export async function activateTenant(id: number) {
  const response = await platformApi.post(ENDPOINTS.SAAS_ADMIN.TENANT_ACTIVATE(id));
  return response.data;
}

export async function deactivateTenant(id: number) {
  const response = await platformApi.post(ENDPOINTS.SAAS_ADMIN.TENANT_DEACTIVATE(id));
  return response.data;
}

// ===== Shops =====

export interface Shop {
  id: number;
  tenant: number;
  tenant_name: string;
  name: string;
  code: string | null;
  address: string | null;
  phone: string | null;
  email: string | null;
  description: string | null;
  schema_name: string;
  subdomain: string;
  is_head_office: boolean;
  is_active: boolean;
  setup_status: 'pending' | 'ready' | 'failed';
  created_at: string;
}

export async function fetchShops(tenantId: number) {
  const response = await platformApi.get(ENDPOINTS.SAAS_ADMIN.SHOPS, {
    params: { tenant_id: tenantId },
  });
  const data = response.data;
  return (Array.isArray(data) ? data : data.results) as Shop[];
}

export interface CreateShopPayload {
  tenant_id: number;
  name: string;
  code?: string;
  address?: string;
  phone?: string;
  email?: string;
  description?: string;
  is_head_office?: boolean;
}

export async function createShop(payload: CreateShopPayload) {
  const response = await platformApi.post(ENDPOINTS.SAAS_ADMIN.SHOPS, payload);
  return response.data as Shop;
}

export async function activateShop(id: number) {
  const response = await platformApi.post(ENDPOINTS.SAAS_ADMIN.SHOP_ACTIVATE(id));
  return response.data;
}

export async function deactivateShop(id: number) {
  const response = await platformApi.post(ENDPOINTS.SAAS_ADMIN.SHOP_DEACTIVATE(id));
  return response.data;
}

// ===== Cross-tenant users =====

export interface TenantUser {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  role: string;
  is_active: boolean;
  created_at: string;
  last_login: string | null;
}

export async function fetchTenantUsers(tenantId: number) {
  const response = await platformApi.get(ENDPOINTS.SAAS_ADMIN.USERS_LIST, {
    params: { tenant_id: tenantId },
  });
  return response.data.users as TenantUser[];
}

export interface CreateTenantAdminPayload {
  tenant_id: number;
  username: string;
  email: string;
  password: string;
  first_name?: string;
  last_name?: string;
}

export async function createTenantAdmin(payload: CreateTenantAdminPayload) {
  const response = await platformApi.post(ENDPOINTS.SAAS_ADMIN.USERS_CREATE_ADMIN, payload);
  return response.data;
}

export async function toggleTenantUserStatus(userId: number) {
  const response = await platformApi.post(ENDPOINTS.SAAS_ADMIN.USERS_TOGGLE_STATUS, {
    user_id: userId,
  });
  return response.data;
}

export async function resetTenantUserPassword(userId: number, newPassword: string) {
  const response = await platformApi.post(ENDPOINTS.SAAS_ADMIN.USERS_RESET_PASSWORD, {
    user_id: userId,
    new_password: newPassword,
  });
  return response.data;
}

// ===== Platform superuser accounts (owner accounts, not tenant users) =====

export interface Superuser {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  is_active: boolean;
  is_superuser: true;
  date_joined: string;
}

export async function fetchSuperusers() {
  const response = await platformApi.get(ENDPOINTS.USERS.SUPERUSERS);
  const data = response.data;
  return (Array.isArray(data) ? data : data.results) as Superuser[];
}

export interface CreateSuperuserPayload {
  username: string;
  email: string;
  password: string;
  first_name?: string;
  last_name?: string;
}

export async function createSuperuser(payload: CreateSuperuserPayload) {
  const response = await platformApi.post(ENDPOINTS.USERS.SUPERUSERS, {
    ...payload,
    is_superuser: true,
  });
  return response.data as Superuser;
}

export async function toggleSuperuserActive(id: number) {
  const response = await platformApi.post(ENDPOINTS.USERS.SUPERUSER_TOGGLE_ACTIVE(id));
  return response.data;
}

export async function setSuperuserPassword(id: number, password: string) {
  const response = await platformApi.post(ENDPOINTS.USERS.SUPERUSER_SET_PASSWORD(id), {
    password,
  });
  return response.data;
}

// ===== Billing (subscription tiers, subscriptions, payments) =====

export interface SubscriptionPlan {
  id: number;
  name: string;
  slug: string;
  description: string;
  price: string;
  setup_fee: string;
  billing_period_days: 30 | 90 | 365;
  billing_period_display: string;
  max_shops: number;
  max_users: number;
  max_invoices_per_month: number;
  features: Record<string, boolean>;
  is_active: boolean;
  is_trial: boolean;
  sort_order: number;
  created_at: string;
  updated_at: string;
}

export type CreateSubscriptionPlanPayload = Partial<
  Omit<SubscriptionPlan, 'id' | 'billing_period_display' | 'created_at' | 'updated_at'>
> & { name: string; slug: string; price: string };

export async function fetchSubscriptionPlans() {
  const response = await platformApi.get(ENDPOINTS.SAAS_ADMIN.SUBSCRIPTION_PLANS);
  const data = response.data;
  return (Array.isArray(data) ? data : data.results) as SubscriptionPlan[];
}

export async function createSubscriptionPlan(payload: CreateSubscriptionPlanPayload) {
  const response = await platformApi.post(ENDPOINTS.SAAS_ADMIN.SUBSCRIPTION_PLANS, payload);
  return response.data as SubscriptionPlan;
}

export async function updateSubscriptionPlan(id: number, payload: Partial<CreateSubscriptionPlanPayload>) {
  const response = await platformApi.patch(ENDPOINTS.SAAS_ADMIN.SUBSCRIPTION_PLAN_DETAIL(id), payload);
  return response.data as SubscriptionPlan;
}

export interface SubscriptionPayment {
  id: number;
  subscription: number;
  amount: string;
  currency: string;
  payment_method: string;
  payment_method_display: string;
  status: 'PENDING' | 'PROCESSING' | 'SUCCEEDED' | 'FAILED' | 'REFUNDED' | 'VOIDED';
  status_display: string;
  gateway_payment_id: string;
  gateway_reference: string;
  paid_at: string | null;
  failed_at: string | null;
  description: string;
  invoice_number: string;
  created_at: string;
  updated_at: string;
}

export interface Subscription {
  id: number;
  tenant: number;
  tenant_name: string;
  plan: SubscriptionPlan;
  status: 'TRIAL' | 'ACTIVE' | 'PAST_DUE' | 'CANCELLED' | 'EXPIRED' | 'SUSPENDED';
  status_display: string;
  start_date: string;
  end_date: string;
  trial_end_date: string | null;
  cancelled_at: string | null;
  auto_renew: boolean;
  current_period_start: string | null;
  current_period_end: string | null;
  invoices_this_period: number;
  gateway_customer_id: string;
  gateway_subscription_id: string;
  is_active_display: boolean;
  is_trial_display: boolean;
  is_expired_display: boolean;
  days_remaining: number;
  payments: SubscriptionPayment[];
  created_at: string;
  updated_at: string;
}

export interface BillingOverview {
  status_counts: Record<Subscription['status'], number>;
  mrr: string;
  revenue_this_month: string;
  total_subscriptions: number;
  expiring_within_7_days: number;
}

export async function fetchBillingOverview() {
  const response = await platformApi.get(ENDPOINTS.SAAS_ADMIN.SUBSCRIPTION_OVERVIEW);
  return response.data as BillingOverview;
}

export async function fetchSubscriptions(params?: { tenant_id?: number; status?: string }) {
  const response = await platformApi.get(ENDPOINTS.SAAS_ADMIN.SUBSCRIPTIONS, { params });
  const data = response.data;
  return (Array.isArray(data) ? data : data.results) as Subscription[];
}

export interface CreateSubscriptionPayload {
  tenant: number;
  plan: number;
  auto_renew?: boolean;
}

export async function createSubscription(payload: CreateSubscriptionPayload) {
  const response = await platformApi.post(ENDPOINTS.SAAS_ADMIN.SUBSCRIPTIONS, payload);
  return response.data as Subscription;
}

export async function changeSubscriptionPlan(id: number, planId: number) {
  const response = await platformApi.post(ENDPOINTS.SAAS_ADMIN.SUBSCRIPTION_CHANGE_PLAN(id), {
    plan_id: planId,
  });
  return response.data as Subscription;
}

export async function cancelSubscription(id: number, immediately: boolean, reason?: string) {
  const response = await platformApi.post(ENDPOINTS.SAAS_ADMIN.SUBSCRIPTION_CANCEL(id), {
    immediately,
    reason,
  });
  return response.data as Subscription;
}

export async function renewSubscription(id: number) {
  const response = await platformApi.post(ENDPOINTS.SAAS_ADMIN.SUBSCRIPTION_RENEW(id));
  return response.data as Subscription;
}

export async function suspendSubscription(id: number) {
  const response = await platformApi.post(ENDPOINTS.SAAS_ADMIN.SUBSCRIPTION_SUSPEND(id));
  return response.data as Subscription;
}

export async function reactivateSubscription(id: number) {
  const response = await platformApi.post(ENDPOINTS.SAAS_ADMIN.SUBSCRIPTION_REACTIVATE(id));
  return response.data as Subscription;
}

export async function fetchSubscriptionPayments(subscriptionId?: number) {
  const response = await platformApi.get(ENDPOINTS.SAAS_ADMIN.SUBSCRIPTION_PAYMENTS, {
    params: subscriptionId ? { subscription_id: subscriptionId } : undefined,
  });
  const data = response.data;
  return (Array.isArray(data) ? data : data.results) as SubscriptionPayment[];
}

export async function refundSubscriptionPayment(id: number) {
  const response = await platformApi.post(ENDPOINTS.SAAS_ADMIN.SUBSCRIPTION_PAYMENT_REFUND(id));
  return response.data as SubscriptionPayment;
}

// ===== Audit log =====

export const AUDIT_ACTIONS = [
  'LOGIN',
  'LOGOUT',
  'LOGIN_FAILED',
  'USER_CREATE',
  'USER_UPDATE',
  'USER_DELETE',
  'PERMISSION_CHANGE',
  'ROLE_CHANGE',
  'TENANT_ACCESS',
  'SUPERUSER_IMPERSONATION',
  'DATA_ACCESS',
  'PASSWORD_CHANGE',
  'POS_POSTED',
  'POS_CANCELLED',
] as const;

export type AuditAction = (typeof AUDIT_ACTIONS)[number];

export interface AuditLogEntry {
  id: number;
  action: AuditAction;
  action_display: string;
  user_id: number | null;
  username: string;
  tenant_id: number | null;
  tenant_name: string | null;
  resource_type: string;
  resource_id: string;
  ip_address: string | null;
  details: Record<string, unknown>;
  success: boolean;
  error_message: string;
  timestamp: string;
}

export interface AuditLogPage {
  count: number;
  next: string | null;
  previous: string | null;
  results: AuditLogEntry[];
}

export async function fetchAuditLogs(params?: {
  action?: string;
  tenant_id?: number;
  success?: boolean;
  search?: string;
  page?: number;
}) {
  const response = await platformApi.get(ENDPOINTS.SAAS_ADMIN.AUDIT_LOGS, { params });
  return response.data as AuditLogPage;
}

// ===== Provisioning health =====

export interface ProvisioningTenant {
  id: number;
  name: string;
  slug: string;
  setup_status: 'pending' | 'db_ready' | 'ready' | 'failed';
  setup_error: string;
  created_at: string;
  minutes_since_created: number;
}

export interface ProvisioningShop {
  id: number;
  name: string;
  tenant_id: number;
  tenant_name: string;
  setup_status: 'pending' | 'ready' | 'failed';
  setup_error: string;
  created_at: string;
  minutes_since_created: number;
}

export interface ProvisioningHealth {
  tenants: ProvisioningTenant[];
  shops: ProvisioningShop[];
}

export async function fetchProvisioningHealth() {
  const response = await platformApi.get(ENDPOINTS.SAAS_ADMIN.PROVISIONING_HEALTH);
  return response.data as ProvisioningHealth;
}

export async function retryTenantProvisioning(id: number) {
  const response = await platformApi.post(ENDPOINTS.SAAS_ADMIN.RETRY_TENANT_PROVISIONING(id));
  return response.data as { message: string };
}

export async function retryShopProvisioning(id: number) {
  const response = await platformApi.post(ENDPOINTS.SAAS_ADMIN.RETRY_SHOP_PROVISIONING(id));
  return response.data as { message: string };
}

// ===== Support login (tenant impersonation) =====

export async function startSupportLogin(tenantId: number, userId: number, reason?: string) {
  const response = await platformApi.post(ENDPOINTS.SAAS_ADMIN.TENANT_SUPPORT_LOGIN(tenantId), {
    user_id: userId,
    reason,
  });
  return response.data as { redirect_url: string };
}
