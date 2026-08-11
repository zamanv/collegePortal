from django.contrib import messages
from django.shortcuts import redirect, render

from accounts.decorators import student_required
from accounts.validators import (
    DEFAULT_MAX_IMAGE_SIZE_MB,
    ImageTypeValidator,
    MaxImageSizeValidator,
)
from faculty.models import course, department
from students.models import student_profile

# Create your views here.


@student_required
def dashboard(request):
    return render(request, "students/student_dash.html")


@student_required
def s_profile(request):
    profile = student_profile.objects.filter(user=request.user).first()
    if profile is None:
        messages.warning(request, "Your student profile is missing. Please contact an admin.")
        return redirect("stud_dash")
    context = {
        "profile": profile,
        "departments": department.objects.all(),
        "courses": course.objects.all(),
    }
    return render(request, "students/stud_myprofile.html", context)


@student_required
def edit_profile(request):
    profile = student_profile.objects.filter(user=request.user).first()
    if profile is None:
        messages.warning(request, "Your student profile is missing. Please contact an admin.")
        return redirect("stud_dash")

    if request.method == "POST":
        fullname = (request.POST.get("fullname") or "").strip()
        if fullname:
            profile.fullname = fullname

        department_id = request.POST.get("department")
        profile.department = department.objects.filter(pk=department_id).first() if department_id else None

        course_id = request.POST.get("course")
        profile.course = course.objects.filter(pk=course_id).first() if course_id else None

        semester = request.POST.get("semester")
        profile.semester = int(semester) if semester and semester.isdigit() else None

        ktu_id = (request.POST.get("ktu_id") or "").strip()
        profile.ktu_id = ktu_id or None

        ph_no = (request.POST.get("ph_no") or "").strip()
        profile.ph_no = ph_no or None

        roll_no = request.POST.get("roll_no")
        profile.roll_no = int(roll_no) if roll_no and roll_no.isdigit() else None

        dob = request.POST.get("dob")
        profile.dob = dob or None

        cgpa = request.POST.get("cgpa")
        profile.cgpa = float(cgpa) if cgpa else None

        image = request.FILES.get("profile_image")
        if image:
            type_validator = ImageTypeValidator()
            size_validator = MaxImageSizeValidator(max_mb=DEFAULT_MAX_IMAGE_SIZE_MB)
            try:
                type_validator(image)
                size_validator(image)
            except Exception as exc:
                messages.error(request, str(exc))
                return redirect("stud_profile")
            profile.profile_image = image

        try:
            profile.save()
            messages.success(request, "Profile updated successfully!")
        except Exception:
            messages.error(request, "Could not save profile. Please check the values.")
            return redirect("stud_profile")

        return redirect("stud_profile")

    return redirect("stud_profile")
