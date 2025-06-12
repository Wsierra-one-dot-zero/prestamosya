from django.views.generic.base import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

class BienvenidaView(LoginRequiredMixin, TemplateView):
    template_name = 'home/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['caracteristicas'] = [
            {"icono": "fa-rocket", "titulo": "Rápido", "descripcion": "Solicitudes procesadas en 24h"},
            {"icono": "fa-percent", "titulo": "Bajas tasas", "descripcion": "Intereses competitivos"},
            {"icono": "fa-shield-alt", "titulo": "Seguro", "descripcion": "Datos 100% protegidos"},
        ]
        return context
