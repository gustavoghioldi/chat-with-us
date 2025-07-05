from django.contrib import admin
from quota.models.tenant_quota_model import TenantQuotaModel

@admin.register(TenantQuotaModel)
class TenantQuotaAdmin(admin.ModelAdmin):
    list_display = ("tenant", "plan", "tokens_used", "last_reset", "monthly_tokens_left")
    list_filter = ("plan", "last_reset")
    search_fields = ("tenant__name",)
    readonly_fields = ("tokens_used", "last_reset", "created_at", "updated_at")
    ordering = ("-created_at",)
    autocomplete_fields = ("tenant", "plan")