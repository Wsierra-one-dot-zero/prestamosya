# urls.py
from django.urls import path
from . import views

urlpatterns = [

    # Página de bienvenida
    path('', views.BienvenidaView.as_view(), name='home'),

    # Clientes
    path('clientes/', views.ListaClientesView.as_view(), name='lista_clientes'),
    path('clientes/nuevo/', views.CrearClienteView.as_view(), name='crear_cliente'),
    
    # Préstamos (anidados bajo cliente)
    path('clientes/<int:cliente_id>/prestamos/', views.ListaPrestamosClienteView.as_view(), name='lista_prestamos_cliente'),
    path('clientes/<int:cliente_id>/prestamos/crear/', views.CrearPrestamoView.as_view(), name='crear_prestamo'),
    path('prestamos/<int:pk>/',  views.DetallePrestamoView.as_view(),  name='detalle_prestamo'),
    
    # Cuotas (anidadas bajo préstamo)
    path('prestamos/<int:prestamo_id>/cuotas/<int:pk>/pagar/', views.PagarCuotaView.as_view(), name='pagar_cuota'),
    path('pagar-cuota/', views.PagarCuotaAjaxView.as_view(), name='pagar_cuota_ajax'),
]