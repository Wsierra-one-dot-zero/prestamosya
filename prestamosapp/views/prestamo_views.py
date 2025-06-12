from datetime import timedelta
from django.http import JsonResponse
from django.urls import reverse
from django.utils import timezone
from django.views.generic import ListView, CreateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from ..models import Cliente, Prestamo, Cuota
from ..forms import PrestamoForm, PrestamoDinamicoForm


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
            valor_cuota=form.instance.monto + (form.instance.monto * (form.instance.tasa_interes_mensual / 100)),
            intereses=form.instance.monto * (form.instance.tasa_interes_mensual / 100),
            amortizacion=0,  # Inicialmente no hay amortización
            pago_total=0,  # Inicialmente no hay pago total
            saldo_pendiente=form.instance.monto,
            fecha_vencimiento=fecha_vencimiento
        )
        return response

    def get_success_url(self):
        return reverse('detalle_prestamo_dinamico', kwargs={'pk': self.object.pk})
    
class DetallePrestamoGenericoView(LoginRequiredMixin, DetailView):
    model = Prestamo

    def get_template_names(self):
        return [self.template_name or 'prestamos/detalle.html']

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