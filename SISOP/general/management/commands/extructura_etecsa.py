from django.core.management.base import BaseCommand, CommandError
from ...models import Provincia, Municipio, DivisionTerritorial, CentroPrincipal, CentroAsociado


class Command(BaseCommand):
    PROV_MUN = {'LAS TUNAS': ('LAS TUNAS', 'MAJIBACOA', 'MANATI', 'PUERTO PADRE', 'JESUS MENENDEZ', 'AMANCIO', 'COLOMBIA', 'JOBABO'),
                'HOLGUIN': ('HOLGUIN', 'BANES')
                }
    # EXTRUCTURA {(division teritorial, nomenclador): {CTP: (CTA1, CTA2,)}}
    DT_CTP_CTA = {('LAS TUNAS', 'DTLT'): {'LAS TUNAS': ('LAS TUNAS', 'MAJIBACOA', 'MANATI'),
                                          'PUERTO PADRE': ('PUERTO PADRE', 'JESUS MENENDEZ'),
                                          'AMANCIO': ('AMANCIO', 'COLOMBIA', 'JOBABO')
                                          },
                  ('HOLGUIN', 'DTHO'): {'HOLGUIN': ('HOLGUIN', 'BANES'),
                                        }

                  }
    CTA_MUN = {'LAS TUNAS': 'LAS TUNAS', 'MAJIBACOA': 'MAJIBACOA', 'MANATI': 'MANATI', 'PUERTO PADRE': 'PUERTO PADRE',
               'JESUS MENENDEZ': 'JESUS MENENDEZ', 'AMANCIO': 'AMANCIO', 'COLOMBIA': 'COLOMBIA', 'JOBABO': 'JOBABO',
               'HOLGUIN': 'HOLGUIN', 'BANES': 'BANES'}

    def handle(self, *args, **options):
        self.adicionnar_prov_mun()
        self.adicionar_dt_ctp_cta()

    def adicionnar_prov_mun(self):
        """
        Adiciona la provincias si no exite en la BD.
        :return:
        """
        for k in self.PROV_MUN:
            try:
                prov = Provincia.objects.get(nombre=k)
            except Provincia.DoesNotExist:
                prov = Provincia(nombre=k)
                prov.save()
            print('La provincia {} actualizada correctamente'.format(k))
            self._adicionar_mu(prov)

    def _adicionar_mu(self, prov):
        """
         Adiciona los municipios correspondientes a cada provincia si existe
        :param prov:
        :return:
        """
        for mun in self.PROV_MUN[prov.nombre]:
            if not Municipio.objects.filter(provincia=prov, nombre=mun).exists():
                n_mun = Municipio(nombre=mun, provincia=prov)
                n_mun.save()
            print('El municipio {} de la provincia {} actualizado correctamente'.format(prov.nombre, mun))

    def adicionar_dt_ctp_cta(self):
        for k in self.DT_CTP_CTA:
            try:
                dt = DivisionTerritorial.objects.get(nombre=k[0])
                dt.identificativo = k[1]
            except DivisionTerritorial.DoesNotExist:
                dt = DivisionTerritorial(nombre=k[0], identificativo=k[1])
            dt.save()
            print('La DT {} actualizada correctamente'.format(k[0]))
            self._adicionar_ctp_cta(dt)

    def _adicionar_ctp_cta(self, dt):
        for k in self.DT_CTP_CTA[(dt.nombre, dt.identificativo)]:
            try:
                ctp = CentroPrincipal.objects.get(division_territorial=dt, nombre=k)
            except CentroPrincipal.DoesNotExist:
                ctp = CentroPrincipal(nombre=k, division_territorial=dt)
                ctp.save()
            print('La CTP {} actualizado correctamente'.format(k))
            self._adicionar_cta(dt, ctp)

    def _adicionar_cta(self, dt, ctp):
        for k in self.DT_CTP_CTA[(dt.nombre, dt.identificativo)][ctp.nombre]:
            try:
                CentroAsociado.objects.get(centro_principal=ctp, nombre=k)
            except CentroAsociado.DoesNotExist:
                cta = CentroAsociado(centro_principal=ctp, nombre=k, municipio=Municipio.objects.get(nombre=self.CTA_MUN[k]))
                cta.save()
            print('La CTA {} actualizado correctamente'.format(k))




