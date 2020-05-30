"""
Django settings for tracery project.

Generated by 'django-admin startproject' using Django 3.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'xvamp=me)66twer&*2cc!yg(q@+r0p_j%w23x(tux@)g$7wpk%'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['23.22.177.127', '127.0.0.1', 'api.tracery.us']


# Application definition

INSTALLED_APPS = [
    'users',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'storages',
    'venues.apps.VenuesConfig',
    'geolocation.apps.GeolocationConfig',
    'ecommerce.apps.EcommerceConfig',
    'api.apps.ApiConfig',
    'rest_framework', 
    'rest_framework.authtoken',
    'djoser',
    'localflavor',
    'django_db_logger',
    'djcelery_email'
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

ROOT_URLCONF = 'tracery.urls'

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

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(asctime)s %(message)s'
        },
    },
    'handlers': {
        'db_log': {
            'level': 'DEBUG',
            'class': 'django_db_logger.db_log_handler.DatabaseLogHandler'
        },
    },
    'loggers': {
        'db': {
            'handlers': ['db_log'],
            'level': 'DEBUG'
        }
    }
}

WSGI_APPLICATION = 'tracery.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases
"""     'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'database2',
        'USER': 'postgres',
        'PASSWORD': 'MY^KDp2D!#S6q=8Gf+?nCUr$zMT&2D',
        'HOST': 'database2.cgemwwt8zjmm.us-east-1.rds.amazonaws.com',
        'PORT': '5432',
    } 
"""

"""
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
"""
DATABASES = {
   'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'resodb',
        'USER': 'dbmasteruser',
        'PASSWORD': 'MRL*J?lyOdmGibV}*xR2LhrXDX0L$MM5',
        'HOST': 'ls-c0018cd33dbdbeb5013976e76c291fda15d358ac.cfsduybybyb5.us-east-1.rds.amazonaws.com',
        'PORT': '5432',
    } 
}


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'EST'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/


AUTH_USER_MODEL = 'users.Account'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',  # <-- And here
    ],
    'DEFAULT_PERMISSIONS_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'HIDE_USERS': True,
    'USER_CREATE_PASSWORD_RETYPE': False,
}
DJOSER = {
    "SERIALIZERS": {
        "user_create": "api.serializers.UserRegistrationSerializer",
        'current_user': 'api.serializers.InternalAccountSerializer',
        'user': 'api.serializers.ExternalAccountSerializer',
    },
    "PASSWORD_RESET_CONFIRM_URL": "api/auth/users/reset_password_confirm/",
}

MEDIA_ROOT = os.path.join(BASE_DIR, 'media').replace('\\', '/')
MEDIA_URL = '/media/'
GEOIP_PATH = os.path.join(BASE_DIR, "geolocation", "services")

AWS_ACCESS_KEY_ID = "AKIA2GVI5VXV2NXOGGMI"
AWS_SECRET_ACCESS_KEY = "3g8/blI1WY/VAbhrPvTsN1u7h9HtIdgzQdEAlE98"
STATICFILES_LOCATION = 'static'
STATICFILES_STORAGE = 'custom_storages.StaticStorage'
MEDIAFILES_LOCATION = 'media'
DEFAULT_FILE_STORAGE = 'custom_storages.MediaStorage'
AWS_REGION = "us-east-1"
AWS_STORAGE_BUCKET_NAME = 'tracery-schedules-static'
AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
STATIC_URL = "https://%s/" % AWS_S3_CUSTOM_DOMAIN
AWS_DEFAULT_ACL = None

GOOGLE_KEY = "AIzaSyC24MIKKYi7s8lxwgTlAHe0wGaMiZeAhRY"


RABBITMQ_USERNAME = "rabbitadmin"
RABBITMQ_PASSWORD = "bJYNuU4bEGwubtQqFZ89"

SENDGRID_API_KEY = "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"
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = 'apikey'
EMAIL_HOST_PASSWORD = SENDGRID_API_KEY
EMAIL_PORT = 587
EMAIL_USE_TLS = True

aws_access_key = "AKIA2GVI5VXV2NXOGGMI"
aws_secret_key = "3g8%2FblI1WY%2FVAbhrPvTsN1u7h9HtIdgzQdEAlE98"

BROKER_URL = "sqs://{aws_access_key}:{aws_secret_key}@".format(
    aws_access_key=aws_access_key, aws_secret_key=aws_secret_key,
)
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'
CELERY_DEFAULT_QUEUE = 'taskbroker'
CELERY_RESULT_BACKEND = None

BROKER_TRANSPORT_OPTIONS = {
    'region': 'us-east-1',
    'polling_interval': 20,
}

EMAIL_BACKEND = 'djcelery_email.backends.CeleryEmailBackend'

DEFAULT_FROM_EMAIL = "reso-users@tracery.us"

STRIPE_SECRET_KEY = "sk_live_7yINcEkJbton07tN6RIq4f6j00XbpEyEQp"

LOGIN_URL = "/signin/"