from .base import *  # noqa

DEBUG = True

INSTALLED_APPS += ["django.contrib.admindocs"]  # noqa

# Email en consola durante desarrollo
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Logging SQL
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "loggers": {
        "django.db.backends": {
            "handlers": ["console"],
            "level": "DEBUG" if DEBUG else "WARNING",
        }
    },
}
