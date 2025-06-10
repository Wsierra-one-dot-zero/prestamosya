# urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [

    # Página de bienvenida
    path('', views.BienvenidaView.as_view(), name='home'),

    # Autenticación
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='prestamos/auth/logout.html'), name='logout'),

    # Clientes
    path('clientes/', views.ListaClientesView.as_view(), name='lista_clientes'),
    path('clientes/nuevo/', views.CrearClienteView.as_view(), name='crear_cliente'),
    
    # Préstamos (anidados bajo cliente)
    path('clientes/<int:cliente_id>/prestamos/', views.ListaPrestamosClienteView.as_view(), name='lista_prestamos_cliente'),
    path('clientes/<int:cliente_id>/prestamos/crear/', views.CrearPrestamoView.as_view(), name='crear_prestamo'),
    path('clientes<int:cliente_id>/prestamo/dinamico/crear/', views.CrearPrestamoDinamicoView.as_view(), name='crear_prestamo_dinamico'),
    path('prestamos/<int:pk>/',  views.DetallePrestamoView.as_view(),  name='detalle_prestamo'),
    
    # Cuotas (anidadas bajo préstamo)
    path('prestamos/<int:prestamo_id>/cuotas/<int:pk>/pagar/', views.PagarCuotaView.as_view(), name='pagar_cuota'),
    path('pagar-cuota/', views.PagarCuotaAjaxView.as_view(), name='pagar_cuota_ajax'),
    path('cuotas/dinamico/<int:pk>/pagar/', views.PagarCuotaDinamicaView.as_view(), name='pagar_cuota_dinamica'),
]