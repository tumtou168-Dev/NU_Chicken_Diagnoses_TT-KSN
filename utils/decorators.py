from functools import wraps
from flask import abort
from flask_login import current_user

def require_permission(perm_slug):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or not current_user.has_permission(perm_slug):
                abort(403) # Forbidden
            return f(*args, **kwargs)
        return decorated_function
    return decorator