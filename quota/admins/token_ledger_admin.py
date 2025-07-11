from django.contrib import admin
from quota.models.tenant_quota_model import TenantQuotaModel
from quota.models.token_plan_model import TokenPlanModel
from quota.models.token_ledger_model import TokenLedgerModel


@admin.register(TokenLedgerModel)
class TokenLedgerAdmin(admin.ModelAdmin):
    list_display = ("tenant", "transaction_type", "amount", "total_remaining", "direction", "created_at")
    list_filter = ("transaction_type", "direction", "tenant")
    search_fields = ("tenant__name",)
    ordering = ("-created_at",)