import json
from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from accounts.models import UserProfile
from workload.models import AISuggestion, Employee, Task, refresh_task_overdue_status

User = get_user_model()

SEED_USER_PREFIX = "seed_user_"


def _remove_existing_seed() -> int:
    """Delete previous seed users and related rows. Returns number of usernames removed."""
    usernames = list(
        User.objects.filter(username__startswith=SEED_USER_PREFIX).values_list(
            "username", flat=True
        )
    )
    if not usernames:
        return 0
    users = User.objects.filter(username__in=usernames)
    emps = Employee.objects.filter(user__in=users)
    Task.objects.filter(assigned_to__in=emps).delete()
    Task.objects.filter(created_by__in=users).delete()
    AISuggestion.objects.filter(generated_by__in=users).delete()
    emps.delete()
    users.delete()
    return len(usernames)


class Command(BaseCommand):
    help = (
        "Create 10 seed rows per app table: User, UserProfile, Employee, Task, AISuggestion. "
        "Usernames are %s01 … %s10. First user is app admin, all have Employee records. "
        "Removes a previous run first."
        % (SEED_USER_PREFIX, SEED_USER_PREFIX)
    )

    @transaction.atomic
    def handle(self, *args, **options):
        n = _remove_existing_seed()
        if n:
            self.stdout.write(f"Removed {n} previous seed user(s) and related data.")

        today = timezone.now().date()
        users: list[User] = []
        for i in range(1, 11):
            u = User.objects.create_user(
                username=f"{SEED_USER_PREFIX}{i:02d}",
                email=f"seed{i:02d}@example.com",
                password="seedpass123",
            )
            if i == 1:
                u.profile.role = UserProfile.Role.ADMIN
                u.profile.save()
            users.append(u)

        employees: list[Employee] = []
        for i, u in enumerate(users, start=1):
            e = Employee.objects.create(
                user=u,
                full_name=f"Seed Employee {i:02d}",
                email=f"seed{i:02d}@example.com",
                department=["Engineering", "Sales", "HR", "Operations", "IT"][(i - 1) % 5],
                designation=["Developer", "Analyst", "Coordinator", "Lead", "Specialist"][
                    (i - 1) % 5
                ],
                is_active=True,
                date_joined=today - timedelta(days=20 * i),
            )
            employees.append(e)

        admin = users[0]
        pr = [
            Task.Priority.LOW,
            Task.Priority.MEDIUM,
            Task.Priority.HIGH,
            Task.Priority.CRITICAL,
        ]
        st = [
            Task.Status.PENDING,
            Task.Status.IN_PROGRESS,
            Task.Status.COMPLETED,
            Task.Status.PENDING,
        ]
        for i in range(10):
            t = Task(
                title=f"Seed Task {i + 1:02d}",
                description=f"Seeded development task {i + 1}.",
                assigned_to=employees[i],
                created_by=admin,
                priority=pr[i % 4],
                start_date=today - timedelta(days=5 + i),
                due_date=today + timedelta(days=(i % 3) - 1),
                estimated_hours=Decimal(4 + (i % 5)),
            )
            if st[i % 4] == Task.Status.COMPLETED:
                t.status = Task.Status.COMPLETED
                t.actual_hours = t.estimated_hours
                t.completed_at = timezone.now() - timedelta(days=1)
            else:
                t.status = st[i % 4]
            t.save()

        refresh_task_overdue_status()

        periods = [
            AISuggestion.PeriodType.DAILY,
            AISuggestion.PeriodType.WEEKLY,
            AISuggestion.PeriodType.MONTHLY,
        ]
        for i in range(10):
            payload = {"seed_index": i + 1, "period": periods[i % 3]}
            AISuggestion.objects.create(
                generated_by=admin,
                suggestion_text=(
                    f"[Seed {i+1:02d}] Rebalance: move one medium-priority item from the "
                    f"heaviest queue to E{(i % 3) + 1} to smooth estimated hours this period."
                ),
                input_summary=json.dumps(payload)[:2000],
                period_type=periods[i % 3],
            )

        self.stdout.write(
            self.style.SUCCESS(
                "Seeded: 10 Users, 10 UserProfiles, 10 Employees, 10 Tasks, 10 AISuggestions.\n"
                f"  Login: {SEED_USER_PREFIX}01 / seedpass123  (app admin, also has employee record)\n"
                f"  Employees: {SEED_USER_PREFIX}02–{SEED_USER_PREFIX}10 / seedpass123"
            )
        )
