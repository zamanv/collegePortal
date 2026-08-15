from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from accounts.audit import set_current_user
from accounts.models import AuditLog, User
from accounts.validators import ImageTypeValidator, MaxImageSizeValidator
from faculty.models import department, faculty_profile
from students.models import student_profile


def create_user(username, role="student", **kwargs):
    user = User.objects.create_user(username=username, password="testpass123", **kwargs)
    if role != "student":
        user.role = role
        user.save(update_fields=["role"])
    return user


class RoleHelperTests(TestCase):
    def test_role_properties(self):
        admin = create_user("admin1", "admin")
        teacher = create_user("teacher1", "teacher")
        student = create_user("student1")

        self.assertTrue(admin.is_admin)
        self.assertFalse(admin.is_teacher)
        self.assertTrue(teacher.is_teacher)
        self.assertFalse(teacher.is_student)
        self.assertTrue(student.is_student)
        self.assertFalse(student.is_admin)

    def test_superuser_is_always_admin(self):
        su = User.objects.create_superuser("root", "root@x.com", "su-per-pass1")
        self.assertTrue(su.is_admin)

    def test_default_role_is_student(self):
        user = User.objects.create_user(username="plain", password="testpass123")
        self.assertEqual(user.role, User.Role.STUDENT)


class LoginRoutingTests(TestCase):
    def setUp(self):
        # The login throttle lives in the process-wide LocMemCache; clear it so
        # failed-attempt counters don't leak between tests.
        cache.clear()

    def test_admin_routes_to_admin_index(self):
        User.objects.create_superuser("a", "a@x.com", "testpass123")
        response = self.client.post(
            reverse("login_p"), {"username": "a", "password": "testpass123"}
        )
        self.assertRedirects(response, reverse("admin:index"))

    def test_student_with_profile_routes_to_dashboard(self):
        student = create_user("s")
        student_profile.objects.create(user=student)
        response = self.client.post(
            reverse("login_p"), {"username": "s", "password": "testpass123"}
        )
        self.assertRedirects(response, reverse("stud_dash"))

    def test_teacher_with_profile_routes_to_faculty_dashboard(self):
        teacher = create_user("t", "teacher")
        faculty_profile.objects.create(user=teacher)
        response = self.client.post(
            reverse("login_p"), {"username": "t", "password": "testpass123"}
        )
        self.assertRedirects(response, reverse("facu_dash"))

    def test_teacher_without_profile_redirects_to_dashboard_without_crash(self):
        create_user("t", "teacher")
        response = self.client.post(
            reverse("login_p"), {"username": "t", "password": "testpass123"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("facu_dash"))

    def test_student_without_profile_redirects_to_dashboard_without_crash(self):
        create_user("s")
        response = self.client.post(
            reverse("login_p"), {"username": "s", "password": "testpass123"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("stud_dash"))

    def test_invalid_credentials_rejected(self):
        create_user("s")
        response = self.client.post(
            reverse("login_p"), {"username": "s", "password": "wrongpass"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid username or password")

    def test_login_throttled_after_max_attempts(self):
        create_user("throttled")
        for _ in range(5):
            self.client.post(
                reverse("login_p"), {"username": "throttled", "password": "wrongpass"}
            )
        response = self.client.post(
            reverse("login_p"), {"username": "throttled", "password": "wrongpass"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Too many failed attempts")

    def test_pending_teacher_login_shows_approval_message(self):
        teacher = create_user("t", "teacher")
        teacher.is_active = False
        teacher.save(update_fields=["is_active"])
        response = self.client.post(
            reverse("login_p"), {"username": "t", "password": "testpass123"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "pending admin approval")

    def test_inactive_teacher_cannot_log_in(self):
        teacher = create_user("t", "teacher")
        teacher.is_active = False
        teacher.save(update_fields=["is_active"])
        self.client.post(
            reverse("login_p"), {"username": "t", "password": "testpass123"}
        )
        response = self.client.get(reverse("facu_dash"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login_p"), response.url)


class RegistrationTests(TestCase):
    def test_student_registration_sets_role_and_creates_profile(self):
        response = self.client.post(
            reverse("stud_reg"),
            {
                "username": "newstud",
                "email": "newstud@college.edu",
                "password1": "strong-pass-123",
                "password2": "strong-pass-123",
            },
        )
        self.assertRedirects(response, reverse("login_p"))
        user = User.objects.get(username="newstud")
        self.assertEqual(user.role, User.Role.STUDENT)
        self.assertTrue(student_profile.objects.filter(user=user).exists())

    def test_faculty_registration_sets_role_and_creates_profile(self):
        response = self.client.post(
            reverse("facu_reg"),
            {
                "username": "newfac",
                "email": "newfac@college.edu",
                "password1": "strong-pass-123",
                "password2": "strong-pass-123",
            },
        )
        self.assertRedirects(response, reverse("login_p"))
        user = User.objects.get(username="newfac")
        self.assertEqual(user.role, User.Role.TEACHER)
        self.assertTrue(faculty_profile.objects.filter(user=user).exists())
        self.assertFalse(user.is_active)  # pending admin approval

    def test_admin_action_approves_inactive_teachers(self):
        User.objects.create_superuser("root", "root@x.com", "su-per-pass1")
        teacher = create_user("t", "teacher")
        teacher.is_active = False
        teacher.save(update_fields=["is_active"])
        self.client.force_login(User.objects.get(username="root"))
        response = self.client.post(
            reverse("admin:accounts_user_changelist"),
            {
                "action": "approve_selected_teachers",
                "_selected_action": [str(teacher.pk)],
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        teacher.refresh_from_db()
        self.assertTrue(teacher.is_active)


class AuditLogTests(TestCase):
    def test_user_create_is_audited(self):
        create_user("audited")
        log = AuditLog.objects.get(model_name="accounts.user")
        self.assertEqual(log.action, AuditLog.Action.CREATE)
        self.assertEqual(log.details.get("role"), User.Role.STUDENT)

    def test_role_change_is_audited(self):
        user = create_user("promoted")
        user.role = User.Role.TEACHER
        user.save(update_fields=["role"])
        logs = AuditLog.objects.filter(
            model_name="accounts.user", action=AuditLog.Action.UPDATE
        ).order_by("created_at")
        self.assertTrue(logs.exists())
        self.assertEqual(logs.last().details.get("role_old"), User.Role.STUDENT)
        self.assertEqual(logs.last().details.get("role_new"), User.Role.TEACHER)

    def test_department_create_is_audited_with_actor(self):
        actor = create_user("admin1", "admin")
        set_current_user(actor)
        try:
            dept = department.objects.create(name="ECE", code="ECE")
        finally:
            set_current_user(None)
        log = AuditLog.objects.get(model_name="faculty.department")
        self.assertEqual(log.actor, actor)
        self.assertEqual(log.object_id, str(dept.pk))

    def test_login_is_audited(self):
        create_user("s")
        self.client.post(
            reverse("login_p"), {"username": "s", "password": "testpass123"}
        )
        log = AuditLog.objects.get(action=AuditLog.Action.LOGIN)
        self.assertEqual(log.model_name, "accounts.user")
        self.assertEqual(log.object_repr, "s")


class ImageValidatorTests(TestCase):
    def test_rejects_disallowed_content_type(self):
        f = SimpleUploadedFile("x.jpg", b"data", content_type="application/x-php")
        with self.assertRaises(Exception):
            ImageTypeValidator()(f)

    def test_rejects_bad_extension(self):
        f = SimpleUploadedFile("x.txt", b"data", content_type="text/plain")
        with self.assertRaises(Exception):
            ImageTypeValidator()(f)

    def test_accepts_valid_image(self):
        f = SimpleUploadedFile("x.jpg", b"data", content_type="image/jpeg")
        ImageTypeValidator()(f)  # should not raise

    def test_rejects_oversized_image(self):
        f = SimpleUploadedFile(
            "big.png", b"x" * (6 * 1024 * 1024), content_type="image/png"
        )
        with self.assertRaises(Exception):
            MaxImageSizeValidator()(f)

    def test_accepts_image_within_limit(self):
        f = SimpleUploadedFile("ok.png", b"x" * 1024, content_type="image/png")
        MaxImageSizeValidator()(f)  # should not raise
