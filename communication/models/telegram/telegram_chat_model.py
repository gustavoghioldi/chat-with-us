from main.models import AppModel, models


class TelegramChatModel(AppModel):
    update_id = models.BigIntegerField(
        help_text="ID de la actualización de Telegram",
        verbose_name="ID de actualización",
    )
    text = models.TextField(
        help_text="Mensaje recibido del usuario",
        verbose_name="Mensaje del usuario",
    )
    message_id = models.BigIntegerField(
        help_text="ID del mensaje de Telegram",
        verbose_name="ID del mensaje",
    )
    chat_id = models.BigIntegerField(
        help_text="ID del chat de Telegram",
    )
    is_bot = models.BooleanField(
        default=False,
        help_text="Indica si el mensaje es de un bot",
    )
    date = models.BigIntegerField(
        help_text="Fecha del mensaje en formato Unix timestamp",
        verbose_name="Fecha del mensaje",
    )
    first_name = models.CharField(
        max_length=255,
        help_text="Nombre del usuario que envió el mensaje",
        verbose_name="Nombre del usuario",
    )
    last_name = models.CharField(
        max_length=255,
        help_text="Apellido del usuario que envió el mensaje",
        verbose_name="Apellido del usuario",
        null=True,
        blank=True,
    )
    language_code = models.CharField(
        max_length=2,
        help_text="Código de idioma del usuario",
        verbose_name="Código de idioma",
        null=True,
        blank=True,
    )
    error = models.CharField(
        help_text="Mensaje de error si hubo un problema al procesar el mensaje",
        verbose_name="Mensaje de error",
        null=True,
        blank=True,
    )
    agent = models.ForeignKey(
        "agents.AgentModel",
        on_delete=models.CASCADE,
        related_name="telegram_chats",
        help_text="Agente asociado a este chat de Telegram",
        verbose_name="Agente asociado",
        null=True,
        blank=True,
    )

    telegram_communication = models.ForeignKey(
        "communication.TelegramCommunicationModel",
        on_delete=models.CASCADE,
        related_name="telegram_chats",
        help_text="Modelo de comunicación de Telegram asociado a este chat",
        verbose_name="Modelo de comunicación de Telegram",
        null=True,
        blank=True,
    )

    class Meta:
        unique_together = ("chat_id", "message_id")
