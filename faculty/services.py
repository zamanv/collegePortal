"""Server-side foundation for dynamic QR attendance.

Future teacher (QR generation / screen projection) and student (check-in
scanner) views should call these functions instead of touching the token
tables directly.

Design notes:
  * A faculty member starts an :class:`attendance_session` for a subject.
  * Short-lived tokens are issued against the session (default TTL 30 s).
  * Only the SHA-256 hash of the token is stored in the database; the
    plaintext value is returned exactly once to the caller.
  * Validation rejects expired, unknown, already-consumed (replayed) and
    closed-session tokens on the server side.
"""

import hashlib
import secrets
from datetime import date as date_type
from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from faculty.models import attendance, attendance_session, attendance_token

TOKEN_TTL_SECONDS = 30

EXPIRED_TOKEN_RETENTION = timedelta(hours=24)
STALE_SESSION_AGE = timedelta(hours=1)


class AttendanceTokenError(Exception):
    """Base error for the QR attendance token workflow."""


class InvalidAttendanceToken(AttendanceTokenError):
    """The token is unknown, malformed or not issued by the system."""


def _hash_token(token):
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def start_session(faculty, subject):
    """Start an open attendance session for ``subject`` by ``faculty``."""
    return attendance_session.objects.create(faculty=faculty, subject=subject)


def issue_token(session, ttl_seconds=TOKEN_TTL_SECONDS):
    """Issue a short-lived token for an open ``session``.

    Returns the plaintext token string (safe to render into a QR code).  Only
    the hash is persisted.  Raises :class:`AttendanceTokenError` if the
    session is not open.
    """
    if session.status != attendance_session.Status.OPEN:
        raise AttendanceTokenError("Cannot issue a token for a session that is not open.")

    token = secrets.token_urlsafe(32)
    attendance_token.objects.create(
        session=session,
        token_hash=_hash_token(token),
        expires_at=timezone.now() + timedelta(seconds=ttl_seconds),
    )
    return token


def validate_token(token):
    """Validate ``token`` and return its session.

    Raises :class:`AttendanceTokenError` (subclasses) for expired, invalid,
    replayed or closed-session tokens.  Does not mark the token consumed;
    use :func:`consume_token` to record attendance.
    """
    if not token:
        raise InvalidAttendanceToken("Missing token.")

    row = attendance_token.objects.select_related("session").filter(
        token_hash=_hash_token(token)
    ).first()

    if row is None:
        raise InvalidAttendanceToken("Invalid token.")

    if row.consumed:
        raise AttendanceTokenError("Token has already been used.")

    if timezone.now() > row.expires_at:
        raise AttendanceTokenError("Token has expired.")

    if row.session.status != attendance_session.Status.OPEN:
        raise AttendanceTokenError("Attendance session is closed.")

    return row.session


@transaction.atomic
def consume_token(token, student_profile, date=None):
    """Validate ``token`` and mark ``student_profile`` present for its session.

    Returns the :class:`attendance` record (created or updated).  Concurrency
    safe: the token row is locked before consumption to prevent replay.
    """
    session = validate_token(token)

    token_obj = attendance_token.objects.select_for_update().get(
        token_hash=_hash_token(token)
    )
    if token_obj.consumed:
        raise AttendanceTokenError("Token has already been used.")
    token_obj.consumed = True
    token_obj.save(update_fields=["consumed"])

    mark_date = date or timezone.localdate()
    if isinstance(mark_date, str):
        mark_date = date_type.fromisoformat(mark_date)

    record, _created = attendance.objects.update_or_create(
        student=student_profile,
        subject=session.subject,
        date=mark_date,
        defaults={
            "session": session,
            "status": attendance.Status.PRESENT,
            "marked_by": session.faculty,
        },
    )
    return record


def close_session(session):
    """Close an attendance session and reject any further tokens."""
    session.close()
    return session


def cleanup_expired():
    """Remove stale tokens and auto-close abandoned sessions.

    Safe to call from a management command or periodic job.
    """
    now = timezone.now()

    token_count, _ = attendance_token.objects.filter(
        expires_at__lt=now - EXPIRED_TOKEN_RETENTION
    ).delete()

    session_count = attendance_session.objects.filter(
        status=attendance_session.Status.OPEN,
        started_at__lt=now - STALE_SESSION_AGE,
    ).update(status=attendance_session.Status.CLOSED, closed_at=now)

    return token_count, session_count
