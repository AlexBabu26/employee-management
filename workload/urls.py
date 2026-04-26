from django.urls import path

from . import views

app_name = "workload"

urlpatterns = [
    path("", views.index, name="index"),
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("employee-dashboard/", views.employee_dashboard, name="employee_dashboard"),
    path("employees/", views.employee_list, name="employee_list"),
    path("employees/add/", views.employee_add, name="employee_add"),
    path("employees/<int:pk>/", views.employee_detail, name="employee_detail"),
    path("employees/<int:pk>/edit/", views.employee_edit, name="employee_edit"),
    path(
        "employees/<int:pk>/deactivate/",
        views.employee_deactivate,
        name="employee_deactivate",
    ),
    path("tasks/", views.task_list, name="task_list"),
    path("tasks/add/", views.task_add, name="task_add"),
    path("tasks/<int:pk>/edit/", views.task_edit, name="task_edit"),
    path("tasks/<int:pk>/delete/", views.task_delete, name="task_delete"),
    path("statistics/", views.statistics, name="statistics"),
    path("ai-suggestions/", views.ai_suggestions, name="ai_suggestions"),
    path("my-tasks/", views.my_tasks, name="my_tasks"),
    path("my-tasks/<int:pk>/", views.task_detail_employee, name="task_detail_employee"),
    path("completed/", views.completed_tasks, name="completed_tasks"),
]
