from datetime import datetime, timedelta, date

from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin

from ..utils import DoTableIndicadores, fecha_ini_fin_disponible_calculo
from general.models import DivisionTerritorial

class Indicadores(LoginRequiredMixin, TemplateView):
    template_name = 'parte_diario/Indicadores.html'

    def get(self, request, *args, **kwargs):
        try:
            div_user = DivisionTerritorial.objects.get(identificativo=request.user.unidad_org.strip())
        except DivisionTerritorial.DoesNotExist:
            return HttpResponse('<h1>Usuario sin DT, no se muestran Datos</h1>')
        fecha_inicio_disponible, fecha_fin_disponible = fecha_ini_fin_disponible_calculo(div_user)

        ayer = (datetime.now()-timedelta(days=1)).date()
        fecha_inicio = ayer if fecha_fin_disponible >= ayer else fecha_fin_disponible
        fecha_fin = fecha_inicio
        d = DoTableIndicadores(fecha_inicio, fecha_fin, div_user)

        table_indicadores_cta_tb, table_indicadores_cta_tx = d.table_nivel_cta()
        table_indicadores_ctp_tb, table_indicadores_ctp_tx = d.table_nivel_ctp()
        titles = d.do_title_tables()

        return render(request, self.template_name, {
            'fecha_inicio': fecha_inicio.strftime('%d/%m/%Y'),
            'table_indicadores_cta_tb': table_indicadores_cta_tb,
            'title_table_indicadores_cta_tb': titles[0],
            'table_indicadores_ctp_tb': table_indicadores_ctp_tb,
            'title_table_indicadores_ctp_tb': titles[1],
            'table_indicadores_cta_tx': table_indicadores_cta_tx,
            'title_table_indicadores_cta_tx': titles[2],
            'table_indicadores_ctp_tx': table_indicadores_ctp_tx,
            'title_table_indicadores_ctp_tx': titles[3],
            'fecha_inicio_disponible': fecha_inicio_disponible.strftime('%Y-%m-%d'),
            'fecha_fin_disponible': fecha_fin_disponible.strftime('%Y-%m-%d')

        })
