from .models import refresh_task_overdue_status


class OverdueTaskMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        refresh_task_overdue_status()
        return self.get_response(request)
