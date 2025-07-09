"""
Tests unitarios para TelegramCommunicationService.
"""

import json
from unittest.mock import Mock, patch

from django.test import TestCase

from communication.models.telegram.telegram_communication_model import (
    TelegramCommunicationModel,
)
from communication.services.telegram_communication_service import (
    TelegramCommunicationService,
)


class TelegramCommunicationServiceTests(TestCase):
    """
    Test suite para TelegramCommunicationService.
    """

    def setUp(self):
        """
        Configuración inicial para cada test.
        """
        # Crear un mock del modelo de comunicación
        self.mock_telegram_model = Mock(spec=TelegramCommunicationModel)
        self.mock_telegram_model.token = "123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZ123456789"

        # Crear instancia del servicio
        self.service = TelegramCommunicationService(self.mock_telegram_model)

        # Datos de prueba
        self.test_chat_id = 123456789
        self.test_message = "Mensaje de prueba"

    @patch("communication.services.telegram_communication_service.requests.post")
    def test_send_message_success(self, mock_post):
        """
        Test para envío exitoso de mensaje.
        """
        # Configurar mock de respuesta exitosa
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "ok": True,
            "result": {
                "message_id": 1,
                "chat": {"id": self.test_chat_id},
                "text": self.test_message,
            },
        }
        mock_post.return_value = mock_response

        # Ejecutar el método
        result = self.service.send_message(self.test_chat_id, self.test_message)

        # Verificaciones
        self.assertIsNone(result)  # El método no retorna nada en caso de éxito

        # Verificar que se llamó con los parámetros correctos
        mock_post.assert_called_once_with(
            f"https://api.telegram.org/bot{self.mock_telegram_model.token}/sendMessage",
            json={
                "chat_id": self.test_chat_id,
                "text": self.test_message,
                "parse_mode": "Markdown",
            },
        )

    @patch("communication.services.telegram_communication_service.requests.post")
    def test_send_message_failure(self, mock_post):
        """
        Test para fallo en envío de mensaje.
        """
        # Configurar mock de respuesta de error
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request: chat not found"
        mock_post.return_value = mock_response

        # Verificar que se lanza excepción
        with self.assertRaises(Exception) as context:
            self.service.send_message(self.test_chat_id, self.test_message)

        # Verificar mensaje de excepción
        self.assertIn("Failed to send message", str(context.exception))
        self.assertIn("Bad Request: chat not found", str(context.exception))

        # Verificar que se llamó con los parámetros correctos
        mock_post.assert_called_once_with(
            f"https://api.telegram.org/bot{self.mock_telegram_model.token}/sendMessage",
            json={
                "chat_id": self.test_chat_id,
                "text": self.test_message,
                "parse_mode": "Markdown",
            },
        )

    @patch("communication.services.telegram_communication_service.requests.post")
    def test_send_message_with_special_characters(self, mock_post):
        """
        Test para envío de mensaje con caracteres especiales.
        """
        # Configurar mock de respuesta exitosa
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        # Mensaje con caracteres especiales
        special_message = "Mensaje con *negrita*, _cursiva_ y `código`"

        # Ejecutar el método
        self.service.send_message(self.test_chat_id, special_message)

        # Verificar que se llamó con el mensaje especial
        mock_post.assert_called_once_with(
            f"https://api.telegram.org/bot{self.mock_telegram_model.token}/sendMessage",
            json={
                "chat_id": self.test_chat_id,
                "text": special_message,
                "parse_mode": "Markdown",
            },
        )

    @patch("communication.services.telegram_communication_service.requests.get")
    def test_get_updates_success(self, mock_get):
        """
        Test para obtención exitosa de updates.
        """
        # Datos de prueba para updates
        mock_updates_data = {
            "ok": True,
            "result": [
                {
                    "update_id": 123456,
                    "message": {
                        "message_id": 1,
                        "from": {
                            "id": 987654321,
                            "is_bot": False,
                            "first_name": "Juan",
                            "last_name": "Pérez",
                            "language_code": "es",
                        },
                        "chat": {"id": self.test_chat_id, "type": "private"},
                        "date": 1609459200,
                        "text": "Hola bot",
                    },
                }
            ],
        }

        # Configurar mock de respuesta exitosa
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_updates_data
        mock_get.return_value = mock_response

        # Ejecutar el método
        result = self.service.get_updates()

        # Verificaciones
        self.assertEqual(result, mock_updates_data)
        self.assertTrue(result["ok"])
        self.assertEqual(len(result["result"]), 1)
        self.assertEqual(result["result"][0]["update_id"], 123456)

        # Verificar que se llamó con la URL correcta
        mock_get.assert_called_once_with(
            f"https://api.telegram.org/bot{self.mock_telegram_model.token}/getUpdates"
        )

    @patch("communication.services.telegram_communication_service.requests.get")
    def test_get_updates_empty_result(self, mock_get):
        """
        Test para obtención de updates con resultado vacío.
        """
        # Datos de prueba sin updates
        mock_updates_data = {"ok": True, "result": []}

        # Configurar mock de respuesta exitosa
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_updates_data
        mock_get.return_value = mock_response

        # Ejecutar el método
        result = self.service.get_updates()

        # Verificaciones
        self.assertEqual(result, mock_updates_data)
        self.assertTrue(result["ok"])
        self.assertEqual(len(result["result"]), 0)

    @patch("communication.services.telegram_communication_service.requests.get")
    def test_get_updates_failure(self, mock_get):
        """
        Test para fallo en obtención de updates.
        """
        # Configurar mock de respuesta de error
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized: bot token is invalid"
        mock_get.return_value = mock_response

        # Verificar que se lanza excepción
        with self.assertRaises(Exception) as context:
            self.service.get_updates()

        # Verificar mensaje de excepción
        self.assertIn("Failed to get updates", str(context.exception))
        self.assertIn("Unauthorized: bot token is invalid", str(context.exception))

        # Verificar que se llamó con la URL correcta
        mock_get.assert_called_once_with(
            f"https://api.telegram.org/bot{self.mock_telegram_model.token}/getUpdates"
        )

    @patch("communication.services.telegram_communication_service.requests.get")
    def test_get_updates_malformed_response(self, mock_get):
        """
        Test para respuesta malformada de la API de Telegram.
        """
        # Configurar mock de respuesta con JSON inválido
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_get.return_value = mock_response

        # Verificar que se lanza excepción JSON
        with self.assertRaises(json.JSONDecodeError):
            self.service.get_updates()

    def test_service_initialization(self):
        """
        Test para verificar la inicialización correcta del servicio.
        """
        # Verificar que el modelo se asigna correctamente
        self.assertEqual(
            self.service.telegram_communication_model, self.mock_telegram_model
        )

    def test_service_with_different_tokens(self):
        """
        Test para verificar comportamiento con diferentes tokens.
        """
        # Crear otro mock con token diferente
        another_mock_model = Mock(spec=TelegramCommunicationModel)
        another_mock_model.token = "DIFFERENT_TOKEN_123"

        another_service = TelegramCommunicationService(another_mock_model)

        # Verificar que cada servicio usa su propio token
        self.assertNotEqual(
            self.service.telegram_communication_model.token,
            another_service.telegram_communication_model.token,
        )

    @patch("communication.services.telegram_communication_service.requests.post")
    def test_send_message_with_empty_message(self, mock_post):
        """
        Test para envío de mensaje vacío.
        """
        # Configurar mock de respuesta exitosa
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        # Enviar mensaje vacío
        empty_message = ""
        self.service.send_message(self.test_chat_id, empty_message)

        # Verificar que se envía el mensaje vacío
        mock_post.assert_called_once_with(
            f"https://api.telegram.org/bot{self.mock_telegram_model.token}/sendMessage",
            json={
                "chat_id": self.test_chat_id,
                "text": empty_message,
                "parse_mode": "Markdown",
            },
        )

    @patch("communication.services.telegram_communication_service.requests.post")
    def test_send_message_with_long_message(self, mock_post):
        """
        Test para envío de mensaje largo.
        """
        # Configurar mock de respuesta exitosa
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        # Crear mensaje largo (mayor a 4096 caracteres que es el límite de Telegram)
        long_message = "A" * 5000

        # Enviar mensaje largo
        self.service.send_message(self.test_chat_id, long_message)

        # Verificar que se intenta enviar el mensaje completo
        # (La validación de longitud debería manejarse en niveles superiores)
        mock_post.assert_called_once_with(
            f"https://api.telegram.org/bot{self.mock_telegram_model.token}/sendMessage",
            json={
                "chat_id": self.test_chat_id,
                "text": long_message,
                "parse_mode": "Markdown",
            },
        )

    @patch("communication.services.telegram_communication_service.requests.post")
    def test_send_message_network_error(self, mock_post):
        """
        Test para error de red al enviar mensaje.
        """
        # Configurar mock para lanzar excepción de red
        mock_post.side_effect = ConnectionError("Network error")

        # Verificar que se propaga la excepción de red
        with self.assertRaises(ConnectionError):
            self.service.send_message(self.test_chat_id, self.test_message)

    @patch("communication.services.telegram_communication_service.requests.get")
    def test_get_updates_network_error(self, mock_get):
        """
        Test para error de red al obtener updates.
        """
        # Configurar mock para lanzar excepción de red
        mock_get.side_effect = ConnectionError("Network error")

        # Verificar que se propaga la excepción de red
        with self.assertRaises(ConnectionError):
            self.service.get_updates()


class TelegramCommunicationServiceIntegrationTests(TestCase):
    """
    Tests de integración para TelegramCommunicationService.
    Estos tests verifican la integración con el modelo real.
    """

    def setUp(self):
        """
        Configuración para tests de integración.
        """
        # Crear un modelo real para tests de integración
        # (En un entorno de test, esto usaría la base de datos de test)
        pass

    def test_service_with_real_model_structure(self):
        """
        Test que verifica que el servicio funciona con la estructura real del modelo.
        """
        # Este test se puede expandir cuando tengas datos reales para testing
        pass


# Ejecutar tests desde la línea de comandos si es necesario
if __name__ == "__main__":
    import unittest

    unittest.main()
