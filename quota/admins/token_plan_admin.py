from django.contrib import admin
from quota.models.tenant_quota_model import TenantQuotaModel
from quota.models.token_plan_model import TokenPlanModel
from quota.models.token_ledger_model import TokenLedgerModel

@admin.register(TokenPlanModel)
class TokenPlanAdmin(admin.ModelAdmin):
    list_display = ("name", "total_amount", "description")
    search_fields = ("name", "description")
    ordering = ("name",)
