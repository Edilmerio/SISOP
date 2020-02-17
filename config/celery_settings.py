# celery -A SISOP worker -l info          start worker  (venv activo)
# si no esta activado el venv J:\SISOPpy1.0\SISOP>"J:\SISOP\venvSISOP\Scripts\celery.exe" -A config  worker -l info
# ctrl + c                                        stop worker

# celery -A SISOP beat --loglevel=info    start beat
# si no esta activado el venv J:\SISOPpy1.0\SISOP>"J:\SISOP\venvSISOP\Scripts\celery.exe" -A config beat -l info

# ctrl + c                                        stop beat

from __future__ import absolute_import, unicode_literals
import os
import sys

from celery import Celery
from celery.schedules import crontab

from config.settings_base_dir import BASE_DIR
from config import utils

sys.path.append(os.path.join(BASE_DIR, 'SISOP'))

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# error ValueError: not enough values to unpack (expected 3, got 0)
os.environ.setdefault('FORKED_BY_MULTIPROCESSING', '1')

app = Celery('SISOP')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')
# app.conf.timezone = get_localzone().zone
app.conf.enable_utc = False

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


app.conf.beat_schedule = {
    'del-files-every-day': {
        'task': 'general.tasks.delete_files_daily',
        # 'schedule': 5.0,
        'schedule': crontab(hour=2, minute=00, day_of_week='*'),
        'args': (os.path.join('temp', 'daily'),)
    },

    'licencias-vencidas-every-day': {
        'task': 'espectro.tasks.licencias_vencidas_daily',
        # 'schedule': 5.0,
        'schedule': crontab(hour=3, minute=00, day_of_week=1),
    },
    'sistemas-renovar-mes': {
        'task': 'espectro.tasks.sistemas_renovar_mes',
        # 'schedule': 5.0,
        'schedule': crontab(hour=4, minute=00, day_of_month='2'),
    },
}

def settings_from_xml():
    data = utils.OverwriteConfiguration.overwrite_celery_beat()
    if data:
        for k, v in utils.OverwriteConfiguration.overwrite_celery_beat().items():
            if k in app.conf.beat_schedule:
                app.conf.beat_schedule[k]['schedule'] = crontab(**v)


settings_from_xml()
