from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class Employee(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="employee"
    )
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    department = models.CharField(max_length=120, blank=True)
    designation = models.CharField(max_length=120, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    date_joined = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["full_name"]
        verbose_name = "Employee"
        verbose_name_plural = "Employees"

    def __str__(self):
        return self.full_name


class Task(models.Model):
    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        CRITICAL = "critical", "Critical"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        OVERDUE = "overdue", "Overdue"

    title = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True)
    assigned_to = models.ForeignKey(
        Employee, on_delete=models.PROTECT, related_name="tasks"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="tasks_created",
    )
    priority = models.CharField(
        max_length=20, choices=Priority.choices, default=Priority.MEDIUM, db_index=True
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True
    )
    start_date = models.DateField()
    due_date = models.DateField(db_index=True)
    estimated_hours = models.DecimalField(
        max_digits=6, decimal_places=1, default=0, validators=[MinValueValidator(0)]
    )
    actual_hours = models.DecimalField(
        max_digits=6,
        decimal_places=1,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
    )
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Task"
        verbose_name_plural = "Tasks"

    def __str__(self):
        return self.title


class AISuggestion(models.Model):
    class PeriodType(models.TextChoices):
        DAILY = "daily", "Daily"
        WEEKLY = "weekly", "Weekly"
        MONTHLY = "monthly", "Monthly"

    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ai_suggestions"
    )
    suggestion_text = models.TextField()
    input_summary = models.TextField(blank=True)
    period_type = models.CharField(
        max_length=20, choices=PeriodType.choices, default=PeriodType.WEEKLY
    )
    model_used = models.CharField(max_length=120, blank=True, default="")
    reasoning_text = models.TextField(blank=True, default="")
    reasoning_details = models.JSONField(blank=True, default=list)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        ordering = ["-created_at"]


# Keep overdue status in sync with due dates
def refresh_task_overdue_status():
    today = timezone.now().date()
    Task.objects.filter(
        due_date__lt=today,
    ).exclude(status=Task.Status.COMPLETED).update(status=Task.Status.OVERDUE)
