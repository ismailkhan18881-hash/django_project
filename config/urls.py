# config/urls.py
# This is the main URL configuration file for the whole project.
# Django reads this first when any request comes in.
# It connects the admin panel, the login and logout pages,
# and all the core app URLs together in one place.

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    # The Django admin panel at /admin/
    # This lets me manage users, profiles, logs and badges
    path("admin/", admin.site.urls),

    # Django's built in authentication URLs
    # This gives us /accounts/login/ and /accounts/logout/ for free
    path("accounts/", include("django.contrib.auth.urls")),

    # All the core app URLs from core/urls.py
    # The empty string means they start at the root of the site
    path("", include("core.urls")),
]