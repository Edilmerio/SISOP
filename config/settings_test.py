# settings for production environment
import sys

from .settings import *
from . import utils
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

WSGI_APPLICATION = 'config.wsgi_dev.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'sisop',
        'USER': 'sisop',
        'PASSWORD': 'sisop',
        'HOST': '192.168.43.61',
        'PORT': '',
    }
}

# this statements must the last for overwrite settings in sisop_conf.py
def settings_from_xml():
    data = utils.OverwriteConfiguration.overwrite_settings()
    if not data:
        return
    for k, v in utils.OverwriteConfiguration.overwrite_settings().items():
        setattr(sys.modules[__name__], k, v)


settings_from_xml()