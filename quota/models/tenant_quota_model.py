from django.db import models
from django.conf import settings
from main.models import AppModel
from quota.models import TokenPlan
from tenants.models import TenantModel



class TenantQuota(AppModel):
    tenant = models.OneToOneField(
        TenantModel,
        on_delete=models.CASCADE,
        related_name='quota'
    )
    plan = models.ForeignKey(TokenPlan, on_delete=models.PROTECT)
    tokens_used = models.PositiveIntegerField(default=0)
    last_reset = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = "Tenant Quota"
        verbose_name_plural = "Tenant Quotas"

    def __str__(self):
        return f"{self.tenant} - {self.plan.name}"

    @property
    def tokens_left(self):
        return max(0, self.plan.monthly_token_limit - self.tokens_used)