from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('core.urls')),
]

# IMPORTANT: put static patterns in front so they always win
if settings.DEBUG:
    urlpatterns = staticfiles_urlpatterns() + urlpatterns
