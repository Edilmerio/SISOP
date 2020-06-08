from datetime import datetime, date
import calendar

from django.shortcuts import render
from django.views.generic import TemplateView
from django.forms import modelformset_factory
from django.http import HttpResponse
from django.db import transaction
from django.http import Http404
from django.contrib.auth.mixins import LoginRequiredMixin

from ..forms import LineasServicioForms
from ..models import LineasServicios
from general.models import DivisionTerritorial
from ..utils import do_formset_lineas_servicio

class LineasServicio(LoginRequiredMixin, TemplateView):
    template_name = 'parte_diario/LineasServicio.html'

    def dispatch(self, request, *args, **kwargs):
        # solo se accede si es una llamada ajax.
        if not request.is_ajax():
            raise Http404('Está página no existe..')
        if request.user.is_anonymous:
            resp = HttpResponse('/sisop')
            resp.status_code = 209
            return resp
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if not request.user.has_perm('parte_diario.estadistico'):
            return HttpResponse('error/Error/El usuario no tiene suficientes privilegios...')
        try:
            div_user = DivisionTerritorial.objects.get(identificativo=request.user.unidad_org.strip())
        except DivisionTerritorial.DoesNotExist:
            div_user = None

        hoy = datetime.now().date()
        first_day_month = date(year=hoy.year, month=hoy.month, day=1)
        last_day_month = date(year=hoy.year, month=hoy.month, day=calendar.monthrange(year=hoy.year, month=hoy.month)[1])

        lineas_servicio_formset = do_formset_lineas_servicio(div_user, first_day_month)
        current_mont = first_day_month.strftime('%m/%Y')
        return render(request, self.template_name, {'lineas_servicio_formset': lineas_servicio_formset,
                                                    'current_mont': current_mont,
                                                    'last_day_month': last_day_month.strftime('%Y-%m-%d')})

    def post(self, request):
        if not request.user.has_perm('parte_diario.estadistico'):
            return HttpResponse('error/Error/El usuario no tiene suficientes privilegios...')
        try:
            div_user = DivisionTerritorial.objects.get(identificativo=request.user.unidad_org.strip())
        except DivisionTerritorial.DoesNotExist:
            div_user = None
        LineasServicioFormSet = modelformset_factory(LineasServicios, form=LineasServicioForms, extra=0)
        queryset = LineasServicios.objects.filter(centro_asociado__centro_principal__division_territorial=div_user)
        lineas_servicio_formset = LineasServicioFormSet(request.POST, queryset=queryset)
        try:
            if not lineas_servicio_formset.is_valid():
                raise ValueError('error en los datos de las lineas')
            if not lineas_servicio_formset.has_changed():
                return HttpResponse('info/INFO/ No se produjeron cambios...')
            with transaction.atomic():
                for form in lineas_servicio_formset:
                    if form.has_changed():
                        form.save()
        except ValueError:
            return render(request, self.template_name, {'lineas_servicio_formset': lineas_servicio_formset,
                                                        'notify_1': 'error/ERROR/Corrija los errores...'})
        return HttpResponse('success/ACEPTADO/Los cambios se guardaron correctamente...')


class GetFormLineasServicio(LoginRequiredMixin, TemplateView):
    template_name = 'parte_diario/FormLineasServicio.html'

    def dispatch(self, request, *args, **kwargs):
        # solo se accede si es una llamada ajax.
        if not request.is_ajax():
            raise Http404('Está página no existe..')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if not request.user.has_perm('parte_diario.estadistico'):
            return HttpResponse('error/Error/El usuario no tiene suficientes privilegios...')
        try:
            div_user = DivisionTerritorial.objects.get(identificativo=request.user.unidad_org.strip())
        except DivisionTerritorial.DoesNotExist:
            div_user = None
        string_date_fecha = '1/{}'.format(request.GET.get('fecha'))
        first_day_month = datetime.strptime(string_date_fecha, '%d/%m/%Y').date()

        lineas_servicio_formset = do_formset_lineas_servicio(div_user, first_day_month)
        return render(request, self.template_name, {'lineas_servicio_formset': lineas_servicio_formset})