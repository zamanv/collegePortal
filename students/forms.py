import math

from django import forms
from django.utils import timezone

from students.models import student_profile


class StudentProfileForm(forms.ModelForm):
    """Validated form for a student profile.

    Model-level constraints (ktu_id uniqueness, image type/size validators)
    are enforced automatically by the ModelForm; extra cross-field rules are
    added below so bad input is rejected with a friendly message instead of
    crashing or surfacing a raw database error.
    """

    class Meta:
        model = student_profile
        fields = [
            "fullname",
            "department",
            "course",
            "semester",
            "ktu_id",
            "ph_no",
            "roll_no",
            "dob",
            "cgpa",
            "profile_image",
        ]

    def clean_semester(self):
        semester = self.cleaned_data.get("semester")
        if semester is not None and not 1 <= semester <= 8:
            raise forms.ValidationError("Semester must be between 1 and 8.")
        return semester

    def clean_dob(self):
        dob = self.cleaned_data.get("dob")
        if dob and dob > timezone.localdate():
            raise forms.ValidationError("Date of birth cannot be in the future.")
        return dob

    def clean_cgpa(self):
        cgpa = self.cleaned_data.get("cgpa")
        if cgpa is not None:
            if math.isnan(cgpa) or cgpa < 0 or cgpa > 10:
                raise forms.ValidationError("CGPA must be a number between 0 and 10.")
        return cgpa
