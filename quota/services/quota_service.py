from quota.models.tenant_quota_model import TenantQuotaModel
from quota.models.token_ledger_model import TokenLedgerModel
from quota.enums.transactions_type import TransactionType
from quota.enums.transactions_direction import TransactionDirectionType

class QuotaService:
    @staticmethod
    def process_agent_request(agent, tenant, prompt, session_id=None):
        """
        Procesa una solicitud de agente verificando y actualizando la cuota de tokens mensual del tenant.
        Si el tenant excede la cuota con este request, se entrega la respuesta pero se bloquean futuros requests.
        Registra cada consumo en el ledger de transacciones.
        Devuelve el texto de respuesta y el session_id.
        """
        try:
            tenant_quota = TenantQuotaModel.objects.select_related("plan").get(tenant=tenant)
        except TenantQuotaModel.DoesNotExist:
            raise Exception("No quota plan assigned to this tenant.")

        plan_limit = tenant_quota.plan.total_amount

        # Ejecutar el mensaje y obtener la respuesta y session_id
        text, response_session_id = agent.send_message(prompt, session_id)

        # Obtener tokens usados (ajusta según tu implementación real)
        metrics = getattr(agent._AgentService__agent, "run_response", None)
        if metrics and hasattr(metrics, "metrics"):
            total_tokens = metrics.metrics.get("total_tokens", [0])
            tokens_used = total_tokens[0] if isinstance(total_tokens, list) and total_tokens else 0
        else:
            tokens_used = 0
        
        tenant_quota.tokens_used += tokens_used     
        tenant_quota.save(update_fields=["tokens_used"])

        TokenLedgerModel.objects.create(
            tenant=tenant,
            transaction_type=TransactionType.CONSUME,
            amount=tokens_used,
            total_remaining=plan_limit - tenant_quota.tokens_used if plan_limit is not None else None,
            direction=TransactionDirectionType.OUT,
        )

        if plan_limit is not None and tenant_quota.tokens_used > plan_limit:
            #TODO pensar a ver que onda como flaggear al tenant
            pass

        return text, response_session_id