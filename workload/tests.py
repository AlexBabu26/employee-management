from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from .models import Employee, Task
from .services.analytics import employee_hour_breakdown


User = get_user_model()


class EmployeeHourBreakdownTests(TestCase):
    def _employee(self, username: str, full_name: str, *, active: bool = True):
        user = User.objects.create_user(username=username, password="testpass123")
        return Employee.objects.create(
            user=user,
            full_name=full_name,
            email=f"{username}@example.com",
            is_active=active,
            date_joined=timezone.now().date(),
        )

    def _task(
        self,
        employee: Employee,
        *,
        status: str,
        estimated: str,
        actual: str | None = None,
    ):
        today = timezone.now().date()
        completed_at = timezone.now() if status == Task.Status.COMPLETED else None
        return Task.objects.create(
            title=f"{employee.full_name} {status}",
            assigned_to=employee,
            created_by=employee.user,
            status=status,
            start_date=today - timedelta(days=1),
            due_date=today + timedelta(days=1),
            estimated_hours=Decimal(estimated),
            actual_hours=Decimal(actual) if actual is not None else None,
            completed_at=completed_at,
        )

    def test_employee_hour_breakdown_separates_open_estimates_from_actual_completed_hours(self):
        alex = self._employee("alex", "Alex")
        blair = self._employee("blair", "Blair")
        inactive = self._employee("casey", "Casey", active=False)

        self._task(alex, status=Task.Status.PENDING, estimated="3.5")
        self._task(alex, status=Task.Status.IN_PROGRESS, estimated="4.0")
        self._task(alex, status=Task.Status.COMPLETED, estimated="8.0", actual="6.5")
        self._task(blair, status=Task.Status.OVERDUE, estimated="2.0")
        self._task(blair, status=Task.Status.COMPLETED, estimated="5.0", actual="7.0")
        self._task(inactive, status=Task.Status.PENDING, estimated="20.0")

        breakdown = employee_hour_breakdown()

        self.assertEqual(
            breakdown,
            [
                {
                    "full_name": "Alex",
                    "open_estimated_hours": 7.5,
                    "actual_completed_hours": 6.5,
                    "open_task_count": 2,
                    "completed_task_count": 1,
                },
                {
                    "full_name": "Blair",
                    "open_estimated_hours": 2.0,
                    "actual_completed_hours": 7.0,
                    "open_task_count": 1,
                    "completed_task_count": 1,
                },
            ],
        )
