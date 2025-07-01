from django.http import HttpResponseForbidden
from functools import wraps

def student_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.shortcuts import redirect
            return redirect('/login/')
        if request.user.is_staff or request.user.is_superuser:
            return HttpResponseForbidden("Admins are not allowed to access student pages.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
            from django.shortcuts import redirect
            return redirect('/admin/login/')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
