from django.db.models import Q
from .models import Ruta, TransporteApp

class AppCotizadora:
    """
    Clase que simula la cotización de traslados en distintas aplicaciones de transporte.
    """

    def __init__(self, app: TransporteApp, ruta: Ruta):
        self.app = app
        self.ruta = ruta

    def calcular_cotizacion(self):
        """
        Calcula el precio estimado del traslado según la distancia y el factor dinámico de la app.
        """
        precio_base = self.app.precio_base
        factor_dinamico = self.app.factor_dinamico
        distancia = self.ruta.distancia_km
        tiempo = self.ruta.tiempo_min

        # Fórmula de cotización del precio
        precio_estimado = precio_base + (distancia * self.app.costo_por_km) + (tiempo * self.app.costo_por_min)
        precio_estimado *= factor_dinamico

        return {
            "app_nombre": self.app.nombre,
            "app_logo": self.app.logo.url if self.app.logo else None,
            "precio": round(precio_estimado, 0),
            "tiempo_espera": self.app.tiempo_espera,
            "factor_dinamico": factor_dinamico,
            "origen_nombre": self.ruta.origen,
            "destino_nombre": self.ruta.destino,
        }


def obtener_datos_ruta(origen: str, destino: str):
    """
    Busca una ruta en la base de datos que coincida con el origen y destino.
    Se admite tanto la dirección directa como inversa.
    """
    condicion_directa = Q(origen__iexact=origen, destino__iexact=destino)
    condicion_inversa = Q(origen__iexact=destino, destino__iexact=origen)
    return Ruta.objects.filter(condicion_directa | condicion_inversa).first()


def obtener_ubicaciones_disponibles():
    """
    Devuelve todas las ubicaciones disponibles (orígenes y destinos) registradas en la base de datos.
    """
    origenes = list(Ruta.objects.values_list('origen', flat=True))
    destinos = list(Ruta.objects.values_list('destino', flat=True))
    ubicaciones = set(origenes + destinos)
    return sorted(ubicaciones)

