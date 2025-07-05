from django.apps import AppConfig


class QuotaConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "quota"

    def ready(self):
        from quota import signals
        from models import TenantQuota, TokenPlan