from django.contrib.auth.models import User
from django.utils import timezone
from django.db import models
from decimal import Decimal

class PerfilUsuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telefono = models.CharField(max_length=15)
    direccion = models.TextField()

class Cliente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)  # Opcional: si el cliente es un usuario registrado
    dni = models.CharField(max_length=20, unique=True, verbose_name="DNI/Cédula")
    nombre_completo = models.CharField(max_length=100)
    telefono = models.CharField(max_length=15)
    direccion = models.TextField()
    fecha_registro = models.DateField(auto_now_add=True)
    estado = models.BooleanField(default=True, verbose_name="Activo")

    def __str__(self):
        return f"{self.nombre_completo} (DNI: {self.dni})"

class Prestamo(models.Model):
    ESTADOS = (
        ('VIGENTE', 'Vigente'),
        ('PAGADO', 'Pagado'),
        ('MORA', 'En mora'),
    )

    TIPO_CHOICES = [
        ('TRADICIONAL', 'Tradicional (Cuotas fijas)'),
        ('DINAMICO', 'Dinámico (Abono a capital)'),
    ]
    
    cliente = models.ForeignKey('Cliente', on_delete=models.CASCADE, related_name='prestamos')
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    tasa_interes_mensual = models.DecimalField(max_digits=5, decimal_places=2)
    numero_cuotas = models.PositiveIntegerField()
    fecha_creacion = models.DateField(auto_now_add=True)
    estado = models.CharField(max_length=10, choices=ESTADOS, default='VIGENTE')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='TRADICIONAL')

    def __str__(self):
        return f"Préstamo #{self.id} - {self.cliente.nombre_completo}"

    def calcular_cuota(self):
        i = self.tasa_interes_mensual / 100
        return (self.monto * i * (1 + i)**self.numero_cuotas) / ((1 + i)**self.numero_cuotas - 1)

    def actualizar_estado(self):
        """Actualiza el estado del préstamo basado en las cuotas"""
        cuotas = self.cuotas.all()
        if cuotas.count() > 0 and all(cuota.pagada for cuota in cuotas):
            self.estado = 'PAGADO'
            self.save()


class Cuota(models.Model):
    prestamo = models.ForeignKey('Prestamo', on_delete=models.CASCADE, related_name='cuotas')
    numero_cuota = models.PositiveIntegerField()
    valor_cuota = models.DecimalField(max_digits=10, decimal_places=2)
    intereses = models.DecimalField(max_digits=10, decimal_places=2)
    amortizacion = models.DecimalField(max_digits=10, decimal_places=2)
    saldo_pendiente = models.DecimalField(max_digits=10, decimal_places=2)
    pago_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True) # Total pagado por la cuota para prestamos dinamicos
    fecha_pago = models.DateField(null=True, blank=True)  # Se llena al pagar
    pagada = models.BooleanField(default=False)
    fecha_vencimiento = models.DateField()  # Nuevo campo para gestión de mora

    class Meta:
        ordering = ['numero_cuota']
        unique_together = ['prestamo', 'numero_cuota']  # Evita duplicados

    def __str__(self):
        return f"Cuota {self.numero_cuota} - Préstamo #{self.prestamo.id}"

    def pagar(self):
        self.pagada = True
        self.fecha_pago = timezone.now().date()
        self.save()
        return self
    
    def calcular_interes(self):
        """Método seguro para calcular intereses"""
        if not hasattr(self, '_interes_calculado'):
            tasa = Decimal(str(self.prestamo.tasa_interes_mensual)) / Decimal('100')
            self._interes_calculado = self.saldo_pendiente * tasa
        return self._interes_calculado