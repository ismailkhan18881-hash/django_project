# config/settings.py
# This is the main settings file for the Django project.
# It controls the database, installed apps, middleware and static files.
# I added WhiteNoise middleware to serve CSS and JS files in production
# because Django does not serve static files itself when DEBUG is False.

from pathlib import Path
import os

# BASE_DIR points to the root of the project
# everything else is built relative to this path
BASE_DIR = Path(__file__).resolve().parent.parent

# SECRET_KEY is used by Django for security like sessions and CSRF tokens
# in a real production app this should be stored as an environment variable
SECRET_KEY = 'django-insecure-quitcig-secret-key-change-this-in-production'

# DEBUG is False because we are in production on Railway
# when DEBUG is True Django shows detailed error pages which is a security risk
DEBUG = False

# ALLOWED_HOSTS controls which domains can access the site
# the star means any domain is allowed which is needed for Railway
ALLOWED_HOSTS = ['*']

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
    # WhiteNoise goes here so it can intercept static file requests
    # before they reach the rest of the Django middleware stack
    # this is how it serves CSS and JS files in production on Railway
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

# Database - using SQLite which is the default Django database
# it does not need any extra setup which made it good for development
# for a larger production app PostgreSQL would be recommended
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation rules that Django enforces when users set passwords
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

# Static files are CSS, JavaScript and images
# STATIC_URL is the URL prefix browsers use to request these files
STATIC_URL = '/static/'

# STATIC_ROOT is where collectstatic puts all the files for production
# Railway runs collectstatic during deployment to gather everything here
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# STATICFILES_DIRS tells Django where my custom CSS lives during development
STATICFILES_DIRS = [
    BASE_DIR / 'core' / 'static',
]

# WhiteNoise compresses and caches static files for faster loading
# this is what actually serves the CSS and JS on Railway
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Default primary key type for all database models
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# After a successful login send the user to the dashboard
LOGIN_REDIRECT_URL = '/dashboard/'

# If a user visits a page without being logged in send them to login
LOGIN_URL = '/accounts/login/'

# After logging out send the user back to the login page
LOGOUT_REDIRECT_URL = '/accounts/login/'