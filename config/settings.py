"""
Django settings for SISOP project base.

Generated by 'django-admin startproject' using Django 3.0.2.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os

from tzlocal import get_localzone

from . import utils
from .settings_base_dir import *
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = utils.key_secret()


# Application definition

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'auth_sisop.apps.AuthSisopConfig',
    'general.apps.GeneralConfig',
    'espectro.apps.EspectroConfig',
    'administracion.apps.AdministracionConfig',
    'django_tables2',
    'parte_diario.apps.ParteDiarioConfig'
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

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ROOT_URLCONF = 'config.urls'

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

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
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

LANGUAGE_CODE = 'es'

TIME_ZONE = get_localzone().zone

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'

# user model (custom)
AUTH_USER_MODEL = 'auth_sisop.UserSisop'


AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'auth_sisop.backends.BackendSisop'
]

# LDAP CONFIGURATION FOR AUTH.

LDAP_AUTH_URL = "ds.etecsa.cu"

LDAP_AUTH_USE_TLS = False

LDAP_AUTH_SEARCH_BASE = 'ou=etecsa.cu,ou=People,dc=etecsa,dc=cu'

LDAP_AUTH_OBJECT_CLASS = "person"

LDAP_AUTH_USER_FIELDS = {
    "usuario": "uid",
    "email": "mail",
    "nombre": "givenName",
    "apellidos": "sn",
    "telefono": "mobile",
    "unidad_org": "ou",
    "departamento": "departmentNumber",
    "cargo": "title"
}

LOGIN_URL = '/auth/login'

# PAGE_DEFAULT = reverse('espectro:listado sistemas', args={1})

# email settings

EMAIL_HOST = 'smtp.etecsa.cu'
EMAIL_PORT = 25
EMAIL_HOST_USER = 'edilmerio.martinez'
EMAIL_HOST_PASSWORD = 'Enero.2020'
EMAIL_USE_TLS = True
# EMAIL_USE_SSL
DEFAULT_FROM_EMAIL = 'Edilmerio Martinez Escobar <edilmerio.martinez@etecsa.cu>'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'node_modules')
]

# Web server para el calculo de los indicadores
WSDL_WEB_SERVER_INDICADORES = 'http://10.30.1.24/scrras/Service.asmx?WSDL'
METHOD_PTE = 'Pendientes'
METHOD_REP = 'Reparadas'