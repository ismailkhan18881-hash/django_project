# config/settings.py
# This is the main settings file for the Django project.
# I added WhiteNoise middleware to serve CSS and JS files in production
# because Django does not serve static files itself when DEBUG is False.
# Without WhiteNoise the CSS would load fine locally but not on Railway.

from pathlib import Path
import os

# BASE_DIR points to the root folder of the project
# all other file paths are built relative to this
BASE_DIR = Path(__file__).resolve().parent.parent

# SECRET_KEY is used by Django for security like sessions and CSRF tokens
# in a real production app this should be an environment variable
SECRET_KEY = 'django-insecure-quitcig-secret-key-change-this-in-production'

# DEBUG is False because we are deployed on Railway in production
# setting this to True would show detailed error pages which is a security risk
DEBUG = False

# ALLOWED_HOSTS controls which domain names can access the site
# the star means any domain is allowed which is needed for Railway
ALLOWED_HOSTS = ['*']

# CSRF_TRUSTED_ORIGINS tells Django which domains are allowed to submit forms
# without this Railway blocks all form submissions with a 403 Forbidden error
# I had to add this after deploying because login was not working on the live site
CSRF_TRUSTED_ORIGINS = ['https://djangoproject-production-045b.up.railway.app']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',   # this is the QuitCig app I built
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # WhiteNoise middleware goes right after SecurityMiddleware
    # it intercepts requests for CSS and JS files and serves them directly
    # this is how static files work on Railway without needing a separate nginx server
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # APP_DIRS tells Django to look for templates inside each app folder
        'APP_DIRS': True,
        'DIRS': [],
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database - using SQLite which needs no setup
# for a larger production app PostgreSQL would be better
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# STATIC_URL is the URL prefix browsers use to request CSS and JS files
STATIC_URL = '/static/'

# STATIC_ROOT is where collectstatic gathers all files for production
# Railway runs collectstatic during deployment and puts everything here
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# STATICFILES_DIRS tells Django where my custom CSS lives
# this must point to core/static where styles.css actually is
STATICFILES_DIRS = [
    BASE_DIR / 'core' / 'static',
]

# CompressedStaticFilesStorage makes WhiteNoise compress CSS for faster loading
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# This tells WhiteNoise to also look in STATICFILES_DIRS
# not just in STATIC_ROOT which fixed the CSS not loading on Railway
WHITENOISE_USE_FINDERS = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# After a successful login send the user to the dashboard
LOGIN_REDIRECT_URL = '/dashboard/'

# If a user visits a page without being logged in send them to login
LOGIN_URL = '/accounts/login/'

# After logging out send the user back to the login page
LOGOUT_REDIRECT_URL = '/accounts/login/'