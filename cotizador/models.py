from django.db import models
from django.contrib.auth.models import User

class TransporteApp(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    logo = models.ImageField(upload_to='logos/', default='logos/default.png')
    precio_base = models.DecimalField(max_digits=8, decimal_places=2, default=3000)
    costo_por_km = models.DecimalField(max_digits=8, decimal_places=2, default=800)
    costo_por_min = models.DecimalField(max_digits=10, decimal_places=2, default=100)
    factor_dinamico = models.DecimalField(max_digits=4, decimal_places=2, default=1.0)
    tiempo_espera = models.IntegerField(default=5)
    link_base = models.CharField(
        max_length=200,
        help_text="URL a la que se redirige al usuario para solicitar el viaje.",
        default='https://www.google.com'
    )
    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Aplicación de Transporte"

class Ruta(models.Model):
    origen = models.CharField(max_length=100)
    destino = models.CharField(max_length=100)
    distancia_km = models.DecimalField (max_digits = 5, decimal_places=2)
    tiempo_min = models.IntegerField(help_text="Tiempo estimado en minutos")
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return (f"{self.origen} -> {self.destino} ({self.distancia_km}km)")

    class Meta:
        unique_together = ('origen', 'destino')
        verbose_name = "Ruta Disponible"
        ordering = ['origen', 'destino']


class CotizacionTraslado(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    ruta = models.ForeignKey(Ruta, on_delete=models.SET_NULL, null=True)
    app_seleccionada = models.ForeignKey(TransporteApp, on_delete=models.SET_NULL, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    tiempo_espera = models.IntegerField(null=True)
    factor_dinamico = models.DecimalField(max_digits=3, decimal_places=2, default=1.00)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.ruta:
            return f"Cotización #{self.pk} - {self.ruta.origen} a {self.ruta.destino}"
        return f"Cotización #{self.pk}"

    class Meta:
        verbose_name = "Solicitud de Cotizacion"
        ordering = ['-fecha_creacion']