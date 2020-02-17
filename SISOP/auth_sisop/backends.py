from django.contrib.auth import get_user_model
# from django.core.exceptions import PermissionDenied
from ldap3 import Connection, Server
from ldap3.core.exceptions import LDAPSocketOpenError

from config import settings
from auth_sisop.exceptions_auth import DatosNoValidos, ServerAuthError


class BackendSisop:
    """
    autentica utilizando el LDAP
    """

    def authenticate(self, request, usuario=None, password=None):
        if not (usuario and password):
            return None
        if self._can_authenticate(usuario):
            return self._auth_ldap(usuario, password)
        raise DatosNoValidos('usuario: {} desactivado'.format(usuario))

    def _auth_ldap(self, usuario, password):
        server = Server(settings.LDAP_AUTH_URL)
        usuario_format = 'uid={},{}'.format(usuario, settings.LDAP_AUTH_SEARCH_BASE)
        try:
            with Connection(server, usuario_format, password) as c:
                if not c:
                    raise LDAPSocketOpenError
                if not c.bound:
                    # raise PermissionDenied
                    return None
                c.search(settings.LDAP_AUTH_SEARCH_BASE,
                         '(&(objectclass={})(uid={}))'.format(settings.LDAP_AUTH_OBJECT_CLASS, usuario),
                         attributes=[v for k, v in settings.LDAP_AUTH_USER_FIELDS.items()])
                datos_ldap = c.entries[0]
        except LDAPSocketOpenError:
            raise ServerAuthError('No hay servidor de inicio de sesión en este momento')

        datos_usuario = {k: getattr(datos_ldap, v).value for k, v in settings.LDAP_AUTH_USER_FIELDS.items()}
        usuario = datos_usuario.pop('usuario', None)
        nombre = datos_usuario.pop('nombre', None)
        email = datos_usuario.pop('email', None)
        unidad_org = datos_usuario.pop('unidad_org', None)
        return get_user_model().objects.create_user(usuario, nombre, email, unidad_org, None, **datos_usuario)

    def _can_authenticate(self, usuario):
        """
        :param usuario:
        :return: Si el usuario no esta desacitivado (is_active = False)
        """
        try:
            user = get_user_model().objects.get(usuario=usuario)
            return user.is_active
        except get_user_model().DoesNotExist:
            return True

    def get_user(self, usuario):
        user = get_user_model()
        try:
            return user.objects.get(usuario=usuario)
        except user.DoesNotExist:
            return None
