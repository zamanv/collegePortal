from django.contrib import admin

from faculty.models import (
    attendance,
    attendance_session,
    attendance_token,
    course,
    department,
    faculty_profile,
    grade,
    subject,
)


@admin.register(department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "created_at")
    list_display_links = ("name", "code")
    search_fields = ("name", "code")
    ordering = ("name",)
    readonly_fields = ("created_at", "updated_at")

    def get_courses_count(self, obj):
        return obj.courses.count()

    get_courses_count.short_description = "Courses"


@admin.register(course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "department", "duration_semesters")
    list_filter = ("department",)
    search_fields = ("name", "code", "department__name")
    autocomplete_fields = ("department",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "course", "semester", "credits", "assigned_faculty")
    list_filter = ("semester", "course__department")
    search_fields = ("code", "name", "course__name")
    autocomplete_fields = ("course", "assigned_faculty")
    readonly_fields = ("created_at", "updated_at")


@admin.register(faculty_profile)
class FacultyProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "fullname", "designation", "department", "employee_id", "ph_no")
    search_fields = ("fullname", "user__username", "user__email", "employee_id")
    list_filter = ("department", "designation")
    autocomplete_fields = ("user", "department")
    readonly_fields = ("created_at", "updated_at")


@admin.register(grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ("student", "subject", "semester", "marks", "grade_value", "grade_point", "entered_by")
    list_filter = ("semester", "subject__course__department")
    search_fields = (
        "student__fullname",
        "student__ktu_id",
        "subject__name",
        "subject__code",
    )
    autocomplete_fields = ("student", "subject", "entered_by")
    readonly_fields = ("created_at", "updated_at")


@admin.register(attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("date", "student", "subject", "status", "marked_by")
    list_filter = ("date", "status", "subject__course__department")
    search_fields = ("student__fullname", "student__ktu_id", "subject__name")
    autocomplete_fields = ("student", "subject", "session", "marked_by")
    date_hierarchy = "date"
    readonly_fields = ("created_at", "updated_at")


@admin.register(attendance_session)
class AttendanceSessionAdmin(admin.ModelAdmin):
    list_display = ("id", "subject", "faculty", "status", "started_at", "closed_at")
    list_filter = ("status", "started_at")
    search_fields = ("subject__name", "subject__code", "faculty__username")
    autocomplete_fields = ("subject", "faculty")
    readonly_fields = ("created_at",)

    def has_add_permission(self, request):
        return False


@admin.register(attendance_token)
class AttendanceTokenAdmin(admin.ModelAdmin):
    list_display = ("id", "session", "expires_at", "consumed", "created_at")
    list_filter = ("consumed", "expires_at")
    search_fields = ("token_hash", "session__subject__name")
    readonly_fields = ("token_hash", "expires_at", "consumed", "created_at")

    def has_add_permission(self, request):
        return False
