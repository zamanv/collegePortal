import json
from collections import defaultdict

from django.contrib import messages
from django.core.files.storage import default_storage
from django.shortcuts import redirect, render

from accounts.decorators import student_required
from faculty.models import attendance, course, department, grade
from students.forms import StudentProfileForm
from students.models import student_profile

ATTENDANCE_THRESHOLD_PCT = 75

# Create your views here.


def _get_student_profile(request):
    """Return the logged-in student's profile, or None if missing."""
    return student_profile.objects.filter(user=request.user).first()


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


def _attendance_stats(profile):
    """Aggregate attendance records into per-subject stats.

    Returns (subject_stats, overall_pct) where subject_stats is a list of
    dicts with name/total/present/absent/pct and overall_pct is the overall
    attendance percentage (None when there are no records).
    """
    buckets = defaultdict(lambda: {"total": 0, "present": 0})
    for rec in attendance.objects.filter(student=profile).select_related("subject"):
        bucket = buckets[rec.subject.name]
        bucket["total"] += 1
        if rec.status == attendance.Status.PRESENT:
            bucket["present"] += 1

    subject_stats = []
    total = present = 0
    for name, bucket in sorted(buckets.items()):
        total += bucket["total"]
        present += bucket["present"]
        subject_stats.append(
            {
                "name": name,
                "total": bucket["total"],
                "present": bucket["present"],
                "absent": bucket["total"] - bucket["present"],
                "pct": round(bucket["present"] / bucket["total"] * 100, 1)
                if bucket["total"]
                else 0.0,
            }
        )

    overall_pct = round(present / total * 100, 1) if total else None
    return subject_stats, overall_pct


def _gpa_series(profile):
    """Credits-weighted GPA per semester from the student's grades."""
    weighted = defaultdict(lambda: {"points": 0.0, "credits": 0.0})
    for g in grade.objects.filter(student=profile).select_related("subject"):
        if g.grade_point is None:
            continue
        credits = float(g.subject.credits or 0) if g.subject else 0.0
        weighted[g.semester]["points"] += float(g.grade_point) * credits
        weighted[g.semester]["credits"] += credits

    return [
        {
            "semester": sem,
            "gpa": round(data["points"] / data["credits"], 2) if data["credits"] else None,
        }
        for sem, data in sorted(weighted.items())
    ]


@student_required
def dashboard(request):
    profile = _get_student_profile(request)
    if profile is None:
        messages.warning(request, "Your student profile is missing. Please contact an admin.")
        return redirect("stud_dash")

    subject_stats, overall_att_pct = _attendance_stats(profile)
    gpa_series = _gpa_series(profile)
    low_attendance = [s for s in subject_stats if s["pct"] < ATTENDANCE_THRESHOLD_PCT]

    context = {
        "profile": profile,
        "gpa_series_json": json.dumps(gpa_series),
        "attendance_series_json": json.dumps(subject_stats),
        "overall_att_pct": overall_att_pct,
        "attendance_threshold": ATTENDANCE_THRESHOLD_PCT,
        "low_attendance": low_attendance,
        "subject_count": len(subject_stats),
    }
    return render(request, "students/student_dash.html", context)


@student_required
def grades(request):
    profile = _get_student_profile(request)
    if profile is None:
        messages.warning(request, "Your student profile is missing. Please contact an admin.")
        return redirect("stud_dash")

    by_semester = defaultdict(list)
    for g in (
        grade.objects.filter(student=profile)
        .select_related("subject", "subject__course")
        .order_by("semester", "subject__name")
    ):
        by_semester[g.semester].append(g)

    semester_blocks = []
    for sem in sorted(by_semester.keys(), reverse=True):
        items = by_semester[sem]
        points = sum(
            float(g.grade_point or 0) * float(g.subject.credits or 0) for g in items
        )
        credits = sum(float(g.subject.credits or 0) for g in items)
        semester_blocks.append(
            {
                "semester": sem,
                "gpa": round(points / credits, 2) if credits else None,
                "grades": items,
            }
        )

    context = {
        "profile": profile,
        "semester_blocks": semester_blocks,
        "grade_count": grade.objects.filter(student=profile).count(),
        "overall_cgpa": profile.cgpa,
    }
    return render(request, "students/grades.html", context)


@student_required
def attendance_history(request):
    profile = _get_student_profile(request)
    if profile is None:
        messages.warning(request, "Your student profile is missing. Please contact an admin.")
        return redirect("stud_dash")

    subject_stats, overall_att_pct = _attendance_stats(profile)
    low_attendance = [s for s in subject_stats if s["pct"] < ATTENDANCE_THRESHOLD_PCT]

    recent = (
        attendance.objects.filter(student=profile)
        .select_related("subject", "marked_by")
        .order_by("-date", "-created_at")[:25]
    )

    context = {
        "profile": profile,
        "subjects": subject_stats,
        "overall_att_pct": overall_att_pct,
        "attendance_threshold": ATTENDANCE_THRESHOLD_PCT,
        "low_attendance": low_attendance,
        "recent": recent,
    }
    return render(request, "students/attendance.html", context)


@student_required
def s_profile(request):
    profile = _get_student_profile(request)
    if profile is None:
        messages.warning(request, "Your student profile is missing. Please contact an admin.")
        return redirect("stud_dash")
    context = {
        "profile": profile,
        "departments": department.objects.all(),
        "courses": course.objects.all(),
        **_avatar_context(profile),
    }
    return render(request, "students/stud_myprofile.html", context)


@student_required
def edit_profile(request):
    profile = _get_student_profile(request)
    if profile is None:
        messages.warning(request, "Your student profile is missing. Please contact an admin.")
        return redirect("stud_dash")

    if request.method == "POST":
        form = StudentProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("stud_profile")

        for field_errors in form.errors.values():
            for error in field_errors:
                messages.error(request, error)
        return redirect("stud_profile")

    return redirect("stud_profile")
