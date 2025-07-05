from django.apps import AppConfig


class QuotaConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "quota"

    def ready(self):
        from quota import signals
        from quota.models import token_ledger_model, tenant_quota_model, token_plan_model