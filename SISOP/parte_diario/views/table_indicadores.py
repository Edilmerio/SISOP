from datetime import datetime

from django.shortcuts import render, redirect, reverse
from django.views.generic import TemplateView
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin

from ..utils import DoTableIndicadores, fecha_ini_fin_disponible_calculo
from general.models import DivisionTerritorial

class TableIndicadores(LoginRequiredMixin, TemplateView):
    template_name = 'parte_diario/TablaIndicadores.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_anonymous:
            resp = HttpResponse('/sisop')
            resp.status_code = 209
            return resp
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        try:
            div_user = DivisionTerritorial.objects.get(identificativo=request.user.unidad_org.strip())
        except DivisionTerritorial.DoesNotExist:
            return HttpResponse('<h1>Usuario sin DT, no se muestran Datos</h1>')

        fecha_inicio_disponible, fecha_fin_disponible = fecha_ini_fin_disponible_calculo(div_user)
        try:
            fecha_inicio = datetime.strptime(request.GET.get('fecha_inicio', None), '%d/%m/%Y').date()
            fecha_fin = datetime.strptime(request.GET.get('fecha_fin', None), '%d/%m/%Y').date()
            if fecha_fin < fecha_inicio:
                raise ValueError
            if fecha_inicio < fecha_inicio_disponible or fecha_fin > fecha_fin_disponible:
                raise ValueError
        except (TypeError, ValueError) as e:
            return HttpResponse('<h1>Incongruencias con las fehcas de inicio y/o fin</h1>')

        d = DoTableIndicadores(fecha_inicio, fecha_fin, div_user)
        table_indicadores_cta_tb, table_indicadores_cta_tx = d.table_nivel_cta()
        table_indicadores_ctp_tb, table_indicadores_ctp_tx = d.table_nivel_ctp()
        titles = d.do_title_tables()
        export_format = request.GET.get('_export', None)
        if not export_format:
            return render(request, self.template_name, {
                'fecha_inicio': fecha_inicio.strftime('%d/%m/%Y'),
                'table_indicadores_cta_tb': table_indicadores_cta_tb,
                'title_table_indicadores_cta_tb': titles[0],
                'table_indicadores_ctp_tb': table_indicadores_ctp_tb,
                'title_table_indicadores_ctp_tb': titles[1],
                'table_indicadores_cta_tx': table_indicadores_cta_tx,
                'title_table_indicadores_cta_tx': titles[2],
                'table_indicadores_ctp_tx': table_indicadores_ctp_tx,
                'title_table_indicadores_ctp_tx': titles[3]
            })

        abs_path = d.export_tables_excel(table_indicadores_cta_tb, table_indicadores_ctp_tb,
                                         table_indicadores_cta_tx, table_indicadores_ctp_tx)
        return redirect(reverse('espectro:descargar_ficheros')+'?dir={}'.format(abs_path), permanent=False)
