import random
from decimal import Decimal
from .models import Ruta, CotizacionTraslado
from django.db.models import Q

class AppCotizadora:
    """
    Clase para simular la cotización de un viaje con una aplicación
    de transporte, basada en los parámetros de la aplicación.
    """
    def __init__(self, app_transporte):
        if not hasattr(app_transporte, 'tarifa_base') or not hasattr(app_transporte, 'costo_por_km'):
            raise TypeError("El objeto pasado debe ser una instancia válida de TransporteApp.")

        self.tarifa_base = app_transporte.tarifa_base
        self.costo_por_km = app_transporte.costo_por_km
        self.max_multiplicador = app_transporte.max_multiplicador

    def cotizar(self, distancia_km):
        if distancia_km is None or distancia_km <= 0:
            raise ValueError("La distancia debe ser positiva.")

        factor_float = random.uniform(1.0, float(self.max_multiplicador))
        factor_dinamico = Decimal(str(factor_float)).quantize(Decimal('0.01'))

        costo_variable = (distancia_km * self.costo_por_km) * factor_dinamico
        precio_total = self.tarifa_base + costo_variable
        precio_final = precio_total.quantize(Decimal('0.01'))

        tiempo_espera = random.randint(3, 12)

        return {
            'precio': precio_final,
            'factor_dinamico': factor_dinamico,
            'tiempo_espera': tiempo_espera
        }

    @staticmethod
    def crear_cotizacion(usuario, ruta, app_transporte):
        cotizador = AppCotizadora(app_transporte)
        datos = cotizador.cotizar(ruta.distancia_km)
        return CotizacionTraslado.objects.create(
            usuario=usuario,
            origen_nombre=ruta.origen,
            destino_nombre=ruta.destino,
            app_seleccionada=app_transporte,
            precio=datos['precio'],
            tiempo_espera=datos['tiempo_espera'],
            factor_dinamico=datos['factor_dinamico']
        )

def obtener_datos_ruta(origen: str, destino: str):
    condicion_directa = Q(origen__iexact=origen, destino__iexact=destino)
    condicion_inversa = Q(origen__iexact=destino, destino__iexact=origen)
    try:
        return Ruta.objects.filter(condicion_directa | condicion_inversa).first()
    except Exception as e:
        print(f"Error al buscar la ruta: {e}")
        return None

def obtener_ubicaciones_disponibles():
    origenes = Ruta.objects.values_list('origen', flat=True)
    destinos = Ruta.objects.values_list('destino', flat=True)
    ubicaciones = origenes.union(destinos)
    return sorted(ubicaciones)

