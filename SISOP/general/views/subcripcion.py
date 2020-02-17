from django.views.generic import TemplateView
from ..models import Informacion, GInformacion, DivisionTerritorial, CentroAsociado,\
    Subcripcion
from django.shortcuts import render
from django.http import Http404, HttpResponse
from django.db import transaction
from django.db import Error

# from .. import models
from .. import utils


class Subcripcion(TemplateView):
    template_name = 'general/Subcripcion.html'

    def __init__(self):
        self.param_ginfo = {'0': 'espectro', '1': 'presupuesto'}
        self.perms_nacional = ['espectro.visualizador_nacional']
        super().__init__()

    def dispatch(self, request, *args, **kwargs):
        # solo se accede si es una llamada ajax.
        if not request.is_ajax():
            raise Http404('Está página no existe..')
        if not request.user.is_authenticated:
            resp = HttpResponse('/auth/login')
            resp.status_code = 209
            return resp
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if args[0] not in self.param_ginfo:
            raise Http404('Está página no existe..')
        ginfo = GInformacion.objects.get(ginfo=self.param_ginfo[args[0]])
        info_ginfo = Informacion.objects.filter(ginfo=ginfo)

        if request.user.has_perms(self.perms_nacional):
            place_info = DivisionTerritorial.objects.all()
            place_info_user = DivisionTerritorial.objects.filter(centroprincipal__centroasociado__subcripcion__user=request.user,
                                                                 centroprincipal__centroasociado__subcripcion__ginfo=ginfo).distinct()

        else:
            try:
                div_user = DivisionTerritorial.objects.get(identificativo=request.user.unidad_org.strip())
            except DivisionTerritorial.DoesNotExist:
                div_user = None
            place_info = CentroAsociado.objects.filter(centro_principal__division_territorial=div_user)
            place_info_user = CentroAsociado.objects.filter(subcripcion__user=request.user,
                                                            subcripcion__ginfo=ginfo)
        place_info_list = place_info.values_list('nombre', flat=True)
        place_info_user_list = place_info_user.values_list('nombre', flat=True)

        dict_info_show = utils.dict_elemen_seleced(place_info_list, place_info_user_list)
        return render(request, self.template_name,
                      {'dict_info_show': dict_info_show,
                       'info_ginfo': info_ginfo.values_list('informacion', flat=True),
                       'notify': ''})

    def post(self, request, *args):
        selected_info_list = request.POST.getlist('select_place_info')

        if args[0] not in self.param_ginfo:
            raise Http404('Está página no existe..')
        ginfo = GInformacion.objects.get(ginfo=self.param_ginfo[args[0]])

        # centros_asociados = []
        if request.user.has_perms(self.perms_nacional):
            # las lista de las informaiciones son divisiones territoriales.
            centros_asociados = CentroAsociado.objects\
                .filter(centro_principal__division_territorial__nombre__in=selected_info_list)
        else:
            # la lista de las informaciones son centros asociados.
            centros_asociados = CentroAsociado.objects.filter(nombre__in=selected_info_list)
        notify_1 = 'success/ACEPTADO/Su subcrioción se guardó correctamente...'
        try:
            with transaction.atomic():
                # remove all items in models Subcripcion
                Subcripcion.objects.filter(user=request.user, ginfo=ginfo).delete()
                for cta in centros_asociados:
                    nueva_subcripcion = Subcripcion(user=request.user, ginfo=ginfo, centro_asociado=cta)
                    nueva_subcripcion.save()
        except Error:
            notify_1 = 'error/ERROR/Ha existido un problema en la BD, pongáse en contacto con el admin del sitio'

        return render(request, 'general/Notificacion.html', {'notify_1': notify_1})
