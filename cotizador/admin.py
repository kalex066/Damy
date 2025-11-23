from django.contrib import admin
from .models import TransporteApp, CotizacionTraslado, Ruta

@admin.register(TransporteApp)
class TransporteAppAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tarifa_base', 'costo_por_km', 'max_multiplicador')
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
        'usuario', 'origen_nombre', 'destino_nombre',
        'app_seleccionada', 'precio', 'factor_dinamico',
        'tiempo_espera', 'fecha_creacion'
    )
    list_filter = ('fecha_creacion', 'app_seleccionada')
    search_fields = ('usuario__username', 'origen_nombre', 'destino_nombre') 
    readonly_fields = ('precio', 'fecha_creacion')
    date_hierarchy = 'fecha_creacion'
    ordering = ('-fecha_creacion',)
