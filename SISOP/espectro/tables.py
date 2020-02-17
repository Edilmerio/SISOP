from datetime import date
from django_tables2.export.views import ExportMixin
import django_tables2 as tables
from django_tables2.utils import A
from django.db.models import Max, Subquery, OuterRef, Case, When, Value, DateField
from django.utils.safestring import mark_safe

from espectro.models import Sistema, Licencia, Solicitud, Radio, PagoSistema, Pago


class SistemasTable(ExportMixin, tables.Table):
    def __init__(self, *args, **kwargs):
        # if not kwargs.pop('ordenar', True):
        #     for _, val in self.base_columns.items():
        #         val.orderable = False
        super(SistemasTable, self).__init__(*args, **kwargs)
    # Agregando Columnas
    municipio = tables.Column('Municipio', accessor='id', orderable=True)
    tramites = tables.Column(verbose_name='Trámites', accessor='id', orderable=True)
    editar = tables.LinkColumn('espectro:editar_sistema', text='editar/detalles', args=[A('pk')], orderable=False)
    estado_licencia = tables.Column('Ultima Licencia', accessor='id', orderable=True)

    class Meta:
        model = Sistema
        attrs = {'class': 'table table-condensed table-hover table-bordered'}

    def render_municipio(self, record):
        """
         muestra una cadena de todos los municipios donde el sistema tiene radios.
        :param record: la instancia correspondiente del sistema.
        :return:
        """
        return '/'.join(sorted(list(set([radio.municipio.__str__() for radio in Radio.objects.filter(sistema=record)]))))
        # return Radio.objects.filter(sistema=record).order_by('municipio__nombre').values_list('municipio__nombre', flat=True)[0]

    def render_tramites(self, record):
        """
        Pte. DT: si no tiene ninguna solicitud realizada
        Pte. Ministerio: si la ultima solicitud no tiene fecha de aprobacion
        OK: si la ultia solicitud tiene fecha de aprobacion y por tanto licencias.
        :param record:
        :return:
        """
        solicitudes = Solicitud.objects.filter(sistema=record)
        if not solicitudes:
            return 'Pte. DT'
        if not solicitudes.order_by('-id')[0].fecha_autorizacion:
            return 'Pte. Ministerio'
        return 'OK'

    def render_estado_licencia(self, record, column):
        """
        :param record:
        :param column:
        :return: los dias para que de falta para que la ultima licencia de la ultima solicitud aprobadoa por el Ministerio vensa.
                 en caso de no haber solicitudes o solicitudes aprobadas por el Ministerio retorna No emitida
        """
        solicitudes = Solicitud.objects.filter(sistema=record).order_by('-id')
        for solicitud in solicitudes:
            if solicitud.fecha_autorizacion:
                ultima_licencia = Licencia.objects.filter(solicitud=solicitud).order_by('-id')[0]
                if ultima_licencia.fecha_vencimiento < date.today():
                    column.attrs = {'td': {'style': 'background-color:#d9534f;border-color:rgb(200, 183, 183);color:white'}}
                    return 'Vencida' + '(' + (ultima_licencia.fecha_vencimiento - date.today()).days.__str__() + ' días )'
                column.attrs = {'td': {'style': 'background-color:#5cb85c; border-color:rgb(200, 183, 183); color:white'}}
                return 'Válida' + '(' + (ultima_licencia.fecha_vencimiento - date.today()).days.__str__() + ' días )'
        column.attrs = {'td': {'style': 'background-color:#f0ad4e; border-color:rgb(200, 183, 183); color:white'}}
        return 'No Emitida'

    def order_estado_licencia(self, queryset, is_descending):
        """
        :param queryset:
        :param is_descending:
        :return: ordena el queryset por la fecha de la ultima licencia de la ultima solicitud aprobada.
        """
        sol_aut = Solicitud.objects.exclude(fecha_autorizacion=None)
        ultima_solicitud = Subquery(sol_aut.filter(sistema__id=OuterRef(OuterRef('id')))
                                    .order_by('-id').values('id')[:1])
        ultima_licencia = Subquery(Licencia.objects.filter(solicitud__id=ultima_solicitud).order_by('-id')
                                   .values('fecha_vencimiento')[:1])
        queryset = queryset.annotate(fecha_vencimiento=ultima_licencia)
        queryset = queryset.annotate(fec=Case(
            When(fecha_vencimiento=None, then=Value(date(2100, 12, 31))),
            default='fecha_vencimiento',
            output_field=DateField()
        ))
        queryset = queryset.order_by(('-' if is_descending else '') + 'fec')
        return queryset, True

    def order_municipio(self, queryset, is_descending):
        list_mun = Subquery(Radio.objects.filter(sistema__id=OuterRef('id')).order_by('municipio__nombre').values('municipio__nombre')[:1])
        queryset = queryset.annotate(list_mun=list_mun)
        queryset = queryset.order_by(('-' if is_descending else '') + 'list_mun')
        return queryset, True

    def order_tramites(self, queryset, is_descending):
        fecha_env_ultima_solicitud = Subquery(Solicitud.objects.
                                              filter(sistema__id=OuterRef('id')).order_by('-id').values('fecha_envio')[:1])
        fecha_aut_ultima_solicitud = Subquery(Solicitud.objects.
                                              filter(sistema__id=OuterRef('id')).order_by('-id').values('fecha_autorizacion')[:1])
        queryset = queryset.annotate(fec_env=fecha_env_ultima_solicitud).annotate(fec_aut=fecha_aut_ultima_solicitud)
        queryset = queryset.order_by(('-' if is_descending else '') + 'fec_aut', ('-' if is_descending else '') + 'fec_env')
        return queryset, True

class SolicitudesTable(tables.Table):
    def __init__(self, *args, **kwargs):
        for _, val in self.base_columns.items():
            val.orderable = False
            val.attrs = {'td': {'class': val.accessor}} if not val.attrs else val.attrs
        super(SolicitudesTable, self).__init__(*args, **kwargs)

    # Agregando Columnas
    editar = tables.LinkColumn('espectro:editar_solicitud', text='editar', args=[A('pk')], orderable=False,
                               attrs={'td': {'class': 'editar'}})
    licencia = tables.LinkColumn('espectro:listado_licencias', text='licencias', args=[A('pk')], orderable=False,
                                 attrs={'td': {'class': 'licencia'}})

    class Meta:
        model = Solicitud
        attrs = {'class': 'table table-condensed table-bordered'}
        exclude = ('sistema',)

    def render_archivo_solicitud(self, record):
        return mark_safe('<a href="/espectro/descargar_fichero?dir='+record.archivo_solicitud.name
                         + '"' + '><i class="fa fa-download"></i>solicitud</a>')

    # def render_Editar(self, record):
    #     # Si la solicitud tya tiene fecha de autorizacion no se puede editar.
    #     if Solicitud.objects.get(pk=record.id).fecha_autorizacion:
    #         return ''
    #     return mark_safe('<a href=' + reverse('espectro:editar_solicitud', args=[record.id])+'>editar</a>')


class LicenciasTable(tables.Table):
    def __init__(self, *args, **kwargs):
        for _, val in self.base_columns.items():
            val.orderable = False
        super(LicenciasTable, self).__init__(*args, **kwargs)

    class Meta:
        model = Licencia
        attrs = {'class': 'table table-condensed table-hover table-bordered'}

    def render_archivo_licencia(self, record):
        return mark_safe('<a href="/espectro/descargar_fichero?dir='+record.archivo_licencia.name+'"'
                         + '><i class="fa fa-download"></i>licencia</a>')


class SolicitudesProcesoTable(tables.Table):

    class Meta:
        model = Solicitud
        attrs = {'class': 'table table-condensed table-hover table-bordered'}
        # exclude = ('id',)
        sequence = ('sistema', 'enlace', 'municipio', 'division_territorial', 'fecha_envio', 'fecha_autorizacion',
                    'tipo_solicitud', 'archivo_solicitud', 'editar')

    # Agregando Columnas
    enlace = tables.Column('Enlace', accessor='id', orderable=False)
    municipio = tables.Column('Municipio', accessor='id', orderable=False)
    editar = tables.LinkColumn('espectro:editar_sistema', text='editar/detalles', args=[A('sistema.id')], orderable=False)
    division_territorial = tables.Column('División Territorial', accessor='id', orderable=False)

    def __init__(self, *args, **kwargs):
        for _, val in self.base_columns.items():
            val.orderable = False
        super().__init__(*args, **kwargs)

    def render_enlace(self, record):
        return Sistema.objects.get(solicitud=record).enlace.__str__()

    def render_archivo_solicitud(self, record):
        return mark_safe('<a href="/espectro/descargar_fichero?dir='+record.archivo_solicitud.name+'"'
                         + '><i class="fa fa-download"></i>Descargar Solicitud</a>')

    def render_sistema(self, record):
        if not record.sistema.sistema:
            return "—"
        return record.sistema.sistema

    def render_municipio(self, record):
        """
         muestra una cadena de todos los municipios donde el sistema tiene radios.
        :param record: la instancia correspondiente del sistema.
        :return:
        """
        sistema = Sistema.objects.filter(solicitud=record)[0]
        return '/'.join(sorted(list(set([radio.municipio.__str__() for radio in Radio.objects.filter(sistema=sistema)]))))

    def render_division_territorial(self, record):
        sistema = Sistema.objects.filter(solicitud=record)[0]
        return sistema.division_territorial


class PagosLicenciaTable(tables.Table):

    class Meta:
        model = PagoSistema
        attrs = {'class': 'table table-condensed table-bordered'}
        exclude = ('id',)
        sequence = ('pago', 'fecha_notificacion', 'valor_pago', 'sistema', 'enlace', 'tipo_sistema', 'municipio', 'valor_total',
                    'valor_mensual', 'fecha_inicio_pago', 'meses_diferir', 'fecha_fin_pago', 'division_territorial', 'archivo_pago')

    # Agregando Columnas
    fecha_notificacion = tables.Column('Fecha Notificación', accessor='id', orderable=False)
    division_territorial = tables.Column('División Territorial', accessor='id', orderable=False)
    archivo_pago = tables.Column('Archivos', accessor='id', orderable=False)
    valor_pago = tables.Column('Valor Total', accessor='id', orderable=False)
    pago = tables.Column('Pago', accessor='id', orderable=True)

    def __init__(self, *args, **kwargs):
        for _, val in self.base_columns.items():
            val.orderable = False
        super().__init__(*args, **kwargs)

    def render_division_territorial(self, record):
        pago = Pago.objects.filter(pagosistema=record)[0]
        return pago.division_territorial

    def render_pago(self, record):
        pago = Pago.objects.filter(pagosistema=record)[0]
        return pago.no_notificacion

    def render_valor_pago(self, record):
        pago = Pago.objects.filter(pagosistema=record)[0]
        return pago.valor_total

    def render_fecha_notificacion(self, record):
        pago = Pago.objects.filter(pagosistema=record)[0]
        return pago.fecha_notificacion.strftime("%d/%m/%Y")

    def render_archivo_pago(self, record):
        return mark_safe('<a href="/espectro/descargar_fichero?dir=' + record.pago.archivo_pago.name + '"'
                         + '><i class="fa fa-download"></i>Archivos</a>') if record.pago.archivo_pago.name != '' else '—'
