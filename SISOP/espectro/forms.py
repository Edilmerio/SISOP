from django import forms
from .models import Sistema, TipoSistema, Radio, Solicitud, Licencia, Equipo, TipoSolicitud, Pago, PagoSistema
from . import utiles


class SistemaForm(forms.ModelForm):
    class Meta:
        model = Sistema
        fields = ['id', 'sistema', 'equipo', 'enlace', 'esta_en_uso']
        widgets = {
            'sistema': forms.TextInput(attrs={'class': 'form-control input-sm'}),
            'equipo': forms.Select(attrs={'class': 'form-control input-sm select-equipo'}),
            'enlace': forms.TextInput(attrs={'class': 'form-control input-sm'}),

        }
        labels = {
            'sistema': 'No. Sistema/Exp.',
            'enlace': 'Nombre del Enlace',
            'esta_en_uso': 'El sistema está en uso',
        }

    def __init__(self, *args, **kwargs):
        self.cbx_solicitud_autorizada = kwargs.pop('cbx_solicitud_autorizada', '')
        super(SistemaForm, self).__init__(*args, **kwargs)

        self.fields['equipo'].empty_label = None

        if self.instance.esta_en_uso:
            self.fields['esta_en_uso'].disabled = True

        if self.is_bound:
            self.fields['equipo'].queryset = Equipo.objects.filter(tipo_sistema=TipoSistema.objects.get(equipo__pk=self.data['equipo']))
            self.fields['equipo'].initial = self.data['equipo']
            return
        if self.instance.id:
            self.fields['equipo'].queryset = Equipo.objects.filter(tipo_sistema=TipoSistema.objects.get(equipo=self.instance.equipo))
            self.fields['equipo'].initial = self.instance.equipo.id
            return
        inicial_tipo_sistema = TipoSistema.objects.order_by('tipo_sistema')[0]
        list_inicial_equipo = Equipo.objects.filter(tipo_sistema=inicial_tipo_sistema).order_by('equipo')
        self.fields['equipo'].queryset = list_inicial_equipo

    # El numero del sistema debe ser unico para todos los sistemas del mismo tipo de sistemas.
    # Si la solicitud esta autrizada el No sistema es obligatorio
    def clean(self):
        super().clean()
        sistema = self.cleaned_data['sistema']
        if self.cleaned_data['sistema']:
            sistemas_tipo_sistema = Sistema.objects.filter(equipo__tipo_sistema=self.cleaned_data['equipo'].tipo_sistema)
            sistemas_exlude_pk = sistemas_tipo_sistema.exclude(pk=self.instance.pk)
            if sistemas_exlude_pk.filter(sistema=sistema).exists():
                self.add_error('sistema', 'El No.Sistema debe ser único')
        else:
            if self.cbx_solicitud_autorizada == 'checked':
                self.add_error('sistema', 'Si la solicitud es autorizada este campo es obligatorio')


class EquipoForm(forms.ModelForm):
    class Meta:
        model = Equipo
        fields = ['tipo_sistema']

        widgets = {
            'tipo_sistema': forms.Select(attrs={'class': 'form-control input-sm'})
        }

    def __init__(self, *args, sistema=None, **kwargs):
        super(EquipoForm, self).__init__(*args, **kwargs)
        self.fields['tipo_sistema'].empty_label = None

        if self.is_bound:
            self.fields['tipo_sistema'].initial = self.data['tipo_sistema']
            return
        if sistema:
            self.fields['tipo_sistema'].initial = TipoSistema.objects.get(equipo=sistema.equipo).id
            return
        self.fields['tipo_sistema'].queryset = TipoSistema.objects.order_by('tipo_sistema')


class RadioForm(forms.ModelForm):
    class Meta:
        model = Radio
        fields = ['ubicacion', 'municipio']
        widgets = {
            'ubicacion': forms.TextInput(attrs={'class': 'form-control input-sm'}),
            'municipio': forms.Select(attrs={'class': 'form-control input-sm'}),
        }
        labels = {
            'ubicacion': 'Ubicación',
        }


class RadioFormSet(forms.models.BaseModelFormSet):
    class Meta:
        model = Radio
        fields = ['ubicacion', 'municipio']
        widgets = {
            'sistema': forms.Select(attrs={'class': 'form-control'}),
            'ubicacion': forms.TextInput(attrs={'class': 'form-control'}),
            'municipio': forms.Select(attrs={'class': 'form-control'}),
        }


class SolicitudForm(forms.ModelForm):
    class Meta:
        model = Solicitud
        fields = ['fecha_envio', 'fecha_autorizacion', 'archivo_solicitud', 'tipo_solicitud']
        widgets = {
            'tipo_solicitud': forms.Select(attrs={'class': 'form-control input-sm select-equipo'}),
        }

    def __init__(self, *args, **kwargs):
        self.cbx_solicitud_autorizada = kwargs.pop('cbx_solicitud_autorizada', '')
        self.sistema = kwargs.pop('sistema', None)

        super(SolicitudForm, self).__init__(*args, **kwargs)
        self.fields['fecha_envio'].widget.attrs["class"] = 'form-control read-only'
        self.fields['fecha_envio'].widget.attrs["placeholder"] = 'fecha de envío'
        self.fields['fecha_envio'].widget.attrs["readonly"] = ''
        self.fields['fecha_autorizacion'].widget.attrs["class"] = 'form-control'
        self.fields['fecha_autorizacion'].widget.attrs["placeholder"] = 'fecha de autorización'
        self.fields['fecha_autorizacion'].widget.attrs["readonly"] = ''
        self.fields['tipo_solicitud'].empty_label = None

        if self.instance.id:
            self.fields['fecha_envio'].disabled = True
            self.fields['tipo_solicitud'].disabled = True
            # self.fields['archivo_solicitud'].disabled = True
            if self.instance.fecha_autorizacion:
                self.fields['fecha_autorizacion'].disabled = True
            self.fields['tipo_solicitud'].initial = self.instance.tipo_solicitud
            return

        #  para configurar la lista de tipo de solicitud
        if self.sistema:
            if Solicitud.objects.filter(sistema=self.sistema).exists():
                # si tiene solicitud de alta se excluye de la lista
                t_sol_sin_alta = TipoSolicitud.objects.exclude(tipo_solicitud='ALTA')
                self.fields['tipo_solicitud'].queryset = t_sol_sin_alta
                #  si tiene solicitud de baja se quita toda la lista no se va a poder poner otra sol de BAJA
                if Solicitud.objects.filter(sistema=self.sistema).filter(tipo_solicitud__tipo_solicitud='BAJA').exists():
                    self.fields['tipo_solicitud'].queryset = TipoSolicitud.objects.filter(tipo_solicitud='BAJA')
                    self.fields['tipo_solicitud'].initial = TipoSolicitud.objects.get(tipo_solicitud='BAJA').pk
            # Solo se da la opcion de alta.
            else:
                self.fields['tipo_solicitud'].queryset = TipoSolicitud.objects.filter(tipo_solicitud='ALTA')
        else:
            self.fields['tipo_solicitud'].queryset = TipoSolicitud.objects.filter(tipo_solicitud='ALTA')

    def clean_fecha_autorizacion(self):
        super().clean()
        fecha_autorizacion = self.cleaned_data['fecha_autorizacion']
        if not fecha_autorizacion and self.cbx_solicitud_autorizada == 'checked':
            raise forms.ValidationError("Este campo es obligatorio")
        return fecha_autorizacion

    def clean_fecha_envio(self):
        super().clean()
        fecha_envio = self.cleaned_data['fecha_envio']
        # si la solicitud es nueva la fecha de envio debe ser mayor a la ultima para este sistema.
        if not self.instance.id:
            if utiles.fecha_ultima_solicitud(sistema=self.sistema) >= fecha_envio:
                raise forms.ValidationError("Se envió una solicitud más reciente ")
        return fecha_envio

    def clean(self):
        if self.sistema:
            super().clean()
            if not self.sistema.sistema and self.cbx_solicitud_autorizada == 'checked':
                raise forms.ValidationError('Si la solicitud es autorizada '
                                            'por el Ministerio, es necesario primero actualizar el No. del sistema')


class LicenciaForm(forms.ModelForm):
    class Meta:
        model = Licencia
        # fields = ['id', 'fecha_emision', 'fecha_vencimiento', 'archivo_licencia', 'licencia']
        exclude = ['solicitud']
        widgets = {
            'licencia':  forms.TextInput(attrs={'class': 'form-control input-sm', 'placeholder': 'No. de la Licencia'}),
        }

    def __init__(self, *args, **kwargs):
        self.solicitud = kwargs.pop('solicitud', None)
        super(LicenciaForm, self).__init__(*args, **kwargs)
        self.fields['fecha_emision'].widget.attrs["class"] = 'form-control'
        self.fields['fecha_emision'].widget.attrs["placeholder"] = 'fecha de emisión'
        self.fields['fecha_emision'].widget.attrs["readonly"] = ''
        self.fields['fecha_vencimiento'].widget.attrs["class"] = 'form-control'
        self.fields['fecha_vencimiento'].widget.attrs["placeholder"] = 'fecha de vencimiento'
        self.fields['fecha_vencimiento'].widget.attrs["readonly"] = ''

        if self.instance.id:
            self.fields['licencia'].disabled = True
            self.fields['fecha_emision'].disabled = True
            self.fields['fecha_vencimiento'].disabled = True
            # self.fields['archivo_licencia'].disabled = True

    def clean_fecha_emision(self):
        super().clean()
        fecha_emision = self.cleaned_data['fecha_emision']
        if self.solicitud:
            licencias = Licencia.objects.filter(solicitud=self.solicitud)
            if licencias.exists():
                f_ultima_licencia = licencias.order_by('-id')[0].fecha_emision
                if fecha_emision < f_ultima_licencia:
                    raise forms.ValidationError("Existe una licencia con fecha posterior...")
        return fecha_emision


class PagoForm(forms.ModelForm):
    class Meta:
        model = Pago
        # fields = ['id', 'fecha_emision', 'fecha_vencimiento', 'archivo_licencia', 'licencia']
        exclude = ['division_territorial']
        # widgets = {
        #     'licencia':  forms.TextInput(attrs={'class': 'form-control input-sm', 'placeholder': 'No. de la Licencia'}),
        # }

    def __init__(self, *args, **kwargs):
        super(PagoForm, self).__init__(*args, **kwargs)
        self.fields['no_notificacion'].widget.attrs["class"] = 'form-control input-sm'
        self.fields['no_notificacion'].widget.attrs["placeholder"] = 'No notificación'
        self.fields['fecha_notificacion'].widget.attrs["placeholder"] = 'Notificación'
        self.fields['fecha_notificacion'].widget.attrs["class"] = 'form-control input-sm'
        self.fields['fecha_notificacion'].widget.attrs["readonly"] = ''
        self.fields['valor_total'].widget.attrs["class"] = 'form-control input-sm'
        self.fields['valor_total'].widget.attrs["placeholder"] = 'Valor total'
        self.fields['valor_total'].widget.attrs["min"] = 0.1
        self.args = args

    def clean(self):
        super().clean()
        valor_total_aux = 0
        for v in self.args[2]:
            try:
                valor_total_aux += int(v)
            except (TypeError, ValueError):
                raise forms.ValidationError('El valor total de la solicitud debe '
                                            'coincidir con la suma del valor total de los sistemas')
        if self.cleaned_data.get('valor_total') is None or self.cleaned_data.get('valor_total') != valor_total_aux:
            raise forms.ValidationError('El valor total de la solicitud debe '
                                        'coincidir con la suma del valor total de los sistemas')


class PagoSistemaForm(forms.ModelForm):
    class Meta:
        model = PagoSistema
        # fields = ['id', 'fecha_emision', 'fecha_vencimiento', 'archivo_licencia', 'licencia']
        exclude = ['pago', 'municipio', 'valor_mensual', 'fecha_fin_pago']
        widgets = {
            'sistema': forms.TextInput(attrs={'class': 'form-control input-sm typeahead sistema',
                                              'placeholder': 'type to search...',
                                              'data-provide': 'typeahead',
                                              'autocomplete': 'off'}),
        }

    def __init__(self, *args, **kwargs):
        super(PagoSistemaForm, self).__init__(*args, **kwargs)
        # self.fields['sistema'].widget.attrs["class"] = 'form-control input-sm'
        # self.fields['sistema'].widget.attrs["placeholder"] = 'No sistema'
        self.fields['enlace'].widget.attrs["class"] = 'form-control input-sm'
        self.fields['enlace'].widget.attrs["placeholder"] = 'Enlace'
        self.fields['tipo_sistema'].widget.attrs["class"] = 'form-control input-sm'
        self.fields['tipo_sistema'].widget.attrs["placeholder"] = 'Tipo sistema'
        self.fields['valor_total'].widget.attrs["class"] = 'form-control input-sm'
        self.fields['valor_total'].widget.attrs["placeholder"] = 'Valor sistema'
        self.fields['valor_total'].widget.attrs["min"] = 0.1
        self.fields['fecha_inicio_pago'].widget.attrs["placeholder"] = 'Inicio pago'
        self.fields['fecha_inicio_pago'].widget.attrs["class"] = 'form-control input-sm'
        self.fields['fecha_inicio_pago'].widget.attrs["readonly"] = ''
        self.fields['fecha_inicio_pago'].widget.attrs["required"] = ''
        self.fields['meses_diferir'].widget.attrs["class"] = 'form-control input-sm'
        self.fields['meses_diferir'].widget.attrs["placeholder"] = 'Meses a diferir'


class PagoSistemaFormSet(forms.models.BaseModelFormSet):
    class Meta:
        model = PagoSistema
        # exclude = ['pago', 'municipio', 'valor_mensual', 'fecha_fin_pago']
