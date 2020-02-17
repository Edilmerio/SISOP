from django.conf.urls import url

from .views import not_found, subcripcion


app_name = 'general'
urlpatterns = [
    url(r'^NotFound$', not_found.not_found, name='not_found'),
    url(r'^subcripcion/([0-9]+)$', subcripcion.Subcripcion.as_view(), name='subcripcion')
]

