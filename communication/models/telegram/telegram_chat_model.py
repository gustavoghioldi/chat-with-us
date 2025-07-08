from main.models import AppModel, models


class TelegramUserModel(AppModel):
    telegram_id = models.BigIntegerField(
        unique=True, help_text="ID de usuario de Telegram"
    )
    is_bot = models.BooleanField(default=False)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    language_code = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name or ''} ({self.telegram_id})"


class TelegramChatModel(AppModel):
    chat_id = models.BigIntegerField(unique=True, help_text="ID del chat de Telegram")
    first_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    type = models.CharField(
        max_length=20, help_text="Tipo de chat (private, group, etc)"
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name or ''} ({self.chat_id})"


class TelegramMessageModel(AppModel):
    update_id = models.BigIntegerField(help_text="ID de actualización de Telegram")
    message_id = models.BigIntegerField(help_text="ID del mensaje de Telegram")
    from_user = models.ForeignKey(
        "TelegramUserModel",
        on_delete=models.CASCADE,
        related_name="messages_from",
        help_text="Usuario que envía el mensaje",
    )
    chat = models.ForeignKey(
        "TelegramChatModel",
        on_delete=models.CASCADE,
        related_name="messages",
        help_text="Chat al que pertenece el mensaje",
    )
    telegram_datetime = models.DateTimeField(
        help_text="Fecha del mensaje (timestamp de Telegram)"
    )
    text = models.TextField(blank=True, null=True, help_text="Texto del mensaje")

    def __str__(self):
        return f"Mensaje {self.message_id} en chat {self.chat_id}"
