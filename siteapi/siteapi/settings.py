
try:
    from .settings_debug import SECRET_KEY as DEBUG_SECRET_KEY
    SECRET_KEY = DEBUG_SECRET_KEY
except ModuleNotFoundError:
    pass

try:
    from .settings_prod import SECRET_KEY as PRODUCTION_SECRET_KEY
    SECRET_KEY = PRODUCTION_SECRET_KEY
except ModuleNotFoundError:
    pass
