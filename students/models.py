from django.conf import settings
from django.db import models

from accounts.validators import ImageTypeValidator, MaxImageSizeValidator


class student_profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="student_profile",
    )
    fullname = models.CharField(max_length=100, blank=True, default="")
    department = models.ForeignKey(
        "faculty.department",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="student_profiles",
    )
    course = models.ForeignKey(
        "faculty.course",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="student_profiles",
    )
    semester = models.PositiveSmallIntegerField(null=True, blank=True)
    ktu_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    ph_no = models.CharField(max_length=15, null=True, blank=True)
    roll_no = models.IntegerField(null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    cgpa = models.FloatField(null=True, blank=True)
    profile_image = models.ImageField(
        upload_to="profile_images/",
        default="default.png",
        blank=True,
        validators=[ImageTypeValidator(), MaxImageSizeValidator()],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["fullname"]
        verbose_name_plural = "student profiles"
        indexes = [
            models.Index(fields=["department", "course"]),
        ]

    def __str__(self):
        return self.fullname or self.user.get_username()
