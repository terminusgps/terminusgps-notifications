import base64
import os
import sys
from pathlib import Path
from socket import gethostbyname, gethostname

from terminusgps.authorizenet.constants import Environment, ValidationMode
from terminusgps.wialon.flags import TokenFlag

ALLOWED_HOSTS = [
    ".terminusgps.com",
    ".elb.amazonaws.com",
    gethostbyname(gethostname()),
]
BASE_DIR = Path(__file__).resolve().parent.parent
CSRF_COOKIE_SECURE = True
CSRF_TRUSTED_ORIGINS = ["https://*.terminusgps.com", "https://terminusgps.com"]
DEBUG = False
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
DJANGO_ENCRYPTED_FIELD_ALGORITHM = os.getenv(
    "DJANGO_ENCRYPTED_FIELD_ALGORITHM", "SS20"
)
DJANGO_ENCRYPTED_FIELD_KEY = base64.b64decode(
    os.getenv("DJANGO_ENCRYPTED_FIELD_KEY", "")
)
LANGUAGE_CODE = "en-us"
LOGIN_REDIRECT_URL = "/dashboard/"
LOGIN_URL = "/login/"
MERCHANT_AUTH_ENVIRONMENT = Environment.SANDBOX
MERCHANT_AUTH_LOGIN_ID = os.getenv("MERCHANT_AUTH_LOGIN_ID")
MERCHANT_AUTH_TRANSACTION_KEY = os.getenv("MERCHANT_AUTH_TRANSACTION_KEY")
MERCHANT_AUTH_VALIDATION_MODE = ValidationMode.TEST
ROOT_URLCONF = "src.urls"
SECRET_KEY = os.getenv("SECRET_KEY")
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = False
STATIC_URL = "static/"
TIME_ZONE = "US/Central"
USE_I18N = False
USE_TZ = True
USE_X_FORWARDED_HOST = True
WIALON_RESOURCE_NAME = "Terminus GPS Notifications"
WIALON_TOKEN = os.getenv("WIALON_TOKEN")
WIALON_TOKEN_ACCESS_TYPE = (
    TokenFlag.VIEW_ACCESS
    | TokenFlag.MANAGE_NONSENSITIVE
    | TokenFlag.MANAGE_SENSITIVE
)
WSGI_APPLICATION = "src.wsgi.application"

ADMINS = (
    ("Peter", "pspeckman@terminusgps.com"),
    ("Blake", "blake@terminusgps.com"),
    ("Lili", "lili@terminusgps.com"),
)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False if "test" not in sys.argv else True,
    "formatters": {
        "verbose": {
            "format": "%(asctime)s [%(process)d] [%(module)s] [%(levelname)s] %(message)s",
            "datefmt": "[%Y-%m-%d %H:%M:%S%z]",
            "class": "logging.Formatter",
        },
        "simple": {
            "format": "%(asctime)s [%(levelname)s] %(message)s",
            "datefmt": "[%Y-%m-%d %H:%M:%S%z]",
            "class": "logging.Formatter",
        },
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "simple"},
        "console_verbose": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {"handlers": ["console"], "level": "WARNING"},
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
        "authorizenet": {
            "handlers": ["console"],
            "level": os.getenv("AUTHORIZENET_LOG_LEVEL", "WARNING"),
            "propagate": False,
        },
        "terminusgps_notifications": {
            "handlers": ["console_verbose"],
            "level": os.getenv("NOTIFICATIONS_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
        "terminusgps_payments": {
            "handlers": ["console_verbose"],
            "level": os.getenv("PAYMENTS_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
    },
}

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "terminusgps_payments.apps.TerminusgpsPaymentsConfig",
    "terminusgps_notifications.apps.TerminusgpsNotificationsConfig",
]

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379",
        "TIMEOUT": 60 * 15,
    }
}

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

STORAGES = {
    "default": {"BACKEND": "django.core.files.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "bucket_name": os.getenv("AWS_S3_BUCKET_NAME"),
            "location": "static/",
            "region_name": os.getenv("AWS_S3_BUCKET_REGION", "us-east-1"),
            "verify": os.getenv(
                "AWS_S3_CERT_PATH",
                ".venv/lib/python3.12/site-packages/certifi/cacert.pem",
            ),
        },
    },
}

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME"),
        "HOST": os.getenv("DB_HOST"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "PORT": os.getenv("DB_PORT", 5432),
        "OPTIONS": {"client_encoding": "UTF8"},
        "CONN_MAX_AGE": None,
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"
    },
]
