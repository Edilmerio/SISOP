from django.shortcuts import render, redirect, reverse
from django.views.generic import TemplateView
from django.forms import modelformset_factory
from django.db import transaction, Error
from django.http import Http404, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import logout

from espectro.exceptions_espectro import DatosNoValidos
from espectro.models import Solicitud, Sistema, Radio, Licencia, Bitacora
from espectro.forms import SistemaForm, RadioForm, SolicitudForm, LicenciaForm, EquipoForm
from espectro import utiles
from auth_sisop.views.auth import logout_view
from general.models import Municipio
from espectro.tasks import nueva_solicitud


class EditarSistema(LoginRequiredMixin, TemplateView):
    template_name = 'espectro/EditarSistema.html'

    def get(self, request, *args, **kwargs):
        try:
            sistema = Sistema.objects.get(id=args[0])
            # si el usuario no pertece a la misma DT que el sistema o no es visualizador nacional no podra ver el detalle del sistema
            if not (request.user.unidad_org.strip() == sistema.division_territorial.identificativo
                    or request.user.has_perm('espectro.visualizador_nacional')):
                return logout_view(request, next=request.path)
        except Sistema.DoesNotExist:
            url = reverse('espectro:listado sistemas', args={1})
            notify = '?notify=error/ERROR/El sistema ya no existe, pudo ser eliminado por otro usuario...'
            return redirect(url+notify, permanent=True)
        sistema_form = SistemaForm(instance=sistema)
        RadioFormSet = modelformset_factory(Radio, form=RadioForm, extra=0, can_delete=True)
        radio_formset = RadioFormSet(queryset=Radio.objects.filter(sistema=sistema))

        if request.user.unidad_org.strip() == sistema.division_territorial.identificativo:
            municipios = Municipio.objects.filter(centroasociado__centro_principal__division_territorial=sistema.division_territorial)
            for radio_form in radio_formset:
                radio_form.fields['municipio'].queryset = municipios
        else:
            for radio_form in radio_formset:
                municipios = Municipio.objects.filter(nombre=radio_form.instance.municipio.nombre)
                radio_form.fields['municipio'].queryset = municipios
        tipo_sistema = EquipoForm(sistema=sistema)

        # Tablas de Solicitudes y Licencias ...........................................................
        table_solicitudes, solicitud_marcada = utiles.tabla_solicitudes_factory(sistema)
        table_licencias = utiles.tabla_licencias_factory(solicitud_marcada)
        return render(request, self.template_name, {'sistema_form': sistema_form, 'radio_formset': radio_formset,
                                                    'tipo_sistema': tipo_sistema,
                                                    'table_solicitudes': table_solicitudes,
                                                    'table_licencias': table_licencias,
                                                    'sistema': sistema,
                                                    'notify': ''})

    def post(self, request, *args):
        if not request.user.has_perm('espectro.permisionario'):
            return logout_view(request, next=request.path)
        try:
            sistema = Sistema.objects.get(id=args[0])
            if not (request.user.unidad_org.strip() == sistema.division_territorial.identificativo):
                return logout_view(request, next=request.path)
        except Sistema.DoesNotExist:
            url = reverse('espectro:listado sistemas', args={1})
            notify = '?notify=error/ERROR/El sistema ya no existe, pudo ser eliminado por otro usuario...'
            return redirect(url + notify, permanent=True)

        # cuando se usa checkbox y este no esta marcado o esta desabilitado el valor no esta en request.POST
        if 'esta_en_uso' not in request.POST and sistema.esta_en_uso:
            datos = request.POST.copy()
            datos['esta_en_uso'] = 'on'
        else:
            datos = request.POST.copy()

        sistema_form = SistemaForm(datos, instance=sistema)
        RadioFormSet = modelformset_factory(Radio, form=RadioForm, can_delete=True)
        radio_formset = RadioFormSet(self.request.POST,
                                     queryset=Radio.objects.filter(sistema=sistema))

        if request.user.unidad_org.strip() == sistema.division_territorial.identificativo:
            municipios = Municipio.objects.filter(centroasociado__centro_principal__division_territorial=sistema.division_territorial)
            for radio_form in radio_formset:
                radio_form.fields['municipio'].queryset = municipios
        else:
            for radio_form in radio_formset:
                municipios = Municipio.objects.filter(nombre=radio_form.instance.municipio.nombre)
                radio_form.fields['municipio'].queryset = municipios

        if sistema_form.is_valid() and radio_formset.is_valid():
            for f in radio_formset:
                f.empty_permitted = False
            try:
                with transaction.atomic():
                    sistema = sistema_form.save()
                    for extra_form in radio_formset.extra_forms:
                        extra_form.instance.sistema = sistema
                    sistema.save()
                    radio_formset.save()
            except Error:
                return render(self.request, 'general/NotFound.html',
                              {'error': 'Ha existido un problema en la BD, pongáse en contacto con el admin del sitio'})

            sistema_form = SistemaForm(instance=sistema)
            RadioFormSet = modelformset_factory(Radio, form=RadioForm, can_delete=True, extra=0)
            radio_formset = RadioFormSet(queryset=Radio.objects.filter(sistema=sistema))
            if request.user.unidad_org.strip() == sistema.division_territorial.identificativo:
                municipios = Municipio.objects.filter(centroasociado__centro_principal__division_territorial=sistema.division_territorial)
                for radio_form in radio_formset:
                    radio_form.fields['municipio'].queryset = municipios
            else:
                for radio_form in radio_formset:
                    municipios = Municipio.objects.filter(nombre=radio_form.instance.municipio.nombre)
                    radio_form.fields['municipio'].queryset = municipios
            notify = 'success/ACEPTADO/El sistema se actualizó correctamente...'
        else:
            notify = 'error/ERROR/Corrija los errores... Pruebe otra vez.'

        try:
            solicitud_marcada = Solicitud.objects.get(id=int(request.POST['id_row_marcada']))
        except Solicitud.DoesNotExist:
            solicitud_marcada = None
        tb_sol_page = int(request.POST['tb_sol_page'])
        tb_lic_page = int(request.POST['tb_lic_page'])
        table_solicitudes, solicitud_marcada = utiles.tabla_solicitudes_factory(sistema, page=tb_sol_page,
                                                                                solicitud_maracada=solicitud_marcada)
        table_licencias = utiles.tabla_licencias_factory(solicitud_marcada, page=tb_lic_page)
        tipo_sistema = EquipoForm(sistema=sistema)
        return render(request, self.template_name, {'sistema_form': sistema_form, 'radio_formset': radio_formset,
                                                    'tipo_sistema': tipo_sistema,
                                                    'id_sistema': args[0], 'table_solicitudes': table_solicitudes,
                                                    'table_licencias': table_licencias,
                                                    'sistema': sistema,
                                                    'notify': notify})


class EditarSolicitud(LoginRequiredMixin, TemplateView):

    template_name = 'espectro/EditarSolicitud.html'

    def dispatch(self, request, *args, **kwargs):
        # solo se accede si es una llamada ajax.
        if not request.is_ajax():
            raise Http404('Está página no existe..')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        try:
            solicitud = Solicitud.objects.get(pk=args[0])
        except Solicitud.DoesNotExist:
            resp = HttpResponse('/espectro/listado_sistemas/1'
                                '?notify=error/ERROR/La Solicitud ya no existe, pudo ser eliminado por otro usuario...')
            resp.status_code = 209
            return resp
        solicitud_form = SolicitudForm(instance=solicitud)
        licencias = Licencia.objects.filter(solicitud=solicitud)
        attr_checked_cbx_solicitud_autorizada = ''
        attr_disabled_cbx_solicitud_autorizada = ''
        attr_checked_cbx_solicitud_enviada = 'checked'
        fecha_ultima_licencia = (solicitud.fecha_autorizacion if solicitud.fecha_autorizacion
                                 else solicitud.fecha_envio).strftime('%Y-%m-%d')
        if licencias.exists():
            ultima_licencia = licencias.order_by('-id')[0]
            attr_checked_cbx_solicitud_autorizada = 'checked'
            attr_disabled_cbx_solicitud_autorizada = 'disabled'
            licencia_form = LicenciaForm(instance=ultima_licencia)
            fecha_ultima_licencia = utiles.fecha_ultima_licencia(solicitud).strftime('%Y-%m-%d')
        else:
            licencia_form = LicenciaForm()
        fecha_ultima_sol = solicitud.fecha_envio.strftime('%d/%m/%Y')
        return render(request, self.template_name, {'solicitud_form': solicitud_form, 'licencia_form': licencia_form,
                                                    'solicitud_id': solicitud.id,
                                                    'attr_checked_cbx_solicitud_enviada': attr_checked_cbx_solicitud_enviada,
                                                    'attr_checked_cbx_solicitud_autorizada': attr_checked_cbx_solicitud_autorizada,
                                                    'attr_disabled_cbx_solicitud_autorizada': attr_disabled_cbx_solicitud_autorizada,
                                                    'attr_disabled_cbx_solicitud_enviada': 'disabled',
                                                    'fecha_ultima_sol': fecha_ultima_sol,
                                                    'fecha_ultima_lic': fecha_ultima_licencia,
                                                    'notify_1': '',
                                                    'sistema': solicitud.sistema
                                                    })

    def post(self, request, *args):
        if not request.user.has_perm('espectro.permisionario'):
            logout(request)
            resp = HttpResponse('/auth/login')
            resp.status_code = 209
            return resp
        try:
            solicitud = Solicitud.objects.get(pk=args[0])
            sistema = solicitud.sistema
            if not request.user.unidad_org.strip() == sistema.division_territorial.identificativo:
                logout(request)
                resp = HttpResponse('/auth/login')
                resp.status_code = 209
                return resp
        except Solicitud.DoesNotExist:
            resp = HttpResponse('/espectro/listado_sistemas/1'
                                '?notify=error/ERROR/La Solicitud ya no existe, pudo ser eliminado por otro usuario...')
            resp.status_code = 209
            return resp
        try:
            licencia_id = int(self.request.POST.get('id_licencia'))
        except ValueError:
            licencia_id = None
        licencia = None
        if licencia_id:
            try:
                licencia = Licencia.objects.get(pk=licencia_id)
            except Licencia.DoesNotExist:
                resp = HttpResponse('/espectro/listado_sistemas/1'
                                    '?notify=error/ERROR/La Licencia ya no existe, pudo ser eliminado por otro usuario...')
                resp.status_code = 209
                return resp
        licencias = Licencia.objects.filter(solicitud=solicitud)
        ultima_licencia = None
        fecha_ultima_licencia = (solicitud.fecha_autorizacion if solicitud.fecha_autorizacion
                                 else solicitud.fecha_envio).strftime('%Y-%m-%d')
        attr_disabled_cbx_solicitud_autorizada = ''
        if licencias:
            ultima_licencia = Licencia.objects.filter(solicitud=solicitud).order_by('-id')[0]
            fecha_ultima_licencia = utiles.fecha_ultima_licencia(solicitud).strftime('%Y-%m-%d')
            attr_disabled_cbx_solicitud_autorizada = 'disabled'
        attr_checked_cbx_solicitud_enviada = 'checked' if request.POST.get('ncbx_solicitud_enviada', '') == 'on' else ''
        attr_checked_cbx_solicitud_autorizada = 'checked' if request.POST.get('ncbx_solicitud_autorizada', '') == 'on' else ''
        dict_req = request.POST.copy()
        if attr_checked_cbx_solicitud_autorizada != 'checked':
            dict_req['fecha_autorizacion'] = ''
        solicitud_form = SolicitudForm(dict_req, request.FILES, instance=solicitud,
                                       cbx_solicitud_autorizada=attr_checked_cbx_solicitud_autorizada, sistema=sistema)
        licencia_form = LicenciaForm(request.POST, request.FILES, instance=licencia)
        table_solicitudes, solicitud_marcada = utiles.tabla_solicitudes_factory(sistema)
        table_licencias = utiles.tabla_licencias_factory(solicitud_marcada)
        notify_1 = 'info/Información/No se realizó ningún cambio...'
        try:
            is_nueva_licencia = False
            with transaction.atomic():
                if attr_checked_cbx_solicitud_autorizada == 'checked' and licencia_form.has_changed():
                    if not licencia_form.is_valid():
                        raise DatosNoValidos('Error de validación de la licencia')
                    if licencia != ultima_licencia:
                        notify_1 = 'error/ERROR/La solicitud o licencia fue actualizada por otro usuario...'
                        return render(request, 'espectro/TablaSolicitudLicencia.html', {'table_solicitudes': table_solicitudes,
                                                                                        'table_licencias': table_licencias,
                                                                                        'sistema': sistema,
                                                                                        'notify_1': notify_1
                                                                                        })
                    if not licencia:
                        # es una nueva licencia, no una actualizacion
                        is_nueva_licencia = True
                    licencia_act = licencia_form.save(commit=False)
                    licencia_act.solicitud = solicitud
                    licencia_act.save()
                    notify_1 = 'success/ACEPTADO/Los datos se guardaron correctamete...'
                solicitud_baja_autorizada = False
                if not solicitud_form.is_valid():
                    raise DatosNoValidos('Error de validación de la solicitud')
                if solicitud_form.has_changed():
                    if solicitud_form.cleaned_data['tipo_solicitud'].tipo_solicitud == 'BAJA' \
                            and attr_checked_cbx_solicitud_autorizada == 'checked':
                        solicitud_baja_autorizada = True
                    solicitud.fecha_autorizacion = solicitud_form.cleaned_data['fecha_autorizacion']
                    solicitud.archivo_solicitud = solicitud_form.cleaned_data['archivo_solicitud']
                    solicitud.save()
                    notify_1 = 'success/ACEPTADO/Los datos se guardaron correctamete...'

        except DatosNoValidos:
            fecha_ultima_sol = solicitud.fecha_envio.strftime('%d/%m/%Y')
            notify_1 = 'error/ERROR/Corrija los errores... Pruebe otra vez...'
            licencia_form.instance.id = None
            return render(request, self.template_name, {'solicitud_form': solicitud_form, 'licencia_form': licencia_form,
                                                        'solicitud_id': solicitud.id,
                                                        'attr_checked_cbx_solicitud_enviada': attr_checked_cbx_solicitud_enviada,
                                                        'attr_checked_cbx_solicitud_autorizada': attr_checked_cbx_solicitud_autorizada,
                                                        'attr_disabled_cbx_solicitud_autorizada': attr_disabled_cbx_solicitud_autorizada,
                                                        'attr_disabled_cbx_solicitud_enviada': 'disabled',
                                                        'fecha_ultima_sol': fecha_ultima_sol,
                                                        'fecha_ultima_lic': fecha_ultima_licencia,
                                                        'notify_1': notify_1
                                                        })
        except Error:
            return render(request, 'general/NotFound.html',
                          {'error': 'Ha existido un problema en la BD, pongáse en contacto con el admin del sitio'})
        else:
            if solicitud_baja_autorizada:
                aux_dict = utiles.sistema_info_subcripcion(sistema, solicitud)
                bitacora = Bitacora(sistema=sistema.sistema,
                                    enlace=sistema.enlace,
                                    accion='Sistema eliminado',
                                    usuario=request.user.email,
                                    fecha=solicitud_form.cleaned_data['fecha_autorizacion'])
                try:
                    with transaction.atomic():
                        bitacora.save()
                        sistema.delete()
                    nueva_solicitud.delay(info=aux_dict, asunto='Autorización de baja', titulo='Autorización de baja')
                    resp = HttpResponse('/espectro/listado_sistemas/1'
                                        '?notify=success/ACEPTADO/El sistema se eliminó correctamente y se guardó en el historial...')
                    resp.status_code = 209
                    return resp
                except Error:
                    return render(request, 'general/NotFound.html',
                                  {'error': 'Ha existido un problema en la BD, pongáse en contacto con el admin del sitio'})
            if is_nueva_licencia:
                aux_dict = utiles.sistema_info_subcripcion(sistema, solicitud)
                nueva_solicitud.delay(info=aux_dict, asunto='Autorización de solicitud', titulo='Autorización de solicitud')
            table_solicitudes, solicitud_marcada = utiles.tabla_solicitudes_factory(sistema)
            table_licencias = utiles.tabla_licencias_factory(solicitud_marcada)
            return render(request, 'espectro/TablaSolicitudLicencia.html', {'table_solicitudes': table_solicitudes,
                                                                            'table_licencias': table_licencias,
                                                                            'sistema': sistema,
                                                                            'notify_1': notify_1
                                                                            })


class Licencias(TemplateView):
    def get(self, request, *args, **kwargs):
        return 'ddd'
