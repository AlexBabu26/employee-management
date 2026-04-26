from django.conf import settings
from django.db import models


class UserProfile(models.Model):
    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        EMPLOYEE = "employee", "Employee"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    role = models.CharField(
        max_length=20, choices=Role.choices, default=Role.EMPLOYEE, db_index=True
    )

    def is_admin(self):
        return self.role == self.Role.ADMIN

    def is_employee_role(self):
        return self.role == self.Role.EMPLOYEE

    def __str__(self):
        return f"{self.user.username} ({self.role})"
