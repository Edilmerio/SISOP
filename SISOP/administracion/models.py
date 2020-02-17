from django.db import models

# Create your models here.


class Permisos(models.Model):
    """
    model para crear permisos en la app espectro no asociados a ningun modelo con
    tabla asociada.
    """
    class Meta:
        managed = False
        permissions = (
            ('administrador', 'Administrador del sistema'),
        )
