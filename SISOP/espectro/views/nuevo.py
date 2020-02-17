from datetime import timedelta

from django.shortcuts import render, redirect, reverse
from django.views.generic import TemplateView
from django.db import Error
from django.db import transaction
from django.forms import modelformset_factory
from django.http import HttpResponse, Http404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import logout

from .. import utiles
from ..models import TipoSolicitud, Radio, Solicitud, Sistema, Licencia, Bitacora
from ..forms import SolicitudForm, LicenciaForm, SistemaForm, RadioForm, EquipoForm
from ..exceptions_espectro import DatosNoValidos
from auth_sisop.views.auth import logout_view
from general.models import Municipio, DivisionTerritorial
from ..tasks import nuevo_sistema, nueva_solicitud, nueva_licencia


class NuevoSistema(LoginRequiredMixin, TemplateView):

    template_name = 'espectro/NuevoSistema.html'

    def get(self, request, *args, **kwargs):
        notify = request.GET.get('notify', None)
        if not request.user.has_perm('espectro.permisionario'):
            return logout_view(request, next=request.path)
        sistema_form = SistemaForm()
        RadioFormSet = modelformset_factory(Radio, form=RadioForm, extra=2, can_delete=True)
        radio_formset = RadioFormSet(queryset=Radio.objects.none())
        for radio_form in radio_formset:
            try:
                div_user = DivisionTerritorial.objects.get(identificativo=request.user.unidad_org.strip())
            except DivisionTerritorial.DoesNotExist:
                div_user = None
            municipios = Municipio.objects.filter(centroasociado__centro_principal__division_territorial=div_user).order_by('nombre')
            radio_form.fields['municipio'].queryset = municipios
        tipo_sistema = EquipoForm()
        solicitud_form = SolicitudForm()
        licencia_form = LicenciaForm()

        return render(request, self.template_name, {'sistema_form': sistema_form, 'radio_formset': radio_formset,
                                                    'tipo_sistema': tipo_sistema,
                                                    'solicitud_form': solicitud_form, 'licencia_form': licencia_form,
                                                    'attr_checked_cbx_solicitud_enviada': '',
                                                    'attr_checked_cbx_solicitud_autorizada': '',
                                                    'fecha_ultima_sol': '01/01/0001',
                                                    'fecha_ultima_lic': '0001-01-01',
                                                    'notify': notify})

    def post(self, request, *args, **kwargs):
        if not request.user.has_perm('espectro.permisionario'):
            return logout_view(request, next=request.path)
        RadioFormSet = modelformset_factory(Radio, form=RadioForm, extra=0, can_delete=True)
        radio_formset = RadioFormSet(request.POST, queryset=Radio.objects.none())
        for radio_form in radio_formset:
            try:
                div_user = DivisionTerritorial.objects.get(identificativo=request.user.unidad_org.strip())
            except DivisionTerritorial.DoesNotExist:
                div_user = None
            municipios = Municipio.objects.filter(centroasociado__centro_principal__division_territorial=div_user).order_by('nombre')
            radio_form.fields['municipio'].queryset = municipios
        tipo_sistema = EquipoForm(request.POST)
        attr_checked_cbx_solicitud_enviada = 'checked' if request.POST.get('ncbx_solicitud_enviada', '') == 'on' else ''
        attr_checked_cbx_solicitud_autorizada = 'checked' if request.POST.get('ncbx_solicitud_autorizada', '') == 'on' else ''
        sistema_form = SistemaForm(request.POST, cbx_solicitud_autorizada=attr_checked_cbx_solicitud_autorizada)
        solicitud_form = SolicitudForm(request.POST, request.FILES, cbx_solicitud_autorizada=attr_checked_cbx_solicitud_autorizada)
        licencia_form = LicenciaForm(request.POST, request.FILES)
        for f in radio_formset:
            f.empty_permitted = False
        try:
            if not (sistema_form.is_valid() and radio_formset.is_valid() and tipo_sistema.is_valid()):
                raise DatosNoValidos('Error de validación del sistema_form o del radio_formset')
            with transaction.atomic():
                sistema = sistema_form.save(commit=False)
                # debe ser la division territorial del permisionario cambiar cuando se haga.
                sistema.division_territorial = div_user
                sistema.save()
                radios = radio_formset.save(commit=False)
                for radio in radios:
                    radio.sistema = sistema
                    radio.save()
                if attr_checked_cbx_solicitud_enviada == 'checked':
                    if not solicitud_form.is_valid():
                        raise DatosNoValidos('Error de validación el solicitud_form')
                    solicitud = solicitud_form.save(commit=False)
                    solicitud.tipo_solicitud = TipoSolicitud.objects.get(tipo_solicitud='ALTA')
                    solicitud.sistema = sistema
                    solicitud.save()
                    if attr_checked_cbx_solicitud_autorizada == 'checked':
                        if not licencia_form.is_valid():
                            raise DatosNoValidos('Error de validación el licencia_form')
                        licencia = licencia_form.save(commit=False)
                        licencia.solicitud = solicitud
                        licencia.save()
        except DatosNoValidos:
            notify = 'error/ERROR/Corrija los errores....Pruebe otra vez.'
            return render(request, self.template_name, {'sistema_form': sistema_form, 'radio_formset': radio_formset,
                                                        'tipo_sistema': tipo_sistema,
                                                        'solicitud_form': solicitud_form, 'licencia_form': licencia_form,
                                                        'attr_checked_cbx_solicitud_enviada': attr_checked_cbx_solicitud_enviada,
                                                        'attr_checked_cbx_solicitud_autorizada': attr_checked_cbx_solicitud_autorizada,
                                                        'fecha_ultima_sol': '01/01/0001',
                                                        'fecha_ultima_lic': '0001-01-01',
                                                        'notify': notify
                                                        })
        except Error:
            return render(request, 'general/NotFound.html',
                          {'error': 'Ha existido un problema en la BD, pongáse en contacto con el admin del sitio'})

        else:
            # este se ejecuta si no hay ninguna exception dentro del try
            # Si el sistema esta en uso redireccionara aa la pagina Lista Sistemas con el argumento 1 para que cargue
            # los sistemas que estan en uso y sino el argumnto sera 0 pra que cargue los sistema previstos a instalar
            # ademas eviara email con notificaciones a los usuarios subcriptos
            nuevo_sistema.delay(sistema.id)
            ir_a_sistemas_en_uso_o_sistemas_previstos_a_istalar = 1 if sistema_form.cleaned_data['esta_en_uso'] else 0
            notify = 'success/ACEPTADO/El sistema se guardó correctamete...'
            if 'nbtn_guardar_y_listar' in request.POST:
                return redirect(reverse('espectro:listado sistemas',
                                        args={ir_a_sistemas_en_uso_o_sistemas_previstos_a_istalar}) + '?notify={}'.format(notify)
                                , permanent=True)
            return redirect(reverse('espectro:nuevo_sistema') + '?notify={}'.format(notify))


class NuevaSolicitud(TemplateView):
    template_name = 'espectro/NuevaSolicitud.html'

    def dispatch(self, request, *args, **kwargs):
        # solo se accede si es una llamada ajax.
        if not request.is_ajax():
            raise Http404('Está página no existe..')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            resp = HttpResponse('/auth/login')
            resp.status_code = 209
            return resp
        if not request.user.has_perm('espectro.permisionario'):
            logout(request)
            resp = HttpResponse('/auth/login')
            resp.status_code = 209
            return resp

        try:
            sistema = Sistema.objects.get(pk=args[0])
            if not request.user.unidad_org.strip() == sistema.division_territorial.identificativo:
                logout(request)
                resp = HttpResponse('/auth/login')
                resp.status_code = 209
                return resp
            solicitud_form = SolicitudForm(sistema=sistema)
            licencia_form = LicenciaForm()
            fecha_ultima_sol = (utiles.fecha_ultima_solicitud(sistema) + timedelta(days=1)).strftime('%d/%m/%Y')
            return render(request, self.template_name, {'solicitud_form': solicitud_form, 'licencia_form': licencia_form,
                                                        'sistema': sistema,
                                                        'attr_checked_cbx_solicitud_enviada': '',
                                                        'attr_checked_cbx_solicitud_autorizada': '',
                                                        'fecha_ultima_sol': fecha_ultima_sol,
                                                        'fecha_ultima_lic': '0001-01-01',
                                                        'notify_1': ''
                                                        })
        except Sistema.DoesNotExist:
            # renviar a la pagina del listado de los sistemas con una notificacion
            resp = HttpResponse('/espectro/listado_sistemas/1'
                                '?notify=error/ERROR/El sistema ya no existe, pudo ser eliminado por otro usuario...')
            resp.status_code = 209
            return resp

    def post(self, request, *args):
        if not request.user.is_authenticated:
            resp = HttpResponse('/auth/login')
            resp.status_code = 209
            return resp

        if not request.user.has_perm('espectro.permisionario'):
            logout(request)
            resp = HttpResponse('/auth/login')
            resp.status_code = 209
            return resp
        try:
            sistema = Sistema.objects.get(pk=args[0])
            if not request.user.unidad_org.strip() == sistema.division_territorial.identificativo:
                logout(request)
                resp = HttpResponse('/auth/login')
                resp.status_code = 209
                return resp
        except Sistema.DoesNotExist:
            # renviar a la pagina del listado de los sistemas con una notificacion
            resp = HttpResponse('/espectro/listado_sistemas/1'
                                '?notify=error/ERROR/El sistema ya no existe, pudo ser eliminado por otro usuario...')
            resp.status_code = 209
            return resp
        attr_checked_cbx_solicitud_enviada = 'checked' if request.POST.get('ncbx_solicitud_enviada', '') == 'on' else ''
        attr_checked_cbx_solicitud_autorizada = 'checked' if request.POST.get('ncbx_solicitud_autorizada', '') == 'on' else ''
        if attr_checked_cbx_solicitud_enviada != 'checked':
            # Se actualiza las lista de solicitudes y licencias
            table_solicitudes, solicitud_marcada = utiles.tabla_solicitudes_factory(sistema)
            table_licencias = utiles.tabla_licencias_factory(solicitud_marcada)
            notify_1 = 'info/Información/No se realizó ningún cambio...'
            return render(request, 'espectro/TablaSolicitudLicencia.html', {'table_solicitudes': table_solicitudes,
                                                                            'table_licencias': table_licencias,
                                                                            'sistema': sistema,
                                                                            'notify_1': notify_1
                                                                            })

        # si la solicitud es de tipo alta o baja y ya existe una solicitud de alta o baja para este sistema, solo se actualizan
        # las tablas de solicitudes y de licencias.
        list_tipo_soli_crtiticas = ['ALTA', 'BAJA']
        tipo_solicitud_resquest = TipoSolicitud.objects.get(pk=request.POST.get('tipo_solicitud', -1)).tipo_solicitud
        if tipo_solicitud_resquest in list_tipo_soli_crtiticas:
            if Solicitud.objects.filter(sistema=sistema, tipo_solicitud__tipo_solicitud=tipo_solicitud_resquest).exists():
                table_solicitudes, solicitud_marcada = utiles.tabla_solicitudes_factory(sistema)
                table_licencias = utiles.tabla_licencias_factory(solicitud_marcada)
                notify_1 = 'error/ERROR/Ya existe una solictud de {} para este sistema...'.format(tipo_solicitud_resquest)
                return render(request, 'espectro/TablaSolicitudLicencia.html', {'table_solicitudes': table_solicitudes,
                                                                                'table_licencias': table_licencias,
                                                                                'sistema': sistema,
                                                                                'notify_1': notify_1
                                                                                })
        dict_req = request.POST.copy()
        if attr_checked_cbx_solicitud_autorizada != 'checked':
            dict_req['fecha_autorizacion'] = ''
        solicitud_form = SolicitudForm(dict_req, request.FILES,
                                       cbx_solicitud_autorizada=attr_checked_cbx_solicitud_autorizada, sistema=sistema)
        licencia_form = LicenciaForm(request.POST, request.FILES)
        try:
            if not solicitud_form.is_valid():
                raise DatosNoValidos('Error de validación de la solicitud')
            solicitud_baja_autorizada = False
            with transaction.atomic():
                solicitud = solicitud_form.save(commit=False)
                solicitud.sistema = sistema
                solicitud.save()
                if solicitud_form.cleaned_data['tipo_solicitud'].tipo_solicitud == 'BAJA' \
                        and attr_checked_cbx_solicitud_autorizada == 'checked':
                    solicitud_baja_autorizada = True
                else:
                    if attr_checked_cbx_solicitud_autorizada == 'checked':
                        if not licencia_form.is_valid():
                            raise DatosNoValidos('Error de validación de la licencia')
                        licencia = licencia_form.save(commit=False)
                        licencia.solicitud = solicitud
                        licencia.save()
                    # si el sistema se le hizo solicitd de baja entonces ya no esta en uso.
                    if solicitud_form.cleaned_data['tipo_solicitud'].tipo_solicitud == 'BAJA':
                        sistema.esta_en_uso = False
                        sistema.save()
        except DatosNoValidos:
            notify_1 = 'error/ERROR/Corrija los errores... Pruebe otra vez...'
            return render(request, self.template_name, {'solicitud_form': solicitud_form, 'licencia_form': licencia_form,
                                                        'sistema': sistema,
                                                        'attr_checked_cbx_solicitud_enviada': attr_checked_cbx_solicitud_enviada,
                                                        'attr_checked_cbx_solicitud_autorizada': attr_checked_cbx_solicitud_autorizada,
                                                        'fecha_ultima_sol': '01/01/0001',
                                                        'fecha_ultima_lic': '0001-01-01',
                                                        'notify_1': notify_1
                                                        })

        except Error:
            return render(request, 'general/NotFound.html',
                          {'error': 'Ha existido un problema en la BD, pongáse en contacto con el admin del sitio'})
        else:
            aux_dict = utiles.sistema_info_subcripcion(sistema, solicitud)
            if solicitud_baja_autorizada:
                bitacora = Bitacora(sistema=sistema.sistema,
                                    enlace=sistema.enlace,
                                    accion='Sistema eliminado',
                                    usuario=request.user.email,
                                    fecha=solicitud_form.cleaned_data['fecha_autorizacion'])
                try:
                    with transaction.atomic():
                        bitacora.save()
                        sistema.delete()
                        # enviar email a los subcriptores
                        nueva_solicitud.delay(info=aux_dict)
                except Error:
                    return render(request, 'general/NotFound.html',
                                  {'error': 'Ha existido un problema en la BD, pongáse en contacto con el admin del sitio'})

                # enviar a la pagina del listado de los sistemas y enviar notificacion
                resp = HttpResponse('/espectro/listado_sistemas/1'
                                    '?notify=success/ACEPTADO/El sistema se eliminó correctamente y se guardó en el historial...')
                resp.status_code = 209
                return resp
            # si no es una solicitud de baja autorizada
            # enviar email a los subcriptores
            nueva_solicitud.delay(info=aux_dict)
            table_solicitudes, solicitud_marcada = utiles.tabla_solicitudes_factory(sistema)
            table_licencias = utiles.tabla_licencias_factory(solicitud_marcada)
            notify_1 = 'success/ACEPTADO/La solicitud se guardó correctamete...'
            return render(request, 'espectro/TablaSolicitudLicencia.html', {'table_solicitudes': table_solicitudes,
                                                                            'table_licencias': table_licencias,
                                                                            'sistema': sistema,
                                                                            'notify_1': notify_1
                                                                            })


class NuevaLicencia(TemplateView):
    template_name = 'espectro/NuevaLicencia.html'

    def dispatch(self, request, *args, **kwargs):
        # solo se accede si es una llamada ajax.
        if not request.is_ajax():
            raise Http404('Está página no existe..')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            resp = HttpResponse('/auth/login')
            resp.status_code = 209
            return resp

        if not request.user.has_perm('espectro.permisionario'):
            logout(request)
            resp = HttpResponse('/auth/login')
            resp.status_code = 209
            return resp
        try:
            solicitud = Solicitud.objects.get(pk=args[0])
            if not request.user.unidad_org.strip() == solicitud.sistema.division_territorial.identificativo:
                logout(request)
                resp = HttpResponse('/auth/login')
                resp.status_code = 209
                return resp
        except Solicitud.DoesNotExist:
            # renviar a la pagina del listado de los sistemas con una notificacion
            resp = HttpResponse('/espectro/listado_sistemas/1'
                                '?notify=error/ERROR/La solicitud ya no existe, pudo ser eliminado por otro usuario...')
            resp.status_code = 209
            return resp

        licencia_form = LicenciaForm()
        fecha_ultima_licencia = solicitud.fecha_autorizacion if solicitud.fecha_autorizacion else solicitud.fecha_envio
        licencias = Licencia.objects.filter(solicitud=solicitud)
        if licencias.exists():
            fecha_ultima_licencia = utiles.fecha_ultima_licencia(solicitud)
        fecha_ultima_licencia = (fecha_ultima_licencia + timedelta(days=1)).strftime('%Y-%m-%d')
        return render(request, self.template_name, {'licencia_form': licencia_form,
                                                    'solicitud_id': solicitud.id,
                                                    'fecha_ultima_lic': fecha_ultima_licencia,
                                                    'notify_1': ''
                                                    })

    def post(self, request, *args):

        if not request.user.is_authenticated:
            resp = HttpResponse('/auth/login')
            resp.status_code = 209
            return resp

        if not request.user.has_perm('espectro.permisionario'):
            logout(request)
            resp = HttpResponse('/auth/login')
            resp.status_code = 209
            return resp
        try:
            solicitud = Solicitud.objects.get(pk=args[0])
            if not request.user.unidad_org.strip() == solicitud.sistema.division_territorial.identificativo:
                logout(request)
                resp = HttpResponse('/auth/login')
                resp.status_code = 209
                return resp
        except Solicitud.DoesNotExist:
            # renviar a la pagina del listado de los sistemas con una notificacion
            resp = HttpResponse('/espectro/listado_sistemas/1'
                                '?notify=error/ERROR/La solicitud ya no existe, pudo ser eliminado por otro usuario...')
            resp.status_code = 209
            return resp
        licencia_form = LicenciaForm(request.POST, request.FILES, solicitud=solicitud)
        if licencia_form.is_valid():
            licencia = licencia_form.save(commit=False)
            licencia.solicitud = solicitud
            try:
                licencia.save()
                nueva_licencia.delay(licencia.pk)
            except Error:
                return HttpResponse('Error en la Base de datos')
            table_licencias = utiles.tabla_licencias_factory(solicitud)
            notify_1 = 'success/ACEPTADO/La licencia se guardó correctamete...'
            return render(request, 'espectro/TablaLicencias.html', {'table_licencias': table_licencias,
                                                                    'sistema': solicitud.sistema,
                                                                    'notify_1': notify_1
                                                                    })
        fecha_ultima_licencia = solicitud.fecha_autorizacion if solicitud.fecha_autorizacion else solicitud.fecha_envio
        licencias = Licencia.objects.filter(solicitud=solicitud)
        if licencias.exists():
            fecha_ultima_licencia = utiles.fecha_ultima_licencia(solicitud)
        fecha_ultima_licencia = (fecha_ultima_licencia + timedelta(days=1)).strftime('%Y-%m-%d')
        return render(request, self.template_name, {'licencia_form': licencia_form,
                                                    'solicitud_id': solicitud.id,
                                                    'fecha_ultima_lic': fecha_ultima_licencia,
                                                    'attr_checked_cbx_solicitud_autorizada': 'checked',
                                                    'attr_checked_cbx_solicitud_enviada': 'checked',
                                                    'notify_1': 'error/ERROR/Corrija los errores... Pruebe otra vez...'
                                                    })



