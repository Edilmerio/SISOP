# settings for production environment
import sys

from .settings import *
from . import utils
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
CONN_MAX_AGE = None

ALLOWED_HOSTS = ['*']

WSGI_APPLICATION = 'config.wsgi_prod.application'

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'sisop',
        'USER': 'sisop',
        'PASSWORD': 'sisop',
        'HOST': 'localhost',
        'PORT': '',
    }
}

STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# for file more than 2MB (default)
FILE_UPLOAD_TEMP_DIR = os.path.join(BASE_DIR, 'temp')
FILE_UPLOAD_PERMISSIONS = 0o644

# this statements must the last for overwrite settings in sisop_conf.py
def settings_from_xml():
    data = utils.OverwriteConfiguration.overwrite_settings()
    if not data:
        return
    for k, v in utils.OverwriteConfiguration.overwrite_settings().items():
        setattr(sys.modules[__name__], k, v)


settings_from_xml()
