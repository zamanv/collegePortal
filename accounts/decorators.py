"""Role-based view decorators.

Usage:
    @student_required
    def my_student_view(request):
        ...

    @teacher_required
    def my_teacher_view(request):
        ...

Unauthenticated users are redirected to the login page; authenticated users
without the required role receive a 403 response.
"""

from functools import wraps

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render

from accounts.models import User
from accounts.roles import is_admin


def _forbidden(request):
    return render(request, "403.html", status=403)


def role_required(*roles):
    """Decorator factory: allow admins plus users with any of ``roles``."""

    def decorator(view_func):
        @wraps(view_func)
        @login_required(login_url="login_p")
        def _wrapped(request, *args, **kwargs):
            user = request.user
            if is_admin(user) or getattr(user, "role", None) in roles:
                return view_func(request, *args, **kwargs)
            return _forbidden(request)

        return _wrapped

    return decorator


student_required = role_required(User.Role.STUDENT)
teacher_required = role_required(User.Role.TEACHER)
admin_required = role_required(User.Role.ADMIN)
