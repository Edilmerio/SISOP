from __future__ import absolute_import, unicode_literals
from datetime import datetime

from config.celery_settings import app

from .procesar_datos_webserver import ProcesarDatos, SaveReparadasWebServer, SavePendientesWebServer

@app.task(name='parte_diario.tasks.procesar_data_pte_rep')
def procesar_data_pte_rep():
    """
    get data web sever 10.30.1.24 for pend
    get data rep from ReparadasAux
    """
    p = ProcesarDatos(datetime.now().date())
    p.procesar_datos()

@app.task(name='parte_diario.tasks.get_rep_web_server')
def get_rep_web_server():
    """
    get data web sever 10.30.1.24 for ReparadasAux
    """
    p = SaveReparadasWebServer()
    p.save_data_web_server()

@app.task(name='parte_diario.tasks.get_pend_web_server')
def get_pen_web_server():
    """
    get data web sever 10.30.1.24 for PendientesAux
    """
    p = SavePendientesWebServer(datetime.now().date())
    p.save_data_web_server()
