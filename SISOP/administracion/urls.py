from django.conf.urls import url

from administracion.views.listados import ListadoUsuarios
from administracion.views.editar import EditarPermisos
app_name = 'administracion'

urlpatterns = [
    url(r'^listado_usuarios$', ListadoUsuarios.as_view(), name='listado usuarios'),
    url(r'^editar_permisos/([0-9]+)$', EditarPermisos.as_view(), name='editar_permisos'),
]