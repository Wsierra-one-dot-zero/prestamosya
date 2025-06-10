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

# forms.py

class PrestamoForm(forms.ModelForm):  # Tradicional
    class Meta:
        model = Prestamo
        fields = ['monto', 'numero_cuotas', 'tasa_interes_mensual']  # los campos que uses para tradicional
        widgets = {
            'monto': forms.NumberInput(attrs={'class': 'form-control'}),
            'numero_cuotas': forms.NumberInput(attrs={'class': 'form-control'}),
            'tasa_interes_mensual': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class PrestamoDinamicoForm(forms.ModelForm):  # Dinámico
    class Meta:
        model = Prestamo
        fields = ['monto', 'tasa_interes_mensual']  # Solo estos para dinámico
        widgets = {
            'monto': forms.NumberInput(attrs={'class': 'form-control'}),
            'tasa_interes_mensual': forms.NumberInput(attrs={'class': 'form-control'}),
        }
