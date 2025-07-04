"""
Test unitarios para ChatAnalysisView

Tests comprehensivos para la vista de análisis de chat migrada desde api a analysis.
"""

import json
import time
from unittest.mock import Mock, patch

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from analysis.models.sentiment_agents_model import SentimentAgentModel
from analysis.views.chat_analysis_view import ChatAnalysisView
from tenants.models import TenantModel


class ChatAnalysisViewTestCase(TestCase):
    """Test cases para ChatAnalysisView"""

    def setUp(self):
        """Configuración inicial para cada test"""
        self.client = APIClient()
        self.url = reverse("analysis:chat-analysis")

        # Crear tenant de prueba
        self.tenant = TenantModel.objects.create(
            name="Test Tenant", description="Tenant para pruebas", model="ollama"
        )

        # Crear agente de sentimiento de prueba
        self.sentiment_agent = SentimentAgentModel.objects.create(
            name="test_analyzer",
            description="Analizador de prueba",
            positive_tokens="excelente,bueno,fantástico",
            negative_tokens="malo,terrible,horrible",
            neutral_tokens="normal,regular,aceptable",
            tenant=self.tenant,
        )

        # Datos de prueba válidos
        self.valid_data = {
            "chat": "Este es un chat de prueba muy positivo",
            "analyzer_name": "test_analyzer",
        }

        # Mock del resultado del servicio
        self.mock_service_result = Mock()
        self.mock_service_result.sentimient = "POSITIVE"
        self.mock_service_result.cause = "El chat contiene palabras positivas"
        self.mock_service_result.log = (
            "Analizado 35 caracteres de texto, sentimiento detectado: POSITIVE"
        )

    @patch("analysis.views.chat_analysis_view.SentimentChatService.run")
    @patch(
        "api.permissions_classes.is_tenant_authenticated.IsTenantAuthenticated.has_permission"
    )
    def test_chat_analysis_success(self, mock_permission, mock_service):
        """Test: Flujo exitoso de análisis de sentimientos"""
        # Configurar mocks
        mock_permission.return_value = True
        mock_service.return_value = self.mock_service_result

        # Realizar solicitud
        response = self.client.post(self.url, self.valid_data, format="json")

        # Verificar respuesta
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.json()
        self.assertIn("sentimient", response_data)
        self.assertIn("cause", response_data)
        self.assertIn("log", response_data)
        self.assertIn("timestamp", response_data)

        # Verificar valores específicos
        self.assertEqual(response_data["sentimient"], "POSITIVE")
        self.assertEqual(response_data["cause"], "El chat contiene palabras positivas")
        self.assertIsInstance(response_data["timestamp"], str)

        # Verificar que el servicio fue llamado
        mock_service.assert_called_once_with(
            text=self.valid_data["chat"], analyzer_name=self.sentiment_agent.name
        )

    @patch(
        "api.permissions_classes.is_tenant_authenticated.IsTenantAuthenticated.has_permission"
    )
    def test_chat_analysis_invalid_data(self, mock_permission):
        """Test: Manejo de datos de entrada inválidos"""
        mock_permission.return_value = True

        invalid_data = {"chat": "", "analyzer_name": "test_analyzer"}  # Chat vacío

        response = self.client.post(self.url, invalid_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_data = response.json()
        self.assertIn("error", response_data)
        self.assertIn("details", response_data)

    @patch(
        "api.permissions_classes.is_tenant_authenticated.IsTenantAuthenticated.has_permission"
    )
    def test_chat_analysis_missing_analyzer_name(self, mock_permission):
        """Test: Manejo cuando falta el campo analyzer_name"""
        mock_permission.return_value = True

        invalid_data = {
            "chat": "Texto de prueba"
            # Falta analyzer_name
        }

        response = self.client.post(self.url, invalid_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_data = response.json()
        self.assertIn("error", response_data)
        self.assertIn("details", response_data)

    @patch(
        "api.permissions_classes.is_tenant_authenticated.IsTenantAuthenticated.has_permission"
    )
    def test_chat_analysis_nonexistent_analyzer(self, mock_permission):
        """Test: Comportamiento con analizador inexistente"""
        mock_permission.return_value = True

        invalid_data = {
            "chat": "Texto de prueba",
            "analyzer_name": "analyzer_inexistente",
        }

        response = self.client.post(self.url, invalid_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_data = response.json()
        self.assertIn("error", response_data)

    @patch("analysis.views.chat_analysis_view.SentimentChatService.run")
    @patch(
        "api.permissions_classes.is_tenant_authenticated.IsTenantAuthenticated.has_permission"
    )
    def test_chat_analysis_service_error(self, mock_permission, mock_service):
        """Test: Error en el servicio de análisis"""
        mock_permission.return_value = True
        mock_service.side_effect = Exception("Error en el servicio")

        response = self.client.post(self.url, self.valid_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        response_data = response.json()
        self.assertIn("error", response_data)
        self.assertEqual(response_data["error"], "Error interno del servidor")

    @patch("analysis.views.chat_analysis_view.SentimentChatService.run")
    @patch(
        "api.permissions_classes.is_tenant_authenticated.IsTenantAuthenticated.has_permission"
    )
    def test_chat_analysis_different_sentiments(self, mock_permission, mock_service):
        """Test: Respuestas para diferentes tipos de sentimientos"""
        mock_permission.return_value = True

        sentiments = ["POSITIVE", "NEGATIVE", "NEUTRAL"]

        for sentiment in sentiments:
            with self.subTest(sentiment=sentiment):
                # Configurar mock para cada sentimiento
                mock_result = Mock()
                mock_result.sentimient = sentiment
                mock_result.cause = f"Análisis de sentimiento {sentiment.lower()}"
                mock_result.log = f"Detectado sentimiento {sentiment}"
                mock_service.return_value = mock_result

                response = self.client.post(self.url, self.valid_data, format="json")

                self.assertEqual(response.status_code, status.HTTP_200_OK)
                response_data = response.json()
                self.assertEqual(response_data["sentimient"], sentiment)

    @patch(
        "api.permissions_classes.is_tenant_authenticated.IsTenantAuthenticated.has_permission"
    )
    def test_chat_analysis_empty_chat_text(self, mock_permission):
        """Test: Manejo de texto con solo espacios en blanco"""
        mock_permission.return_value = True

        invalid_data = {
            "chat": "   ",  # Solo espacios
            "analyzer_name": "test_analyzer",
        }

        response = self.client.post(self.url, invalid_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_data = response.json()
        self.assertIn("error", response_data)

    @patch(
        "api.permissions_classes.is_tenant_authenticated.IsTenantAuthenticated.has_permission"
    )
    def test_chat_analysis_long_text(self, mock_permission):
        """Test: Validación de máximo de caracteres"""
        mock_permission.return_value = True

        # Texto que excede los 5000 caracteres
        long_text = "A" * 5001
        invalid_data = {"chat": long_text, "analyzer_name": "test_analyzer"}

        response = self.client.post(self.url, invalid_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_data = response.json()
        self.assertIn("error", response_data)

    @patch("analysis.views.chat_analysis_view.SentimentChatService.run")
    @patch(
        "api.permissions_classes.is_tenant_authenticated.IsTenantAuthenticated.has_permission"
    )
    def test_chat_analysis_response_serialization_error(
        self, mock_permission, mock_service
    ):
        """Test: Error en serialización de respuesta"""
        mock_permission.return_value = True

        # Configurar mock con sentimiento inválido
        mock_result = Mock()
        mock_result.sentimient = "INVALID_SENTIMENT"  # Sentimiento inválido
        mock_result.cause = "Test cause"
        mock_result.log = "Test log"
        mock_service.return_value = mock_result

        response = self.client.post(self.url, self.valid_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_data = response.json()
        self.assertIn("error", response_data)

    @patch(
        "api.permissions_classes.is_tenant_authenticated.IsTenantAuthenticated.has_permission"
    )
    def test_chat_analysis_method_not_allowed(self, mock_permission):
        """Test: Solo el método POST está permitido"""
        mock_permission.return_value = True

        # Probar métodos no permitidos
        methods = ["GET", "PUT", "DELETE", "PATCH"]

        for method in methods:
            with self.subTest(method=method):
                if method == "GET":
                    response = self.client.get(self.url)
                elif method == "PUT":
                    response = self.client.put(self.url, self.valid_data, format="json")
                elif method == "DELETE":
                    response = self.client.delete(self.url)
                elif method == "PATCH":
                    response = self.client.patch(
                        self.url, self.valid_data, format="json"
                    )

                self.assertEqual(
                    response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
                )

    @patch(
        "api.permissions_classes.is_tenant_authenticated.IsTenantAuthenticated.has_permission"
    )
    def test_chat_analysis_validates_json_format(self, mock_permission):
        """Test: Validación de formato JSON"""
        mock_permission.return_value = True

        # Enviar datos malformados
        response = self.client.post(
            self.url,
            data='{"chat": "test", "analyzer_name": "test_analyzer"',  # JSON malformado
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_data = response.json()
        self.assertIn("error", response_data)

    @patch("analysis.views.chat_analysis_view.SentimentChatService.run")
    @patch(
        "api.permissions_classes.is_tenant_authenticated.IsTenantAuthenticated.has_permission"
    )
    def test_chat_analysis_timestamp_format(self, mock_permission, mock_service):
        """Test: Verificación del formato correcto del timestamp"""
        mock_permission.return_value = True
        mock_service.return_value = self.mock_service_result

        # Capturar tiempo antes de la solicitud
        before_time = int(time.time())

        response = self.client.post(self.url, self.valid_data, format="json")

        # Capturar tiempo después de la solicitud
        after_time = int(time.time())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()

        # Verificar que el timestamp es un string
        self.assertIsInstance(response_data["timestamp"], str)

        # Verificar que el timestamp está en el rango temporal correcto
        timestamp = int(response_data["timestamp"])
        self.assertGreaterEqual(timestamp, before_time)
        self.assertLessEqual(timestamp, after_time)

    @patch(
        "api.permissions_classes.is_tenant_authenticated.IsTenantAuthenticated.has_permission"
    )
    def test_chat_analysis_unauthorized_access(self, mock_permission):
        """Test: Acceso no autorizado"""
        mock_permission.return_value = False

        response = self.client.post(self.url, self.valid_data, format="json")

        # El comportamiento exacto depende de la implementación de IsTenantAuthenticated
        # pero típicamente sería 401 o 403
        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )

    def tearDown(self):
        """Limpieza después de cada test"""
        # Limpiar datos de prueba
        SentimentAgentModel.objects.all().delete()
        TenantModel.objects.all().delete()
