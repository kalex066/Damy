from django import forms
from .simulador import obtener_ubicaciones_disponibles
from .models import CotizacionTraslado

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
        ubicaciones = obtener_ubicaciones_disponibles()
        CHOICES = [(u, u) for u in ubicaciones]
        if not CHOICES:
            CHOICES = [('', '--- No hay ubicaciones disponibles ---')]

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

class EditarCotizacionForm(forms.ModelForm):
    origen = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Origen"
    )
    destino = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Destino"
    )

    class Meta:
        model = CotizacionTraslado
        fields = ['origen', 'destino', 'app_seleccionada']
        widgets = {
            'app_seleccionada': forms.Select(attrs={'class': 'form-control'}),
        }
    # precarga de datos de la cotizacion original
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.ruta:
            self.fields['origen'].initial = self.instance.ruta.origen
            self.fields['destino'].initial = self.instance.ruta.destino

