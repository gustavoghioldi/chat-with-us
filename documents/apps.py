from django.apps import AppConfig


class DocumentsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "documents"

    def ready(self):
        """
        Importar signals cuando la aplicación está lista.
        Esto asegura que los signals estén correctamente registrados.
        """
        import documents.signals.receivers.handle_knowledge_change_recreate_receiver  # noqa
