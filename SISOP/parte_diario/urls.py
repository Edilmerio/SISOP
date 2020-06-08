from django.conf.urls import url

from .views.indicadores import Indicadores
from .views.table_indicadores import TableIndicadores
from .views.actualizar_lineas_servicio import LineasServicio, GetFormLineasServicio

app_name = 'parte_diario'
urlpatterns = [
    url(r'^indicadores$', Indicadores.as_view(), name='indicadores'),
    url(r'^table_indicadores$', TableIndicadores.as_view(), name='table_indicadores'),
    url(r'^lineas_servicio$', LineasServicio.as_view(), name='lineas_servicio'),
    url(r'^form_lineas_servicio$', GetFormLineasServicio.as_view(), name='form_lineas_servicio')
]
