from django.db import models
from django.conf import settings
from main.models import AppModel
from quota.models import TokenPlanModel
from tenants.models import TenantModel


class TenantQuotaModel(AppModel):
    tenant = models.OneToOneField(
        TenantModel, on_delete=models.CASCADE, related_name="tenant-quota"
    )
    plan = models.ForeignKey(TokenPlanModel, on_delete=models.PROTECT)
    tokens_used = models.PositiveIntegerField(default=0)
    last_reset = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = "Tenant Quota"
        verbose_name_plural = "Tenant Quotas"


    def __str__(self):
        return f"{self.tenant} - {self.plan.name}"

    @property
    def monthly_tokens_left(self):
        """
        Devuelve la cantidad de tokens mensuales restantes para el tenant según el plan asignado.
        Si el plan no tiene límite mensual configurado, retorna None.
        El cálculo se realiza restando los tokens usados del límite mensual definido en el plan.
        """
        if (
            hasattr(self.plan, "monthly_token_limit")
            and self.plan.monthly_token_limit is not None
        ):
            return max(0, self.plan.monthly_token_limit - self.tokens_used)
        return None

    @property
    def daily_tokens_left(self):
        """
        Devuelve la cantidad de tokens diarios restantes para el tenant según el plan asignado.
        Si el plan no tiene límite diario configurado, retorna None.
        El cálculo se realiza restando los tokens usados del límite diario definido en el plan.
        """
        if (
            hasattr(self.plan, "daily_token_limit")
            and self.plan.daily_token_limit is not None
        ):
            return max(0, self.plan.daily_token_limit - self.tokens_used)
        return None