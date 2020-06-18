from django.db import models
from auth_sisop.models import UserSisop

# Create your models here.

class Provincia(models.Model):
    nombre = models.CharField(max_length=100, unique=True)


class Municipio(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    provincia = models.ForeignKey(Provincia, on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.nombre


class DivisionTerritorial(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    identificativo = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.nombre


class CentroPrincipal(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    division_territorial = models.ForeignKey(DivisionTerritorial, on_delete=models.DO_NOTHING)


class CentroAsociado(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    centro_principal = models.ForeignKey(CentroPrincipal, on_delete=models.DO_NOTHING)
    municipio = models.ForeignKey(Municipio, on_delete=models.DO_NOTHING)


class GInformacion(models.Model):
    """
    model for group of informations
    """
    ginfo = models.CharField(max_length=100, unique=True)


class Informacion(models.Model):
    """
    model for informations
    """
    informacion = models.CharField(max_length=100, unique=True)
    ginfo = models.ForeignKey(GInformacion, on_delete=models.CASCADE)


class Subcripcion(models.Model):
    """
    model for realtionship between user, GInformaciones and Centro Asociado
    """
    user = models.ForeignKey(UserSisop, on_delete=models.CASCADE)
    ginfo = models.ForeignKey(GInformacion, on_delete=models.CASCADE)
    centro_asociado = models.ForeignKey(CentroAsociado, on_delete=models.CASCADE)

class CentralTelefonica(models.Model):
    central = models.CharField(max_length=100, unique=True)
    identificativo = models.CharField(max_length=50, null=True, unique=True)
    centro_asociado = models.ForeignKey(CentroAsociado, on_delete=models.CASCADE, null=True)

