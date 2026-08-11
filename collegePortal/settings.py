"""
Django settings for collegePortal project.

Configuration is environment-driven so the same codebase works locally
(SQLite / local media) and in serverless production (PostgreSQL on
Vercel/Render, durable media on Cloudinary or S3).

All secrets must be provided through environment variables (or a local
`.env` file) - never hard-coded.
"""

import os

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def env(key, default=None):
    return os.environ.get(key, default)


# Load variables from a local .env file if present (development convenience).
try:
    from dotenv import load_dotenv

    load_dotenv(BASE_DIR / ".env")
except ImportError:
    pass


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY", "django-insecure-<development-only-key-override-me>")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DEBUG", "True").lower() in ("1", "true", "yes")

ALLOWED_HOSTS = [
    host.strip()
    for host in env(
        "ALLOWED_HOSTS", "localhost,127.0.0.1,.onrender.com,.vercel.app"
    ).split(",")
    if host.strip()
]

# Custom user model with role-based access control.
AUTH_USER_MODEL = "accounts.User"

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "accounts",
    "students",
    "faculty",
]

STORAGE_BACKEND = env("STORAGE_BACKEND", "local").lower()

if STORAGE_BACKEND == "cloudinary":
    INSTALLED_APPS.insert(
        INSTALLED_APPS.index("django.contrib.staticfiles"), "cloudinary_storage"
    )
    INSTALLED_APPS.append("cloudinary")

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "accounts.middleware.CurrentUserMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "collegePortal.urls"

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

WSGI_APPLICATION = "collegePortal.wsgi.application"

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases
# Prefer a DATABASE_URL connection string (set automatically by Render for its
# managed Postgres, and by Neon/Vercel). Fall back to DB_* variables for a
# local Postgres, or to SQLite so `manage.py` works out of the box locally.
# DB_ENGINE can be e.g. "django.db.backends.sqlite3" for a simple local setup.

_db_url = env("DATABASE_URL", "")
if _db_url:
    import dj_database_url

    DATABASES = {
        "default": dj_database_url.parse(_db_url, conn_max_age=600),
    }
else:
    _engine = env("DB_ENGINE", "django.db.backends.sqlite3")
    if _engine == "django.db.backends.sqlite3":
        DATABASES = {
            "default": {
                "ENGINE": _engine,
                "NAME": env("DB_NAME", str(BASE_DIR / "db.sqlite3")),
            }
        }
    else:
        DATABASES = {
            "default": {
                "ENGINE": _engine,
                "NAME": env("DB_NAME", "college_db"),
                "USER": env("DB_USER", "postgres"),
                "PASSWORD": env("DB_PASSWORD", ""),
                "HOST": env("DB_HOST", "localhost"),
                "PORT": env("DB_PORT", "5432"),
            }
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

STATIC_URL = "static/"

STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Storage backends
# https://docs.djangoproject.com/en/6.0/topics/files/
# STORAGE_BACKEND = "local" | "cloudinary" | "s3"
# Durable media (profile images) in production is configured via env vars,
# while local development keeps working with the local file system.

if STORAGE_BACKEND == "cloudinary":
    CLOUDINARY_STORAGE = {
        "CLOUD_NAME": env("CLOUDINARY_CLOUD_NAME", ""),
        "API_KEY": env("CLOUDINARY_API_KEY", ""),
        "API_SECRET": env("CLOUDINARY_API_SECRET", ""),
        "SECURE": True,
    }
    DEFAULT_STORAGE_BACKEND = "cloudinary_storage.storage.MediaCloudinaryStorage"
elif STORAGE_BACKEND == "s3":
    AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY", "")
    AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME", "")
    AWS_DEFAULT_ACL = None
    AWS_S3_FILE_OVERWRITE = False
    AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400"}
    DEFAULT_STORAGE_BACKEND = "storages.backends.s3boto3.S3Boto3Storage"
else:
    DEFAULT_STORAGE_BACKEND = "django.core.files.storage.FileSystemStorage"

STORAGES = {
    "default": {
        "BACKEND": DEFAULT_STORAGE_BACKEND,
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

if not DEBUG:
    STORAGES["staticfiles"][
        "BACKEND"
    ] = "whitenoise.storage.CompressedManifestStaticFilesStorage"
