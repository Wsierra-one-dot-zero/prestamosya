from django.apps import AppConfig


class PrestamosappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'prestamosapp'

    def ready(self):
        import prestamosapp.signals  # Importa las señales