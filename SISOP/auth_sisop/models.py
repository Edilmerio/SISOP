from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser

from auth_sisop.user_manger import SisopUserManager

# Create your models here.


class UserSisop(PermissionsMixin, AbstractBaseUser):
    usuario = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)
    nombre = models.CharField(max_length=20)
    apellidos = models.CharField(max_length=50, blank=True, null=True)
    telefono = models.CharField(max_length=10, blank=True, null=True)
    unidad_org = models.CharField(max_length=10, verbose_name='Unidad Org.')
    departamento = models.CharField(max_length=50, blank=True, null=True)
    cargo = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    # is_superuser = models.BooleanField(default=False) se hereda de PermissionsMixin

    objects = SisopUserManager()

    USERNAME_FIELD = 'usuario'
    REQUIRED_FIELDS = ['email', 'nombre', 'unidad_org']
    EMAIL_FIELD = 'email'

    def get_full_name(self):
        """
        :return: el nombre completo del user
        """
        full_name = '{} {}'.format(self.nombre.strip(), self.apellidos.strip())
        return full_name

    def get_sort_name(self):
        """
        :return: el nombre del user
        """
        sort_name = '{}'.format(self.nombre.strip())
        return sort_name

    @staticmethod
    def name_fields_user():
        """
        :return: Una tuple con el nombre de todos los campos del ususrio
        """
        return (field.attname for field in UserSisop._meta.fields)
