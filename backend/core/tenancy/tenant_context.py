# tenancy/tenant_context.py
import threading

_thread_locals = threading.local()

def set_current_tenant(tenant):
    _thread_locals.tenant = tenant

def get_current_tenant():
    return getattr(_thread_locals, "tenant", None)

def set_current_shop(shop_schema_name):
    _thread_locals.shop_schema = shop_schema_name

def get_current_shop():
    return getattr(_thread_locals, "shop_schema", None)

def clear_current():
    for attr in ("tenant", "shop_schema"):
        if hasattr(_thread_locals, attr):
            delattr(_thread_locals, attr)
