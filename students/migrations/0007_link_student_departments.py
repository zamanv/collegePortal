"""
Data migration: link student profiles to the new department model.

Existing ``department_legacy`` text values are normalised into Department
records (get_or_create by code) and linked.  Idempotent and safe on databases
that have no rows.
"""

import re

from django.db import migrations


def _make_code(name):
    code = re.sub(r"[^A-Z0-9]+", "_", name.upper()).strip("_")[:20]
    return code or "GEN"


def link_student_departments(apps, schema_editor):
    StudentProfile = apps.get_model("students", "student_profile")
    Department = apps.get_model("faculty", "department")

    for profile in StudentProfile.objects.all().iterator():
        name = (profile.department_legacy or "").strip()
        if not name:
            continue
        code = _make_code(name)
        dept, _ = Department.objects.get_or_create(
            code=code,
            defaults={"name": name[:100]},
        )
        if profile.department_id != dept.pk:
            profile.department = dept
            profile.save(update_fields=["department"])


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("students", "0006_alter_student_profile_options_student_profile_course_and_more"),
    ]

    operations = [
        migrations.RunPython(link_student_departments, noop),
    ]
