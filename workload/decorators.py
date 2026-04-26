from functools import wraps

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import redirect


def admin_only(view_func):
    @wraps(view_func)
    @login_required
    def _wrapped(request, *args, **kwargs):
        p = getattr(request.user, "profile", None)
        if not p or not p.is_admin():
            return HttpResponseForbidden("Admins only.")
        return view_func(request, *args, **kwargs)

    return _wrapped


def employee_only(view_func):
    @wraps(view_func)
    @login_required
    def _wrapped(request, *args, **kwargs):
        p = getattr(request.user, "profile", None)
        if not p or not p.is_employee_role():
            return redirect("workload:admin_dashboard")
        if not hasattr(request.user, "employee"):
            return HttpResponseForbidden("No employee record linked to this account.")
        return view_func(request, *args, **kwargs)

    return _wrapped
