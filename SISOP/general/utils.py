from wsgiref.util import FileWrapper
import os
import random
from smtplib import SMTPException
from datetime import time, datetime
import calendar

from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.core.mail import EmailMessage, get_connection
from django.template.loader import render_to_string

from config.settings_base_dir import BASE_DIR
from .models import CentroAsociado


class FixedFileWrapper(FileWrapper):
    def __iter__(self):
        self.filelike.seek(0)
        return self


def download_file_memory(file):
    """
    return the response with file for download
    :param file:
    :return:
    """
    f = FileWrapper(file)
    response = HttpResponse(f)
    # response['Content-Length'] = os.path.getsize(abs_path)
    # response['Content-Disposition'] = "attachment; filename=%s" % os.path.basename(path)
    return response


def name_file_unique(dir_directory, base_name_file, ext_file):
    """
    retuur a unique name the a file , based in relative dir_directory  to setting.BASE_DIR
    with extension ext_file
    """
    b = base_name_file
    abs_path = os.path.join(BASE_DIR, dir_directory, b + '.{}'.format(ext_file))
    while os.path.isfile(abs_path):
        b = base_name_file + '_{}'.format(int(random.random()*1000000))
        abs_path = os.path.join(BASE_DIR, dir_directory, b + '.{}'.format(ext_file))
    return b + '.{}'.format(ext_file)


def dict_elemen_seleced(list_elem, list_selected):
    """
    return dictionary, key = list_elemnt[n] and value = 'selected' if list_elemt[n] in lis_selected
    else ''
    :param list_elem:
    :param list_selected:
    :return:
    """
    dict_elements = {}
    for elem in list_elem:
        if elem in list_selected:
            dict_elements[elem] = 'selected'
        else:
            dict_elements[elem] = ''
    return dict_elements


def info_user_subcripcion(ginfo, dict_info):
    """
    dado un grupo de informaciones y un diccionario con la informacioes
    por centro asociado, como clave, centroasociado.pk y valor otro diccionario
    con clave identificativo de la informacion y valor los datos de la informacion
    genera un dict con clave email y valor un dict con los datos de la info.
    :param ginfo:
    :param dict_info:
    :return:
    """
    if dict_info == {} or not dict_info:
        return
    User = get_user_model()
    user_info = User.objects.filter(subcripcion__ginfo__ginfo=ginfo).distinct()

    info_user_sub = {}
    for u in user_info:
        aux_dict = {}
        for cta in CentroAsociado.objects.filter(subcripcion__user=u, subcripcion__ginfo__ginfo=ginfo):
            if cta.pk in dict_info:
                aux_dict.update(dict_info[cta.pk])
            elif str(cta.pk) in dict_info:
                aux_dict.update(dict_info[str(cta.pk)])
        if aux_dict != {}:
            info_user_sub.update({u.email: aux_dict})
    return None if info_user_sub == {} else info_user_sub


def do_emails_subcripcion(info_user_sub, asunto='Notificación', titulo='Notificación'):
    """
    genera una tupla de EmailMessage con los datos
    en info_user_sub
    :param info_user_sub:
    :param asunto
    :param titulo
    :return:
    """
    if info_user_sub is None:
        return
    emails = []
    for key, value in info_user_sub.items():
        attach = []
        if value == {}:
            continue
        for k1, v1 in value.items():
            if 'attach' in v1 and v1['attach']:
                attach.append(v1['attach'])
        saludos = good_days() + '....'
        body_html = render_to_string('general/Email.html', {'dict_data': value, 'titulo': titulo, 'saludos': saludos})
        e = EmailMessage(subject=asunto, body=body_html, to=[key])
        e.content_subtype = 'html'
        for a in attach:
            e.attach_file(a)
        emails.append(e)
    return emails


def send_emails(emails):
    connection = get_connection()  # Use default email connection
    try:
        if emails:
            connection.send_messages(emails)
    except SMTPException:
        write_log('Error en el envio de email')


def good_days():
    """
    return Buenos dias, buenas Noches, etc
    :return:
    """
    hour0 = time(hour=0, minute=0)
    hour12 = time(hour=12, minute=0)
    hour19 = time(hour=19, minute=0)
    hour24 = time(hour=23, minute=59, second=59)

    time_now = datetime.now().time()
    if hour0 <= time_now < hour12:
        return 'Buenos días'
    elif hour12 <= time_now < hour19:
        return 'Buenas tardes'
    elif hour19 <= time_now <= hour24:
        return 'Buenas noches'


def write_log(string):
    dir_log = os.path.join(BASE_DIR, 'log')
    try:
        with open(dir_log, mode='a', errors='ignore') as f:
            line = '[{}]: '.format(datetime.now().strftime('%d/%m/%Y %H:%M:%S')) + string + '\n'
            f.writelines(line)
    except OSError:
        pass


def write_txt(dirr, string):
    """
    write the string in txt with dirr
    :param string:
    :param dirr
    :return:
    """
    # if not os.path.isfile(dirr):
    #     return
    try:
        with open(dirr, mode='w', errors='ignore') as f:
            line = string
            f.writelines(line)
    except OSError:
        pass


def red_txt(dirr, n):
    """
    red n line
    :param dirr:
    :param n
    :return:
    """
    if not os.path.isfile(dirr):
        return
    lines = []
    try:
        with open(dirr, mode='r', errors='ignore') as f:
            for i, line in enumerate(f):
                if n == i:
                    return lines
                lines.append(line)
        return lines
    except OSError:
        return


def make_directory(dirr):
    """
    make directory if not exist
    :param dirr:
    :return:
    """
    try:
        os.makedirs(dirr)
    except OSError:
        pass


def add_month_to_date(d, cant_month):
    """
    add month to date and replace day for last day of new month
    :param d:
    :param cant_month:
    :return:
    """
    r = (d.month + cant_month - 1) % 12
    q = (d.month + cant_month - 1) // 12
    if r == 0:
        rel_years = q - 1
        m = 12
    else:
        rel_years = q
        m = r
    last_day = calendar.monthrange(d.year+rel_years, m)[1]
    return d.replace(d.year+rel_years, month=m, day=last_day)
