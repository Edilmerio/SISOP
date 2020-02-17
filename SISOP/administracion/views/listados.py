from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from administracion.tables import UsuariosTable
from auth_sisop.models import UserSisop
from espectro import utiles
from auth_sisop.views.auth import logout_view


class ListadoUsuarios(LoginRequiredMixin, TemplateView):
    template_name = 'administracion/ListadoUsuarios.html'

    def get(self, request, *args, **kwargs):
        if not request.user.has_perm('administracion.administrador'):
            return logout_view(request, next=request.path)

        usuarios = UserSisop.objects.exclude(is_superuser=1).order_by('usuario')
        search = request.GET.get('search', None)
        if search:
            usuarios = usuarios.filter(usuario__contains=search)
        if not usuarios.exists():
            return render(request, self.template_name, {'table': None, 'busqueda': request.GET.get('search', '')})
        page = utiles.pagina_valida(request.GET.get('page', 1), 2, usuarios.count())
        table_usuarios = UsuariosTable(usuarios)
        table_usuarios.paginate(page=page, per_page=10)

        notify = request.GET.get('notify', None)

        return render(request, self.template_name, {'table': table_usuarios,
                                                    'busqueda': request.GET.get('search', ''),
                                                    'notify': notify})
