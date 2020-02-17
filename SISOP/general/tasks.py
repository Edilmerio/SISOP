from __future__ import absolute_import, unicode_literals
import os

from config.celery_settings import app
from config.settings import BASE_DIR


@app.task(name='general.tasks.delete_files_daily')
def delete_files_daily(directory_files):
    """
    delete all file in  relative directory_files directory
    """
    abs_path = os.path.join(BASE_DIR, directory_files)
    if os.path.exists(abs_path):
        with os.scandir(abs_path) as directory:
            for entry in directory:
                if entry.stat().st_ctime > 10:
                    try:
                        os.remove(entry.path)
                    except OSError:
                        pass
