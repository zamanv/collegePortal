from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from accounts.models import AuditLog, User
from faculty.models import faculty_profile
from students.models import student_profile


class StudentProfileInline(admin.StackedInline):
    model = student_profile
    extra = 0
    can_delete = False


class FacultyProfileInline(admin.StackedInline):
    model = faculty_profile
    extra = 0
    can_delete = False


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("username", "email", "role", "is_staff", "is_active", "date_joined")
    list_filter = ("role", "is_staff", "is_active", "is_superuser")
    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ("-date_joined",)
    inlines = [StudentProfileInline, FacultyProfileInline]

    fieldsets = BaseUserAdmin.fieldsets + (
        ("Portal role", {"fields": ("role",)}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("Portal role", {"fields": ("role",)}),
    )


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Audit entries are view-only for everyone (including superusers)."""

    list_display = ("created_at", "actor", "action", "model_name", "object_repr")
    list_filter = ("action", "model_name", "created_at")
    search_fields = ("object_repr", "model_name", "actor__username")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    readonly_fields = (
        "actor",
        "action",
        "model_name",
        "object_id",
        "object_repr",
        "details",
        "created_at",
    )

    def has_view_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return False
