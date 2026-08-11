from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from faculty.models import course, department
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
