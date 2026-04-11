# config/settings.py
# This is the main settings file for the Django project.
# It controls everything from the database to static files.
# I have added comments to the parts I changed or that are important.
# The rest was generated automatically by Django when I created the project.

from pathlib import Path

# BASE_DIR is the root folder of the project
# All other paths are built relative to this
BASE_DIR = Path(__file__).resolve().parent.parent

# SECRET_KEY is used by Django for security things like sessions and tokens
# In production this should be stored in an environment variable
SECRET_KEY = 'django-insecure-quitcig-secret-key-change-this-in-production'

# DEBUG is set to False for production deployment
# This stops Django showing detailed error pages to users
DEBUG = False

# ALLOWED_HOSTS controls which domain names can access the site
# The star means any domain is allowed which is needed for Railway deployment
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

# Database settings
# I am using SQLite during development because it needs no setup
# For a larger production deployment PostgreSQL would be recommended
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation rules
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Use UTC as the default timezone
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files are things like CSS and JavaScript
# STATIC_URL is the URL prefix for static files
STATIC_URL = '/static/'

# Tell Django where to find static files in the core app
STATICFILES_DIRS = [
    BASE_DIR / 'core' / 'static',
]

# STATIC_ROOT is where collectstatic puts files for production
# Railway needs this to serve CSS and JS files correctly
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Default primary key type for database models
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# After a successful login send the user to the dashboard
LOGIN_REDIRECT_URL = '/dashboard/'

# If a user tries to visit a page without being logged in
# send them to the login page
LOGIN_URL = '/accounts/login/'

# After logging out send the user back to the login page
LOGOUT_REDIRECT_URL = '/accounts/login/'