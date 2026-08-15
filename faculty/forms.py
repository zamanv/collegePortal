from django import forms

from faculty.models import faculty_profile


class FacultyProfileForm(forms.ModelForm):
    """Validated form for a faculty profile.

    ``email`` lives on the user, not the profile, so it is exposed here and
    applied to ``request.user`` by the view. Model-level validators (image
    type/size) are enforced automatically by the ModelForm.
    """

    email = forms.EmailField(required=False)

    class Meta:
        model = faculty_profile
        fields = [
            "fullname",
            "designation",
            "department",
            "employee_id",
            "ph_no",
            "profile_image",
        ]
