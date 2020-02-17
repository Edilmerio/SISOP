from __future__ import absolute_import, unicode_literals
from datetime import date, timedelta
import locale
import calendar

from config.celery_settings import app
from espectro.utiles import sistemas_licencias_vencidas, sistema_info_subcripcion
from general.utils import info_user_subcripcion, do_emails_subcripcion, send_emails
from espectro.models import Sistema, Solicitud, Licencia


@app.task(name='espectro.tasks.licencias_vencidas_daily')
def licencias_vencidas_daily():
    """
    send email with licencias_vencidas (o casi al vencer)
     to all subcriptor of the group espectro
    """
    dict_info = sistemas_licencias_vencidas(date.today() + timedelta(days=3))
    info_user = info_user_subcripcion('espectro', dict_info)
    email = do_emails_subcripcion(info_user, 'Licencias Vencidas', 'Licencias Vencidas')
    send_emails(email)


@app.task(name='espectro.tasks.nuevo_sistema')
def nuevo_sistema(sistema_id):
    """
    send email to all user subcription al ginfo espectro
    and cta equal cta of the radios of the sistema.
    :param sistema_id:
    :return:
    """
    try:
        sistema = Sistema.objects.get(pk=int(sistema_id))
        dict_info = sistema_info_subcripcion(sistema)
        info_user = info_user_subcripcion('espectro', dict_info)
        email = do_emails_subcripcion(info_user, 'Nuevo Sistema', 'Nuevo Sistema')
        send_emails(email)
    except (Sistema.DoesNotExist, ValueError):
        pass


@app.task(name='espectro.tasks.nueva_solicitud')
def nueva_solicitud(info=None, asunto='Nueva Solicitud', titulo='Nueva Solicitud'):
    """
    send email to all user subcription al ginfo espectro
    and cta equal cta of the radios of the sistema.
    :param info
    :param asunto
    :param titulo
    :return:
    """
    info_user = info_user_subcripcion('espectro', info)
    email = do_emails_subcripcion(info_user, asunto, titulo)
    send_emails(email)


@app.task(name='espectro.tasks.nueva_licencia')
def nueva_licencia(licencia_id):
    """
        send email to all user subcription to ginfo espectro
        and cta equal cta of the radios of the sistema
        if that licencia is associate to the last solicitud
        with licenicia
        :param licencia_id:
        :return:
        """
    try:
        licencia = Licencia.objects.get(pk=int(licencia_id))
        solicitud = licencia.solicitud
        ult_sol = Solicitud.objects.filter(sistema=solicitud.sistema, fecha_autorizacion__isnull=False).order_by('-id')[0]
        if solicitud != ult_sol:
            raise ValueError
        dict_info = sistema_info_subcripcion(solicitud.sistema, solicitud, licencia)
        info_user = info_user_subcripcion('espectro', dict_info)
        email = do_emails_subcripcion(info_user, 'Nueva Licencia', 'Nueva Licencia')
        send_emails(email)
    except (Licencia.DoesNotExist, ValueError):
        pass


@app.task(name='espectro.tasks.sistemas_renovar_mes')
def sistemas_renovar_mes():
    """
   send email with sistemas a renovar en el mes o no renovados
    to all subcriptor of the group espectro
    se enviara todo los dias 1 de cada mes
   """
    today = date.today()
    d = date(year=today.year, month=today.month, day=calendar.monthrange(
        year=today.year, month=today.month
    )[-1])
    dict_info = sistemas_licencias_vencidas(d)
    info_user = info_user_subcripcion('espectro', dict_info)

    locale.setlocale(locale.LC_ALL, '')
    mes_string = calendar.month_name[date.today().month].upper()
    email = do_emails_subcripcion(info_user, 'Sistemas a renovar mes {}'.format(mes_string),
                                  'Sistemas a renovar mes {}'.format(mes_string))
    send_emails(email)
