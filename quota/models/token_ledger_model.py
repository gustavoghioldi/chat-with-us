from django.db import models
from main.models import AppModel
from quota.enums.transactions_direction import TransactionDirectionType
from tenants.models import TenantModel
from quota.enums.transactions_type import TransactionType


class TokenLedgerModel(AppModel):
    tenant = models.ForeignKey(
        TenantModel, on_delete=models.CASCADE, related_name="token_ledgers"
    )
    transaction_type = models.CharField(choices=TransactionType.choices)
    amount = models.IntegerField(
        help_text="Cantidad de tokens involucrados en la transaccion"
    )
    total_remaining = models.IntegerField(
        help_text="Balance restante despues de la operacion"
    )
    direction = models.CharField(
        choices=TransactionDirectionType.choices, max_length=3
    )
    metadata = models.JSONField(blank=True, null=True)

    class Meta:
        verbose_name = "Token Transaction Ledger"
        verbose_name_plural = "Token Transaction Ledgers"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.tenant} | {self.transaction_type} | {self.amount} | {self.created_at}"
