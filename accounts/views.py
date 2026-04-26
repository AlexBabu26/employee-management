from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render


def redirect_by_role(user):
    if hasattr(user, "profile") and user.profile.is_admin():
        return redirect("workload:admin_dashboard")
    return redirect("workload:employee_dashboard")


def login_view(request):
    if request.user.is_authenticated:
        return redirect_by_role(request.user)
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            messages.success(request, "Welcome back.")
            return redirect_by_role(request.user)
    else:
        form = AuthenticationForm()
    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("accounts:login")
