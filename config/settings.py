import dj_database_url
import os
import sys

from django.contrib.messages import constants as message_constants
from pathlib import Path
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


PLATFORM_NAME = config("PLATFORM_NAME", default="Platform Name")


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY")

if not SECRET_KEY:
    raise ValueError("'SECRET_KEY' must be set!")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config("DEBUG", default=False, cast=bool)
ALLOWED_HOSTS = [h.strip() for h in config("ALLOWED_HOSTS", default="").split(",") if h.strip()]


# Application definition
INSTALLED_APPS = [
    # custom accounts
    "accounts.apps.AccountsConfig",
    # default apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # custom apps
    "core.apps.CoreConfig",
]

if "test" in sys.argv:
    INSTALLED_APPS.append("tests.apps.TestsConfig")

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

if not DEBUG:
    security_index = MIDDLEWARE.index("django.middleware.security.SecurityMiddleware")
    MIDDLEWARE.insert(security_index + 1, "whitenoise.middleware.WhiteNoiseMiddleware")

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases
DATABASE_URL = config("DATABASE_URL", default="").strip()

if not DEBUG and not DATABASE_URL:
    raise ValueError("Production DB not configured. Set 'DATABASE_URL'.")

DATABASES = {
    "default": dj_database_url.config(
        default=DATABASE_URL or f"sqlite:///{BASE_DIR / 'blog.sqlite3'}",
        conn_max_age=config("DB_CONN_MAX_AGE", default=600, cast=int),
        ssl_require=config("DB_SSL_REQUIRE", default=not DEBUG, cast=bool),
    )
}


# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/
STATIC_ROOT = BASE_DIR / "staticfiles"
STATIC_URL = "static/"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

staticfiles_backend = (
    "whitenoise.storage.CompressedManifestStaticFilesStorage"
    if not DEBUG
    else "django.contrib.staticfiles.storage.StaticFilesStorage"
)

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
        "OPTIONS": {"location": MEDIA_ROOT},
    },
    "private": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
        "OPTIONS": {
            "location": MEDIA_ROOT / "private",
            "base_url": f"{MEDIA_URL}private/",
        },
    },
    "staticfiles": {
        "BACKEND": staticfiles_backend,
    },
}

# Thumbnail configurations -- easy-thumbnails
THUMBNAIL_PROCESSORS = (
    "easy_thumbnails.processors.colorspace",
    "easy_thumbnails.processors.autocrop",
    "easy_thumbnails.processors.scale_and_crop",
    "easy_thumbnails.processors.filters",
)
THUMBNAIL_QUALITY = 85
THUMBNAIL_PRESERVE_FORMAT = True
THUMBNAIL_ALIASES = {
    "": {
        "img_sm": {"size": (64, 64), "crop": True},
        "img_md": {"size": (160, 160), "crop": True},
        "img_lg": {"size": (256, 256), "crop": True},
    }
}

# Set Auth User Model
AUTH_USER_MODEL = "accounts.CustomUser"

# Login configuration
LOGIN_REDIRECT_URL = "core:home_page"
LOGIN_URL = "accounts:login"
LOGOUT_URL = "accounts:logout"


# CSRF (Cross-Site Request Forgery) A CSRF cookie that is a random secret value,
# which other sites will not have access to.
# SET WHEN MOVING TO PRODUCTION: CSRF_TRUSTED_ORIGINS
CSRF_TRUSTED_ORIGINS = [
    o.strip() for o in config("CSRF_TRUSTED_ORIGINS", default="").split(",") if o.strip()
]


# Email configuration
EMAIL_BACKEND = config("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")
EMAIL_HOST = config("EMAIL_HOST", "")
EMAIL_PORT = config("EMAIL_PORT", 587, cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", True, cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", "")
SUPPORT_EMAIL = config("SUPPORT_EMAIL", "")
# Error/Logging monitoring for production
SERVER_EMAIL = config("SERVER_EMAIL", "")
ADMINS = [a.strip() for a in config("ADMINS", default="").split(",") if a.strip()]


# Configuration for Django Message Framework
MESSAGE_TAGS = {
    message_constants.DEBUG: "alert-secondary",
    message_constants.INFO: "alert-info",
    message_constants.SUCCESS: "alert-success",
    message_constants.WARNING: "alert-warning",
    message_constants.ERROR: "alert-danger",
}


# Django Debug Toolbar configurations
# -------------------------------------
DJANGO_DEBUG_TOOLBAR = config("DJANGO_DEBUG_TOOLBAR", default=False, cast=bool)
TESTING = "test" in sys.argv or "PYTEST_VERSION" in os.environ
ENABLE_DEBUG_TOOLBAR = DEBUG and DJANGO_DEBUG_TOOLBAR and not TESTING

if ENABLE_DEBUG_TOOLBAR:
    INSTALLED_APPS.append("debug_toolbar")
    MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")
    INTERNAL_IPS = ["127.0.0.1", "::1"]
    DEBUG_TOOLBAR_CONFIG = {
        "SHOW_TOOLBAR_CALLBACK": config(
            "SHOW_TOOLBAR_CALLBACK",
            default="debug_toolbar.middleware.show_toolbar",
        ),
    }
