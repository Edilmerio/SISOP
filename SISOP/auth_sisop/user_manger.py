from datetime import datetime

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth import get_user_model
from django.db.utils import DatabaseError
from django.utils import timezone

from auth_sisop.exceptions_auth import DatosNoValidos


class SisopUserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, usuario, nombre, email, unidad_org, password, **extra_fields):
        """
        Metodo que crea o actualiza un usurio en BD
        :param usuario:
        :param password:
        :param email:
        :param extra_fields:
        :return: user
        """
        email = self.normalize_email(email)
        requiered_fields = self.model.REQUIRED_FIELDS + ['usuario', 'id']
        for name in self.model.name_fields_user():
            if name in requiered_fields:
                continue
            else:
                extra_fields.setdefault(name, None)
        try:
            user = self.model.objects.get(usuario=usuario)
        except get_user_model().DoesNotExist:
            user = self.model(usuario=usuario, nombre=nombre, email=email, unidad_org=unidad_org, **extra_fields)
        for extra in extra_fields:
            setattr(user, extra, extra_fields[extra])
        user.set_password(password)
        try:
            user.save(using=self.db)
            return user
        except DatabaseError:
            raise DatosNoValidos('Datos inconsistentes para el usuario: {} en el servidor LDAP'.format(usuario))

    def create_user(self, usuario, nombre, email, unidad_org, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('last_login', timezone.now())
        extra_fields.setdefault('is_active', True)
        return self._create_user(usuario, nombre, email, unidad_org, password, **extra_fields)

    def create_superuser(self, usuario, nombre, email, unidad_org, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('last_login', datetime.now())
        extra_fields.setdefault('is_active', True)
        return self._create_user(usuario, nombre, email, unidad_org, password, **extra_fields)





