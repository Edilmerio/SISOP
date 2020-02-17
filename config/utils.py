import os
from xml.etree import ElementTree

from django.core.management.utils import get_random_secret_key

from .settings_base_dir import BASE_DIR

def key_secret():
    """
    function that return SECRET_KEY for setting
    red file secret_key or creat it con key
    Returns: secret_key
    """
    abs_path = os.path.join(BASE_DIR, 'file_secret_key')
    if os.path.isfile(abs_path):
        with open(abs_path, 'r') as f:
            for i, line in enumerate(f):
                return line
    sk = get_random_secret_key()
    with open(abs_path, 'w') as f:
        f.writelines(sk)
    return key_secret()

def config_from_sisop_config():
    """
    this function read sisop.conf.xml
    this file contains settings
    Returns: a dict configuration
    """
    path = os.path.join(BASE_DIR, 'sisop.conf.xml')
    if not os.path.isfile(path):
        return {}
    try:
        root1 = (ElementTree.parse(path).getroot())
    except ElementTree.ParseError:
        return {}

    def dict_from_xml(root):
        if not list(root):
            return root.text.rstrip('\n').strip()
        return {child.tag: dict_from_xml(child) for child in root}

    return dict_from_xml(root1)


CONFIG_SISOP = config_from_sisop_config()


class OverwriteConfiguration:
    """
    class for overwrite configuration
    """
    @staticmethod
    def overwrite_settings():
        """
        this function return settings property in sisop_conf.py
        """
        return CONFIG_SISOP.get('settings', None)

    @staticmethod
    def overwrite_celery_beat():
        """
        this function return celery beat property in sisop_conf.py
        Returns:
        """
        return CONFIG_SISOP.get('celery_beat', None)
