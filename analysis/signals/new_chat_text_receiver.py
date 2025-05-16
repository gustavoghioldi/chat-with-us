from django.dispatch import receiver
from chats.models import ContentChatModel
from chats.signals.content_chat_emit import new_chat_text
from analysis.services import SentimentMessageService
from analysis.models.sentiment_chat_model import SentimentChatModel
from analysis.services import SentimientScript

@receiver(new_chat_text)
def handler(sender, **kwargs):
    print(f"Signal recibido de {sender} con datos: {kwargs}")
    sent: SentimientScript = SentimentMessageService.run(kwargs.get("message"))
    content = ContentChatModel.objects.get(chat=kwargs.get("session_id"), created_at=kwargs.get("timestamp"))
    SentimentChatModel.objects.create(content_chat= content, actitude = sent.sentimient, cause = sent.cause)