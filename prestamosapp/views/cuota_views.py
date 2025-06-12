from django.views.generic import UpdateView, View
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from prestamosapp.models import Cuota
import json
from decimal import Decimal
from datetime import timedelta

# --- CUOTAS ---

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
            cuota.pago_total = abono_capital + interes
            cuota.save()
            
            # Crear nueva cuota si queda saldo
            nuevo_saldo = cuota.saldo_pendiente - abono_capital
            if nuevo_saldo > 0:
                nueva_cuota_numero = Cuota.objects.filter(
                    prestamo=cuota.prestamo
                ).count() + 1

                interes = nuevo_saldo * (Decimal(str(cuota.prestamo.tasa_interes_mensual)) / Decimal('100'))
                
                Cuota.objects.create(
                    prestamo=cuota.prestamo,
                    numero_cuota=nueva_cuota_numero,
                    valor_cuota=nuevo_saldo + interes,  # Valor de la nueva cuota
                    intereses=interes,  # Se calculará al pagar
                    amortizacion=Decimal('0'),
                    saldo_pendiente=nuevo_saldo,
                    pago_total=Decimal('0'),
                    fecha_vencimiento=cuota.fecha_vencimiento + timedelta(days=30)
                )
            
            return super().form_valid(form)
        
        except (TypeError, ValueError) as e:
            form.add_error(None, f"Error en los datos: {str(e)}")
            return self.form_invalid(form)
        
    def get_success_url(self):
        return reverse('detalle_prestamo_dinamico', kwargs={'pk': self.object.prestamo.id})