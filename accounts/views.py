from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.cache import cache
from django.shortcuts import redirect, render

from accounts.forms import createuserform
from accounts.models import User
from faculty.models import faculty_profile
from students.models import student_profile

MAX_LOGIN_ATTEMPTS = 5
LOGIN_LOCKOUT_SECONDS = 300
_LOGIN_ATTEMPTS_KEY = "login_failed_attempts:%s"


def _route_authenticated_user(request, user):
    """Route a successfully authenticated user to the right portal.

    Admins go to the Django admin site. Students and teachers go to their
    portal dashboards; a missing profile is handled gracefully with a warning
    instead of raising DoesNotExist.
    """
    if user.is_superuser or user.role == User.Role.ADMIN:
        messages.success(request, "Welcome back!")
        return redirect("admin:index")

    if user.role == User.Role.TEACHER:
        if faculty_profile.objects.filter(user=user).exists():
            return redirect("facu_dash")
        messages.warning(
            request,
            "Welcome! Complete your faculty profile before using faculty features.",
        )
        return redirect("facu_dash")

    # Student (default role).
    if student_profile.objects.filter(user=user).exists():
        return redirect("stud_dash")
    messages.warning(
        request,
        "Welcome! Complete your student profile before using student features.",
    )
    return redirect("stud_dash")


# Student Registration
def stud_reg(request):
    if request.method == "POST":
        form = createuserform(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.role = User.Role.STUDENT
            user.save()
            form.save_m2m()

            student_profile.objects.create(user=user)

            messages.success(request, "Student registered successfully.")
            return redirect("login_p")

        messages.error(request, "Registration failed. Please correct the errors below.")

    else:
        form = createuserform()

    return render(request, "accounts/studreg.html", {"form": form})


# Faculty Registration
def faculty_reg(request):
    if request.method == "POST":
        form = createuserform(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.role = User.Role.TEACHER
            # Teachers must be approved by an admin before they can log in.
            user.is_active = False
            user.save()
            form.save_m2m()

            faculty_profile.objects.create(user=user)

            messages.success(
                request,
                "Faculty registered successfully. Your account is pending admin approval.",
            )
            return redirect("login_p")

        messages.error(request, "Registration failed. Please correct the errors below.")

    else:
        form = createuserform()

    return render(request, "accounts/facultyreg.html", {"form": form})


# Login
def login_page(request):
    if request.method == "POST":
        username = (request.POST.get("username") or "").strip()
        password = request.POST.get("password")

        key = _LOGIN_ATTEMPTS_KEY % username
        failed = cache.get(key, 0)

        if failed >= MAX_LOGIN_ATTEMPTS:
            messages.error(
                request,
                "Too many failed attempts. Please try again in 5 minutes.",
            )
            return render(request, "accounts/login.html")

        user = authenticate(username=username, password=password)

        if user is not None:
            cache.delete(key)
            login(request, user)
            return _route_authenticated_user(request, user)

        cache.set(key, failed + 1, LOGIN_LOCKOUT_SECONDS)

        existing = User.objects.filter(username=username).first()
        if existing is not None and not existing.is_active:
            messages.error(
                request,
                "Your account is pending admin approval. Please wait for an admin to activate it.",
            )
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "accounts/login.html")


def logout_page(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect("login_p")
