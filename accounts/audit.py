"""Audit service.

Provides a small, dependency-free way to record audit entries from anywhere
(signals, views, admin) and to resolve the acting user.  Passwords, tokens and
other secrets must never be written into audit records.
"""

import threading

from accounts.models import AuditLog

_local = threading.local()


def set_current_user(user):
    _local.user = user


def get_current_user():
    return getattr(_local, "user", None)


def write_audit(action, instance, actor=None, details=None):
    """Create an AuditLog entry for ``instance``.

    ``action`` is one of AuditLog.Action values. ``instance`` should be a model
    instance; model name, object id and a readable repr are extracted from it.
    ``details`` must be JSON-serialisable and must not contain secrets.
    """
    if instance is None:
        return

    meta = getattr(instance, "_meta", None)
    model_name = meta.label_lower if meta else "unknown"
    object_id = str(getattr(instance, "pk", "") or "")
    object_repr = str(instance)[:200]

    actor = actor or get_current_user() or None
    if actor is not None and not getattr(actor, "is_authenticated", False):
        actor = None

    AuditLog.objects.create(
        actor=actor,
        action=action,
        model_name=model_name,
        object_id=object_id,
        object_repr=object_repr,
        details=details or {},
    )
