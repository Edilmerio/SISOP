import django_tables2 as tables

from auth_sisop.models import UserSisop
from django_tables2.utils import A


class UsuariosTable(tables.Table):
    class Meta:
        model = UserSisop
        attrs = {'class': 'table table-condensed table-hover table-bordered'}
        fields = ('usuario', 'nombre', 'unidad_org', 'email', 'is_active', 'is_superuser')
        sequence = ('usuario', 'nombre', 'email', 'unidad_org', 'is_active', 'is_superuser')

    # Agregando Columnas
    permisos = tables.LinkColumn('administracion:editar_permisos', text='editar/detalles', args=[A('pk')], orderable=False,
                                 attrs={'td': {'class': 'permisos'}})

    def __init__(self, *args, **kwargs):
        for _, val in self.base_columns.items():
            val.orderable = False
            val.attrs = {'td': {'class': val.accessor}} if not val.attrs else val.attrs
        super().__init__(*args, **kwargs)

