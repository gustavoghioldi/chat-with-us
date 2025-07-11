from django.db.models.signals import post_save
from django.dispatch import receiver
from quota.models.token_ledger_model import TokenLedgerModel
from quota.models.tenant_quota_model import TenantQuotaModel
from quota.enums.transactions_type import TransactionType

@receiver(
    post_save,
    sender=TokenLedgerModel,
    dispatch_uid="post_save_token_ledger_model_signal",
)
def post_save_token_ledger_model_signal(sender, instance, **kwargs):
    """
    Si se genera recarga o reset, desbloquea el tenant.
    """
    if instance.transaction_type in [TransactionType.RECHARGE, TransactionType.RESET]:
        tenant_quota = TenantQuotaModel.objects.filter(tenant=instance.tenant).first()
        if tenant_quota and getattr(tenant_quota, "plan_exceeded", False):
            tenant_quota.plan_exceeded = False
            tenant_quota.save(update_fields=["plan_exceeded"])
            
