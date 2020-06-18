# settings for production environment
import sys

from .settings import *
from . import utils

ALLOWED_HOSTS = ['*']

WSGI_APPLICATION = 'config.wsgi_dev.application'

# this statements must the last for overwrite settings in sisop_conf.py
def settings_from_xml():
    data = utils.OverwriteConfiguration.overwrite_settings()
    if not data:
        return
    for k, v in utils.OverwriteConfiguration.overwrite_settings().items():
        setattr(sys.modules[__name__], k, v)


settings_from_xml()
