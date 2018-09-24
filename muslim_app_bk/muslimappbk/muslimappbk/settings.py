"""
Django settings for muslimappbk project.

Generated by 'django-admin startproject' using Django 2.1.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'jmo%i=431(gx*2(*rn)c%f9@c!(22fzy$-s-*p#*w(a!i%hip9'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'muslimapp.cn', 'www.muslimapp.cn', 'testmuslimapp.cn']

INTERNAL_IPS = ['127.0.0.1']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'management.apps.ManagementConfig',
    'widget_tweaks',
    'debug_toolbar',
    'basic',
    'userauth',
    'showcase',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.weixin',
    'sorl.thumbnail',
    'django_comments_xtd',
    'django_comments',
    'rest_framework',
    'mod_wsgi.server',
    'star_ratings',
    'django_upyun'
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'muslimappbk.urls'

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

WSGI_APPLICATION = 'muslimappbk.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'sqlite3': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    },
    'default': {
        'NAME': 'muslim_app',
        'ENGINE': 'django.db.backends.mysql',
        'USER': 'muslim_app',
        'PASSWORD': 'muslim_app'
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

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

AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',

    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
)


# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "assets"),
]

STATICFILES_STORAGE = 'django_upyun.backends.UpYunStaticStorage'
DEFAULT_FILE_STORAGE = 'django_upyun.backends.UpYunMediaStorage'

UPY_SERVICE = 'muslimapp'

UPY_USERNAME = 'muslimapp'

UPY_PASSWORD = 'muslimapp2018'

UPY_SERVICE_URL = 'http://upyun.muslimapp.cn'

UPY_NEED_COVERAGE = False

UPY_SAVE_FULL_URL = False


# LOGIN_REDIRECT_URL = 'basic:index'
LOGIN_URL = 'userauth:login'

LOGGING = {
    'version': 1,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/home/musa/file.log',
            'formatter': 'simple'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'management': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        }
    }
}

if DEBUG:
    # make all loggers use the console.
    for logger in LOGGING['loggers']:
        LOGGING['loggers'][logger]['handlers'] = ['console']
        
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = "smtp.exmail.qq.com"
EMAIL_PORT = 465
EMAIL_HOST_USER = "admin@muslimapp.cn"
EMAIL_HOST_PASSWORD = "926419@Jelsyj"
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
EMAIL_SUBJECT_PREFIX = '[Muslim App] '
EMAIL_USE_SSL = True

SITE_ID = 1

COMMENTS_APP = 'django_comments_xtd'

COMMENTS_XTD_MAX_THREAD_LEVEL = 1

#  To help obfuscating comments before they are sent for confirmation.
COMMENTS_XTD_SALT = (b"Timendi causa est nescire. "
                     b"Aequam memento rebus in arduis servare mentem.")

# Source mail address used for notifications.
COMMENTS_XTD_FROM_EMAIL = "admin@muslimapp.cn"

# Contact mail address to show in messages.
COMMENTS_XTD_CONTACT_EMAIL = "admin@muslimapp.cn"

MANAGERS = (
    ('Administrator', 'admin@muslimapp.cn'),
    ('Ali Zhou', 'alizhou@muslimapp.cn')
)

COMMENTS_XTD_CONFIRM_EMAIL = False

COMMENTS_XTD_APP_MODEL_OPTIONS = {
    'management.mobileapp': {
        'allow_flagging': True,
        'allow_feedback': False,
        'show_feedback': False,
    }
}

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
#     'DEFAULT_PERMISSION_CLASSES': [
#         'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
#     ]
}

STAR_RATINGS_RERATE = True
STAR_RATINGS_ANONYMOUS = True
