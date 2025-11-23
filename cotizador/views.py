from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from urllib.parse import urlencode
from decimal import Decimal
from .formularios import CotizacionForm, EditarCotizacionForm
from .models import TransporteApp, CotizacionTraslado
from .simulador import AppCotizadora, obtener_datos_ruta
from decimal import Decimal, InvalidOperation
from django.http import HttpResponseRedirect

class CotizacionView(LoginRequiredMixin, View):
    """
    Visualización del formulario de cotización (GET) y 
    generación de las cotizaciones (POST).
    """
    template_name = 'home.html'
    def _calcular_cotizacion(self, request, origen, destino): 
        """
        funcion para la validación del formulario 
        y cálculo de las cotizaciones para las tres apps.
        """
        form = CotizacionForm(data={'origen': origen, 'destino': destino})
        cotizaciones = []
        if form.is_valid():
            ruta_obj = obtener_datos_ruta(origen, destino)
            if ruta_obj:
                distancia_km = ruta_obj.distancia_km # la distancia es la base del calculo del tiempo de espera y precio
                todas_las_apps = TransporteApp.objects.all()
                for app in todas_las_apps:
                    try:
                        cotizadora = AppCotizadora(app)
                        resultado = cotizadora.cotizar(distancia_km) # Devuelve precio_estimado y tiempo_espera
                        cotizaciones.append({
                            'app_id': app.pk,
                            'app_nombre': app.nombre,
                            'app_logo': app.logo.url, 
                            'precio': resultado['precio'],
                            'tiempo_espera': resultado['tiempo_espera'],
                            'factor_dinamico': resultado['factor_dinamico'], 
                            'origen_nombre': origen,
                            'destino_nombre': destino,
                        })
                    except Exception as e:
                        print(f"Error al cotizar con {app.nombre}: {e}")
                        continue            
        return form, cotizaciones

    def get(self, request):
        """
        Visualización inicial del formulario (GET normal) 
        o la recarga con resultados (GET con parámetros desde la edición).
        """
        form = CotizacionForm()
        cotizaciones = None
        # 1. Verificar si es una edicion o creacion 
        origen_param = request.GET.get('origen')
        destino_param = request.GET.get('destino')
        if origen_param and destino_param:
            form, cotizaciones = self._calcular_cotizacion(request, origen_param, destino_param)
        return render(request, self.template_name, {
            'form': form,
            'cotizaciones': cotizaciones,
            'origen_seleccionado': origen_param,
            'destino_seleccionado': destino_param,
        })

    def post(self, request):
        origen = request.POST.get('origen')
        destino = request.POST.get('destino')
        form, cotizaciones = self._calcular_cotizacion(request, origen, destino)
        return render(request, self.template_name, {
            'form': form,
            'cotizaciones': cotizaciones,
            'origen_seleccionado': origen,
            'destino_seleccionado': destino,
        })

class RedireccionView(LoginRequiredMixin, View):
    def post(self, request, app_id):
        origen = request.POST.get('origen')
        destino = request.POST.get('destino')
        precio = request.POST.get('precio')
        tiempo = request.POST.get('tiempo_espera')
        factor = request.POST.get('factor_dinamico')

        app_seleccionada = get_object_or_404(TransporteApp, pk=app_id)

        try:
            CotizacionTraslado.objects.create(
                usuario=request.user,
                origen_nombre=origen,
                destino_nombre=destino,
                app_seleccionada=app_seleccionada,
                precio=Decimal(precio),
                tiempo_espera=int(tiempo),
                factor_dinamico=Decimal(factor),
            )
        except (TypeError, ValueError, InvalidOperation):
            # Si algo falla, redirige al home sin guardar
            return redirect('home')
        print("Redirigiendo a:", app_seleccionada.link_base)
        return HttpResponseRedirect(app_seleccionada.link_base)

class MisCotizacionesView(LoginRequiredMixin, ListView):
    """
    Muestra un listado de todas las solicitudes cotizacion de traslado 
    realizadas por usuario autenticado.
    """
    model = CotizacionTraslado
    template_name = 'mis_cotizaciones.html'
    context_object_name = 'cotizaciones'
    
    def get_queryset(self):
        return CotizacionTraslado.objects.filter(usuario=self.request.user).order_by('-fecha_creacion')
        # Equivale en mysql a SELECT *FROM cotizador_cotizaciontraslado WHERE usuario_id = [USER_ID_ACTUAL] ORDER BY fecha_creacion DESC;

class EditarCotizacionView(LoginRequiredMixin, UpdateView):
    model = CotizacionTraslado
    form_class = EditarCotizacionForm
    template_name = 'editar_cotizacion.html'
    success_url = reverse_lazy('mis_cotizaciones')

    def get_queryset(self):
        # Solo las cotizaciones creadas por el usuario actual
        return self.model.objects.filter(usuario=self.request.user)

    def form_valid(self, form):
        cotizacion = form.save(commit=False)

        # Recalcular SIEMPRE al editar (ya sea origen, destino o app)
        ruta_obj = obtener_datos_ruta(cotizacion.origen_nombre, cotizacion.destino_nombre)
        if ruta_obj:
            distancia_km = ruta_obj.distancia_km
            cotizadora = AppCotizadora(cotizacion.app_seleccionada)
            resultado = cotizadora.cotizar(distancia_km)
            cotizacion.precio = resultado['precio']
            cotizacion.tiempo_espera = resultado['tiempo_espera']
            cotizacion.factor_dinamico = resultado['factor_dinamico']

        cotizacion.usuario = self.request.user
        cotizacion.save()
        return super().form_valid(form)
        
class EliminarCotizacionView(LoginRequiredMixin, DeleteView):
    model = CotizacionTraslado
    template_name = 'confirmar_eliminar.html'
    success_url = reverse_lazy('mis_cotizaciones') 

    def get_queryset(self):
        return self.model.objects.filter(usuario=self.request.user)