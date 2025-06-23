from django.apps import AppConfig


class KnowledgeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "knowledge"

    def ready(self):
        """
        Importar signals cuando la aplicación está lista.
        Esto asegura que los signals estén correctamente registrados.
        """
        # Signals existentes
        # Nuevo sistema centralizado de signals
        import knowledge.signals
        import knowledge.signals.receivers.document_update_receiver
        import knowledge.signals.receivers.knowledge_model_change_receiver
