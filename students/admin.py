from django.contrib import admin

from students.models import student_profile


@admin.register(student_profile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ("fullname", "ktu_id", "roll_no", "department", "course", "semester", "cgpa")
    list_filter = ("department", "course", "semester")
    search_fields = ("fullname", "ktu_id", "user__username", "user__email")
    autocomplete_fields = ("user", "department", "course")
    readonly_fields = ("created_at", "updated_at")
