# forms.py
from django import forms
from .models import Cliente, Prestamo

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['dni', 'nombre_completo', 'telefono', 'direccion']
        widgets = {
            'direccion': forms.Textarea(attrs={'rows': 3}),
        }

class PrestamoForm(forms.ModelForm):
    class Meta:
        model = Prestamo
        fields = ['monto', 'tasa_interes_mensual', 'numero_cuotas']
        widgets = {
            'monto': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'tasa_interes_mensual': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'numero_cuotas': forms.NumberInput(attrs={
                'class': 'form-control'
            }),
        }
        labels = {
            'tasa_interes_mensual': 'Tasa de interés mensual (%)',
            'numero_cuotas': 'Número de cuotas'
        }