from django.db import models
from django.conf import settings
from main.models import AppModel


class TokenPlanModel(AppModel):
    name = models.CharField(max_length=50, unique=True)
    monthly_token_limit = models.PositiveIntegerField(null=True, blank=True)
    daily_token_limit = models.PositiveIntegerField(null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    


    class Meta:
        verbose_name = "Token Plan"
        verbose_name_plural = "Token Plans"

    def __str__(self):
        return self.name
