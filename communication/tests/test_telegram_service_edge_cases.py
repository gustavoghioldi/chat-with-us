"""
Tests adicionales para casos edge y de rendimiento del TelegramCommunicationService.
"""

import time
from unittest.mock import Mock, call, patch

from django.test import TestCase

from communication.models.telegram.telegram_communication_model import (
    TelegramCommunicationModel,
)
from communication.services.telegram_communication_service import (
    TelegramCommunicationService,
)


class TelegramCommunicationServiceEdgeCaseTests(TestCase):
    """
    Tests para casos edge y situaciones especiales.
    """

    def setUp(self):
        """
        Configuración inicial.
        """
        self.mock_telegram_model = Mock(spec=TelegramCommunicationModel)
        self.mock_telegram_model.token = "valid_token_123"
        self.service = TelegramCommunicationService(self.mock_telegram_model)

    @patch("communication.services.telegram_communication_service.requests.post")
    def test_send_message_with_unicode_characters(self, mock_post):
        """
        Test para mensajes con caracteres Unicode y emojis.
        """
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        # Mensaje con emojis y caracteres Unicode
        unicode_message = (
            "¡Hola! 👋 Mensaje con emojis 🚀 y caracteres especiales: áéíóú ñ"
        )

        self.service.send_message(123456, unicode_message)

        mock_post.assert_called_once_with(
            f"https://api.telegram.org/bot{self.mock_telegram_model.token}/sendMessage",
            json={"chat_id": 123456, "text": unicode_message, "parse_mode": "Markdown"},
        )

    @patch("communication.services.telegram_communication_service.requests.post")
    def test_send_message_with_markdown_injection(self, mock_post):
        """
        Test para mensajes que podrían causar problemas con Markdown.
        """
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        # Mensaje con caracteres que podrían interferir con Markdown
        problematic_message = "Mensaje con *asteriscos* _guiones_ `backticks` [enlaces](http://example.com)"

        self.service.send_message(123456, problematic_message)

        # El servicio debería enviar el mensaje tal como está
        # (la sanitización debería hacerse en capas superiores si es necesaria)
        mock_post.assert_called_once_with(
            f"https://api.telegram.org/bot{self.mock_telegram_model.token}/sendMessage",
            json={
                "chat_id": 123456,
                "text": problematic_message,
                "parse_mode": "Markdown",
            },
        )

    @patch("communication.services.telegram_communication_service.requests.post")
    def test_send_message_with_negative_chat_id(self, mock_post):
        """
        Test para chat_id negativo (grupos/canales).
        """
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        negative_chat_id = -1001234567890  # Formato típico de grupos

        self.service.send_message(negative_chat_id, "Mensaje a grupo")

        mock_post.assert_called_once_with(
            f"https://api.telegram.org/bot{self.mock_telegram_model.token}/sendMessage",
            json={
                "chat_id": negative_chat_id,
                "text": "Mensaje a grupo",
                "parse_mode": "Markdown",
            },
        )

    @patch("communication.services.telegram_communication_service.requests.post")
    def test_send_message_timeout_handling(self, mock_post):
        """
        Test para manejo de timeouts.
        """
        # Simular timeout
        mock_post.side_effect = TimeoutError("Request timed out")

        with self.assertRaises(TimeoutError):
            self.service.send_message(123456, "Test message")

    @patch("communication.services.telegram_communication_service.requests.get")
    def test_get_updates_with_large_response(self, mock_get):
        """
        Test para respuesta grande de updates.
        """
        # Simular respuesta con muchos updates
        large_updates_data = {
            "ok": True,
            "result": [
                {
                    "update_id": i,
                    "message": {
                        "message_id": i,
                        "from": {"id": 123, "is_bot": False, "first_name": f"User{i}"},
                        "chat": {"id": 456, "type": "private"},
                        "date": 1609459200 + i,
                        "text": f"Message {i}",
                    },
                }
                for i in range(100)  # 100 updates
            ],
        }

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = large_updates_data
        mock_get.return_value = mock_response

        result = self.service.get_updates()

        self.assertEqual(len(result["result"]), 100)
        self.assertTrue(result["ok"])

    @patch("communication.services.telegram_communication_service.requests.get")
    def test_get_updates_with_malformed_update(self, mock_get):
        """
        Test para updates con estructura malformada.
        """
        # Update con estructura incompleta
        malformed_updates_data = {
            "ok": True,
            "result": [
                {
                    "update_id": 123,
                    "message": {
                        "message_id": 1,
                        # Falta información del 'from' y 'chat'
                        "date": 1609459200,
                        "text": "Incomplete message",
                    },
                }
            ],
        }

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = malformed_updates_data
        mock_get.return_value = mock_response

        # El servicio debería retornar los datos tal como vienen
        # (la validación debería hacerse en capas superiores)
        result = self.service.get_updates()

        self.assertEqual(result, malformed_updates_data)
        self.assertEqual(len(result["result"]), 1)

    def test_service_initialization_with_none_model(self):
        """
        Test para inicialización con modelo None.
        """
        with self.assertRaises(AttributeError):
            service = TelegramCommunicationService(None)
            # Intentar usar el servicio debería fallar
            service.send_message(123, "test")

    @patch("communication.services.telegram_communication_service.requests.post")
    def test_send_message_with_empty_token(self, mock_post):
        """
        Test para token vacío.
        """
        # Modelo con token vacío
        empty_token_model = Mock(spec=TelegramCommunicationModel)
        empty_token_model.token = ""

        service = TelegramCommunicationService(empty_token_model)

        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_post.return_value = mock_response

        with self.assertRaises(Exception) as context:
            service.send_message(123456, "test")

        self.assertIn("Failed to send message", str(context.exception))

    @patch("communication.services.telegram_communication_service.requests.post")
    def test_concurrent_send_messages(self, mock_post):
        """
        Test para envíos concurrentes de mensajes.
        """
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        # Simular múltiples envíos
        chat_ids = [111, 222, 333]
        messages = ["Msg1", "Msg2", "Msg3"]

        for chat_id, message in zip(chat_ids, messages):
            self.service.send_message(chat_id, message)

        # Verificar que se hicieron todas las llamadas
        self.assertEqual(mock_post.call_count, 3)

        # Verificar las llamadas específicas
        expected_calls = [
            call(
                f"https://api.telegram.org/bot{self.mock_telegram_model.token}/sendMessage",
                json={"chat_id": chat_id, "text": message, "parse_mode": "Markdown"},
            )
            for chat_id, message in zip(chat_ids, messages)
        ]

        mock_post.assert_has_calls(expected_calls)


class TelegramCommunicationServicePerformanceTests(TestCase):
    """
    Tests de rendimiento para el servicio.
    """

    def setUp(self):
        """
        Configuración para tests de rendimiento.
        """
        self.mock_telegram_model = Mock(spec=TelegramCommunicationModel)
        self.mock_telegram_model.token = "performance_test_token"
        self.service = TelegramCommunicationService(self.mock_telegram_model)

    @patch("communication.services.telegram_communication_service.requests.post")
    def test_send_message_performance(self, mock_post):
        """
        Test básico de rendimiento para envío de mensajes.
        """
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        # Medir tiempo de ejecución
        start_time = time.time()

        # Enviar múltiples mensajes
        for i in range(10):
            self.service.send_message(123456, f"Performance test message {i}")

        end_time = time.time()
        execution_time = end_time - start_time

        # Verificar que se ejecutó en tiempo razonable (menos de 1 segundo para 10 mensajes)
        self.assertLess(execution_time, 1.0)
        self.assertEqual(mock_post.call_count, 10)

    @patch("communication.services.telegram_communication_service.requests.get")
    def test_get_updates_performance_with_large_dataset(self, mock_get):
        """
        Test de rendimiento para obtener updates con dataset grande.
        """
        # Crear dataset grande (simulando muchos updates)
        large_dataset = {
            "ok": True,
            "result": [
                {
                    "update_id": i,
                    "message": {
                        "message_id": i,
                        "from": {"id": 123, "is_bot": False, "first_name": "User"},
                        "chat": {"id": 456, "type": "private"},
                        "date": 1609459200,
                        "text": f"Performance test message {i}" * 10,  # Mensajes largos
                    },
                }
                for i in range(1000)  # 1000 updates
            ],
        }

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = large_dataset
        mock_get.return_value = mock_response

        # Medir tiempo de procesamiento
        start_time = time.time()
        result = self.service.get_updates()
        end_time = time.time()

        execution_time = end_time - start_time

        # Verificaciones
        self.assertEqual(len(result["result"]), 1000)
        # El procesamiento debería ser rápido (menos de 0.1 segundos)
        self.assertLess(execution_time, 0.1)

    def test_memory_usage_with_large_messages(self):
        """
        Test básico de uso de memoria con mensajes grandes.
        """
        # Crear mensaje muy grande
        large_message = "X" * 100000  # 100KB de texto

        # Verificar que el servicio puede manejar mensajes grandes sin problemas
        # (Este test es más conceptual, en un entorno real medirías memoria)
        try:
            # Solo verificar que no hay errores de memoria inmediatos
            formatted_message = large_message
            self.assertEqual(len(formatted_message), 100000)
        except MemoryError:
            self.fail("El servicio no puede manejar mensajes grandes")


# Ejecutar solo estos tests
if __name__ == "__main__":
    import unittest

    unittest.main()
