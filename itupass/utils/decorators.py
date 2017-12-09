from functools import wraps
from flask import request, redirect, url_for
from flask_login import current_user


def admin_required(f):
    @wraps(f)
    def decorator_function(*args, **kwargs):
        if current_user and not current_user.is_staff:
            return redirect(url_for('client.index'))
        return f(*args, **kwargs)
    return decorator_function
