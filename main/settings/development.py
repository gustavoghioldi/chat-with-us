"""
Development settings for Django project.
Contains settings specific to development environment.
"""

import os

from .base import *  # noqa: F403

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-_z5pp)x=e7$cp9nld_&$(y@twgy^k(z_@+u4$7swn#2^btx$+e"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# CORS settings
CORS_ALLOW_ALL_ORIGINS = True  # Solo para desarrollo
CORS_ALLOW_CREDENTIALS = True

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME", "barbadb"),
        "USER": os.environ.get("DB_USER", "postgres"),
        "PASSWORD": os.environ.get("DB_PASSWORD", "barba"),
        "HOST": os.environ.get("DB_HOST", "127.0.0.1"),
        "PORT": os.environ.get("DB_PORT", "5732"),
    }
}

# Celery
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.environ.get(
    "CELERY_RESULT_BACKEND", "redis://localhost:6379/0"
)

# Email configuration for development
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Logging configuration for development
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "db_log": {
            'level': 'DEBUG',
            'class': 'logger.db_log_handler.DatabaseLogHandler'
        }
    },
    "loggers": {
        "django": {
            "handlers": ["db_log","console"],
            "level": "INFO",
        },
        "agents": {
            "handlers": ["console"],
            "level": "DEBUG",
        },
    },
}

# Development tools configuration (sin debug toolbar)
if DEBUG:
    # Mostrar SQL queries en consola (alternativa a debug toolbar)
    LOGGING["loggers"]["django.db.backends"] = {
        "level": "DEBUG",
        "handlers": ["console"],
        "propagate": False,
    }

    # Configuración para desarrollo más detallada
    LOGGING["loggers"]["agents.services"] = {
        "level": "DEBUG",
        "handlers": ["console"],
        "propagate": False,
    }

    # Configuración adicional para desarrollo
    ALLOWED_HOSTS += ["*"]  # Permitir cualquier host en desarrollo

    # Configuración de archivos estáticos mejorada
    STATICFILES_DIRS = [
        BASE_DIR / "static",  # noqa: F405
    ]

CELERY_TASK_ALWAYS_EAGER = True  # fuerza ejecución inmediata
CELERY_TASK_EAGER_PROPAGATES = True  # que reviente aquí la excepción si algo falla
