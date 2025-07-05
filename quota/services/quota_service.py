from quota.models.tenant_quota_model import TenantQuotaModel
from quota.models.token_ledger_model import TokenLedgerModel
from quota.enums.transactions_type import TransactionType
from quota.enums.transactions_direction import TransactionDirectionType

class QuotaService:
    @staticmethod
    def process_agent_request(agent, tenant, prompt):
        """
        Procesa una solicitud de agente verificando y actualizando la cuota de tokens mensual del tenant.
        Si el tenant excede la cuota con este request, se entrega la respuesta pero se bloquean futuros requests.
        Registra cada consumo en el ledger de transacciones.
        """
        try:
            tenant_quota = TenantQuotaModel.objects.select_related("plan").get(tenant=tenant)
        except TenantQuotaModel.DoesNotExist:
            raise Exception("No quota plan assigned to this tenant.")

        plan_limit = tenant_quota.plan.total_amount
        run_response = agent.run(prompt)
        metrics = getattr(run_response, "metrics", {})
        tokens_used = metrics.get("total_tokens", 0)

        # Actualizo tokens
        tenant_quota.tokens_used += tokens_used
        tenant_quota.save(update_fields=["tokens_used"])

        #TODO pasar a algun servicio
        TokenLedgerModel.objects.create(
            tenant=tenant,
            transaction_type=TransactionType.CONSUME,
            total_amount=tokens_used,
            total_remaining=plan_limit - tenant_quota.tokens_used if plan_limit is not None else None,
            direction=TransactionDirectionType.OUT,
            reason="Agent request"
        )

        if plan_limit is not None and tenant_quota.tokens_used > plan_limit:
            #TODO pensar a ver que onda como flaggear al tenant
            pass

        return run_response