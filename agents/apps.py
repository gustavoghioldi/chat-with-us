from django.apps import AppConfig


class AgentsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "agents"

    def ready(self):
        """
        Método que se ejecuta cuando la app está lista.
        Importa los signals para que se registren automáticamente.
        """
        import agents.signals
