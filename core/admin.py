# core/admin.py
# This file registers the models with the Django admin panel.
# Registering a model means I can view, add, edit and delete
# records through the admin interface at /admin/
# This was very useful during development for checking data.

from django.contrib import admin
from .models import Profile, ProgressLog, Achievement

# Register the Profile model so I can see user profiles in the admin panel
admin.site.register(Profile)

# Register the ProgressLog model so I can see all log entries
admin.site.register(ProgressLog)

# Register the Achievement model so I can see which badges users have earned
admin.site.register(Achievement)