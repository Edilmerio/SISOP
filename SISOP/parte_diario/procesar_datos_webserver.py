import os
from datetime import datetime

import zeep
from django.db import IntegrityError
from django.db.models import Min

from config import settings, settings_base_dir
from general import utils
from .utils import diff_days
from .models import ClavesInvalidas, TipoServicio, Reparadas, Pendientes, ClasificacionServicio, ReparadasAux, PendientesAux
from general.models import CentralTelefonica, CentroAsociado

class ProcesarDatos:

    def __init__(self, fecha):
        self.fecha = fecha
        self.pendientes = []
        self.reparadas = []
        self.folios = {}
        # formato de rep_tb y  rep_tx {'nombpta':{'id': 'valor', 'rep_lte_1d': valor, 'rep_lte_3d': valor, 'rep_gt_3d': valor,
        # 'demora_lte_1d':valor
        # 'demora_lte_3':valor, 'demora_gt_3d':valor}}]
        self.rep_tb = {}
        self.rep_tx = {}
        # formato de pen {'nombpta':{'nombpta': pendientes}}
        self.pend_tb = {}
        self.pend_tx = {}

        self.claves_invalidas = ClavesInvalidas.objects.all().values_list('clave', flat=True)
        self.tipos_servico_tb = TipoServicio.objects\
            .filter(clasificacion__clasificacion='telefono').values_list('identificativo', flat=True)
        self.tipos_servicio_tx = TipoServicio.objects \
            .filter(clasificacion__clasificacion='datos').values_list('identificativo', flat=True)

    def procesar_datos(self):
        self.folios = {}
        if not self.__read_data():
            return
        # self.__write_data_in_txt()
        if self.pendientes:
            self.__procesar_pendientes()
        self.folios = {}
        if self.reparadas:
            self.__procesar_reparadas()
        self.__write_bd()

    def __read_data(self):
        try:
            self.pendientes = PendientesAux.objects.filter(date_r=self.fecha).values()
            self.reparadas = ReparadasAux.objects.filter(date_c=self.fecha).values()
            return True
        except Exception as e:
            utils.write_log('Error al recuperar los datos de las pte_aux y/o rep_aux')
            return False

    def __write_data_in_txt(self):
        """
        write pendientes in txt, reparadas in BD
        """
        dir_pte = os.path.join(settings_base_dir.BASE_DIR,
                               'files', 'parte diario', 'pendientes', str(self.fecha.year), str(self.fecha.month))
        utils.make_directory(dir_pte)
        if self.pendientes:
            keys_pend = list(self.pendientes[0])
            array_values_pend = ['{'.join(keys_pend)]
            for p in self.pendientes:
                a_aux = []
                for k in keys_pend:
                    a_aux.append((p[k] if p[k] else ''))
                array_values_pend.append('{'.join(a_aux))
        else:
            array_values_pend = ['NO hay datos']
        try:
            with open(os.path.join(dir_pte, 'pendientes {}.txt'.format(self.fecha.strftime('%d-%m-%Y'))), 'w') as f:
                for p in array_values_pend:
                    f.writelines(p + '\n')
        except Exception as e:
            utils.write_log('Error al escribir pte in txt {}'.format(settings.WSDL_WEB_SERVER_INDICADORES + str(e)))

    def __procesar_reparadas(self):
        for repp in self.reparadas:
            if not self.__verificar_folio(repp):
                continue
            if not self.__verificar_clave_cierre(repp):
                continue
            r = self.__verificar_tipo_servicio_valido(repp)
            if not r:
                continue
            self.__add_reparadas(repp, r)

    def __procesar_pendientes(self):
        for pendd in self.pendientes:
            if not self.__verificar_folio(pendd):
                continue
            if not ProcesarDatos.__verificar_grupo_valido(pendd):
                continue
            r = self.__verificar_tipo_servicio_valido(pendd)
            if not r:
                continue
            self.__add_pendientes(pendd, r)

    def __verificar_folio(self, data):
        """
        verifica si el folio esta duplicado
        en caso de no estar los adiciona al dict
        return True si es valido o False en caso contrario.
        """
        f = data['folio'].strip()
        if not self.folios.get(f, None):
            self.folios[f] = f
            return True
        return False

    def __verificar_clave_cierre(self, data):
        """
        verifica si la clave de cierre es valida
        return True si es valida o False en caso contrario
        """
        return not data['clave'].strip() in self.claves_invalidas

    def __verificar_tipo_servicio_valido(self, data):
        """
        verifica si el el tipo se servicio es valido
        return False si no es un tipo se servicio valido
        return 'TB' si es esta en el tipo de servicios TB
        retun TX si esta en el tipo se servicio de TX
        """
        if data['tiposerv'].strip() in self.tipos_servico_tb:
            # para eliminar los servicios LB, LBN, LT, LTN
            if data['telefono'].strip().startswith('VI L'):
                return False
            return 'TB'
        if data['tiposerv'].strip() in self.tipos_servicio_tx:
            # para eliminar los LD, LR
            if data['telefono'].strip() in ['LD', 'LR']:
                return False
            return 'TX'
        return False

    @staticmethod
    def __verificar_grupo_valido(data):
        """
        verifica si el grupo es valido que no contega PZ
        return false si no es valido
        """
        if not data['grupo']:
            return True
        return 'PZ' not in data['grupo']

    @staticmethod
    def __add_centrales(central, municipio=None):
        """
        en la informacion revisada del webserver el municipio coincide con el CTA
        almenos en las DTLT
        """
        cta = municipio
        if cta:
            try:
                cta = CentroAsociado.objects.get(nombre=municipio)
            except CentroAsociado.DoesNotExist:
                pass
        try:
            c = CentralTelefonica(central=central, centro_asociado=cta)
            c.save()
        except IntegrityError:
            pass

    @staticmethod
    def __get_centrales_id_dic():
        """
        devuelve un dictionary con clave central y valor id
        """
        return {x['central']: x['id']for x in CentralTelefonica.objects.all().values('central', 'id')}

    @staticmethod
    def __calcular_demora(d1, t1, d2, t2):
        """
        calcula la demora en horas dado cadenas de fecha y hora
        return
        """
        string_datetime2 = d2.strip() + ' {}'.format(t2.strip())
        datetime2 = datetime.strptime(string_datetime2, '%Y-%m-%d %H:%M')
        string_datetime1 = d1.strip() + ' {}'.format(t1.strip())
        datetime1 = datetime.strptime(string_datetime1, '%Y-%m-%d %H:%M')
        delta = datetime2 - datetime1
        return round(delta.days*24 + delta.seconds/3600, 2)

    def __add_reparadas(self, data, tipo):
        """
        add reparada de TB o Tx al dict correspondiente
        tipo: TB o Tx
        """

        diff = diff_days(data['fechar'].strip(), data['fechac'].strip())
        if tipo == 'TB':
            dict_aux = self.rep_tb
            clasificacion_id = ClasificacionServicio.objects.get(clasificacion='telefono').pk
        elif tipo == 'TX':
            dict_aux = self.rep_tx
            clasificacion_id = ClasificacionServicio.objects.get(clasificacion='datos').pk
        else:
            clasificacion_id = -1
            dict_aux = {}
            pass

        dict_centrales_id = ProcesarDatos.__get_centrales_id_dic()
        planta = data['nombpta'].strip()
        demora = ProcesarDatos.__calcular_demora(data['fechar'], data['horar'], data['fechac'], data['horac'])
        if not dict_centrales_id.get(planta, None):
            ProcesarDatos.__add_centrales(planta, municipio=data['municipio'].strip())
            dict_centrales_id[planta] = 0
        if planta not in dict_aux:
            dict_aux[planta] = {'fecha': self.fecha, 'clasificacion_id': clasificacion_id}

        # mennor o igual a 1 dia
        if diff <= 1:
            if 'rep_lte_1d' not in dict_aux[planta]:
                dict_aux[planta]['rep_lte_1d'] = 1
                dict_aux[planta]['demora_lte_1d'] = (0.00 if demora < 0 else demora)
            else:
                dict_aux[planta]['rep_lte_1d'] += 1
                dict_aux[planta]['demora_lte_1d'] += (0.00 if demora < 0 else demora)
            return

        # mennor o igual a 3 dias
        if diff <= 3:
            if 'rep_lte_3d' not in dict_aux[planta]:
                dict_aux[planta]['rep_lte_3d'] = 1
                dict_aux[planta]['demora_lte_3d'] = (0.00 if demora < 0 else demora)
            else:
                dict_aux[planta]['rep_lte_3d'] += 1
                dict_aux[planta]['demora_lte_3d'] += (0.00 if demora < 0 else demora)
            return

        if diff > 3:
            if 'rep_gt_3d' not in dict_aux[planta]:
                dict_aux[planta]['rep_gt_3d'] = 1
                dict_aux[planta]['demora_gt_3d'] = (0.00 if demora < 0 else demora)
            else:
                dict_aux[planta]['rep_gt_3d'] += 1
                dict_aux[planta]['demora_gt_3d'] += (0.00 if demora < 0 else demora)

    def __add_pendientes(self, data, tipo):
        if tipo == 'TB':
            dict_aux = self.pend_tb
            clasificacion_id = ClasificacionServicio.objects.get(clasificacion='telefono').pk
        elif tipo == 'TX':
            dict_aux = self.pend_tx
            clasificacion_id = ClasificacionServicio.objects.get(clasificacion='datos').pk
        else:
            clasificacion_id = -1
            dict_aux = {}
            pass
        dict_centrales_id = ProcesarDatos.__get_centrales_id_dic()
        planta = data['nombpta'].strip()
        if not dict_centrales_id.get(planta, None):
            ProcesarDatos.__add_centrales(planta, municipio=data['municipio'].strip())
            dict_centrales_id[planta] = 0
        if planta not in dict_aux:
            dict_aux[planta] = {'pendientes': 1, 'fecha': self.fecha, 'clasificacion_id': clasificacion_id}
        else:
            dict_aux[planta]['pendientes'] += 1

    def __write_bd(self):
        """
        escribe en BD los resumenes de la pendientes y las repardas
        rep_tb, rep_tx, pend_tb, pend_tx
        """
        dict_centrales_id = ProcesarDatos.__get_centrales_id_dic()
        r = []
        for k, v in self.rep_tb.items():
            d = {'central_id': dict_centrales_id.get(k)}
            d.update(v)
            r.append(Reparadas(**d))
        for k, v in self.rep_tx.items():
            d = {'central_id': dict_centrales_id.get(k)}
            d.update(v)
            r.append(Reparadas(**d))
        # delete todas las reparadas de ese dia si hay
        Reparadas.objects.filter(fecha=self.fecha).delete()
        if r:
            Reparadas.objects.bulk_create(r)
        p = []
        for k, v in self.pend_tb.items():
            d = {'central_id': dict_centrales_id.get(k)}
            d.update(v)
            p.append(Pendientes(**d))
        for k, v in self.pend_tx.items():
            d = {'central_id': dict_centrales_id.get(k)}
            d.update(v)
            p.append(Pendientes(**d))

        # delete todas las pendientes de ese dia si hay
        Pendientes.objects.filter(fecha=self.fecha).delete()
        if p:
            Pendientes.objects.bulk_create(p)
        else:
            # write one pte por cada DT para mantener la referencia de la fecha
            one_ct_x_dt = CentralTelefonica.objects\
                .values('centro_asociado__centro_principal__division_territorial').annotate(min_id=Min('id'))
            p1 = []
            clasificacion = ClasificacionServicio.objects.get(clasificacion='telefono')
            for ct in one_ct_x_dt:
                p1.append(Pendientes(fecha=self.fecha, central_id=ct['min_id'], clasificacion=clasificacion))
            Pendientes.objects.bulk_create(p1)

class SaveReparadasWebServer:

    def __init__(self):
        self.reparadas = []

    def save_data_web_server(self):
        """
        obtinene los dotos de webserver y los guarda en BD
        """
        if not self.__read_data_web_server():
            return
        if self.reparadas:
            self.__write_bd()

    def __read_data_web_server(self):
        """
        read data web sever
        """
        try:
            client = zeep.Client(wsdl=settings.WSDL_WEB_SERVER_INDICADORES)
            self.reparadas = getattr(client.service, settings.METHOD_REP)(14)
            return True
        except Exception as e:
            utils.write_log('Error en la llamada al web server {}'.format(settings.WSDL_WEB_SERVER_INDICADORES + str(e)))
            return False

    def __write_bd(self):
        """
        write the data reparadas in BD ReparadasAux
        """
        rep_aux = []
        fields = ReparadasAux._meta.get_fields()
        for r in self.reparadas:
            data = {}
            for f in fields:
                if f.name in ['id', 'date_r', 'date_c']:
                    continue
                data[f.name] = r[f.name].strip() if r[f.name] else None
            try:
                data['date_r'] = datetime.strptime(data['fechar'], '%Y-%m-%d').date()
                data['date_c'] = datetime.strptime(data['fechac'], '%Y-%m-%d').date()
            except ValueError:
                data['date_r'] = None
                data['date_c'] = None
            rep_aux.append(ReparadasAux(**data))
        ReparadasAux.objects.bulk_create(rep_aux)


class SavePendientesWebServer:

    def __init__(self, fecha):
        self.fecha = fecha
        self.pendientes = []

    def save_data_web_server(self):
        """
        obtinene los dotos de webserver y los guarda en BD
        """
        if not self.__read_data_web_server():
            return
        if self.pendientes:
            self.__write_bd()

    def __read_data_web_server(self):
        """
        read data web sever
        """
        try:
            client = zeep.Client(wsdl=settings.WSDL_WEB_SERVER_INDICADORES)
            self.pendientes = getattr(client.service, settings.METHOD_PTE)(14)
            return True
        except Exception as e:
            utils.write_log('Error en la llamada al web server {}'.format(settings.WSDL_WEB_SERVER_INDICADORES + str(e)))
            return False

    def __write_bd(self):
        """
        write the data pendientes in BD PendientesAux
        """
        pend_aux = []
        fields = PendientesAux._meta.get_fields()
        for r in self.pendientes:
            data = {}
            for f in fields:
                if f.name in ['id', 'date_r']:
                    continue
                data[f.name] = r[f.name].strip() if r[f.name] else None
            data['date_r'] = self.fecha
            pend_aux.append(PendientesAux(**data))
        # delete all pendientes de ese dia si hay
        PendientesAux.objects.filter(date_r=self.fecha).delete()
        PendientesAux.objects.bulk_create(pend_aux)
