from chats.models import ContentChatModel
from main.models import AppModel, models


# Create your models here.
class SentimentChatModel(AppModel):
    SENTIMENT_OPTIONS = [
        ("POSITIVO", "Positivo"),
        ("NEGATIVO", "Negativo"),
        ("NEUTRO", "Neutro"),
    ]

    content_chat = models.ForeignKey(ContentChatModel, on_delete=models.CASCADE)
    actitude = models.CharField(max_length=10, choices=SENTIMENT_OPTIONS)
    cause = models.TextField()
