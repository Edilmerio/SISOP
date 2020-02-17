import os

from django.db import models
from django.dispatch import receiver
from django.core.validators import MinValueValidator

from general.models import Municipio, DivisionTerritorial
from config.settings_base_dir import BASE_DIR

# Create your models here .


def upload_path_solicitud(instance, filename):
    """
    :param instance:
    :param filename:
    :return: la ruta donde se guardara la solicitud
    """
    return os.path.join(BASE_DIR, 'uploads', 'espectro', 'solicitudes', str(instance.fecha_envio.year), filename)


def upload_path_licencia(instance, filename):
    """
        :param instance:
        :param filename:
        :return: la ruta donde se guardara la licencia
        """
    return os.path.join(BASE_DIR, 'uploads', 'espectro', 'licencias', str(instance.fecha_emision.year), filename)


def upload_path_pago(instance, filename):
    """
        :param instance:
        :param filename:
        :return: la ruta donde se guardara la licencia
        """
    return os.path.join(BASE_DIR, 'uploads', 'espectro', 'pagos', str(instance.fecha_notificacion.year), filename)


class Permisos(models.Model):
    """
    model para crear permisos en la app espectro no asociados a ningun modelo con
    tabla asociada.
    """
    class Meta:
        managed = False
        permissions = (
            ('visualizador_nacional', 'Visualizador Nacional'),
            ('permisionario', 'Permisionario')
        )


class TipoSistema(models.Model):
    tipo_sistema = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.tipo_sistema


class Equipo(models.Model):
    equipo = models.CharField(max_length=100, unique=True)
    tipo_sistema = models.ForeignKey(TipoSistema, on_delete=models.DO_NOTHING)
    valor_pago_licencia = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    meses_diferir_pago = models.PositiveIntegerField(validators=[MinValueValidator(1, 'El valor debe ser mayor 0')], null=True)

    def __str__(self):
        return self.equipo


class Sistema(models.Model):
    id = models.AutoField(primary_key=True)
    sistema = models.CharField(null=True, blank=True, max_length=20, verbose_name='No. Sistema/Expediente')
    enlace = models.CharField(max_length=200, unique=True)
    equipo = models.ForeignKey(Equipo, on_delete=models.DO_NOTHING)
    division_territorial = models.ForeignKey(DivisionTerritorial, on_delete=models.DO_NOTHING, verbose_name='División Territorial')
    esta_en_uso = models.BooleanField(default=False)

    def __str__(self):
        return self.sistema.__str__()


class Radio(models.Model):
    sistema = models.ForeignKey(Sistema, on_delete=models.CASCADE)
    ubicacion = models.CharField(max_length=100)
    municipio = models.ForeignKey(Municipio, on_delete=models.DO_NOTHING)


class TipoSolicitud(models.Model):
    tipo_solicitud = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.tipo_solicitud


class Solicitud(models.Model):
    fecha_envio = models.DateField(null=False, blank=False)
    fecha_autorizacion = models.DateField(null=True, blank=True)
    sistema = models.ForeignKey(Sistema, on_delete=models.CASCADE)
    tipo_solicitud = models.ForeignKey(TipoSolicitud, on_delete=models.DO_NOTHING)
    archivo_solicitud = models.FileField(null=True, blank=True, upload_to=upload_path_solicitud, max_length=200)

    def __str__(self):
        return str(self.id)

    # la idea es eliminal el false en el campo de la BD y en su lugar poner Null,
    # para evitar el nombre de False como si fuera el nombre de un archivo.
    def save(self, *args, **kwargs):
        if not self.archivo_solicitud:
            self.archivo_solicitud = None
        super().save(*args, **kwargs)


class Licencia(models.Model):
    licencia = models.CharField(max_length=50, unique=True)
    fecha_emision = models.DateField()
    fecha_vencimiento = models.DateField()
    solicitud = models.ForeignKey(Solicitud, on_delete=models.CASCADE)
    archivo_licencia = models.FileField(null=True, blank=True, upload_to=upload_path_licencia, max_length=200)


class Bitacora(models.Model):
    sistema = models.CharField(null=True, blank=True, max_length=20, verbose_name='No. Sistema')
    enlace = models.CharField(max_length=200)
    accion = models.CharField(max_length=200)
    usuario = models.CharField(max_length=200)
    fecha = models.DateField()


@receiver(models.signals.post_delete, sender=Solicitud)
def delete_file_solicitud(sender, instance, **kwargs):
    """
    Elimina el fichero correspondiente a la solicir=tud cuando se elimina
    la intancia
    """
    if instance.archivo_solicitud:
        if os.path.isfile(instance.archivo_solicitud.path):
            os.remove(instance.archivo_solicitud.path)


@receiver(models.signals.pre_save, sender=Solicitud)
def save_field_solicitud(sender, instance, **kwargs):
    """
    Elimina el archivo viejo cuando se actualiza la intance
    """
    # if not instance is new.
    if not instance.pk:
        return
    archivo_viejo = Solicitud.objects.get(pk=instance.pk).archivo_solicitud
    if archivo_viejo and not archivo_viejo == instance.archivo_solicitud:
        if os.path.isfile(archivo_viejo.path):
            os.remove(archivo_viejo.path)


@receiver(models.signals.post_delete, sender=Licencia)
def delete_file_licencia(sender, instance, **kwargs):
    """
    Elimina el fichero correspondiente a la solicir=tud cuando se elimina
    la intancia
    """
    if instance.archivo_licencia:
        if os.path.isfile(instance.archivo_licencia.path):
            os.remove(instance.archivo_licencia.path)


@receiver(models.signals.pre_save, sender=Licencia)
def save_field_licencia(sender, instance, **kwargs):
    """
    Elimina el archivo viejo cuando se actualiza la intance
    """
    # if not instance is new.
    if not instance.pk:
        return
    archivo_viejo = Licencia.objects.get(pk=instance.pk).archivo_licencia
    if archivo_viejo and not archivo_viejo == instance.archivo_licencia:
        if os.path.isfile(archivo_viejo.path):
            os.remove(archivo_viejo.path)


class Pago(models.Model):
    no_notificacion = models.CharField(max_length=20, unique=True)
    fecha_notificacion = models.DateField()
    valor_total = models.DecimalField(max_digits=10, decimal_places=2,
                                      validators=[MinValueValidator(limit_value=0.1, message='El valor debe ser mayor 0')])
    archivo_pago = models.FileField(null=True, blank=True, upload_to=upload_path_pago)
    division_territorial = models.ForeignKey(DivisionTerritorial, on_delete=models.DO_NOTHING)

    def __str__(self):
        return str(self.no_notificacion)


class PagoSistema(models.Model):
    pago = models.ForeignKey(Pago, on_delete=models.CASCADE)
    sistema = models.CharField(max_length=20)
    enlace = models.CharField(max_length=100)
    tipo_sistema = models.CharField(max_length=20)
    municipio = models.CharField(max_length=100)
    valor_total = models.DecimalField(verbose_name='Valor Sistema', max_digits=10, decimal_places=2,
                                      validators=[MinValueValidator(limit_value=0.1, message='El valor debe ser mayor 0')])
    valor_mensual = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_inicio_pago = models.DateField()
    fecha_fin_pago = models.DateField()
    meses_diferir = models.PositiveIntegerField(validators=[MinValueValidator(limit_value=1, message='El valor debe ser mayor 0')])
