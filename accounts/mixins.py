"""Role mixins for class-based views."""

from django.http import HttpResponseForbidden
from django.shortcuts import render

from accounts.roles import is_admin


class RoleRequiredMixin:
    """Mixin for class-based views.

    Set ``allowed_roles`` on the view to a tuple of User.Role values.
    """

    allowed_roles = ()
    login_url = "login_p"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.shortcuts import redirect

            return redirect(self.login_url)
        if is_admin(request.user) or getattr(request.user, "role", None) in self.allowed_roles:
            return super().dispatch(request, *args, **kwargs)
        return render(request, "403.html", status=403)
