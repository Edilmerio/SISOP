from datetime import datetime

from django.core.management.base import BaseCommand

from ... models import ClavesInvalidas, ClasificacionServicio, TipoServicio, LineasServicios
from general.models import CentroAsociado


class Command(BaseCommand):
    CLAVES_INVALIDAS = ['01-ZC', '01-ZR', '02-Z', '02-ZC', '02-ZR', '03-Z', '03-ZC', '03-ZR', '04-Z',
                        '04-ZC', '04-ZR', '05-Z', '05-ZC', '05-ZR', '06-Z', '06-ZC', '06-ZR', '07-Z',
                        '07-ZC', '07-ZR', '08-Z', '09-Z', '15-Z', '16-Z', '17-Z', '18-Z', '18-ZC', '19-Z',
                        '20-Z', '21-Z', '21-ZC', '21-ZR', '25-Z', '25-ZC', '25-ZR', '35-Z', '39-Z', '41-Z',
                        '42-Z', '43-Z', '46-Z', '1V', '01-V', '02-V', '2V', '03-V', '3V', '04-V', '4V', '05-V',
                        '5V', '06-V', '6V', '1E', '2E', '3E', '4E']

    CLASIFICACION_SERVICIO = ['telefono', 'datos']

    TIPO_SERVICIO = {'TELEFONO': {'identificativo': 'TE', 'clasificacion': 'telefono'},
                     'TRONCO PPAL DE PIZARRA': {'identificativo': 'TPP', 'clasificacion': 'telefono'},
                     'TRONCO DE PIZARRA': {'identificativo': 'TPZ', 'clasificacion': 'telefono'},
                     'RDSI': {'identificativo': None, 'clasificacion': 'telefono'},
                     'SISTEMA DE CONDUCCION DE SENALES': {'identificativo': None, 'clasificacion': 'telefono'},
                     'SERVICIO DE TRASMISION DE DATOS': {'identificativo': None, 'clasificacion': 'datos'},
                     'SERVICIO HOSTEADO EN LA RED IPMPLS': {'identificativo': 'IPMPLS', 'clasificacion': 'datos'},
                     'PUNTO A PUNTO': {'identificativo': None, 'clasificacion': 'datos'},
                     'FLUJO': {'identificativo': 'FJ', 'clasificacion': 'datos'}
                     }

    def handle(self, *args, **options):
        self.adicionar_claves_invalidas()
        self.adicionar_clasificacion()
        self.adicionar_tipo_servicio()
        # self.inicializar_lineas_servicio()

    def adicionar_claves_invalidas(self):
        for c in self.CLAVES_INVALIDAS:
            if not ClavesInvalidas.objects.filter(clave=c).exists():
                clave = ClavesInvalidas(clave=c)
                clave.save()

    def adicionar_clasificacion(self):
        for c in self.CLASIFICACION_SERVICIO:
            if not ClasificacionServicio.objects.filter(clasificacion=c).exists():
                clasificacion = ClasificacionServicio(clasificacion=c)
                clasificacion.save()

    def adicionar_tipo_servicio(self):
        for k, v in self.TIPO_SERVICIO.items():
            clasificacion = ClasificacionServicio.objects.get(clasificacion=v['clasificacion'])
            try:
                tipo_servicio = TipoServicio.objects.get(tipo_servicio=k)
                tipo_servicio.clasificacion = clasificacion
                tipo_servicio.identificativo = v['identificativo']
                tipo_servicio.save()
            except TipoServicio.DoesNotExist:
                tipo_servicio = TipoServicio(tipo_servicio=k,
                                             identificativo=v['identificativo'],
                                             clasificacion=clasificacion)
                tipo_servicio.save()

    def inicializar_lineas_servicio(self):
        """crea un registro por cada cta si no existe con
        las lineas de datos y abonado en 0
        """
        hoy = datetime.now().date()
        for cta in CentroAsociado.objects.all():
            if not LineasServicios.objects.filter(centro_asociado=cta).exists():
                lineas = LineasServicios(centro_asociado=cta, abonado=0, datos=0, fecha=hoy)
                lineas.save()
