from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class faculty_profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fullname = models.CharField(max_length=150, null=True, blank=True)
    designation = models.CharField(max_length=100, null=True, blank=True)
    department = models.CharField(max_length=100, blank=True)
    ph_no = models.CharField(max_length=15, null=True, blank=True)

    def __str__(self):
        return f"{self.fullname or self.user.username} - {self.department}"