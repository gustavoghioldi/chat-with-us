from django.contrib import admin
from quota.models.tenant_quota_model import TenantQuotaModel

@admin.register(TenantQuotaModel)
class TenantQuotaAdmin(admin.ModelAdmin):
    list_display = ("tenant", "plan", "tokens_used", "last_reset", "monthly_tokens_left")
    list_filter = ("plan", "last_reset")
    search_fields = ("tenant__name",)
    ordering = ("-created_at",)
