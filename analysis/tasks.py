from celery import shared_task
from analysis.models.sentiment_chat_model import SentimentChatModel
from analysis.services import SentimentMessageService
from chats.models import ContentChatModel

@shared_task
def run_sentiment_analysis(message, session_id, timestamp):
    sent = SentimentMessageService.run(message)
    content = ContentChatModel.objects.get(chat=session_id, created_at=timestamp)
    SentimentChatModel.objects.create(content_chat= content, actitude = sent.sentimient, cause = sent.cause)
    