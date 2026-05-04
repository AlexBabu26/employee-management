from datetime import date, timedelta
from typing import List

from django.db.models import Count, Q, Sum
from django.utils import timezone

from ..models import Employee, Task


def _date_bounds(period: str) -> tuple[date, date]:
    today = timezone.now().date()
    if period == "daily":
        return today, today
    if period == "weekly":
        start = today - timedelta(days=today.weekday())
        return start, today
    if period == "monthly":
        return today.replace(day=1), today
    raise ValueError(period)


def _first_day_prev_months(n: int) -> List[date]:
    d = timezone.now().date().replace(day=1)
    out = []
    y, m = d.year, d.month
    for _ in range(n):
        out.append(date(y, m, 1))
        m -= 1
        if m < 1:
            m = 12
            y -= 1
    return list(reversed(out))


def active_employees():
    return Employee.objects.filter(is_active=True)


def workload_hours(employee: Employee) -> float:
    qs = Task.objects.filter(
        assigned_to=employee,
        status__in=[
            Task.Status.PENDING,
            Task.Status.IN_PROGRESS,
            Task.Status.OVERDUE,
        ],
    )
    total = qs.aggregate(s=Sum("estimated_hours"))["s"] or 0
    return float(total)


def daily_summary() -> dict:
    today = timezone.now().date()
    return {
        "assigned_today": Task.objects.filter(created_at__date=today).count(),
        "completed_today": Task.objects.filter(
            status=Task.Status.COMPLETED, completed_at__date=today
        ).count(),
        "pending_today": Task.objects.filter(
            status=Task.Status.PENDING, due_date=today
        ).count(),
        "overdue": Task.objects.filter(status=Task.Status.OVERDUE).count(),
        "per_employee_estimated": _per_employee_hours_today("estimated"),
        "per_employee_actual": _per_employee_hours_today("actual"),
    }


def _per_employee_hours_today(kind: str) -> list[dict[str, object]]:
    today = timezone.now().date()
    qs = Task.objects.filter(
        start_date__lte=today, due_date__gte=today
    ).values("assigned_to__full_name", "assigned_to_id")
    if kind == "actual":
        qs = qs.annotate(h=Sum("actual_hours"))
    else:
        qs = qs.annotate(h=Sum("estimated_hours"))
    return [
        {
            "name": r["assigned_to__full_name"] or f"ID {r['assigned_to_id']}",
            "hours": float(r["h"] or 0),
        }
        for r in qs
    ]


def period_stats(period: str) -> dict:
    start, end = _date_bounds(period)
    window = Q(due_date__range=(start, end)) | Q(created_at__date__range=(start, end))
    qs = Task.objects.filter(window)
    total = qs.count()
    completed = qs.filter(status=Task.Status.COMPLETED).count()
    est = float(qs.aggregate(s=Sum("estimated_hours"))["s"] or 0)
    act = float(qs.aggregate(s=Sum("actual_hours"))["s"] or 0)

    per_emp = (
        qs.values("assigned_to", "assigned_to__full_name")
        .annotate(
            c=Count("id"),
            overdue_n=Count("id", filter=Q(status=Task.Status.OVERDUE)),
        )
        .order_by()
    )

    high, low = high_low_employees()
    return {
        "start": start,
        "end": end,
        "total_tasks": total,
        "completed": completed,
        "pending": qs.filter(status=Task.Status.PENDING).count(),
        "overdue": qs.filter(status=Task.Status.OVERDUE).count(),
        "completion_pct": (completed * 100.0 / total) if total else 0.0,
        "sum_estimated": est,
        "sum_actual": act,
        "per_employee": list(per_emp),
        "high_workload_employees": high,
        "low_workload_employees": low,
    }


_PERIOD_LABELS = {"daily": "Daily", "weekly": "Weekly", "monthly": "Monthly"}


def employee_worklife(employee: Employee, period: str) -> dict[str, object]:
    """
    Per-employee workload snapshot for daily / weekly / monthly windows.

    Open workload uses the same task window as Statistics (due or created in range).
    Completed workload counts tasks finished in-range by ``completed_at`` date.
    """
    start, end = _date_bounds(period)
    window = Q(due_date__range=(start, end)) | Q(created_at__date__range=(start, end))
    base = Task.objects.filter(assigned_to=employee).filter(window)

    open_statuses = [
        Task.Status.PENDING,
        Task.Status.IN_PROGRESS,
        Task.Status.OVERDUE,
    ]
    open_qs = base.filter(status__in=open_statuses)
    open_est = open_qs.aggregate(s=Sum("estimated_hours"))["s"] or 0

    completed_qs = Task.objects.filter(
        assigned_to=employee,
        status=Task.Status.COMPLETED,
        completed_at__isnull=False,
        completed_at__date__range=(start, end),
    )
    actual_done = completed_qs.aggregate(s=Sum("actual_hours"))["s"] or 0

    return {
        "period": period,
        "label": _PERIOD_LABELS[period],
        "start": start,
        "end": end,
        "open_estimated_hours": float(open_est),
        "actual_completed_hours": float(actual_done),
        "open_task_count": open_qs.count(),
        "completed_task_count": completed_qs.count(),
        "overdue_count": base.filter(status=Task.Status.OVERDUE).count(),
    }


def employee_worklife_snapshots(employee: Employee) -> list[dict[str, object]]:
    return [
        employee_worklife(employee, "daily"),
        employee_worklife(employee, "weekly"),
        employee_worklife(employee, "monthly"),
    ]


def high_low_employees() -> tuple[list[dict], list[dict]]:
    data = []
    for emp in active_employees():
        h = workload_hours(emp)
        data.append({"id": emp.pk, "name": emp.full_name, "load_hours": h})
    if not data:
        return [], []
    data.sort(key=lambda x: x["load_hours"], reverse=True)
    n = max(1, (len(data) + 1) // 3)
    return data[:n], data[-n:][::-1]


def employee_hour_breakdown() -> list[dict[str, object]]:
    open_statuses = [
        Task.Status.PENDING,
        Task.Status.IN_PROGRESS,
        Task.Status.OVERDUE,
    ]
    rows = (
        active_employees()
        .annotate(
            open_estimated=Sum(
                "tasks__estimated_hours", filter=Q(tasks__status__in=open_statuses)
            ),
            actual_completed=Sum(
                "tasks__actual_hours", filter=Q(tasks__status=Task.Status.COMPLETED)
            ),
            open_tasks=Count("tasks", filter=Q(tasks__status__in=open_statuses)),
            completed_tasks=Count("tasks", filter=Q(tasks__status=Task.Status.COMPLETED)),
        )
        .values(
            "full_name",
            "open_estimated",
            "actual_completed",
            "open_tasks",
            "completed_tasks",
        )
    )
    data = [
        {
            "full_name": row["full_name"],
            "open_estimated_hours": float(row["open_estimated"] or 0),
            "actual_completed_hours": float(row["actual_completed"] or 0),
            "open_task_count": row["open_tasks"],
            "completed_task_count": row["completed_tasks"],
        }
        for row in rows
    ]
    data.sort(key=lambda row: (-row["open_estimated_hours"], row["full_name"]))
    return data


def completion_trend_monthly() -> list[dict[str, int | str]]:
    out = []
    for month_start in _first_day_prev_months(6):
        y, m = month_start.year, month_start.month
        c = Task.objects.filter(
            completed_at__isnull=False,
            completed_at__date__year=y,
            completed_at__date__month=m,
        ).count()
        out.append(
            {
                "label": f"{y}-{m:02d}",
                "completed": c,
            }
        )
    return out


def workload_distribution() -> list[dict[str, object]]:
    return employee_hour_breakdown()
