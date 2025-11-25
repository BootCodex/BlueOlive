# tenancy/tenant_context.py
import threading

_thread_locals = threading.local()

# ----------------------------
# Tenant getters/setters
# ----------------------------
def set_current_tenant(tenant):
    _thread_locals.tenant = tenant

def get_current_tenant():
    return getattr(_thread_locals, "tenant", None)

def clear_current_tenant():
    if hasattr(_thread_locals, "tenant"):
        delattr(_thread_locals, "tenant")

# ----------------------------
# Shop getters/setters
# ----------------------------
def set_current_shop(shop_schema_name):
    _thread_locals.shop_schema = shop_schema_name

def get_current_shop():
    return getattr(_thread_locals, "shop_schema", None)

def clear_current_shop():
    if hasattr(_thread_locals, "shop_schema"):
        delattr(_thread_locals, "shop_schema")

# ----------------------------
# Clear everything
# ----------------------------
def clear_current():
    clear_current_tenant()
    clear_current_shop()
