from django.db import models
from django.core.validators import MinValueValidator

from general.models import CentroAsociado, CentralTelefonica

class Permisos(models.Model):
    """
    model para crear permisos en la app espectro no asociados a ningun modelo con
    tabla asociada.
    """
    class Meta:
        managed = False
        permissions = (
            ('estadistico', 'Estadistico'),
        )

class ClavesInvalidas(models.Model):
    clave = models.CharField(max_length=100, unique=True)

class ClasificacionServicio(models.Model):
    clasificacion = models.CharField(max_length=100, unique=True)

class TipoServicio(models.Model):
    tipo_servicio = models.CharField(max_length=100, unique=True)
    identificativo = models.CharField(max_length=50, null=True, unique=True)
    clasificacion = models.ForeignKey(ClasificacionServicio, on_delete=models.CASCADE)

class LineasServicios(models.Model):
    datos = models.PositiveIntegerField(validators=[MinValueValidator(limit_value=0, message='El valor debe ser mayor 0')])
    abonado = models.PositiveIntegerField(validators=[MinValueValidator(limit_value=0, message='El valor debe ser mayor 0')])
    centro_asociado = models.ForeignKey(CentroAsociado, on_delete=models.CASCADE)
    fecha = models.DateField()

class Reparadas(models.Model):
    central = models.ForeignKey(CentralTelefonica, on_delete=models.CASCADE)
    fecha = models.DateField()
    clasificacion = models.ForeignKey(ClasificacionServicio, on_delete=models.CASCADE)
    rep_lte_1d = models.PositiveIntegerField(validators=[MinValueValidator(limit_value=0, message='El valor debe ser mayor 0')], default=0)
    demora_lte_1d = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    rep_lte_3d = models.PositiveIntegerField(validators=[MinValueValidator(limit_value=0, message='El valor debe ser mayor 0')], default=0)
    demora_lte_3d = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    rep_gt_3d = models.PositiveIntegerField(validators=[MinValueValidator(limit_value=0, message='El valor debe ser mayor 0')], default=0)
    demora_gt_3d = models.DecimalField(max_digits=10, decimal_places=2, default=0)

class Pendientes(models.Model):
    central = models.ForeignKey(CentralTelefonica, on_delete=models.CASCADE)
    fecha = models.DateField()
    clasificacion = models.ForeignKey(ClasificacionServicio, on_delete=models.CASCADE)
    pendientes = models.PositiveIntegerField(validators=[MinValueValidator(limit_value=0, message='El valor debe ser mayor 0')], default=0)

class ReparadasAux(models.Model):
    folio = models.CharField(max_length=100, null=True)
    fechar = models.CharField(max_length=100, null=True)
    horar = models.CharField(max_length=100, null=True)
    fechac = models.CharField(max_length=100, null=True)
    horac = models.CharField(max_length=100, null=True)
    grupo = models.CharField(max_length=100, null=True)
    descgrupo = models.CharField(max_length=100, null=True)
    centro = models.CharField(max_length=100, null=True)
    telefono = models.CharField(max_length=100, null=True)
    tiposerv = models.CharField(max_length=100, null=True)
    categcli = models.CharField(max_length=100, null=True)
    clave = models.CharField(max_length=100, null=True)
    ultimademora = models.CharField(max_length=100, null=True)
    idplantas = models.CharField(max_length=100, null=True)
    nombpta = models.CharField(max_length=100, null=True)
    idcentel = models.CharField(max_length=100, null=True)
    descenttel = models.CharField(max_length=100, null=True)
    iddt = models.CharField(max_length=100, null=True)
    descdt = models.CharField(max_length=100, null=True)
    region = models.CharField(max_length=100, null=True)
    zona = models.CharField(max_length=100, null=True)
    municipio = models.CharField(max_length=100, null=True)
    date_r = models.DateField(null=True)
    date_c = models.DateField(null=True)


class PendientesAux(models.Model):
    folio = models.CharField(max_length=100, null=True)
    fechar = models.CharField(max_length=100, null=True)
    horar = models.CharField(max_length=100, null=True)
    fechac = models.CharField(max_length=100, null=True)
    horac = models.CharField(max_length=100, null=True)
    grupo = models.CharField(max_length=100, null=True)
    descgrupo = models.CharField(max_length=100, null=True)
    centro = models.CharField(max_length=100, null=True)
    telefono = models.CharField(max_length=100, null=True)
    tiposerv = models.CharField(max_length=100, null=True)
    categcli = models.CharField(max_length=100, null=True)
    ultimademora = models.CharField(max_length=100, null=True)
    idplantas = models.CharField(max_length=100, null=True)
    nombpta = models.CharField(max_length=100, null=True)
    idcentel = models.CharField(max_length=100, null=True)
    descenttel = models.CharField(max_length=100, null=True)
    iddt = models.CharField(max_length=100, null=True)
    descdt = models.CharField(max_length=100, null=True)
    region = models.CharField(max_length=100, null=True)
    zona = models.CharField(max_length=100, null=True)
    municipio = models.CharField(max_length=100, null=True)
    date_r = models.DateField(null=True)
