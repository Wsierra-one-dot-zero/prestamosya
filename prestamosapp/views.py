# views.py
from django.views.generic import ListView, CreateView, UpdateView, DetailView, View
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy, reverse
from .models import Cliente, Prestamo, Cuota
from .forms import ClienteForm, PrestamoForm, PrestamoDinamicoForm
from django.http import JsonResponse
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import TemplateView
from datetime import timedelta
from decimal import Decimal
import json

# --- HOME ---
class BienvenidaView(LoginRequiredMixin, TemplateView):
    template_name = 'home/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Datos de ejemplo para la versión pública (puedes personalizar)
        context['caracteristicas'] = [
            {"icono": "fa-rocket", "titulo": "Rápido", "descripcion": "Solicitudes procesadas en 24h"},
            {"icono": "fa-percent", "titulo": "Bajas tasas", "descripcion": "Intereses competitivos"},
            {"icono": "fa-shield-alt", "titulo": "Seguro", "descripcion": "Datos 100% protegidos"}
        ]
            
        return context

# --- AUTENTICACIÓN ---
class CustomLoginView(LoginView):
    template_name = 'auth/login.html'
    redirect_authenticated_user = True  # Redirige si ya está autenticado


# --- CLIENTES ---
class ListaClientesView(LoginRequiredMixin, ListView):
    model = Cliente
    template_name = 'clientes/lista.html'
    context_object_name = 'clientes'
    ordering = ['-fecha_registro']  # Ordenar por más recientes primero
    paginate_by = 10  # Paginación de 10 clientes por página

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ClienteForm()  # Formulario en la misma vista
        return context
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_prestamo'] = PrestamoForm()  # Formulario para modal
        context['form_prestamo_dinamico'] = PrestamoDinamicoForm()
        return context

class CrearClienteView(LoginRequiredMixin, CreateView):
    model = Cliente
    fields = ['dni', 'nombre_completo', 'telefono', 'direccion']
    success_url = reverse_lazy('lista_clientes')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'cliente_id': self.object.id,
                'cliente_nombre': self.object.nombre_completo
            })
        return response
# --- PRÉSTAMOS ---
class ListaPrestamosClienteView(LoginRequiredMixin, ListView):
    model = Prestamo
    template_name = 'prestamos/lista.html'
    context_object_name = 'prestamos'

    def get_queryset(self):
        cliente_id = self.kwargs['cliente_id']
        return Prestamo.objects.filter(cliente_id=cliente_id).select_related('cliente')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cliente'] = Cliente.objects.get(pk=self.kwargs['cliente_id'])
        return context

class CrearPrestamoView(LoginRequiredMixin, CreateView):
    model = Prestamo
    form_class = PrestamoForm
    template_name = 'prestamos/lista.html'
    
    def form_valid(self, form):
        cliente = Cliente.objects.get(pk=self.kwargs['cliente_id'])
        form.instance.cliente = cliente
        form.instance.tipo = 'TRADICIONAL'
        response = super().form_valid(form)
        return response

    def get_success_url(self):
        return reverse('detalle_prestamo', kwargs={'pk': self.object.pk})
    
class CrearPrestamoDinamicoView(LoginRequiredMixin, CreateView):
    model = Prestamo
    form_class = PrestamoDinamicoForm
    template_name = 'prestamos/lista.html'

    def form_valid(self, form):
        cliente = Cliente.objects.get(pk=self.kwargs['cliente_id'])
        form.instance.cliente = cliente
        form.instance.tipo = 'DINAMICO'
        form.instance.numero_cuotas = 1  # Dinámico: una sola cuota inicial
        response = super().form_valid(form)

        fecha_vencimiento = timezone.now().date() + timedelta(days=30)
        
        # Crear única cuota inicial correctamente
        Cuota.objects.create(
            prestamo=self.object,
            numero_cuota=1,
            valor_cuota=form.instance.monto,
            intereses=form.instance.monto * (form.instance.tasa_interes_mensual / 100),
            amortizacion=0,  # Inicialmente no hay amortización
            saldo_pendiente=form.instance.monto,
            fecha_vencimiento=fecha_vencimiento
        )
        return response

    def get_success_url(self):
        return reverse('detalle_prestamo', kwargs={'pk': self.object.pk})

# --- CUOTAS ---
class DetallePrestamoView(LoginRequiredMixin, DetailView):
    model = Prestamo
    template_name = 'prestamos/detalle.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        prestamo = self.object
        context['cuotas'] = prestamo.cuotas.all().order_by('numero_cuota')
        return context
    
    def post(self, request, *args, **kwargs):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            cuota_id = request.POST.get('cuota_id')
            try:
                cuota = Cuota.objects.get(pk=cuota_id)
                cuota.pagada = True
                cuota.fecha_pago = timezone.now().date()
                cuota.save()
                return JsonResponse({
                    'success': True,
                    'cuota_id': cuota_id,
                    'fecha_pago': cuota.fecha_pago.strftime("%d/%m/%Y")
                })
            except Cuota.DoesNotExist:
                return JsonResponse({'success': False}, status=404)
        return super().get(request, *args, **kwargs)

class PagarCuotaView(LoginRequiredMixin, UpdateView):
    model = Cuota
    fields = ['pagada', 'fecha_pago']
    template_name = 'cuotas/lista.html'
    
    def get_success_url(self):
        return reverse_lazy('detalle_prestamo', kwargs={
            'prestamo_id': self.kwargs['prestamo_id']
        })
    
@method_decorator(csrf_exempt, name='dispatch')
class PagarCuotaAjaxView(LoginRequiredMixin, View):
    def post(self, request):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            try:
                data = json.loads(request.body)
                cuota = Cuota.objects.get(pk=data.get('cuota_id'))
                cuota.pagada = True
                cuota.fecha_pago = timezone.now().date()
                cuota.save()

                # Actualizar estado del préstamo
                prestamo = cuota.prestamo
                prestamo.actualizar_estado()
                
                return JsonResponse({
                    'success': True,
                    'cuota_id': cuota.id,
                    'fecha_pago': cuota.fecha_pago.strftime("%d/%m/%Y"),
                    'prestamo_pagado': prestamo.estado == 'PAGADO'
                })
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'error': str(e)
                }, status=400)
        return JsonResponse({'success': False}, status=403)
    
class PagarCuotaDinamicaView(UpdateView):
    model = Cuota
    fields = []
    template_name = 'cuotas/pagar_cuota_dinamica.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cuota = self.object
        # Convertir explícitamente a Decimal
        context['interes_actual'] = cuota.saldo_pendiente * (Decimal(str(cuota.prestamo.tasa_interes_mensual)) / Decimal('100'))
        return context

    def form_valid(self, form):
        cuota = self.object
        try:
            # Convertir el input a Decimal
            abono_capital = Decimal(str(self.request.POST.get('abono_capital', 0)))
            interes = cuota.saldo_pendiente * (Decimal(str(cuota.prestamo.tasa_interes_mensual)) / Decimal('100'))
            
            # Validar que el abono no exceda el saldo
            if abono_capital > cuota.saldo_pendiente:
                form.add_error(None, "El abono no puede ser mayor al saldo pendiente")
                return self.form_invalid(form)
            
            # Actualizar la cuota actual
            cuota.pagada = True
            cuota.fecha_pago = timezone.now().date()
            cuota.intereses = interes
            cuota.amortizacion = abono_capital
            cuota.save()
            
            # Crear nueva cuota si queda saldo
            nuevo_saldo = cuota.saldo_pendiente - abono_capital
            if nuevo_saldo > 0:
                nueva_cuota_numero = Cuota.objects.filter(
                    prestamo=cuota.prestamo
                ).count() + 1
                
                Cuota.objects.create(
                    prestamo=cuota.prestamo,
                    numero_cuota=nueva_cuota_numero,
                    valor_cuota=nuevo_saldo,
                    intereses=Decimal('0'),  # Se calculará al pagar
                    amortizacion=Decimal('0'),
                    saldo_pendiente=nuevo_saldo,
                    fecha_vencimiento=cuota.fecha_vencimiento + timedelta(days=30)
                )
            
            return super().form_valid(form)
        
        except (TypeError, ValueError) as e:
            form.add_error(None, f"Error en los datos: {str(e)}")
            return self.form_invalid(form)
        
    def get_success_url(self):
        return reverse('detalle_prestamo', kwargs={'pk': self.object.prestamo.id})