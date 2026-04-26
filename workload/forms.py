from django import forms
from django.contrib.auth.models import User

from .models import Employee, Task


class EmployeeForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Employee
        fields = [
            "full_name",
            "email",
            "department",
            "designation",
            "is_active",
            "date_joined",
        ]
        widgets = {"date_joined": forms.DateInput(attrs={"type": "date"})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields["password"].required = False
            self.fields["password"].help_text = "Leave blank to keep current password."
            if self.instance.user_id:
                self.fields["username"].initial = self.instance.user.username


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            "title",
            "description",
            "assigned_to",
            "priority",
            "status",
            "start_date",
            "due_date",
            "estimated_hours",
            "actual_hours",
        ]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "due_date": forms.DateInput(attrs={"type": "date"}),
        }


class EmployeeTaskUpdateForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["status", "actual_hours"]
        widgets = {
            "actual_hours": forms.NumberInput(attrs={"step": "0.1", "min": "0"}),
        }
