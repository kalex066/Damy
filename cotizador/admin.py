from django.contrib import admin
from .models import TransporteApp, CotizacionTraslado, Ruta

@admin.register(TransporteApp)
class TransporteAppAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio_base', 'costo_por_km', 'costo_por_min', 'factor_dinamico', 'tiempo_espera',)
    list_display_links = ('nombre',)
    ordering = ('nombre',)

@admin.register(Ruta)
class RutaAdmin(admin.ModelAdmin):
    list_display = ('origen', 'destino', 'distancia_km', 'tiempo_min')
    search_fields = ('origen', 'destino')
    list_filter = ('origen', 'destino')
    ordering = ('origen', 'destino')

@admin.register(CotizacionTraslado)
class CotizacionTrasladoAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'usuario',
        'get_origen',
        'get_destino',
        'app_seleccionada',
        'precio',
        'tiempo_espera',
        'factor_dinamico',
        'fecha_creacion',
    )
    list_display_links = ('id', 'usuario')
    ordering = ('-fecha_creacion',)

    def get_origen(self, obj):
        return obj.ruta.origen if obj.ruta else None
    get_origen.short_description = 'Origen'

    def get_destino(self, obj):
        return obj.ruta.destino if obj.ruta else None
    get_destino.short_description = 'Destino'
