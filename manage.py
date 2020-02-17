#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

from config import settings_base_dir


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_dev')
    sys.path.append(os.path.join(settings_base_dir.BASE_DIR, 'SISOP'))
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        )
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
