"""Audit logging signals.

Records create/update/delete events for academic and profile models, login
events, and role changes.  Secrets (passwords, tokens) are never logged.
"""

from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from accounts.audit import write_audit
from accounts.models import AuditLog

# (app_label, model_name) pairs that should be audited.  The custom user model
# is audited for create / role-change events only (handled in the receiver).
AUDITED_MODELS = {
    ("accounts", "user"),
    ("faculty", "department"),
    ("faculty", "course"),
    ("faculty", "subject"),
    ("faculty", "grade"),
    ("faculty", "attendance"),
    ("faculty", "faculty_profile"),
    ("students", "student_profile"),
}


def _auditable(sender):
    return sender is not AuditLog and (sender._meta.app_label, sender._meta.model_name) in AUDITED_MODELS


@receiver(post_save)
def audit_model_save(sender, instance, created, **kwargs):
    if not _auditable(sender):
        return

    action = AuditLog.Action.CREATE if created else AuditLog.Action.UPDATE
    details = {}

    if sender._meta.model_name == "user":
        # For users, only record meaningful role changes (never passwords).
        old_role = getattr(instance, "_old_role", None)
        if created:
            details = {"role": instance.role}
        elif old_role is not None and old_role != instance.role:
            details = {"role_old": old_role, "role_new": instance.role}
        else:
            return

    write_audit(action, instance, details=details or None)


@receiver(post_delete)
def audit_model_delete(sender, instance, **kwargs):
    if _auditable(sender):
        write_audit(AuditLog.Action.DELETE, instance, details={"deleted": True})


@receiver(pre_save, sender="accounts.User")
def capture_previous_role(sender, instance, **kwargs):
    if instance.pk:
        try:
            instance._old_role = sender.objects.get(pk=instance.pk).role
        except sender.DoesNotExist:
            instance._old_role = None
    else:
        instance._old_role = None


@receiver(user_logged_in)
def audit_login(sender, request, user, **kwargs):
    write_audit(AuditLog.Action.LOGIN, user, actor=user)
