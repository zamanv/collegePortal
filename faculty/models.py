from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class faculty_profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fullname=models.CharField(null=True)
    designation=models.CharField(null=True)
    department = models.CharField(max_length=100, blank=True)
    ph_no=models.CharField(max_length=15,null=True)
      