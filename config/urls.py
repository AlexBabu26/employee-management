from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/django/", admin.site.urls),
    path("accounts/", include("accounts.urls", namespace="accounts")),
    path("", include("workload.urls", namespace="workload")),
]
