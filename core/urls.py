from django.urls import path
from .views import profile_view, log_progress, plan_view, dashboard_view

urlpatterns = [
    path("dashboard/", dashboard_view, name="dashboard"),
    path("profile/", profile_view, name="profile"),
    path("progress/", log_progress, name="progress"),
    path("plan/", plan_view, name="plan"),
]
