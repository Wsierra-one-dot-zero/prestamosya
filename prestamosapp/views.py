# views.py
from django.views.generic import ListView, CreateView, UpdateView, DetailView, View
from django.urls import reverse_lazy, reverse
from .models import Cliente, Prestamo, Cuota
from .forms import ClienteForm, PrestamoForm
from django.http import JsonResponse
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json

# --- CLIENTES ---
class ListaClientesView(ListView):
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
        return context

class CrearClienteView(CreateView):
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
class ListaPrestamosClienteView(ListView):
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

class CrearPrestamoView(CreateView):
    model = Prestamo
    form_class = PrestamoForm
    template_name = 'prestamos/lista.html'
    
    def form_valid(self, form):
        cliente = Cliente.objects.get(pk=self.kwargs['cliente_id'])
        form.instance.cliente = cliente
        response = super().form_valid(form)
        return response

    def get_success_url(self):
        return reverse('detalle_prestamo', kwargs={'pk': self.object.pk})

# --- CUOTAS ---
class DetallePrestamoView(DetailView):
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

class PagarCuotaView(UpdateView):
    model = Cuota
    fields = ['pagada', 'fecha_pago']
    template_name = 'cuotas/lista.html'
    
    def get_success_url(self):
        return reverse_lazy('detalle_prestamo', kwargs={
            'prestamo_id': self.kwargs['prestamo_id']
        })
    
@method_decorator(csrf_exempt, name='dispatch')
class PagarCuotaAjaxView(View):
    def post(self, request):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            try:
                data = json.loads(request.body)
                cuota = Cuota.objects.get(pk=data.get('cuota_id'))
                cuota.pagada = True
                cuota.fecha_pago = timezone.now().date()
                cuota.save()
                
                return JsonResponse({
                    'success': True,
                    'cuota_id': cuota.id,
                    'fecha_pago': cuota.fecha_pago.strftime("%d/%m/%Y")
                })
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'error': str(e)
                }, status=400)
        return JsonResponse({'success': False}, status=403)