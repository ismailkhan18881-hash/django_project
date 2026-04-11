# core/apps.py
# This file tells Django about the core app.
# Django uses it to configure the app when the server starts.
# I did not need to change anything here from the default.

from django.apps import AppConfig


class CoreConfig(AppConfig):
    # The default type for auto-generated primary keys in the database
    default_auto_field = 'django.db.models.BigAutoField'

    # The name of this app - must match the folder name
    name = 'core'