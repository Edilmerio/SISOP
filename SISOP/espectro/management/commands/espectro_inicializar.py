from django.core.management.base import BaseCommand

from espectro.models import TipoSistema, Equipo, TipoSolicitud


class Command(BaseCommand):
    TIPO_SISTEMA_EQUIPOS = {'RADIOENLACE': (['MONOKON', 12, 100], ['BIKON', 12, 100], ['9400LX', 12, 100]),
                            'WIFI': (['HUAWEI 2.4GHZ', 12, 100], ['HUAWEI 5.7GHZ', 12, 100], ['HUAWEI 2.4-5.7GHZ', 12, 100]),
                            'VSAT': (['VSAT', 12, 100],)}
    TIPO_SOLICITUD = ('ALTA', 'MODIFICACION', 'BAJA')

    def handle(self, *args, **options):
        self.adiciionar_tipo_sistemas_equipos()
        self.adicionar_titpo_solicitudes()

    def adiciionar_tipo_sistemas_equipos(self):
        for k in self.TIPO_SISTEMA_EQUIPOS:
            try:
                tipo_sistema = TipoSistema.objects.get(tipo_sistema=k)
            except TipoSistema.DoesNotExist:
                tipo_sistema = TipoSistema(tipo_sistema=k)
                tipo_sistema.save()
            print('El sistema {} actualizado correctamente'.format(k))
            self._adicionar_equipos(tipo_sistema)

    def _adicionar_equipos(self, tipo_sistema):
        for k in self.TIPO_SISTEMA_EQUIPOS[tipo_sistema.tipo_sistema]:
            try:
                equipo = Equipo.objects.get(tipo_sistema=tipo_sistema, equipo=k[0], meses_diferir_pago=k[1],
                                            valor_pago_licencia=k[2])
            except Equipo.DoesNotExist:
                equipo = Equipo(tipo_sistema=tipo_sistema, equipo=k[0], meses_diferir_pago=k[1],
                                valor_pago_licencia=k[2])
                equipo.save()
            print('El equipo {} actualizado correctamente'.format(k))

    def adicionar_titpo_solicitudes(self):
        for k in self.TIPO_SOLICITUD:
            try:
                TipoSolicitud.objects.get(tipo_solicitud=k)
            except TipoSolicitud.DoesNotExist:
                tipo_solic = TipoSolicitud(tipo_solicitud=k)
                tipo_solic.save()
            print('La Solicitud {} actualizada correctamente'.format(k))
