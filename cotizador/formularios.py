from django import forms
from django.forms import ModelForm
from django.db import DatabaseError
from .simulador import obtener_ubicaciones_disponibles
from .models import CotizacionTraslado, TransporteApp

class CotizacionForm(forms.Form):
    origen = forms.ChoiceField(
        label="Punto de Origen",
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )
    destino = forms.ChoiceField(
        label="Punto de Destino",
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            ubicaciones = obtener_ubicaciones_disponibles()
            CHOICES = [(u, u) for u in ubicaciones]
        except DatabaseError:
            CHOICES = [('', '--- No está lista la Base de Datos ---')]

        CHOICES.insert(0, ('', '--- Seleccione un lugar ---'))
        self.fields['origen'].choices = CHOICES
        self.fields['destino'].choices = CHOICES

    def clean(self):
        cleaned_data = super().clean()
        origen = cleaned_data.get("origen")
        destino = cleaned_data.get("destino")
        if origen and destino and origen == destino:
            raise forms.ValidationError("El origen y destino no pueden ser iguales.")
        return cleaned_data

class EditarCotizacionForm(ModelForm):
    """
    Formulario para modificar los datos de una solicitud de cotización
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        self.fields['app_seleccionada'].queryset = TransporteApp.objects.all().order_by('nombre')

    class Meta:
        model = CotizacionTraslado
        fields = ['origen_nombre', 'destino_nombre', 'app_seleccionada']
        labels = {
            'origen_nombre': 'Origen',
            'destino_nombre': 'Destino',
            'app_seleccionada': 'Aplicación Seleccionada',
        }
