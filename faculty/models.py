from django.conf import settings
from django.db import models

from accounts.validators import ImageTypeValidator, MaxImageSizeValidator


class department(models.Model):
    """Academic department (e.g. Computer Science & Engineering)."""

    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "departments"

    def __str__(self):
        return self.name


class course(models.Model):
    """Course / degree programme offered by a department."""

    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(
        department,
        on_delete=models.PROTECT,
        related_name="courses",
        help_text="Department that owns this course.",
    )
    duration_semesters = models.PositiveSmallIntegerField(default=8)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "courses"

    def __str__(self):
        return f"{self.name} ({self.code})"


class subject(models.Model):
    """Subject taught within a course, tied to a semester."""

    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    course = models.ForeignKey(course, on_delete=models.CASCADE, related_name="subjects")
    semester = models.PositiveSmallIntegerField()
    credits = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    assigned_faculty = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_subjects",
        help_text="Faculty member responsible for this subject.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["semester", "name"]
        verbose_name_plural = "subjects"
        indexes = [
            models.Index(fields=["course", "semester"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"


class faculty_profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="faculty_profile",
    )
    fullname = models.CharField(max_length=100, null=True, blank=True)
    designation = models.CharField(max_length=100, null=True, blank=True)
    department = models.ForeignKey(
        department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="faculty_profiles",
    )
    employee_id = models.CharField(max_length=20, null=True, blank=True)
    ph_no = models.CharField(max_length=15, null=True, blank=True)
    profile_image = models.ImageField(
        upload_to="profile_images",
        blank=True,
        validators=[ImageTypeValidator(), MaxImageSizeValidator()],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "faculty profiles"

    def __str__(self):
        return self.fullname or self.user.get_username()


class grade(models.Model):
    """Academic grade for a student, subject and semester (one per combo)."""

    student = models.ForeignKey(
        "students.student_profile",
        on_delete=models.CASCADE,
        related_name="grades",
    )
    subject = models.ForeignKey(subject, on_delete=models.PROTECT, related_name="grades")
    semester = models.PositiveSmallIntegerField()
    marks = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    grade_value = models.CharField(max_length=2, null=True, blank=True)
    grade_point = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    entered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="entered_grades",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["semester", "subject__name"]
        verbose_name_plural = "grades"
        indexes = [
            models.Index(fields=["student", "semester"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["student", "subject", "semester"],
                name="unique_grade_per_student_subject_semester",
            )
        ]

    def __str__(self):
        return f"{self.student} - {self.subject} (Sem {self.semester})"


class attendance_session(models.Model):
    """A time-bound attendance window started by a faculty member.

    Tokens issued against an open session expire every ~30 seconds and are
    validated server-side when a student checks in.
    """

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        CLOSED = "closed", "Closed"

    faculty = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="attendance_sessions",
    )
    subject = models.ForeignKey(subject, on_delete=models.CASCADE, related_name="attendance_sessions")
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.OPEN,
        db_index=True,
    )
    started_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-started_at"]
        verbose_name_plural = "attendance sessions"

    def __str__(self):
        return f"{self.subject} by {self.faculty} ({self.status})"

    def close(self):
        from django.utils import timezone

        if self.status == self.Status.OPEN:
            self.status = self.Status.CLOSED
            self.closed_at = timezone.now()
            self.save(update_fields=["status", "closed_at"])


class attendance_token(models.Model):
    """A short-lived signed attendance token.

    Only the SHA-256 hash of the opaque token is stored; the plaintext value
    is returned to the caller once when the token is issued.
    """

    session = models.ForeignKey(
        attendance_session,
        on_delete=models.CASCADE,
        related_name="tokens",
    )
    token_hash = models.CharField(max_length=64, unique=True)
    expires_at = models.DateTimeField(db_index=True)
    consumed = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "attendance tokens"

    def __str__(self):
        return f"Token for session #{self.session_id} (expires {self.expires_at:%H:%M:%S})"


class attendance(models.Model):
    """Daily attendance record for a student/subject.

    One record per student, subject and date (enforced by a DB constraint).
    """

    class Status(models.TextChoices):
        PRESENT = "present", "Present"
        ABSENT = "absent", "Absent"

    student = models.ForeignKey(
        "students.student_profile",
        on_delete=models.CASCADE,
        related_name="attendance_records",
    )
    subject = models.ForeignKey(subject, on_delete=models.PROTECT, related_name="attendance_records")
    session = models.ForeignKey(
        attendance_session,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="records",
        help_text="Attendance session this record was created through, if any.",
    )
    date = models.DateField(db_index=True)
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PRESENT,
    )
    marked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="marked_attendance",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date"]
        verbose_name_plural = "attendance records"
        indexes = [
            models.Index(fields=["subject", "date"]),
            models.Index(fields=["student", "subject"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["student", "subject", "date"],
                name="unique_attendance_per_student_subject_date",
            )
        ]

    def __str__(self):
        return f"{self.student} - {self.subject} on {self.date}"
