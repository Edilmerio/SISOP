from django.conf.urls import url

from espectro.views import nuevo, editar, listados, desacarga_ficheros, pago_licencia
from espectro import utiles

app_name = 'espectro'
urlpatterns = [
    url(r'^nuevo_sistema$', nuevo.NuevoSistema.as_view(), name='nuevo_sistema'),
    url(r'^lista_equipos/([0-9]+)$', utiles.lista_equipos, name='lista_equipos'),
    url(r'^editar_sistema/([0-9]+)$', editar.EditarSistema.as_view(), name='editar_sistema'),
    url(r'^editar_solicitud/([0-9]+)$', editar.EditarSolicitud.as_view(), name='editar_solicitud'),
    url(r'^licencias/([0-9]+)$', editar.Licencias.as_view(), name='licencias'),
    url(r'^nueva_solicitud/([0-9]+)$', nuevo.NuevaSolicitud.as_view(), name='nueva_solicitud'),
    url(r'^listado_solicitudes_licencias/([0-9]+)$', listados.ListadoSolicitudesLicencias.as_view(),
        name='listado_solicitudes_licencias'),
    url(r'^listado_licencias/([0-9]+)$', listados.ListadoLicencias.as_view(), name='listado_licencias'),
    url(r'^descargar_fichero/$', desacarga_ficheros.descargar_ficheros, name='descargar_ficheros'),
    url(r'^nueva_licencia/([0-9]+)$', nuevo.NuevaLicencia.as_view(), name='nueva_licencia'),
    url(r'^listado_sistemas/([0-1])$', listados.ListadoSistemas.as_view(), name='listado sistemas'),
    url(r'^listado_solicitudes_proceso/([0-4])$', listados.ListadoSolicitudesProceso.as_view(), name='listado solicitudes proceso'),
    url(r'^listado_pagos/([0-1])', pago_licencia.ListadoPago.as_view(), name='listado pagos'),
    url(r'nuevo_pago$', pago_licencia.NuevoPago.as_view(), name='nuevo_pago'),
    url(r'lista_sistemas_pago_licencias$', pago_licencia.lista_sistemas_pago_licencias, name='lista_sistemas_pago_licencias')
]
