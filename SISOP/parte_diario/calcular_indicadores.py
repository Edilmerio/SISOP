from datetime import timedelta, date
import calendar

from django.db.models import Sum, Q, Subquery, OuterRef

from general.models import CentralTelefonica, CentroAsociado, DivisionTerritorial, CentroPrincipal
from .models import Reparadas, Pendientes, LineasServicios, ClasificacionServicio


class CalcularIndicadores:

    def __init__(self, fecha_inicio, fecha_fin, dt):
        """
        fecha_inicio es el inicio del periodo de calculo
        fecha_fin es el fin del periodo de calculo.
        """
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.dt = dt
        self.fecha_utilizar_lineas = None
        self.data_ind_ct_tb = {}
        self.data_ind_ct_tx = {}
        self.data_ind_cta_tb = {}
        self.data_ind_cta_tx = {}
        self.data_ind_ctp_tb = {}
        self.data_ind_ctp_tx = {}

        self.set_fecha_utilizar_lineas()

    def set_fecha_utilizar_lineas(self):
        first_day_month = date(year=self.fecha_inicio.year, month=self.fecha_inicio.month, day=1)
        ultimas_lineas = LineasServicios.objects\
            .filter(centro_asociado__centro_principal__division_territorial=self.dt, fecha__lte=first_day_month)
        if ultimas_lineas:
            self.fecha_utilizar_lineas = ultimas_lineas.order_by('-fecha')[0].fecha

    def get_fecha_utilizar_lineas(self):
        return self.fecha_utilizar_lineas

    def obtener_data_primarios(self):
        """
        Realiza el calculo de los indicadores
        a nivel de CT, tanto para datos como para telefono
        """
        centrales = CentralTelefonica.objects.filter(centro_asociado__centro_principal__division_territorial=self.dt) \
            .order_by('centro_asociado__centro_principal__nombre')
        self.data_ind_ct_tb = self.data_indicadores_nivel_ct(centrales, ClasificacionServicio.objects.get(clasificacion='telefono'))
        self.data_ind_ct_tx = self.data_indicadores_nivel_ct(centrales, ClasificacionServicio.objects.get(clasificacion='datos'))

    def data_indicadores_nivel_ct(self, centrales, clasificacion):
        """
        Obtiene los datos primarios para el calculo de los indicadores
        a nivel de CT
        tipo es la clasificacion del servicio (datos o telefono)
        centrales son la centrales para el calculo.
        """
        reparadas_periodo = Reparadas.objects.filter(Q(clasificacion=clasificacion)
                                                     & Q(fecha__gte=self.fecha_inicio)
                                                     & Q(fecha__lte=self.fecha_fin))
        pendientes_periodo = Pendientes.objects.filter(Q(clasificacion=clasificacion)
                                                       & Q(fecha=self.fecha_fin))
        pendintes_dia_anterior = Pendientes.objects.filter(Q(clasificacion=clasificacion)
                                                           & Q(fecha=(self.fecha_inicio - timedelta(days=1))))
        sum_rep_lte_1d = Subquery(reparadas_periodo.filter(central_id=OuterRef('id'))
                                  .values('central').annotate(s=Sum('rep_lte_1d')).values('s')[:1])
        sum_demora_lte_1d = Subquery(reparadas_periodo.filter(central_id=OuterRef('id'))
                                     .values('central').annotate(s=Sum('demora_lte_1d')).values('s')[:1])
        sum_rep_lte_3d = Subquery(reparadas_periodo.filter(central_id=OuterRef('id'))
                                  .values('central').annotate(s=Sum('rep_lte_3d')).values('s')[:1])
        sum_demora_lte_3d = Subquery(reparadas_periodo.filter(central_id=OuterRef('id'))
                                     .values('central').annotate(s=Sum('demora_lte_3d')).values('s')[:1])
        sum_rep_gt_3d = Subquery(reparadas_periodo.filter(central_id=OuterRef('id'))
                                 .values('central').annotate(s=Sum('rep_gt_3d')).values('s')[:1])
        sum_demora_gt_3d = Subquery(reparadas_periodo.filter(central_id=OuterRef('id'))
                                    .values('central').annotate(s=Sum('demora_gt_3d')).values('s')[:1])
        sum_pend = Subquery(pendientes_periodo.filter(central_id=OuterRef('id'))
                            .values('central').annotate(s=Sum('pendientes')).values('s')[:1])
        pend_dia_anterior = Subquery(pendintes_dia_anterior.filter(central_id=OuterRef('id'))
                                     .values('central').annotate(s=Sum('pendientes')).values('s')[:1])
        queryset = centrales.annotate(sum_rep_lte_1d=sum_rep_lte_1d, sum_demora_lte_1d=sum_demora_lte_1d,
                                      sum_rep_lte_3d=sum_rep_lte_3d, sum_demora_lte_3d=sum_demora_lte_3d,
                                      sum_rep_gt_3d=sum_rep_gt_3d, sum_demora_gt_3d=sum_demora_gt_3d,
                                      sum_pend=sum_pend, pend_dia_anterior=pend_dia_anterior) \
            .values('central', 'sum_rep_lte_1d', 'sum_demora_lte_1d', 'sum_rep_lte_3d', 'sum_demora_lte_3d',
                    'sum_rep_gt_3d', 'sum_demora_gt_3d', 'sum_pend', 'pend_dia_anterior')
        return {q['central']: q for q in queryset}

    def calculo_indicadores_nivel_ct(self):
        """
        realiza el calculo de los indicadores a nivel de CT
        data_indicadores_ct es un dict con los datos primario a nivel de CT para el calculo
        del tipo {central: data}
        """
        result_tb = []
        result_tx = []

        for k, v in self.data_ind_ct_tb.items():
            r = self.do_calculo(0, [v])
            r.update({'nivel': k})
            result_tb.append(r)

        for k, v in self.data_ind_ct_tx.items():
            r = self.do_calculo(0, [v])
            r.update({'nivel': k})
            result_tx.append(r)
        return result_tb, result_tx

    def get_data_nivel(self, centrales):
        """return los datos relacionados con un nivel
            centrales son las centrales asociadas a ese nivel
        """
        data_tb = []
        data_tx = []
        for c in centrales:
            try:
                data_tb.append(self.data_ind_ct_tb[c])
            except KeyError:
                pass
            try:
                data_tx.append(self.data_ind_ct_tx[c])
            except KeyError:
                pass
        return data_tb, data_tx

    def calculo_indicadores_nivel_cta(self):
        """
        realiza el calculo de los indicadores a nivel de CTA)
        """
        resul_tb = []
        resul_tx = []
        for cta in CentroAsociado.objects.filter(centro_principal__division_territorial=self.dt).order_by('centro_principal__nombre'):
            lineas_tb = 0 if not self.fecha_utilizar_lineas else LineasServicios.objects\
                .filter(centro_asociado=cta, fecha=self.fecha_utilizar_lineas)[0].abonado
            lineas_tx = 0 if not self.fecha_utilizar_lineas else LineasServicios.objects \
                .filter(centro_asociado=cta, fecha=self.fecha_utilizar_lineas)[0].datos
            centrales = cta.centraltelefonica_set.values_list('central', flat=True)
            data_tb, data_tx = self.get_data_nivel(centrales)
            r = self.do_calculo(lineas_tb, data_tb)
            r.update({'nivel': cta.nombre})
            resul_tb.append(r)

            r = self.do_calculo(lineas_tx, data_tx)
            r.update({'nivel': cta.nombre})
            resul_tx.append(r)
        return resul_tb, resul_tx

    def calculo_indicadores_nivel_ctp(self):
        """
        realiza el calculo de los indicadores a nivel de CTP)
        """
        resul_tb = []
        resul_tx = []
        sum_lineas_tb = Subquery(LineasServicios.objects
                                 .filter(centro_asociado__centro_principal_id=OuterRef('id'), fecha=self.fecha_utilizar_lineas)
                                 .values('centro_asociado__centro_principal').annotate(s=Sum('abonado')).values('s')[:1])
        sum_lineas_tx = Subquery(LineasServicios.objects
                                 .filter(centro_asociado__centro_principal_id=OuterRef('id'), fecha=self.fecha_utilizar_lineas)
                                 .values('centro_asociado__centro_principal').annotate(s=Sum('datos')).values('s')[:1])
        for ctp in CentroPrincipal.objects.filter(division_territorial=self.dt).order_by('nombre') \
                .annotate(lineas_tb=sum_lineas_tb, lineas_tx=sum_lineas_tx):
            centrales = CentralTelefonica.objects.filter(centro_asociado__centro_principal=ctp).values_list('central', flat=True)
            data_tb, data_tx = self.get_data_nivel(centrales)
            r = self.do_calculo(ctp.lineas_tb, data_tb)
            r.update({'nivel': ctp.nombre})
            resul_tb.append(r)

            r = self.do_calculo(ctp.lineas_tx, data_tx)
            r.update({'nivel': ctp.nombre})
            resul_tx.append(r)
        return resul_tb, resul_tx

    def calculo_indicadores_nivel_dt(self):
        """
        realiza el calculo de los indicadores a nivel de DT)
        """
        resul_tb = []
        resul_tx = []
        lineas_tb = 0 if not self.fecha_utilizar_lineas else LineasServicios.objects\
            .filter(centro_asociado__centro_principal__division_territorial=self.dt, fecha=self.fecha_utilizar_lineas)\
            .aggregate(sum=Sum('abonado'))['sum']
        lineas_tx = 0 if not self.fecha_utilizar_lineas else LineasServicios.objects \
            .filter(centro_asociado__centro_principal__division_territorial=self.dt, fecha=self.fecha_utilizar_lineas) \
            .aggregate(sum=Sum('datos'))['sum']
        centrales = CentralTelefonica.objects.filter(centro_asociado__centro_principal__division_territorial=self.dt) \
            .values_list('central', flat=True)
        data_tb, data_tx = self.get_data_nivel(centrales)
        r = self.do_calculo(lineas_tb, data_tb)
        r.update({'nivel': 'DT-{}'.format(self.dt.nombre)})
        resul_tb.append(r)

        r = self.do_calculo(lineas_tx, data_tx)
        r.update({'nivel': 'DT-{}'.format(self.dt.nombre)})
        resul_tx.append(r)
        return resul_tb, resul_tx

    def do_calculo(self, lineas, data):

        """
        realiza el calculo de los indicadores agrupando todos los
        data es una lista de dictionarios con los datos de las centrales
        que se quieren agrupar
        datos de data
        retun dictionario
        """

        def group():
            # dict con la extructuta de los datos
            r = {'sum_rep_lte_1d': 0, 'sum_demora_lte_1d': 0, 'sum_rep_lte_3d': 0, 'sum_demora_lte_3d': 0, 'sum_rep_gt_3d': 0,
                 'sum_demora_gt_3d': 0, 'sum_pend': 0, 'pend_dia_anterior': 0}
            if not data:
                return r
            for d in data:
                for k, v in r.items():
                    r[k] = v + (0 if not d[k] else d[k])
            return r

        dias_ac_ri = (self.fecha_fin - self.fecha_inicio).days + 1
        cant_dias_mes = calendar.monthrange(self.fecha_inicio.year, self.fecha_inicio.month)[1]
        resultado = group()
        resultado.update(
            {'rep_total': resultado['sum_rep_lte_1d'] + resultado['sum_rep_lte_3d'] + resultado['sum_rep_gt_3d'],
             'demora_total': round(resultado['sum_demora_lte_1d'] + resultado['sum_demora_lte_3d'] + resultado['sum_demora_gt_3d'], 2),
             'lineas': lineas if lineas else 0
             })
        sum_rep_lte_1d_rep_lte_3d = resultado['sum_rep_lte_1d'] + resultado['sum_rep_lte_3d']
        resultado.update(
            {'ri': resultado['rep_total'] + resultado['sum_pend'] - resultado['pend_dia_anterior'],
             'demora_prom': round((resultado['demora_total'] / resultado['rep_total'] if resultado['rep_total'] > 0 else 0.00), 2),
             'por_ciento_rep_lte_1d': round(
                 (resultado['sum_rep_lte_1d'] * 100 / resultado['rep_total'] if resultado['rep_total'] > 0 else 100.00), 2),
             'por_ciento_rep_lte_3d': round(
                 (sum_rep_lte_1d_rep_lte_3d * 100 / resultado['rep_total'] if resultado['rep_total'] > 0 else 100.00), 2),
             'por_ciento_rep_gt_3d': round(
                 (resultado['sum_rep_gt_3d'] * 100 / resultado['rep_total'] if resultado['rep_total'] > 0 else 0.00), 2),
             'disponibilidad': round(
                 ((resultado['lineas'] - resultado['sum_pend']) * 100 / resultado['lineas'] if resultado['lineas'] > 0 else 0.00), 2)
             })
        resultado.update(
            {'por_ciento_ri': round(
                (resultado['ri'] * cant_dias_mes * 100 / (resultado['lineas'] * dias_ac_ri) if resultado['lineas'] > 0 else 0.00), 2)
             })
        return resultado
