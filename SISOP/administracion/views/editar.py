from django.views.generic import TemplateView
from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.db import transaction
from django.db import Error
from django.contrib.auth.models import Permission
from django.contrib.auth import logout

from auth_sisop.models import UserSisop


class EditarPermisos(TemplateView):
    template_name = 'administracion/EdiarPermisos.html'

    def __init__(self):
        self.apps_perms = [{'espectro': ['permisionario', 'visualizador_nacional']},
                           {'administracion': ['administrador']},
                           {'parte_diario': ['estadistico']}]

        super().__init__()

    def dispatch(self, request, *args, **kwargs):
        # solo se accede si es una llamada ajax.
        if not request.is_ajax():
            raise Http404('Está página no existe..')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if not request.user.has_perm('administracion.administrador'):
            logout(request)
            resp = HttpResponse('/auth/login')
            resp.status_code = 209
            return resp
        try:
            user = UserSisop.objects.get(pk=args[0])
        except UserSisop.DoesNotExist:
            resp = HttpResponse('/admin/listado_usuarios'
                                '?notify=error/ERROR/El usuario ya no existe...')
            resp.status_code = 209
            return resp
        user_all_permission = user.get_all_permissions()
        app_perm_acces = []
        for app_perms in self.apps_perms:
            app = list(app_perms.keys())[0]
            perms = list(app_perms.values())[0]
            aux = {app: {}}
            for perm in perms:
                if ('{}.{}'.format(app, perm)) in user_all_permission:
                    aux[app].update({perm: 'selected'})
                else:
                    aux[app].update({perm: ''})
            app_perm_acces.append(aux)

        return render(request, self.template_name, {'app_perm_acces': app_perm_acces,
                                                    'usuario': user})

    def post(self, request, *args, **kwargs):
        if not request.user.has_perm('administracion.administrador'):
            logout(request)
            resp = HttpResponse('/auth/login')
            resp.status_code = 209
            return resp
        try:
            user = UserSisop.objects.get(pk=args[0])
        except UserSisop.DoesNotExist:
            resp = HttpResponse('/admin/listado_usuarios'
                                '?notify=error/ERROR/El usuario ya no existe...')
            resp.status_code = 209
            return resp
        new_perms = []
        try:
            with transaction.atomic():
                user.user_permissions.clear()
                for app_perms in self.apps_perms:
                    app = list(app_perms.keys())[0]
                    perms = list(app_perms.values())[0]
                    if app not in request.POST:
                        continue
                    for perm in request.POST.getlist(app):
                        if perm not in perms:
                            continue
                        new_perms.append(Permission.objects.get(codename=perm, content_type__app_label=app))
                if len(new_perms) > 0:
                    user.user_permissions.set(new_perms)
                return HttpResponse('success/ACEPATADO/Los cambios se guardaron correctamente')
        except Error:
            resp = HttpResponse('/admin/listado_usuarios'
                                '?notify=error/ERROR/Ha existido un problema en la BD, pongáse en contacto con el admin del sitio')
            resp.status_code = 209
            return resp

