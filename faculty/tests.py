from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from accounts.models import User
from faculty.models import (
    attendance,
    attendance_session,
    attendance_token,
    course,
    department,
    faculty_profile,
    subject,
)
from faculty.services import (
    AttendanceTokenError,
    InvalidAttendanceToken,
    _hash_token,
    cleanup_expired,
    close_session,
    consume_token,
    issue_token,
    start_session,
    validate_token,
)
from students.models import student_profile


class QRAttendanceBase(TestCase):
    def setUp(self):
        self.dept = department.objects.create(name="Computer Science", code="CS")
        self.course = course.objects.create(
            name="B.Tech CSE", code="BTCSE", department=self.dept
        )
        self.subject = subject.objects.create(
            name="Data Structures", code="DS301", course=self.course, semester=3
        )
        self.teacher = User.objects.create_user(username="t", password="testpass123")
        self.teacher.role = User.Role.TEACHER
        self.teacher.save(update_fields=["role"])
        faculty_profile.objects.create(user=self.teacher)
        self.student = User.objects.create_user(username="s", password="testpass123")
        self.student_profile = student_profile.objects.create(user=self.student)
        self.session = start_session(self.teacher, self.subject)


class TokenLifecycleTests(QRAttendanceBase):
    def test_issue_token_stores_only_hash(self):
        token = issue_token(self.session)
        row = attendance_token.objects.get()
        self.assertEqual(len(row.token_hash), 64)
        self.assertNotEqual(row.token_hash, token)
        self.assertNotIn(token, row.token_hash)

    def test_validate_returns_session(self):
        token = issue_token(self.session)
        self.assertEqual(validate_token(token), self.session)

    def test_invalid_token_raises(self):
        with self.assertRaises(InvalidAttendanceToken):
            validate_token("not-a-real-token")

    def test_missing_token_raises(self):
        with self.assertRaises(InvalidAttendanceToken):
            validate_token("")

    def test_expired_token_raises(self):
        token = issue_token(self.session, ttl_seconds=1)
        row = attendance_token.objects.get()
        row.expires_at = timezone.now() - timedelta(seconds=1)
        row.save(update_fields=["expires_at"])
        with self.assertRaises(AttendanceTokenError):
            validate_token(token)

    def test_replayed_token_raises(self):
        token = issue_token(self.session)
        consume_token(token, self.student_profile)
        with self.assertRaises(AttendanceTokenError):
            validate_token(token)
        with self.assertRaises(AttendanceTokenError):
            consume_token(token, self.student_profile)

    def test_closed_session_rejects_tokens(self):
        token = issue_token(self.session)
        close_session(self.session)
        with self.assertRaises(AttendanceTokenError):
            validate_token(token)

    def test_cannot_issue_token_for_closed_session(self):
        close_session(self.session)
        with self.assertRaises(AttendanceTokenError):
            issue_token(self.session)


class TokenConsumptionTests(QRAttendanceBase):
    def test_consume_creates_attendance_record(self):
        token = issue_token(self.session)
        record = consume_token(token, self.student_profile)
        self.assertEqual(record.status, attendance.Status.PRESENT)
        self.assertEqual(record.student, self.student_profile)
        self.assertEqual(record.subject, self.subject)
        self.assertEqual(record.marked_by, self.teacher)
        self.assertEqual(record.session, self.session)
        self.assertTrue(
            attendance_token.objects.get().consumed,
        )

    def test_two_tokens_same_date_keep_single_record(self):
        token1 = issue_token(self.session)
        consume_token(token1, self.student_profile)
        token2 = issue_token(self.session)
        consume_token(token2, self.student_profile)
        self.assertEqual(attendance.objects.count(), 1)

    def test_consume_uses_provided_date(self):
        token = issue_token(self.session)
        record = consume_token(token, self.student_profile, date="2026-01-15")
        self.assertEqual(record.date.isoformat(), "2026-01-15")


class CleanupTests(QRAttendanceBase):
    def test_cleanup_expired_tokens_and_stale_sessions(self):
        stale_session = start_session(self.teacher, self.subject)
        stale_session.started_at = timezone.now() - timedelta(hours=2)
        stale_session.save(update_fields=["started_at"])

        token = issue_token(self.session)
        token_obj = attendance_token.objects.get(token_hash=_hash_token(token))
        token_obj.expires_at = timezone.now() - timedelta(hours=25)
        token_obj.save(update_fields=["expires_at"])

        tokens_deleted, sessions_closed = cleanup_expired()
        self.assertEqual(tokens_deleted, 1)
        self.assertEqual(sessions_closed, 1)
        stale_session.refresh_from_db()
        self.assertEqual(stale_session.status, attendance_session.Status.CLOSED)
