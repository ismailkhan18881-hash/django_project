# core/urls.py
# This file maps URLs to view functions.
# When a user visits a URL Django looks here to find
# which view function should handle that request.
# Each path connects a URL pattern to a function in views.py
# and gives it a name so templates can link to it easily.

from django.urls import path
from .views import (
    profile_view,
    log_progress,
    plan_view,
    dashboard_view,
    questionnaire_view,
    register_view,
)

urlpatterns = [
    # The main dashboard page shown after login
    path("dashboard/", dashboard_view, name="dashboard"),

    # The profile update page where users can change their details
    path("profile/", profile_view, name="profile"),

    # The daily progress logging page
    path("progress/", log_progress, name="progress"),

    # The personalised exercise plan page
    path("plan/", plan_view, name="plan"),

    # The 15 question onboarding questionnaire
    # New users are redirected here before they can see the dashboard
    path("questionnaire/", questionnaire_view, name="questionnaire"),

    # The registration page for new users to create an account
    path("register/", register_view, name="register"),
]