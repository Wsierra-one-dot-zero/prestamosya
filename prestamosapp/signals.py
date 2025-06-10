# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Prestamo, Cuota
from datetime import timedelta

@receiver(post_save, sender=Prestamo)
def generar_cuotas(sender, instance, created, **kwargs):
    # Solo generar cuotas para préstamos tradicionales
    if created and instance.estado == 'VIGENTE' and instance.tipo == 'TRADICIONAL':
        tasa_mensual = instance.tasa_interes_mensual / 100
        cuota_mensual = instance.calcular_cuota()
        saldo = instance.monto
        
        for numero in range(1, instance.numero_cuotas + 1):
            intereses = saldo * tasa_mensual
            amortizacion = cuota_mensual - intereses
            saldo -= amortizacion
            
            Cuota.objects.create(
                prestamo=instance,
                numero_cuota=numero,
                valor_cuota=cuota_mensual,
                intereses=intereses,
                amortizacion=amortizacion,
                saldo_pendiente=max(0, saldo),
                fecha_vencimiento=instance.fecha_creacion + timedelta(days=30*numero)
            )


@receiver(post_save, sender=Cuota)
def actualizar_estado_prestamo(sender, instance, **kwargs):
    instance.prestamo.actualizar_estado()