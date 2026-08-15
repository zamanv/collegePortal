from datetime import date

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from faculty.models import attendance, course, department, grade, subject
from students.models import student_profile


def create_user(username, role="student"):
    user = User.objects.create_user(username=username, password="testpass123")
    if role != "student":
        user.role = role
        user.save(update_fields=["role"])
    return user


class StudentDashboardAccessTests(TestCase):
    def test_student_can_access_dashboard(self):
        student = create_user("s")
        student_profile.objects.create(user=student)
        self.client.force_login(student)
        response = self.client.get(reverse("stud_dash"))
        self.assertEqual(response.status_code, 200)

    def test_anonymous_redirected_to_login(self):
        response = self.client.get(reverse("stud_dash"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login_p"), response.url)

    def test_teacher_blocked_from_student_dashboard(self):
        teacher = create_user("t", "teacher")
        self.client.force_login(teacher)
        response = self.client.get(reverse("stud_dash"))
        self.assertEqual(response.status_code, 403)

    def test_student_profile_view_without_profile_redirects_gracefully(self):
        student = create_user("noprofile")
        self.client.force_login(student)
        response = self.client.get(reverse("stud_profile"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("stud_dash"))


class StudentProfileEditTests(TestCase):
    def setUp(self):
        self.dept = department.objects.create(name="Computer Science", code="CS")
        self.course = course.objects.create(
            name="B.Tech CSE", code="BTCSE", department=self.dept
        )
        self.student = create_user("s")
        self.profile = student_profile.objects.create(user=self.student)
        self.client.force_login(self.student)

    def test_edit_profile_sets_department_and_course_fk(self):
        response = self.client.post(
            reverse("edit_profile"),
            {
                "fullname": "Adil Zaman",
                "department": self.dept.pk,
                "course": self.course.pk,
                "semester": "3",
                "ktu_id": "KTU2024CS001",
                "ph_no": "9876543210",
                "roll_no": "12",
                "cgpa": "8.75",
            },
        )
        self.assertRedirects(response, reverse("stud_profile"))
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.fullname, "Adil Zaman")
        self.assertEqual(self.profile.department, self.dept)
        self.assertEqual(self.profile.course, self.course)
        self.assertEqual(self.profile.semester, 3)
        self.assertEqual(self.profile.ktu_id, "KTU2024CS001")

    def test_edit_profile_without_department_clears_fk(self):
        self.profile.department = self.dept
        self.profile.save(update_fields=["department"])
        self.client.post(reverse("edit_profile"), {"fullname": "No Dept"})
        self.profile.refresh_from_db()
        self.assertIsNone(self.profile.department)

    def test_edit_profile_rejects_non_image_upload(self):
        response = self.client.post(
            reverse("edit_profile"),
            {
                "fullname": "Adil Zaman",
                "profile_image": SimpleUploadedFile(
                    "x.txt", b"not an image", content_type="text/plain"
                ),
            },
        )
        self.assertRedirects(response, reverse("stud_profile"))
        self.profile.refresh_from_db()
        self.assertFalse(self.profile.profile_image)

    def test_edit_profile_rejects_oversized_image(self):
        response = self.client.post(
            reverse("edit_profile"),
            {
                "fullname": "Adil Zaman",
                "profile_image": SimpleUploadedFile(
                    "big.png", b"x" * (6 * 1024 * 1024), content_type="image/png"
                ),
            },
        )
        self.assertRedirects(response, reverse("stud_profile"))
        self.profile.refresh_from_db()
        self.assertFalse(self.profile.profile_image)


class StudentAvatarTests(TestCase):
    def setUp(self):
        self.student = create_user("s")
        self.profile = student_profile.objects.create(user=self.student)
        self.client.force_login(self.student)

    def test_profile_renders_initials_when_no_image(self):
        self.profile.fullname = "Adil Zaman"
        self.profile.save(update_fields=["fullname"])
        response = self.client.get(reverse("stud_profile"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'class="avatar"')
        self.assertContains(response, "AZ")
        self.assertNotContains(response, "default.png")

    def test_profile_renders_image_when_uploaded(self):
        self.profile.profile_image = SimpleUploadedFile(
            "pic.jpg", b"image-data", content_type="image/jpeg"
        )
        self.profile.save(update_fields=["profile_image"])
        response = self.client.get(reverse("stud_profile"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'class="profile-image"')
        self.assertNotContains(response, 'class="avatar"')


class StudentAcademicViewsTests(TestCase):
    def setUp(self):
        self.dept = department.objects.create(name="Computer Science", code="CS")
        self.course = course.objects.create(
            name="B.Tech CSE", code="BTCSE", department=self.dept
        )
        self.s1 = subject.objects.create(
            name="Data Structures", code="DS301", course=self.course,
            semester=3, credits=4,
        )
        self.s2 = subject.objects.create(
            name="Maths", code="MA302", course=self.course,
            semester=3, credits=3,
        )
        self.student = create_user("s")
        self.profile = student_profile.objects.create(
            user=self.student, semester=3, cgpa=8.5
        )
        grade.objects.create(
            student=self.profile, subject=self.s1, semester=3,
            marks=85, grade_value="A", grade_point=9,
        )
        grade.objects.create(
            student=self.profile, subject=self.s2, semester=3,
            marks=80, grade_value="A", grade_point=8,
        )
        # s1: 75% attendance (not below threshold), s2: 25% (below).
        for i, status in enumerate(
            [attendance.Status.PRESENT] * 3 + [attendance.Status.ABSENT]
        ):
            attendance.objects.create(
                student=self.profile, subject=self.s1,
                date=date(2026, 1, 1 + i), status=status,
            )
        for i, status in enumerate(
            [attendance.Status.PRESENT]
            + [attendance.Status.ABSENT] * 3
        ):
            attendance.objects.create(
                student=self.profile, subject=self.s2,
                date=date(2026, 2, 1 + i), status=status,
            )
        self.client.force_login(self.student)

    def test_dashboard_renders_charts_and_stats(self):
        response = self.client.get(reverse("stud_dash"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Semester GPA")
        self.assertContains(response, "attendanceChart")
        self.assertContains(response, "50.0%")  # overall attendance

    def test_grades_page_groups_by_semester(self):
        response = self.client.get(reverse("stud_grades"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Semester 3")
        self.assertContains(response, "Data Structures")
        self.assertContains(response, "Maths")

    def test_attendance_page_flags_low_attendance(self):
        response = self.client.get(reverse("stud_attendance"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Below threshold")
        self.assertContains(response, "On track")
        self.assertContains(response, "Maths")

    def test_dashboard_empty_state_renders(self):
        empty = create_user("empty")
        student_profile.objects.create(user=empty)
        self.client.force_login(empty)
        response = self.client.get(reverse("stud_dash"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No grades recorded yet.")

    def test_teacher_blocked_from_student_academic_pages(self):
        teacher = create_user("t", "teacher")
        self.client.force_login(teacher)
        self.assertEqual(self.client.get(reverse("stud_grades")).status_code, 403)
        self.assertEqual(self.client.get(reverse("stud_attendance")).status_code, 403)

    def test_anonymous_redirected_from_attendance_page(self):
        self.client.logout()
        response = self.client.get(reverse("stud_attendance"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login_p"), response.url)
