from datetime import date
import functools
import calendar

from django.http import HttpResponse
from django.core import serializers
from django.shortcuts import render
from django.db.models import Subquery, OuterRef, DateField
from django.db.models import F

from espectro import tables
from espectro.models import Equipo, TipoSistema, Licencia, Solicitud, Sistema
from general.models import Municipio, DivisionTerritorial, CentroAsociado


# funcion que devuelve una lista de equipos, dado el id del tipo_sistema (con id=-1 se devuleven todos los equipos)
def equipos_por_tipo_sistema(id_tipo_sistema=-100):
    try:
        if id_tipo_sistema == -1:
            data = Equipo.objects.all()
        else:
            tipo_sistema = TipoSistema.objects.get(pk=id_tipo_sistema)
            data = Equipo.objects.filter(tipo_sistema=tipo_sistema)
    except TipoSistema.DoesNotExist:
        return None
    else:
        return data


# funcion que devuelve una lista de equipos, dado el id del tipo_sistema en json para llamadas Ajax
def lista_equipos(request, id_tipo_sistema):
    data = equipos_por_tipo_sistema(id_tipo_sistema)
    if data is None:
        return render(request, 'general/NotFound.html',
                      {'error': 'Este Tipo de Sistema no existe, pongáse en contacto con el admin del sitio'})
    else:
        data_json = serializers.serialize("json", data, fields='equipo')
        return HttpResponse(data_json)


#   funcion para la cracion de una tabla de solicitudes dado un sistema.
def tabla_solicitudes_factory(sistema=None, page=1, solicitud_maracada=None, elem_per_pge=2):
    solicitudes = Solicitud.objects.filter(sistema=sistema).order_by('-id')
    cant_sol = solicitudes.count()
    if cant_sol == 0:
        return None, None
    page = pagina_valida(page, elem_per_pge, cant_sol)
    if solicitud_maracada is None:
        # sera la primera solicitud de la pagina la solicitud_marcada
        solicitud_maracada = solicitudes[elem_per_pge * (page-1)]
    else:
        sol_para_page = solicitudes[elem_per_pge * (page-1): elem_per_pge * page + 1]
        if solicitud_maracada not in sol_para_page:
            ind_sol_marcada = solicitudes.index(solicitud_maracada)
            page = ind_sol_marcada // elem_per_pge if ind_sol_marcada % elem_per_pge == 0 else ind_sol_marcada // elem_per_pge + 1

    table_solicitud = tables.SolicitudesTable(solicitudes, prefix='tb_sol_',
                                              row_attrs={
                                                  'class': lambda record: 'row-marcada' if record.pk == solicitud_maracada.id else ''})
    table_solicitud.order_by = '-id'
    table_solicitud.paginate(page=page, per_page=elem_per_pge)
    return table_solicitud, solicitud_maracada


#   funcion para la cracion de una tabla de licencias, dada una solicitud
def tabla_licencias_factory(solicitud, page=1, elem_per_page=1):
    licencias = Licencia.objects.filter(solicitud=solicitud).order_by('-id')
    cant_lic = licencias.count()
    if cant_lic == 0:
        return None
    page = pagina_valida(page, elem_per_page, cant_lic)
    table_licencias = tables.LicenciasTable(licencias, prefix='tb_lic_')
    table_licencias.order_by = '-id'
    table_licencias.paginate(page=page, per_page=elem_per_page)
    return table_licencias


# funcion que devuelve la fecha de envio de la ultima solicitud enviadad dado un sistema
def fecha_ultima_solicitud(sistema=None):
    if sistema:
        solicitudes = Solicitud.objects.filter(sistema=sistema)
        if solicitudes.exists():
            return solicitudes.order_by('-id')[0].fecha_envio
    #     format Y/M/d
    return date(1, 1, 1)


# funcion que devuelve la fecha de emision de la ultima licencia dado una solicitud
def fecha_ultima_licencia(solicitud=None):
    if solicitud:
        licencias = Licencia.objects.filter(solicitud=solicitud)
        if licencias.exists():
            return licencias.order_by('-id')[0].fecha_emision
    return date(1, 1, 1)


def municipios_validos_seleccionados(dt, cad_municipios):
    """
    dado una cadena de municipios y una DT, devuelve un diccionario con los municipios validos como clave y seleccionados como valor,
    si la cadena es 'todos' devuelve todos los municipios seleccionados de la DT .
    :param dt:
    :param cad_municipios:
    :return:
    """
    if not dt:
        return {}
    municipio_dt_all_set = set(Municipio.objects.filter(centroasociado__centro_principal__division_territorial=dt)
                               .values_list('nombre', flat=True))
    # un diccionario con key el nombre y value si esta en el listado de la url (seleccionado por el user)
    municipio_dt_dict = {mun: '' for mun in municipio_dt_all_set}
    if cad_municipios == 'todos':
        municipio_dt_select_set = municipio_dt_all_set
    else:
        list_mun = cad_municipios.split(',')
        municipio_dt_select_set = {m.strip() for m in list_mun}
    for mun in municipio_dt_select_set:
        if mun in municipio_dt_all_set:
            municipio_dt_dict[mun] = 'selected'
    return municipio_dt_dict


def div_terrotiriales_validas_seleccionadas(cad_dt):
    """
    Dado una cadena de dt devuelve un dicccionario con las dt y marcadas las validas. si la cadena es 'todos' deulve todas
    las dt mrcadas.
    :param cad_dt:
    :return:
    """
    dt_all_set = set(DivisionTerritorial.objects.all().values_list('nombre', flat=True))
    dt_all_dict = {dt: '' for dt in dt_all_set}
    if cad_dt == 'todos':
        dt_select_set = dt_all_set
    else:
        list_dt = cad_dt.split(',')
        dt_select_set = {m.strip() for m in list_dt}
    for dt_nombre in dt_select_set:
        if DivisionTerritorial.objects.filter(nombre=dt_nombre).exists():
            dt_all_dict[dt_nombre] = 'selected'
    return dt_all_dict


def pagina_valida(num_page, elem_per_page, cant_elem):
    """
    funcion que devuelve la pagina adecuada.
    :param num_page: pagina propuesta
    :param elem_per_page: cantidad de elementos por pagina
    :param cant_elem: total de elementos
    :return:
    """
    if elem_per_page == 0:
        return 1
    cant_paginas = cant_elem/elem_per_page if cant_elem % elem_per_page == 0 else cant_elem/elem_per_page + 1
    try:
        page = abs(int(num_page))
    except ValueError:
        return 1
    if cant_paginas >= page:
        return page
    return abs(int(cant_paginas)) if cant_paginas > 0 else 1


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


def sistemas_licencias_vencidas(d):
    """
    return query_set sistemas con licencias vencidas
    ademas el estado del ultimo tramite y la fecha de
    vencimiento
    solo se aplica a los sistemas que tienen al menos
    una licencia y a los q no tinene solicitud de
    BAJA.
    :return:
    q: fecha para realizar ver cuales licenicias estan vencidas
    """
    sist_no_sol_baja = Sistema.objects.exclude(solicitud__tipo_solicitud__tipo_solicitud='BAJA')
    sist_with_lic = sist_no_sol_baja.filter(solicitud__licencia__isnull=False).distinct()

    # fecha de vencimiento de la ultima licencia de la ultima solicitud con licencia
    sol_aut = Solicitud.objects.exclude(fecha_autorizacion=None)
    ult_sol_aut = Subquery(sol_aut.filter(sistema__id=OuterRef(OuterRef('id'))).order_by('-id').values('id')[:1])
    fecha_vencimiento = Subquery(Licencia.objects.filter(solicitud=ult_sol_aut)
                                 .order_by('-id').values('fecha_vencimiento')[:1])
    # sistemas con fecha de vencimiento menor o igual 3 dias despues del dia actual.
    sist_lic_vencidas = sist_with_lic.annotate(fec_venc=fecha_vencimiento).filter(fec_venc__lte=d)

    # dictionary aux {cta:{id_sistema:{sistema:sistema, enlace: enlace, div:div, uso:uso, fecha_vencimiento: fecha_vencimiento}, },}
    # centros asociados a los cuales el sistema afecta
    aux_info = {}
    for sist in sist_lic_vencidas:
        municipios_list = Municipio.objects.filter(radio__sistema__id=sist.pk).distinct().values_list('nombre', flat=True)
        ult_sol = Solicitud.objects.filter(sistema__id=sist.pk).order_by('-id')[0]
        if ult_sol.fecha_autorizacion:
            estado_tramites = 'OK'
        else:
            estado_tramites = 'Pte. Ministerio'
        ctas = CentroAsociado.objects.filter(municipio__nombre__in=municipios_list).distinct()
        for cta in ctas:
            if cta.pk in aux_info:
                aux_info[cta.pk].update(
                    {sist.pk: {'sistema': sist.sistema, 'enlace': sist.enlace, 'equipo': sist.equipo.equipo,
                               'dt': sist.division_territorial.nombre, 'uso': sist.esta_en_uso,
                               'estado_tramite': estado_tramites,
                               'fecha_vencimiento': sist.fec_venc.strftime("%d-%m-%Y")}})
            else:
                aux_info[cta.pk] = {sist.pk: {'sistema': sist.sistema, 'enlace': sist.enlace, 'equipo': sist.equipo.equipo,
                                              'dt': sist.division_territorial.nombre, 'uso': sist.esta_en_uso,
                                              'estado_tramite': estado_tramites,
                                              'fecha_vencimiento': sist.fec_venc.strftime("%d-%m-%Y")}}
    return aux_info


def sistema_info_subcripcion(sistema, solicitud=None, licencia=None):
    """
    return info new sistema for subcription
    :param sistema:
    :param solicitud
    :param licencia
    :return:
    """
    if not sistema:
        return
    municipios_list = Municipio.objects.filter(radio__sistema=sistema)\
        .distinct().values_list('nombre', flat=True)
    ctas = CentroAsociado.objects.filter(municipio__nombre__in=municipios_list).distinct()
    aux_info = {}
    tipo_solicitud = None
    solicitud_id = None
    fecha_vencimiento = None
    licencia_id = None
    attach = None
    if not solicitud:
        solicitudes = Solicitud.objects.filter(sistema=sistema).order_by('-id')
        solicitud_aux = solicitudes[0] if solicitudes else None
    else:
        solicitud_aux = solicitud

    if not solicitud_aux:
        estado_tramites = 'Pte. DT'
    else:
        estado_tramites = 'OK' if solicitud_aux.fecha_autorizacion else 'Pte. Ministerio'
        tipo_solicitud = solicitud_aux.tipo_solicitud.tipo_solicitud
        solicitud_id = solicitud_aux.pk
        if not licencia:
            licencias = Licencia.objects.filter(solicitud=solicitud_aux).order_by('-id')
            licencia_aux = licencias[0] if licencias else None
        else:
            licencia_aux = licencia
        if licencia_aux:
            fecha_vencimiento = licencia_aux.fecha_vencimiento.strftime("%d-%m-%Y")
            licencia_id = licencia_aux.pk
            if licencia_aux.archivo_licencia:
                attach = licencia_aux.archivo_licencia.path

    for cta in ctas:
        if cta.pk in aux_info:
            aux_info[cta.pk].update(
                {sistema.pk: {'sistema': sistema.sistema, 'enlace': sistema.enlace, 'equipo': sistema.equipo.equipo,
                              'dt': sistema.division_territorial.nombre, 'uso': sistema.esta_en_uso, 'solicitud_id': solicitud_id,
                              'tipo_solicitud': tipo_solicitud, 'estado_tramite': estado_tramites, 'licencia_id': licencia_id,
                              'fecha_vencimiento': fecha_vencimiento,
                              'attach': attach}})
        else:
            aux_info[cta.pk] = {sistema.pk: {'sistema': sistema.sistema, 'enlace': sistema.enlace, 'equipo': sistema.equipo.equipo,
                                             'dt': sistema.division_territorial.nombre, 'uso': sistema.esta_en_uso,
                                             'solicitud_id': solicitud_id,
                                             'tipo_solicitud': tipo_solicitud, 'estado_tramite': estado_tramites,
                                             'licencia_id': licencia_id,
                                             'fecha_vencimiento': fecha_vencimiento,
                                             'attach': attach}}
    return aux_info


def p_decorator(f):
    @functools.wraps(f)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponse('NO esta')
        result = f(request*args, **kwargs)
        return result
    return wrapper


def query_pagos_annotate_data():
    pass
    # return PagoSistema.objects.all().annotate(valor_mensual=F('valor_total')/F('meses_diferir'))

