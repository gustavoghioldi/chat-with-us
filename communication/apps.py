from django.apps import AppConfig


class CommunicationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "communication"

    def ready(self):
        # Import the admin modules to ensure they are registered
        import communication.admins.telegram_communication_admin  # noqa: F401
        import communication.models.telegram.telegram_chat_model  # noqa: F401
        import communication.models.telegram.telegram_communication_model  # noqa: F401

        # Import other admin modules if they exist
        # import communication.admins.other_admin_module  # Uncomment if you have other admin modules
