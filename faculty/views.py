from django.contrib import messages
from django.core.files.storage import default_storage
from django.shortcuts import redirect, render

from accounts.decorators import teacher_required
from faculty.forms import FacultyProfileForm
from faculty.models import department, faculty_profile

# Create your views here.


def _get_faculty_profile(request):
    """Return the logged-in faculty's profile, or None if missing."""
    return faculty_profile.objects.filter(user=request.user).first()


def _avatar_context(profile):
    """Whether the profile has a real uploaded image + initials fallback."""
    image = getattr(profile, "profile_image", None)
    has_image = bool(
        image
        and image.name
        and image.name != "default.png"
        and default_storage.exists(image.name)
    )
    name = profile.fullname or profile.user.get_username() or "?"
    initials = "".join(word[0] for word in name.split()[:2]).upper() or "?"
    return {"has_image": has_image, "initials": initials}


@teacher_required
def dashboard(request):
    return render(request, "faculty/faculty_dash.html")


@teacher_required
def f_profile(request):
    profile = _get_faculty_profile(request)
    if profile is None:
        messages.warning(request, "Your faculty profile is missing. Please contact an admin.")
        return redirect("facu_dash")
    context = {
        "profile": profile,
        "departments": department.objects.all(),
        **_avatar_context(profile),
    }
    return render(request, "faculty/faculty_myprofile.html", context)


@teacher_required
def f_edit_profile(request):
    profile = _get_faculty_profile(request)
    if profile is None:
        messages.warning(request, "Your faculty profile is missing. Please contact an admin.")
        return redirect("facu_dash")

    if request.method == "POST":
        form = FacultyProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            email = (form.cleaned_data.get("email") or "").strip()
            if email and email != request.user.email:
                request.user.email = email
                request.user.save()
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("facu_profile")

        for field_errors in form.errors.values():
            for error in field_errors:
                messages.error(request, error)
        return redirect("facu_profile")

    return redirect("facu_profile")
