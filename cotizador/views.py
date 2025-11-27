from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, UpdateView, DeleteView
from django.urls import reverse_lazy
from decimal import Decimal, InvalidOperation
from django.http import HttpResponseRedirect
from .formularios import CotizacionForm, EditarCotizacionForm
from .models import TransporteApp, CotizacionTraslado, Ruta
from .simulador import AppCotizadora, obtener_datos_ruta


class CotizacionView(LoginRequiredMixin, View):
    """
    Vista principal del cotizador.
    Permite al usuario ingresar origen y destino,
    y calcula cotizaciones en todas las apps de transporte disponibles.
    """
    template_name = 'home.html'

    def _calcular_cotizacion(self, request, origen, destino):
        """
        Método auxiliar que recibe origen y destino,
        valida el formulario y genera cotizaciones para cada app.
        """
        form = CotizacionForm(data={'origen': origen, 'destino': destino})
        cotizaciones = []

        if form.is_valid():
            ruta_obj = obtener_datos_ruta(origen, destino)
            if ruta_obj:
                todas_las_apps = TransporteApp.objects.all()
                for app in todas_las_apps:
                    try:
                        cotizadora = AppCotizadora(app, ruta_obj)
                        resultado = cotizadora.calcular_cotizacion()
                        cotizaciones.append({
                            'app_id': app.pk,
                            'app_nombre': app.nombre,
                            'app_logo': app.logo.url,
                            'precio': resultado['precio'],
                            'tiempo_espera': resultado['tiempo_espera'],
                            'factor_dinamico': resultado['factor_dinamico'],
                            'origen_nombre': ruta_obj.origen,
                            'destino_nombre': ruta_obj.destino,
                        })
                    except Exception as e:
                        # Si alguna app falla, se ignora y se continúa con las demás
                        print(f"Error al cotizar con {app.nombre}: {e}")
                        continue
        return form, cotizaciones

    def get(self, request):
        """
        GET: siempre muestra el formulario vacío al cargar la página.
        No abre modal automáticamente.
        """
        form = CotizacionForm()
        rutas = Ruta.objects.all()

        return render(request, self.template_name, {
            'form': form,
            'cotizaciones': None,            # no mostrar resultados
            'origen_seleccionado': None,     # no rellenar origen
            'destino_seleccionado': None,    # no rellenar destino
            'rutas': rutas,
            'mostrar_modal': False           # <- asegura que el modal no se abra al volver
        })

    def post(self, request):
        """
        POST: recibe origen y destino desde el formulario y calcula cotizaciones.
        Abre modal automáticamente para mostrar resultados.
        """
        origen = request.POST.get('origen')
        destino = request.POST.get('destino')
        form, cotizaciones = self._calcular_cotizacion(request, origen, destino)

        return render(request, self.template_name, {
            'form': form,
            'cotizaciones': cotizaciones,
            'origen_seleccionado': origen,
            'destino_seleccionado': destino,
            'mostrar_modal': True            # <- abre modal solo tras cotizar
        })


class RedireccionView(LoginRequiredMixin, View):
    """
    Guarda la cotización seleccionada y redirige al usuario
    a la página externa de la app de transporte.
    """
    def post(self, request, app_id):
        origen = request.POST.get('origen')
        destino = request.POST.get('destino')
        precio = request.POST.get('precio')
        tiempo = request.POST.get('tiempo_espera')
        factor = request.POST.get('factor_dinamico')

        # Buscar la app seleccionada (equivale a SELECT * FROM transporte_app WHERE id = app_id LIMIT 1)
        app_seleccionada = get_object_or_404(TransporteApp, pk=app_id)
        ruta_obj = obtener_datos_ruta(origen, destino)

        try:
            CotizacionTraslado.objects.create(
                usuario=request.user,
                ruta=ruta_obj,
                app_seleccionada=app_seleccionada,
                precio=Decimal(precio),
                tiempo_espera=int(tiempo),
                factor_dinamico=Decimal(factor) if factor else Decimal("1.0"),
            )
        except (TypeError, ValueError, InvalidOperation):
            # Si algo falla al guardar, se redirige al home
            return redirect('home')

        # Redirigir a la URL externa de la app
        return HttpResponseRedirect(app_seleccionada.link_base)


class MisCotizacionesView(LoginRequiredMixin, ListView):
    """
    Muestra un listado de todas las cotizaciones realizadas por el usuario autenticado.
    """
    model = CotizacionTraslado
    template_name = 'mis_cotizaciones.html'
    context_object_name = 'cotizaciones'

    def get_queryset(self):
        # Equivale a: SELECT * FROM cotizador_cotizaciontraslado WHERE usuario_id = [USER_ID] ORDER BY fecha_creacion DESC
        return CotizacionTraslado.objects.filter(usuario=self.request.user).order_by('-fecha_creacion')


class EditarCotizacionView(LoginRequiredMixin, UpdateView):
    """
    Permite editar una cotización existente.
    Si se cambia origen/destino, se elimina la cotización original y se generan nuevas.
    Si se cambia solo la app, se recalculan los valores.
    """
    model = CotizacionTraslado
    form_class = EditarCotizacionForm
    template_name = 'editar_cotizacion.html'
    success_url = reverse_lazy('mis_cotizaciones')

    def form_valid(self, form):
        cotizacion = form.instance

        # Caso 1: el usuario edita origen o destino
        if 'origen' in form.changed_data or 'destino' in form.changed_data:
            origen = form.cleaned_data['origen']
            destino = form.cleaned_data['destino']

            # Guardar datos antes de borrar
            usuario = cotizacion.usuario
            distancia = cotizacion.ruta.distancia_km if cotizacion.ruta else 0
            tiempo = cotizacion.ruta.tiempo_min if cotizacion.ruta else 0

            # Eliminar la cotización original
            cotizacion.delete()

            # Crear/obtener nueva ruta
            ruta, _ = Ruta.objects.get_or_create(
                origen=origen,
                destino=destino,
                defaults={
                    'distancia_km': distancia,
                    'tiempo_min': tiempo,
                    'creado_por': usuario
                }
            )

            # Generar nuevas cotizaciones para todas las apps
            cotizaciones = []
            for app in TransporteApp.objects.all():
                cotizador = AppCotizadora(app, ruta)
                datos = cotizador.calcular_cotizacion()
                cotizaciones.append({
                    'app_id': app.id,
                    'app_nombre': app.nombre,
                    'app_logo': app.logo.url,
                    'precio': datos['precio'],
                    'tiempo_espera': datos['tiempo_espera'],
                    'factor_dinamico': datos['factor_dinamico'],
                    'origen_nombre': origen,
                    'destino_nombre': destino,
                })

            # Mostrar modal con nuevas cotizaciones
            return self.render_to_response(
                self.get_context_data(
                    form=form,
                    recotizar=True,
                    cotizaciones=cotizaciones,
                    mostrar_modal=True   # <- abre modal solo tras recotizar
                )
            )

        # Caso 2: el usuario solo cambia la app seleccionada
        elif 'app_seleccionada' in form.changed_data and cotizacion.ruta:
            cotizador = AppCotizadora(cotizacion.app_seleccionada, cotizacion.ruta)
            datos = cotizador.calcular_cotizacion()
            cotizacion.precio = datos['precio']
            cotizacion.tiempo_espera = datos['tiempo_espera']
            cotizacion.factor_dinamico = datos['factor_dinamico']
            cotizacion.save()

        return super().form_valid(form)

    def get(self, request, *args, **kwargs):
        """
        GET: al volver desde la app externa, no abrir modal.
        """
        response = super().get(request, *args, **kwargs)
        # Forzar que el modal no se abra automáticamente
        response.context_data['mostrar_modal'] = False
        return response


class EliminarCotizacionView(LoginRequiredMixin, DeleteView):
    """
    Permite eliminar una cotización del usuario autenticado.
    """
    model = CotizacionTraslado
    template_name = 'confirmar_eliminar.html'
    success_url = reverse_lazy('mis_cotizaciones')

    def get_queryset(self):
        # Solo permite eliminar cotizaciones del usuario actual
        return self.model.objects.filter(usuario=self.request.user)

