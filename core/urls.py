from django.urls import path
from .views import profile_view

urlpatterns = [
    path('profile/', profile_view, name='profile'),
]
from .views import profile_view, log_progress

urlpatterns = [
    path('profile/', profile_view, name='profile'),
    path('progress/', log_progress, name='progress'),
]
