"""
Tests para la aplicación communication.

Este módulo contiene todos los tests unitarios y de integración
para los servicios de comunicación con Telegram.
"""

# Importar todos los test cases para que Django los descubra
from .test_telegram_communication_service import (
    TelegramCommunicationServiceIntegrationTests,
    TelegramCommunicationServiceTests,
)
from .test_telegram_service_edge_cases import (
    TelegramCommunicationServiceEdgeCaseTests,
    TelegramCommunicationServicePerformanceTests,
)

__all__ = [
    "TelegramCommunicationServiceTests",
    "TelegramCommunicationServiceIntegrationTests",
    "TelegramCommunicationServiceEdgeCaseTests",
    "TelegramCommunicationServicePerformanceTests",
]
