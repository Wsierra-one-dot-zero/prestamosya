from django.views.generic import ListView, CreateView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from ..models import Cliente
from ..forms import ClienteForm, PrestamoForm, PrestamoDinamicoForm

class ListaClientesView(LoginRequiredMixin, ListView):
    model = Cliente
    template_name = 'clientes/lista.html'
    context_object_name = 'clientes'
    ordering = ['-fecha_registro']
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ClienteForm()
        context['form_prestamo'] = PrestamoForm()
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
