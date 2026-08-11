from django.contrib import messages
from django.shortcuts import redirect, render

from accounts.decorators import teacher_required
from accounts.validators import (
    DEFAULT_MAX_IMAGE_SIZE_MB,
    ImageTypeValidator,
    MaxImageSizeValidator,
)
from faculty.models import department, faculty_profile

# Create your views here.


@teacher_required
def dashboard(request):
    return render(request, "faculty/faculty_dash.html")


@teacher_required
def f_profile(request):
    profile = faculty_profile.objects.filter(user=request.user).first()
    if profile is None:
        messages.warning(request, "Your faculty profile is missing. Please contact an admin.")
        return redirect("facu_dash")
    context = {
        "profile": profile,
        "departments": department.objects.all(),
    }
    return render(request, "faculty/faculty_myprofile.html", context)


@teacher_required
def f_edit_profile(request):
    profile = faculty_profile.objects.filter(user=request.user).first()
    if profile is None:
        messages.warning(request, "Your faculty profile is missing. Please contact an admin.")
        return redirect("facu_dash")

    if request.method == "POST":
        fullname = (request.POST.get("fullname") or "").strip()
        profile.fullname = fullname or None

        department_id = request.POST.get("department")
        profile.department = department.objects.filter(pk=department_id).first() if department_id else None

        designation = (request.POST.get("designation") or "").strip()
        profile.designation = designation or None

        employee_id = (request.POST.get("employee_id") or "").strip()
        profile.employee_id = employee_id or None

        ph_no = (request.POST.get("ph_no") or "").strip()
        profile.ph_no = ph_no or None

        email = (request.POST.get("email") or "").strip()
        if email:
            request.user.email = email
            request.user.save()

        image = request.FILES.get("profile_image")
        if image:
            type_validator = ImageTypeValidator()
            size_validator = MaxImageSizeValidator(max_mb=DEFAULT_MAX_IMAGE_SIZE_MB)
            try:
                type_validator(image)
                size_validator(image)
            except Exception as exc:
                messages.error(request, str(exc))
                return redirect("facu_profile")
            profile.profile_image = image

        profile.save()
        messages.success(request, "Profile updated successfully!")
        return redirect("facu_profile")

    return redirect("facu_profile")
