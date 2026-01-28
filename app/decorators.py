from flask_login import current_user
from flask import abort
from functools import wraps

def role_required(role_name):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)

            if current_user.role.name != role_name:
                abort(403)

            return func(*args, **kwargs)
        return wrapper
    return decorator
