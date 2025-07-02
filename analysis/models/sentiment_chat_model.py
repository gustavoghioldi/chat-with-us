from main.models import AppModel, models


class SentimentChatModel(AppModel):
    SENTIMENT_OPTIONS = [
        ("POSITIVO", "Positivo"),
        ("NEGATIVO", "Negativo"),
        ("NEUTRO", "Neutro"),
    ]

    content_chat = models.ForeignKey("chats.ContentChatModel", on_delete=models.CASCADE)
    actitude = models.CharField(max_length=10, choices=SENTIMENT_OPTIONS)
    cause = models.TextField()
