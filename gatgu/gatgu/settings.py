"""
Django settings for gatgu project.

Generated by 'django-admin startproject' using Django 3.1.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""
import datetime
import json
from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
import boto3
from botocore.config import Config
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECRET_KEY 파일 위치
secret_file = os.path.join(BASE_DIR, 'secrets.json')

with open(secret_file) as f:
    secrets = json.loads(f.read())


# secrets.json 파일에서 SECRET_KEY 가져오기
def get_secret(setting, secrets=secrets):
    try:
        return secrets[setting]
    except KeyError:
        error_msg = "Set the {} environment variable".format(setting)
        raise ImproperlyConfigured(error_msg)


SECRET_KEY = get_secret("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
DEBUG_TOOLBAR = os.getenv('DEBUG_TOOLBAR') in ('true', 'True')

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework.authtoken',
    'user.apps.UserConfig',

    'corsheaders',

    'article',
    'chat',
    'channels',
    'push_notification',

    'report',

    'django_crontab',
    'django_redis',
]

ASGI_APPLICATION = 'gatgu.routing.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('localhost', 6379)],
        }
    }
}

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'corsheaders.middleware.CorsMiddleware',

]

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'EXCEPTION_HANDLER': 'gatgu.utils.custom_exception_handler',
    'DATETIME_FORMAT': '%s.%f',
}
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': datetime.timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': datetime.timedelta(days=30),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',

    'JTI_CLAIM': 'jti',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': datetime.timedelta(days=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': datetime.timedelta(days=10),
}

if DEBUG_TOOLBAR:
    INSTALLED_APPS.append('debug_toolbar')
    MIDDLEWARE.append('debug_toolbar.middleware.DebugToolbarMiddleware')
    INTERNAL_IPS = ('127.0.0.1',)

ROOT_URLCONF = 'gatgu.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'gatgu.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        # local
        'HOST': '127.0.0.1',
        # # test
        'HOST': 'gatgu-rds-test.cmdozwbtes0r.ap-northeast-2.rds.amazonaws.com',

        'PORT': 3306,
        'NAME': 'gatgu_db',
        'USER': 'team-gatgu',
        'PASSWORD': 'gatgu',
    }
}
REDIS_LOCATION_PRIMARY = "redis://test-redasdfis-001.ltzcxl.0001.apn2.cache.amazonaws.com:6379/"
REDIS_LOCATION_REPLICA = "redis://test-redis-002.ltzcxl.0001.apn2.cache.amazonaws.com:6379/"

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        # "LOCATION": "redis://127.0.0.1:6379/3",
        "LOCATION": [
            # os.environ["REDIS_LOCATION_PRIMARY"],
            "redis://test-redis-001.ltzcxl.0001.apn2.cache.amazonaws.com:6379/",
            "redis://test-redis-002.ltzcxl.0001.apn2.cache.amazonaws.com:6379/"
            # os.environ["REDIS_LOCATION_REPLICA"],
        ],
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "MASTER_CACHE": "redis://test-redasdfis-001.ltzcxl.0001.apn2.cache.amazonaws.com:6379/"
        }
    },

    "email": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": [
            "redis://test-redis-001.ltzcxl.0001.apn2.cache.amazonaws.com:6379/",
            "redis://test-redis-002.ltzcxl.0001.apn2.cache.amazonaws.com:6379/"
        ],
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "MASTER_CACHE": "redis://test-redasdfis-001.ltzcxl.0001.apn2.cache.amazonaws.com:6379/"
        }
    },
    "number_of_confirm": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": [
            "redis://test-redis-001.ltzcxl.0001.apn2.cache.amazonaws.com:6379/",
            "redis://test-redis-002.ltzcxl.0001.apn2.cache.amazonaws.com:6379/"
        ],
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "MASTER_CACHE": "redis://test-redasdfis-001.ltzcxl.0001.apn2.cache.amazonaws.com:6379/"
        }
    },
    "activated_email": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": [
            "redis://test-redis-001.ltzcxl.0001.apn2.cache.amazonaws.com:6379/",
            "redis://test-redis-002.ltzcxl.0001.apn2.cache.amazonaws.com:6379/"
        ],
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "MASTER_CACHE": "redis://test-redasdfis-001.ltzcxl.0001.apn2.cache.amazonaws.com:6379/"
        }
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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


# Email

EMAIL_HOST = 'smtp.gmail.com'
# 메일을 호스트하는 서버
EMAIL_PORT = '587'
# gmail과의 통신하는 포트
EMAIL_HOST_USER = 'swppsend@gmail.com'
# 발신할 이메일
EMAIL_HOST_PASSWORD = 'swppsend2020'
# 발신할 메일의 비밀번호
EMAIL_USE_TLS = True
# TLS 보안 방법
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
# 사이트와 관련한 자동응답을 받을 이메일 주소,'team-gatgu@localhost'

# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Seoul'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'
# STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_ROOT = 'static'

CORS_ORIGIN_ALLOW_ALL = True
# CORS_ORIGIN_WHITELIST = [
#     'http://localhost',
#     'http://localhost:3000',
# ]

import firebase_admin
from firebase_admin import credentials

cred = credentials.Certificate("gatgu-firebase-admin-hs.json")
firebase_admin.initialize_app(cred)

CLIENT = boto3.client('s3', config=Config(signature_version='s3v4', region_name='ap-northeast-2'))
BUCKET_NAME = 'gatgubucket'
