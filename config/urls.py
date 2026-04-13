# config/urls.py
# This is the main URL configuration file for the whole project.
# Django reads this first when any request comes in.
# I added a redirect at the root URL so visiting the homepage
# sends the user to the dashboard instead of showing a 404 error.

from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    # The root URL redirects to dashboard
    # without this visiting the homepage shows a Not Found error
    path('', RedirectView.as_view(url='/dashboard/'), name='home'),

    # The Django admin panel at /admin/
    path('admin/', admin.site.urls),

    # Django's built in login and logout URLs
    path('accounts/', include('django.contrib.auth.urls')),

    # All the core app URLs from core/urls.py
    path('', include('core.urls')),
]