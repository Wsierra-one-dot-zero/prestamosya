from django.contrib import admin
from .models import Cliente, Prestamo, Cuota

# Register your models here.
admin.site.register(Cliente)
admin.site.register(Prestamo)
admin.site.register(Cuota)