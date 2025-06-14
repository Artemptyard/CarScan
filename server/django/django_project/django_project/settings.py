"""
Django settings for django_project project.

Generated by 'django-admin startproject' using Django 3.2.25.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

import os
from pathlib import Path
from os import environ  # Сокрытие настроек в env папке
import logging
import datetime as dt

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure--a8*@r3z9rvpsxyvp=7rak%@-^@5v($l*75cxtlyz!)6(uj=1l'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'carscan',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
]

CORS_ORIGIN_ALLOW_ALL = True

ROOT_URLCONF = 'django_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'django_project.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


class MyDebugFormatter(logging.Formatter):
    """"""

    COLOR_CODES = {
        'DEBUG': '\033[92m',  # Зелённый
        'INFO': '\033[94m',  # Синий
        'WARNING': '\033[93m',  # Жёлтый
        'ERROR': '\033[91m',  # Красный
        'CRITICAL': '\033[95m'  # Фиолетовый
    }
    RESET_CODE = '\033[0m'  # Белый

    def __init__(self, max_length, *args, **kwargs):
        self.max_length = max_length
        super().__init__(*args, **kwargs)

    def format(self, record):
        log_message = super().format(record)
        if record.levelname in self.COLOR_CODES:
            if record.levelname == 'DEBUG':
                return f"{self.COLOR_CODES[record.levelname]}{log_message[:self.max_length]}{self.RESET_CODE}"
            else:
                return f"{self.COLOR_CODES[record.levelname]}{log_message}{self.RESET_CODE}"
        else:
            return log_message


def get_handlers(log_level: int, console: int, filemode: str) -> [logging.Handler]:
    """Получение обработчиков для вывода сообщений"""
    fpath = os.path.join(BASE_DIR, f"logs/django {dt.date.today().strftime('%d-%m-%Y')}.log")
    os.makedirs(os.path.dirname(fpath), exist_ok=True)
    if not os.path.isfile(fpath):
        open(fpath, "w+").close()
    # Настройка лога для файла
    file_handler = logging.FileHandler(fpath, mode=filemode)
    file_handler.setLevel(log_level)
    # Настройка лога консоли
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console)
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s: (%(filename)s %(funcName)s %(lineno)d) %(message)s.",
                                  datefmt="%H:%M:%S")
    formatter = MyDebugFormatter(200, formatter._fmt)
    console_handler.setFormatter(formatter)
    return [file_handler, console_handler]


def log_settings(file_log_level: int = logging.INFO, console_log_level: int = logging.DEBUG,
                 filemode: str = 'a') -> dict:
    """Настройки логирования."""
    handlers = get_handlers(file_log_level, console_log_level, filemode)
    return {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': "[%(asctime)s] %(levelname)s: (%(filename)s %(funcName)s %(lineno)d) %(message)s.",
                'datefmt': "%H:%M:%S",
            },
            'colored': {
                '()': MyDebugFormatter,
                'max_length': 200,
                'format': "[%(asctime)s] %(levelname)s: (%(filename)s %(funcName)s %(lineno)d) %(message)s.",
                'datefmt': "%H:%M:%S",
            },
        },
        'handlers': {
            'file': {
                'level': file_log_level,
                'class': 'logging.FileHandler',
                'filename': os.path.join(BASE_DIR, f"logs/django {dt.date.today().strftime('%d-%m-%Y')}.log"),
                'mode': filemode,
                'formatter': 'standard',
            },
            'console': {
                'level': console_log_level,
                'class': 'logging.StreamHandler',
                'formatter': 'colored',
            },
        },
        'root': {
            'level': 'DEBUG',
            'handlers': ['file', 'console'],
        },
    }


LOGGING = log_settings()

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'carscan.User'
