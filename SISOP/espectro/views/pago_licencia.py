import io
import os
import json
from datetime import date, datetime

from django.shortcuts import render, redirect, reverse
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django_tables2.export.export import TableExport
from openpyxl import Workbook, load_workbook
from django.db.models import Q
from django.forms import modelformset_factory
from django.db.models import Max, Subquery, OuterRef, Case, When, Value, DateField
from django.http import HttpResponse
from django.db import transaction

from general.models import DivisionTerritorial
from espectro.models import PagoSistema, Sistema, TipoSistema, Radio, Equipo,\
    Solicitud, Licencia
from espectro import utiles, tables
from general.user_metadata import UserPreference
from general.utils import name_file_unique, add_month_to_date, make_directory
from config.settings_base_dir import BASE_DIR
from espectro.forms import PagoForm, PagoSistemaForm
from espectro.exceptions_espectro import DatosNoValidos


class ListadoPago(LoginRequiredMixin, TemplateView):
    template_name = 'espectro/ListadoPagos.html'

    def __init__(self):
        self.per_page_list = ['8', '10', '15', '25', 'todos']
        super().__init__()

    def get(self, request, *args, **kwargs):
        # si args[0]=='1' seran los pagos en proceso == True)
        # si args[0]=='0' seran los pagos terminados
        notify = request.GET.get('notify', None)

        try:
            div_user = DivisionTerritorial.objects.get(identificativo=request.user.unidad_org.strip())
        except DivisionTerritorial.DoesNotExist:
            div_user = None
        if request.user.has_perm('espectro.visualizador_nacional'):
            pagos_visualizar = PagoSistema.objects.all().order_by('-pago__fecha_notificacion')
        else:
            pagos_visualizar = PagoSistema.objects.filter(pago__division_territorial=div_user).order_by('-pago__fecha_notificacion')
        today = date.today()
        if args[0] == '1':
            pagos_buscados = pagos_visualizar.filter(fecha_fin_pago__gte=today)
        else:
            pagos_buscados = pagos_visualizar.filter(fecha_fin_pago__lt=today)
        search = request.GET.get('search', '')
        pagos_filter_search = pagos_buscados
        if search != '':
            pagos_filter_search = pagos_buscados.filter(Q(pago__no_notificacion__icontains=search) | Q(sistema__contains=search))

        if request.user.has_perm('espectro.visualizador_nacional'):
            dict_loc = utiles.div_terrotiriales_validas_seleccionadas(request.GET.get('list_mun', 'todos'))
            pagos_filter_loc = pagos_filter_search \
                .filter(pago__division_territorial__nombre__in=[s for s in dict_loc if dict_loc[s] == 'selected']).distinct()
        else:
            pagos_filter_loc = pagos_filter_search.filter(pago__division_territorial=div_user)
            dict_loc = None

        table = tables.PagosLicenciaTable(pagos_filter_loc)
        # table_order_by = request.GET.get('sort', 'pago')
        # name_orderable_coloum = [colum.order_by_alias for colum in table.columns.orderable()] + \
        #                         ['-' + colum.order_by_alias for colum in table.columns.orderable()]
        # table_order_by = '-fecha_notificacion, division_territorial' if table_order_by not in name_orderable_coloum else table_order_by
        table.order_by = '-fecha_notificacion'
        export_format = request.GET.get('_export', None)
        if not export_format:
            cant_elem = pagos_filter_loc.count()
            per_page = request.GET.get('per_pag', None)
            user_pref = UserPreference(request.user)
            per_page = UserPreference.determine_value_preference(per_page, user_pref.per_page_list_pago_lic, self.per_page_list)[0]
            user_pref.per_page_list_pago_lic = per_page
            int_per_page = cant_elem if per_page == 'todos' else int(per_page)
            page = utiles.pagina_valida(request.GET.get('page', 1), int_per_page, cant_elem)
            table.paginate(page=page, per_page=int_per_page)
            table.cant_rows = len(list(table.data))
            dict_per_page = utiles.dict_elemen_seleced(self.per_page_list, [per_page])
            return render(request, self.template_name,
                          {'table': table, 'busqueda': request.GET.get('search', ''),
                           'municipio_dt_dict': dict_loc, 'dict_per_page': dict_per_page,
                           'cant_elem': cant_elem,
                           'notify': notify})
        else:
            if not TableExport.is_valid_format(export_format):
                export_format = 'xlsx'
            exporter = TableExport(export_format, table, exclude_columns=('archivo_pago',))
            wb = load_workbook(filename=io.BytesIO(exporter.export()))
            wb.active.title = 'Pago Sistemas'
            name_base = 'pago sistemas {}'.format(datetime.now().strftime("%d-%m-%Y %H-%M-%S"))
            ext_file = export_format
            dir_directory = os.path.join('temp', 'daily')
            make_directory(os.path.join(BASE_DIR, dir_directory))
            name_file = name_file_unique(dir_directory, name_base, ext_file)
            abs_path = os.path.join(BASE_DIR, dir_directory, name_file)
            wb.save(os.path.join(abs_path))
            return redirect(reverse('espectro:descargar_ficheros') + '?dir={}'.format(abs_path), permanent=False)


class NuevoPago(LoginRequiredMixin, TemplateView):

    template_name = 'espectro/OperacionesPago.html'

    def get(self, request, *args, **kwargs):
        # return HttpResponse('Hola edilmerio')
        # if not request.user.has_perm('espectro.permisionario'):
        #     return logout_view(request, next=request.path)
        pago_form = PagoForm()
        PagoSistemaFormSet = modelformset_factory(PagoSistema, form=PagoSistemaForm, extra=2, can_delete=True)
        pago_sistemas_formset = PagoSistemaFormSet(queryset=PagoSistema.objects.none())
        # for radio_form in radio_formset:
        #     try:
        #         div_user = DivisionTerritorial.objects.get(identificativo=request.user.unidad_org.strip())
        #     except DivisionTerritorial.DoesNotExist:
        #         div_user = None
        #     municipios = Municipio.objects.filter(centroasociado__centro_principal__division_territorial=div_user).order_by('nombre')
        #     radio_form.fields['municipio'].queryset = municipios
        # tipo_sistema = EquipoForm()
        # solicitud_form = SolicitudForm()
        # licencia_form = LicenciaForm()

        return render(request, self.template_name, {'pago_form': pago_form, 'pago_sistemas_formset': pago_sistemas_formset
                                                    })

    def post(self, request, *args, **kwargs):
        PagoSistemaFormSet = modelformset_factory(PagoSistema, form=PagoSistemaForm, extra=0, can_delete=True)
        pago_sistemas_formset = PagoSistemaFormSet(request.POST, request.FILES,
                                                   queryset=PagoSistema.objects.none())
        valor_total_sist = []
        for i, f in enumerate(pago_sistemas_formset):
            f.empty_permitted = False
            valor_total_sist.append(f.data['form-{}-valor_total'.format(i)])

        pago_form = PagoForm(request.POST, request.FILES, valor_total_sist, instance=None)

        try:
            if not (pago_form.is_valid() and pago_sistemas_formset.is_valid()):
                raise DatosNoValidos('error en los datos del pago')
            with transaction.atomic():
                pago = pago_form.save(commit=False)
                sistema = Sistema.objects.get(sistema=pago_sistemas_formset[0].cleaned_data['sistema'])
                pago.division_territorial = sistema.division_territorial
                pago.save()
                for p in pago_sistemas_formset:
                    sistema = Sistema.objects.get(sistema=p.cleaned_data['sistema'])
                    ps = p.save(commit=False)
                    ps.pago = pago
                    ps.municipio = '/'.join(sorted(list(set([
                        radio.municipio.__str__() for radio in Radio.objects.filter(sistema=sistema)]))))
                    ps.fecha_fin_pago = add_month_to_date(p.cleaned_data['fecha_inicio_pago'], p.cleaned_data['meses_diferir'])
                    ps.valor_mensual = p.cleaned_data['valor_total'] / p.cleaned_data['meses_diferir']
                    ps.save()
        except DatosNoValidos:
            return render(request, self.template_name, {'pago_form': pago_form, 'pago_sistemas_formset': pago_sistemas_formset,
                                                        'notify_1': 'error/ERROR/Corrija los errores... Pruebe otra vez...'})

        resp = HttpResponse('/espectro/listado_pagos/1?notify=success/ACEPTADO/El pago se guardó correctamete...')
        resp.status_code = 209
        return resp


def lista_sistemas_pago_licencias(request):
    """
    function that return json with informaction of system for pago licencia.
    :param request:
    :return:
    """
    query_string = request.GET.get('q', None)
    try:
        div_user = DivisionTerritorial.objects.get(identificativo=request.user.unidad_org.strip())
    except DivisionTerritorial.DoesNotExist:
        div_user = None
    if not request.user.has_perm('espectro.permisionario'):
        HttpResponse(json.dumps([]))
    # sistemas de la DT que no tenga solicitud de baja y tenga numero de sistema.

    sist_dt = Sistema.objects.filter(division_territorial=div_user)
    sist_dt_sin_baja = sist_dt.exclude(solicitud__tipo_solicitud__tipo_solicitud='BAJA')
    sistemas_pagos_proceso = PagoSistema.objects.filter(fecha_fin_pago__gte=date.today()).values_list('sistema', flat=True)
    sist_posibles_pagar = sist_dt_sin_baja.exclude(sistema__in=sistemas_pagos_proceso)
    tipo_sist = Subquery(TipoSistema.objects.filter(equipo__sistema__id=OuterRef('id')).values('tipo_sistema')[:1])
    valor_total = Subquery(Equipo.objects.filter(sistema__id=OuterRef('id')).values('valor_pago_licencia')[:1])
    meses_diferir = Subquery(Equipo.objects.filter(sistema__id=OuterRef('id')).values('meses_diferir_pago')[:1])
    ultima_solicitud = Subquery(Solicitud.objects.filter(Q(sistema__id=OuterRef(OuterRef('id'))), Q(fecha_autorizacion__isnull=False))
                                .order_by('-id').values('id')[:1])
    fecha_ultima_licencia = Subquery(Licencia.objects.filter(solicitud__id=ultima_solicitud).order_by('-id')
                                     .values('fecha_emision')[:1])
    sist = sist_posibles_pagar.filter(sistema__icontains=query_string)\
        .annotate(tipo_sistema_n=tipo_sist)\
        .annotate(valor_total=valor_total)\
        .annotate(meses_diferir=meses_diferir)\
        .annotate(fecha_inicio_pago=fecha_ultima_licencia)\
        .values('id', 'sistema', 'enlace', 'tipo_sistema_n', 'valor_total', 'meses_diferir',
                'fecha_inicio_pago')
    list_dic_id_name = []
    dict_data = {}
    for s in sist:
        # list_dic_id_name.append({'id': s['id'], 'name': '{}|{}'.format(s['sistema'], s['enlace'])})
        list_dic_id_name.append({'id': s['id'], 'name': '{}'.format(s['sistema'])})
        s['valor_total'] = float(s['valor_total']) if s['valor_total'] else s['valor_total']
        s['fecha_inicio_pago'] = s['fecha_inicio_pago'].strftime("%d/%m/%Y") if s['fecha_inicio_pago'] else None
        dict_data[s['id']] = s
    return HttpResponse(json.dumps([list_dic_id_name, dict_data]))
