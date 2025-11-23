from django.urls import path
from .views import CotizacionView, RedireccionView, MisCotizacionesView, EditarCotizacionView, EliminarCotizacionView

urlpatterns = [
    path('', CotizacionView.as_view(), name='home'),
    path('redireccion/<int:app_id>/', RedireccionView.as_view(), name='redireccion'),
    path('mis_cotizaciones/', MisCotizacionesView.as_view(), name='mis_cotizaciones'),
    path('cotizacion/editar/<int:pk>/', EditarCotizacionView.as_view(), name='editar_cotizacion'),
    path('cotizacion/eliminar/<int:pk>/', EliminarCotizacionView.as_view(), name='eliminar_cotizacion'),
]

