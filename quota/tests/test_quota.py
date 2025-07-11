from unittest.mock import MagicMock
from django.test import TestCase
from tenants.models import TenantModel
from quota.models.token_plan_model import TokenPlanModel
from quota.models.tenant_quota_model import TenantQuotaModel
from quota.models.token_ledger_model import TokenLedgerModel
from quota.enums.transactions_type import TransactionType
from quota.enums.transactions_direction import TransactionDirectionType
from quota.enums.transaction_messages import SystemMessages
from quota.services.quota_service import QuotaService

class QuotaServiceTestCase(TestCase):
    def setUp(self):
        self.tenant = TenantModel.objects.create(name="Tenant1")
        self.plan = TokenPlanModel.objects.create(name="Plan", total_amount=100)
        self.quota = TenantQuotaModel.objects.create(tenant=self.tenant, plan=self.plan, tokens_used=0, plan_exceeded=False)

    def get_agent_mock(self, tokens=10, text="respuesta", session_id="session123"):
        agent = MagicMock()
        agent.send_message.return_value = (text, session_id)
        class DummyRunResponse:
            metrics = {"total_tokens": [tokens]}
        agent._AgentService__agent = MagicMock(run_response=DummyRunResponse())
        return agent

    def test_process_agent_request_consumes_tokens(self):
        agent = self.get_agent_mock(tokens=10)
        text, session_id = QuotaService.process_agent_request(agent, self.tenant, "hola", session_id=None)
        self.quota.refresh_from_db()
        self.assertEqual(text, "respuesta")
        self.assertEqual(session_id, "session123")
        self.assertEqual(self.quota.tokens_used, 10)
        # Ledger creado
        ledger = TokenLedgerModel.objects.filter(tenant=self.tenant).first()
        self.assertIsNotNone(ledger)
        self.assertEqual(ledger.amount, 10)
        self.assertEqual(ledger.transaction_type, TransactionType.CONSUME)

    def test_process_agent_request_blocks_when_exceeded(self):
        self.quota.tokens_used = 100
        self.quota.plan_exceeded = True
        self.quota.save()
        agent = self.get_agent_mock(tokens=5)
        text, session_id = QuotaService.process_agent_request(agent, self.tenant, "hola", session_id=None)
        self.assertEqual(text, SystemMessages.PLAN_EXCEEDED.value)
        self.assertTrue(self.quota.plan_exceeded)

    def test_process_agent_request_blocks_after_exceeding(self):
        self.quota.tokens_used = 95
        self.quota.plan_exceeded = False
        self.quota.save()
        agent = self.get_agent_mock(tokens=10)
        text, session_id = QuotaService.process_agent_request(agent, self.tenant, "hola", session_id=None)
        self.quota.refresh_from_db()
        self.assertTrue(self.quota.plan_exceeded)
        self.assertGreater(self.quota.tokens_used, self.plan.total_amount)

    def test_token_ledger_str(self):
        ledger = TokenLedgerModel.objects.create(
            tenant=self.tenant,
            transaction_type=TransactionType.CONSUME,
            amount=10,
            total_remaining=90,
            direction=TransactionDirectionType.OUT,
        )
        self.assertIn(self.tenant.name, str(ledger))
        self.assertIn("consume", str(ledger))

    def test_tenant_quota_str(self):
        self.assertEqual(str(self.quota), f"{self.tenant} - {self.plan.name}")

    def test_signal_unblocks_on_recharge(self):
        self.quota.plan_exceeded = True
        self.quota.save()
        TokenLedgerModel.objects.create(
            tenant=self.tenant,
            transaction_type=TransactionType.RECHARGE,
            amount=100,
            total_remaining=200,
            direction=TransactionDirectionType.IN,
        )
        self.quota.refresh_from_db()
        self.assertFalse(self.quota.plan_exceeded)