# urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from .views import home_views, login_views, cliente_views, cuota_views, prestamo_views


urlpatterns = [

    # Página de bienvenida
    path('', home_views.BienvenidaView.as_view(), name='home'),

    # Autenticación
    path('login/', login_views.CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='prestamos/auth/logout.html'), name='logout'),

    # Clientes
    path('clientes/', cliente_views.ListaClientesView.as_view(), name='lista_clientes'),
    path('clientes/nuevo/', cliente_views.CrearClienteView.as_view(), name='crear_cliente'),
    
    # Préstamos (anidados bajo cliente)
    path('clientes/<int:cliente_id>/prestamos/', prestamo_views.ListaPrestamosClienteView.as_view(), name='lista_prestamos_cliente'),
    path('clientes/<int:cliente_id>/prestamos/crear/', prestamo_views.CrearPrestamoView.as_view(), name='crear_prestamo'),
    path('clientes<int:cliente_id>/prestamo/dinamico/crear/', prestamo_views.CrearPrestamoDinamicoView.as_view(), name='crear_prestamo_dinamico'),
    path('prestamos/<int:pk>/',  prestamo_views.DetallePrestamoGenericoView.as_view(template_name='prestamos/detalle.html'), name='detalle_prestamo'),
    path('prestamos/dinamico/<int:pk>/',  prestamo_views.DetallePrestamoGenericoView.as_view(template_name='prestamos/detalle_PD.html'), name='detalle_prestamo_dinamico'),
    
    # Cuotas (anidadas bajo préstamo)
    path('prestamos/<int:prestamo_id>/cuotas/<int:pk>/pagar/', cuota_views.PagarCuotaView.as_view(), name='pagar_cuota'),
    path('pagar-cuota/', cuota_views.PagarCuotaAjaxView.as_view(), name='pagar_cuota_ajax'),
    path('cuotas/dinamico/<int:pk>/pagar/', cuota_views.PagarCuotaDinamicaView.as_view(), name='pagar_cuota_dinamica'),
]