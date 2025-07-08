from django.db import models

# Create your models here.
from main.models import AppModel, models


class TelegramCommunicationModel(AppModel):

    agent = models.ForeignKey(
        "agents.AgentModel",
        on_delete=models.CASCADE,
        related_name="telegram_communication",
        help_text="Agente asociado al bot de Telegram",
        verbose_name="Agente",
    )

    token = models.CharField(
        max_length=255,
        help_text="Token de acceso del bot de Telegram",
        verbose_name="Token de Telegram",
    )

    bot_name = models.CharField(
        max_length=255,
        help_text="Nombre del bot de Telegram",
        verbose_name="Nombre del bot de Telegram",
    )

    voice = models.BooleanField(
        default=False,
        help_text="Indica si el bot puede enviar mensajes de voz",
        verbose_name="Enviar mensajes de voz",
    )

    files = models.BooleanField(
        default=False,
        help_text="Indica si el bot puede enviar archivos",
        verbose_name="Enviar archivos",
    )
