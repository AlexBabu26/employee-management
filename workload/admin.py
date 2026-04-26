from django.contrib import admin

from .models import AISuggestion, Employee, Task


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("full_name", "user", "department", "is_active", "date_joined")
    list_filter = ("is_active", "department")
    search_fields = ("full_name", "user__username", "email")


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "assigned_to", "status", "priority", "due_date", "created_at")
    list_filter = ("status", "priority", "due_date")
    search_fields = ("title",)
    date_hierarchy = "due_date"


@admin.register(AISuggestion)
class AISuggestionAdmin(admin.ModelAdmin):
    list_display = ("period_type", "created_at", "generated_by")
    list_filter = ("period_type",)
