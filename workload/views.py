import json
import logging

from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.models import UserProfile

from .decorators import admin_only, employee_only
from .forms import EmployeeForm, EmployeeTaskUpdateForm, TaskForm
from .models import AISuggestion, Employee, Task, refresh_task_overdue_status
from .services import ai_groq
from .services.analytics import (
    active_employees,
    completion_trend_monthly,
    daily_summary,
    high_low_employees,
    period_stats,
    workload_distribution,
    workload_hours,
)

logger = logging.getLogger(__name__)

HIGH_LOAD_THRESHOLD = 40.0


def index(request):
    if not request.user.is_authenticated:
        return redirect("accounts:login")
    if hasattr(request.user, "profile") and request.user.profile.is_admin():
        return redirect("workload:admin_dashboard")
    return redirect("workload:employee_dashboard")


def _admin_summary():
    refresh_task_overdue_status()
    today = timezone.now().date()
    total_emp = Employee.objects.count()
    active_emp = Employee.objects.filter(is_active=True).count()
    tasks = Task.objects.all()
    tc = tasks.count()
    comp = tasks.filter(status=Task.Status.COMPLETED).count()
    return {
        "total_employees": total_emp,
        "active_employees": active_emp,
        "total_tasks": tc,
        "pending_tasks": tasks.filter(status=Task.Status.PENDING).count(),
        "in_progress_tasks": tasks.filter(status=Task.Status.IN_PROGRESS).count(),
        "completed_tasks": comp,
        "completion_rate": (comp * 100.0 / tc) if tc else 0.0,
        "overdue_tasks": tasks.filter(status=Task.Status.OVERDUE).count(),
        "due_today": tasks.filter(due_date=today).exclude(
            status=Task.Status.COMPLETED
        ).count(),
        "daily": daily_summary(),
        "weekly": period_stats("weekly"),
        "monthly": period_stats("monthly"),
        "high_workload": high_low_employees()[0],
        "low_workload": high_low_employees()[1],
        "recent_ai": AISuggestion.objects.all()[:5],
    }


@admin_only
def admin_dashboard(request):
    return render(request, "workload/admin_dashboard.html", _admin_summary())


@employee_only
def employee_dashboard(request):
    emp = request.user.employee
    today = timezone.now().date()
    mine = Task.objects.filter(assigned_to=emp)
    refresh_task_overdue_status()
    return render(
        request,
        "workload/employee_dashboard.html",
        {
            "due_today": mine.filter(due_date=today).exclude(
                status=Task.Status.COMPLETED
            ),
            "pending": mine.filter(status=Task.Status.PENDING),
            "in_progress": mine.filter(status=Task.Status.IN_PROGRESS),
            "completed": mine.filter(status=Task.Status.COMPLETED),
            "overdue": mine.filter(status=Task.Status.OVERDUE),
            "upcoming": mine.filter(due_date__gt=today).exclude(
                status=Task.Status.COMPLETED
            )[:10],
        },
    )


@admin_only
def employee_list(request):
    q = request.GET.get("q", "").strip()
    dept = request.GET.get("department", "").strip()
    qs = Employee.objects.all()
    if q:
        qs = qs.filter(
            Q(full_name__icontains=q)
            | Q(user__username__icontains=q)
            | Q(email__icontains=q)
        )
    if dept:
        qs = qs.filter(department__iexact=dept)
    return render(request, "workload/employee_list.html", {"employees": qs})


@admin_only
def employee_add(request):
    if request.method == "POST":
        form = EmployeeForm(request.POST)
        if form.is_valid():
            u = User.objects.create_user(
                username=form.cleaned_data["username"],
                email=form.cleaned_data["email"],
                password=form.cleaned_data["password"],
            )
            UserProfile.objects.filter(user=u).update(role=UserProfile.Role.EMPLOYEE)
            emp = form.save(commit=False)
            emp.user = u
            emp.save()
            messages.success(request, "Employee created.")
            return redirect("workload:employee_detail", pk=emp.pk)
    else:
        form = EmployeeForm()
    return render(request, "workload/employee_form.html", {"form": form, "add": True})


@admin_only
def employee_edit(request, pk):
    emp = get_object_or_404(Employee, pk=pk)
    if request.method == "POST":
        form = EmployeeForm(request.POST, instance=emp)
        if form.is_valid():
            pwd = form.cleaned_data.get("password")
            if pwd:
                emp.user.set_password(pwd)
                emp.user.save()
            emp.user.username = form.cleaned_data["username"]
            emp.user.email = form.cleaned_data["email"]
            emp.user.save()
            form.save()
            messages.success(request, "Employee updated.")
            return redirect("workload:employee_detail", pk=emp.pk)
    else:
        form = EmployeeForm(instance=emp)
    return render(
        request,
        "workload/employee_form.html",
        {"form": form, "add": False, "employee": emp},
    )


@admin_only
def employee_detail(request, pk):
    emp = get_object_or_404(Employee, pk=pk)
    tasks = Task.objects.filter(assigned_to=emp)
    completed = tasks.filter(status=Task.Status.COMPLETED).count()
    return render(
        request,
        "workload/employee_detail.html",
        {
            "employee": emp,
            "tasks": tasks[:50],
            "load_hours": workload_hours(emp),
            "completed_count": completed,
        },
    )


@admin_only
def employee_deactivate(request, pk):
    emp = get_object_or_404(Employee, pk=pk)
    if request.method == "POST":
        emp.is_active = False
        emp.save()
        emp.user.is_active = False
        emp.user.save()
        messages.info(request, "Employee deactivated.")
        return redirect("workload:employee_list")
    return render(request, "workload/confirm_deactivate.html", {"employee": emp})


def _filter_tasks(request):
    qs = Task.objects.select_related("assigned_to", "created_by")
    st = request.GET.get("status")
    pr = request.GET.get("priority")
    emp_id = request.GET.get("employee")
    q = request.GET.get("q", "").strip()
    dfrom = request.GET.get("due_from")
    dto = request.GET.get("due_to")
    if st:
        qs = qs.filter(status=st)
    if pr:
        qs = qs.filter(priority=pr)
    if emp_id:
        qs = qs.filter(assigned_to_id=emp_id)
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))
    if dfrom:
        qs = qs.filter(due_date__gte=dfrom)
    if dto:
        qs = qs.filter(due_date__lte=dto)
    return qs


@admin_only
def task_list(request):
    qs = _filter_tasks(request).order_by("-created_at")
    return render(
        request,
        "workload/task_list.html",
        {
            "tasks": qs,
            "employees": active_employees(),
            "filters": request.GET,
        },
    )


@admin_only
def task_add(request):
    loads = {e.id: workload_hours(e) for e in active_employees()}
    load_list = [(e, loads.get(e.id, 0.0)) for e in active_employees()]
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            t = form.save(commit=False)
            t.created_by = request.user
            if t.status == Task.Status.COMPLETED:
                t.completed_at = timezone.now()
            else:
                t.completed_at = None
            t.save()
            messages.success(request, "Task created.")
            return redirect("workload:task_list")
    else:
        initial = {}
        raw = request.GET.get("employee")
        if raw and raw.isdigit():
            initial["assigned_to"] = get_object_or_404(Employee, pk=int(raw))
        form = TaskForm(initial=initial)
    return render(
        request,
        "workload/task_form.html",
        {
            "form": form,
            "add": True,
            "loads": loads,
            "load_list": load_list,
            "high_load_threshold": HIGH_LOAD_THRESHOLD,
        },
    )


@admin_only
def task_edit(request, pk):
    task = get_object_or_404(Task, pk=pk)
    loads = {e.id: workload_hours(e) for e in active_employees()}
    load_list = [(e, loads.get(e.id, 0.0)) for e in active_employees()]
    assignee = task.assigned_to
    warn = workload_hours(assignee) > HIGH_LOAD_THRESHOLD
    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            t = form.save(commit=False)
            if t.status == Task.Status.COMPLETED:
                t.completed_at = timezone.now()
            else:
                t.completed_at = None
            t.save()
            messages.success(request, "Task saved.")
            return redirect("workload:task_list")
    else:
        form = TaskForm(instance=task)
    return render(
        request,
        "workload/task_form.html",
        {
            "form": form,
            "add": False,
            "task": task,
            "loads": loads,
            "load_list": load_list,
            "high_load_threshold": HIGH_LOAD_THRESHOLD,
            "workload_warn": warn,
        },
    )


@admin_only
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == "POST":
        task.delete()
        messages.info(request, "Task deleted.")
        return redirect("workload:task_list")
    return render(request, "workload/confirm_delete_task.html", {"task": task})


@admin_only
def statistics(request):
    period = request.GET.get("period", "weekly")
    if period not in ("daily", "weekly", "monthly"):
        period = "weekly"
    return render(
        request,
        "workload/statistics.html",
        {
            "period": period,
            "daily": daily_summary() if period == "daily" else None,
            "stats": period_stats(period),
            "trend": completion_trend_monthly(),
            "distribution": workload_distribution(),
        },
    )


def _anonymized_payload(period: str) -> dict:
    refresh_task_overdue_status()
    out = {"period": period, "employees": [], "totals": {}}
    open_statuses = [
        Task.Status.PENDING,
        Task.Status.IN_PROGRESS,
        Task.Status.OVERDUE,
    ]
    for i, e in enumerate(active_employees()):
        qs = Task.objects.filter(assigned_to=e)
        est = qs.filter(status__in=open_statuses).aggregate(s=Sum("estimated_hours"))[
            "s"
        ]
        out["employees"].append(
            {
                "id": f"E{i+1}",
                "pending": qs.filter(status=Task.Status.PENDING).count(),
                "in_progress": qs.filter(status=Task.Status.IN_PROGRESS).count(),
                "overdue": qs.filter(status=Task.Status.OVERDUE).count(),
                "completed": qs.filter(status=Task.Status.COMPLETED).count(),
                "open_est_hours": float(est or 0),
            }
        )
    tq = Task.objects.all()
    out["totals"] = {
        "pending": tq.filter(status=Task.Status.PENDING).count(),
        "overdue": tq.filter(status=Task.Status.OVERDUE).count(),
        "in_progress": tq.filter(status=Task.Status.IN_PROGRESS).count(),
    }
    return out


@admin_only
def ai_suggestions(request):
    period = request.GET.get("period", "weekly")
    if period not in ("daily", "weekly", "monthly"):
        period = "weekly"
    items = AISuggestion.objects.all()[:20]
    error = None
    if request.method == "POST":
        period = request.POST.get("period", period)
        if period not in ("daily", "weekly", "monthly"):
            period = "weekly"
        payload = _anonymized_payload(period)
        try:
            result = ai_groq.fetch_workload_suggestion(payload, period)
            AISuggestion.objects.create(
                generated_by=request.user,
                suggestion_text=result["content"],
                input_summary=json.dumps(payload)[:2000],
                period_type=period,
                model_used=result.get("model", ""),
                reasoning_text=result.get("reasoning", "") or "",
                reasoning_details=result.get("reasoning_details") or [],
            )
            messages.success(request, "Suggestions updated.")
            return redirect("workload:ai_suggestions")
        except Exception as ex:
            logger.exception("AI suggestion failed")
            error = str(ex)
    return render(
        request,
        "workload/ai_suggestions.html",
        {
            "suggestions": items,
            "period": period,
            "error": error,
        },
    )


@employee_only
def my_tasks(request):
    mine = _employee_task_qs(request)
    return render(
        request,
        "workload/my_tasks.html",
        {
            "tasks": mine,
            "filters": request.GET,
        },
    )


def _employee_task_qs(request):
    emp = request.user.employee
    qs = Task.objects.filter(assigned_to=emp)
    st = request.GET.get("status")
    if st:
        qs = qs.filter(status=st)
    return qs.order_by("due_date", "-priority")


@employee_only
def task_detail_employee(request, pk):
    emp = request.user.employee
    task = get_object_or_404(Task, pk=pk, assigned_to=emp)
    if request.method == "POST":
        form = EmployeeTaskUpdateForm(request.POST, instance=task)
        if form.is_valid():
            t = form.save(commit=False)
            if t.status == Task.Status.COMPLETED:
                t.completed_at = timezone.now()
            else:
                t.completed_at = None
            t.save()
            messages.success(request, "Task updated.")
            return redirect("workload:task_detail_employee", pk=task.pk)
    else:
        form = EmployeeTaskUpdateForm(instance=task)
    return render(
        request,
        "workload/employee_task_detail.html",
        {"task": task, "form": form},
    )


@employee_only
def completed_tasks(request):
    mine = Task.objects.filter(
        assigned_to=request.user.employee, status=Task.Status.COMPLETED
    ).order_by("-completed_at")
    return render(request, "workload/completed_tasks.html", {"tasks": mine})
