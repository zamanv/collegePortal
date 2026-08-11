"""Role helpers.

Central place for role checks so views never hard-code role comparisons.
"""

from accounts.models import User


def is_admin(user):
    """Superusers are always administrators."""
    return bool(
        user
        and user.is_authenticated
        and (user.is_superuser or user.role == User.Role.ADMIN)
    )


def is_teacher(user):
    return bool(user and user.is_authenticated and user.role == User.Role.TEACHER)


def is_student(user):
    return bool(user and user.is_authenticated and user.role == User.Role.STUDENT)


def user_role(user):
    if not user or not user.is_authenticated:
        return None
    return user.role
