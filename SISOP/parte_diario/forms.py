from django import forms

from .models import LineasServicios

class LineasServicioForms(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(LineasServicioForms, self).__init__(*args, **kwargs)
        self.fields['centro_asociado'].widget = forms.HiddenInput()
        self.fields['fecha'].widget = forms.HiddenInput()
        self.fields['abonado'].widget.attrs["class"] = 'form-control input-sm'
        self.fields['datos'].widget.attrs["class"] = 'form-control input-sm'
        self.args = args

    class Meta:
        model = LineasServicios
        fields = ['abonado', 'datos', 'centro_asociado', 'fecha']
        widgets = {
            'centro_asociado': forms.TextInput(),
        }
        labels = {
            'centro_asociado': 'CTA'
        }

class LineasServicioFormSet(forms.models.BaseModelFormSet):
    class Meta:
        model = LineasServicios