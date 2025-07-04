import json
import time
from unittest.mock import MagicMock, patch

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from analysis.models.sentiment_agents_model import SentimentAgentModel
from analysis.services import sentimentChatScript
from tenants.models import TenantModel


class ChatAnalysisViewTestCase(TestCase):
    """Test case para ChatAnalysisView"""

    def setUp(self):
        """Configuración inicial para cada test"""
        self.client = APIClient()

        # Crear tenant de prueba
        self.tenant = TenantModel.objects.create(
            name="Test Tenant",
            description="Tenant de prueba para tests",
            model="ollama",
        )

        # Crear agente de sentimiento de prueba
        self.sentiment_agent = SentimentAgentModel.objects.create(
            name="test_analyzer",
            description="Analizador de prueba",
            positive_tokens="excelente, bueno, fantástico",
            negative_tokens="malo, terrible, horrible",
            neutral_tokens="normal, regular, ok",
            tenant=self.tenant,
        )

        # URL del endpoint
        self.url = reverse("analysis:chat-analysis")

        # Datos de prueba válidos
        self.valid_payload = {
            "chat": "Este es un texto de prueba para analizar",
            "analyzer_name": "test_analyzer",
        }

        # Mock del resultado del análisis
        self.mock_analysis_result = sentimentChatScript(
            sentimient="POSITIVE",
            cause="El texto contiene palabras positivas",
            log="Analizado 35 caracteres de texto, sentimiento detectado: POSITIVO",
        )

    def test_chat_analysis_success(self):
        """Test: Análisis exitoso de chat"""
        with patch("analysis.services.SentimentChatService.run") as mock_service:
            mock_service.return_value = self.mock_analysis_result

            with patch(
                "api.permissions_classes.is_tenant_authenticated.IsTenantAuthenticated.has_permission"
            ) as mock_permission:
                mock_permission.return_value = True

                response = self.client.post(
                    self.url,
                    data=json.dumps(self.valid_payload),
                    content_type="application/json",
                )

                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertEqual(response.data["sentimient"], "POSITIVE")
                self.assertEqual(
                    response.data["cause"], "El texto contiene palabras positivas"
                )
                self.assertIn("log", response.data)
                self.assertIn("timestamp", response.data)

    def test_chat_analysis_invalid_data(self):
        """Test: Datos de entrada inválidos"""
        invalid_payload = {"chat": "", "analyzer_name": "test_analyzer"}  # Chat vacío

        with patch(
            "api.permissions_classes.is_tenant_authenticated.IsTenantAuthenticated.has_permission"
        ) as mock_permission:
            mock_permission.return_value = True

            response = self.client.post(
                self.url,
                data=json.dumps(invalid_payload),
                content_type="application/json",
            )

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn("error", response.data)
            self.assertEqual(response.data["error"], "Datos de solicitud inválidos")

    def test_chat_analysis_missing_analyzer_name(self):
        """Test: Analyzer name faltante"""
        invalid_payload = {
            "chat": "Texto de prueba"
            # analyzer_name faltante
        }

        with patch(
            "api.permissions_classes.is_tenant_authenticated.IsTenantAuthenticated.has_permission"
        ) as mock_permission:
            mock_permission.return_value = True

            response = self.client.post(
                self.url,
                data=json.dumps(invalid_payload),
                content_type="application/json",
            )

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn("error", response.data)

    def test_chat_analysis_nonexistent_analyzer(self):
        """Test: Analizador no existente"""
        invalid_payload = {
            "chat": "Texto de prueba",
            "analyzer_name": "nonexistent_analyzer",
        }

        with patch(
            "api.permissions_classes.is_tenant_authenticated.IsTenantAuthenticated.has_permission"
        ) as mock_permission:
            mock_permission.return_value = True

            response = self.client.post(
                self.url,
                data=json.dumps(invalid_payload),
                content_type="application/json",
            )

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn("error", response.data)

    def test_chat_analysis_service_error(self):
        """Test: Error en el servicio de análisis"""
        with patch("analysis.services.SentimentChatService.run") as mock_service:
            mock_service.side_effect = Exception("Error en el servicio")

            with patch(
                "api.permissions_classes.is_tenant_authenticated.IsTenantAuthenticated.has_permission"
            ) as mock_permission:
                mock_permission.return_value = True

                response = self.client.post(
                    self.url,
                    data=json.dumps(self.valid_payload),
                    content_type="application/json",
                )

                self.assertEqual(
                    response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                self.assertEqual(response.data["error"], "Error interno del servidor")

    def test_chat_analysis_different_sentiments(self):
        """Test: Diferentes tipos de sentimientos"""
        sentiments = ["POSITIVE", "NEGATIVE", "NEUTRAL"]

        for sentiment in sentiments:
            with self.subTest(sentiment=sentiment):
                mock_result = sentimentChatScript(
                    sentimient=sentiment,
                    cause=f"El texto es {sentiment.lower()}",
                    log=f"Sentimiento detectado: {sentiment}",
                )

                with patch(
                    "analysis.services.SentimentChatService.run"
                ) as mock_service:
                    mock_service.return_value = mock_result

                    with patch(
                        "api.permissions_classes.is_tenant_authenticated.IsTenantAuthenticated.has_permission"
                    ) as mock_permission:
                        mock_permission.return_value = True

                        response = self.client.post(
                            self.url,
                            data=json.dumps(self.valid_payload),
                            content_type="application/json",
                        )

                        self.assertEqual(response.status_code, status.HTTP_200_OK)
                        self.assertEqual(response.data["sentimient"], sentiment)

    def test_chat_analysis_empty_chat_text(self):
        """Test: Texto de chat vacío"""
        empty_payload = {
            "chat": "   ",  # Solo espacios
            "analyzer_name": "test_analyzer",
        }

        with patch(
            "api.permissions_classes.is_tenant_authenticated.IsTenantAuthenticated.has_permission"
        ) as mock_permission:
            mock_permission.return_value = True

            response = self.client.post(
                self.url,
                data=json.dumps(empty_payload),
                content_type="application/json",
            )

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn("error", response.data)

    def test_chat_analysis_long_text(self):
        """Test: Texto muy largo"""
        long_text = "a" * 6000  # Más de 5000 caracteres
        long_payload = {"chat": long_text, "analyzer_name": "test_analyzer"}

        with patch(
            "api.permissions_classes.is_tenant_authenticated.IsTenantAuthenticated.has_permission"
        ) as mock_permission:
            mock_permission.return_value = True

            response = self.client.post(
                self.url, data=json.dumps(long_payload), content_type="application/json"
            )

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn("error", response.data)

    def test_chat_analysis_response_serialization_error(self):
        """Test: Error en serialización de respuesta"""
        mock_result = MagicMock()
        mock_result.sentimient = "INVALID_SENTIMENT"  # Sentimiento inválido
        mock_result.cause = "Causa de prueba"
        mock_result.log = "Log de prueba"

        with patch("analysis.services.SentimentChatService.run") as mock_service:
            mock_service.return_value = mock_result

            with patch(
                "api.permissions_classes.is_tenant_authenticated.IsTenantAuthenticated.has_permission"
            ) as mock_permission:
                mock_permission.return_value = True

                response = self.client.post(
                    self.url,
                    data=json.dumps(self.valid_payload),
                    content_type="application/json",
                )

                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn("error", response.data)

    def test_chat_analysis_method_not_allowed(self):
        """Test: Método HTTP no permitido"""
        with patch(
            "api.permissions_classes.is_tenant_authenticated.IsTenantAuthenticated.has_permission"
        ) as mock_permission:
            mock_permission.return_value = True

            response = self.client.get(self.url)

            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_chat_analysis_validates_json_format(self):
        """Test: Validación del formato JSON"""
        with patch(
            "api.permissions_classes.is_tenant_authenticated.IsTenantAuthenticated.has_permission"
        ) as mock_permission:
            mock_permission.return_value = True

            response = self.client.post(
                self.url, data="invalid json", content_type="application/json"
            )

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_chat_analysis_timestamp_format(self):
        """Test: Formato del timestamp en la respuesta"""
        with patch("analysis.services.SentimentChatService.run") as mock_service:
            mock_service.return_value = self.mock_analysis_result

            with patch(
                "api.permissions_classes.is_tenant_authenticated.IsTenantAuthenticated.has_permission"
            ) as mock_permission:
                mock_permission.return_value = True

                response = self.client.post(
                    self.url,
                    data=json.dumps(self.valid_payload),
                    content_type="application/json",
                )

                self.assertEqual(response.status_code, status.HTTP_200_OK)

                # Verificar que timestamp es un string que representa un número
                timestamp = response.data["timestamp"]
                self.assertIsInstance(timestamp, str)
                self.assertTrue(timestamp.isdigit())

                # Verificar que es un timestamp válido (no muy antiguo ni muy futuro)
                timestamp_int = int(timestamp)
                current_time = int(time.time())
                self.assertGreater(
                    timestamp_int, current_time - 60
                )  # No más de 1 minuto atrás
                self.assertLess(
                    timestamp_int, current_time + 60
                )  # No más de 1 minuto adelante

    def tearDown(self):
        """Limpieza después de cada test"""
        SentimentAgentModel.objects.all().delete()
        TenantModel.objects.all().delete()
