from celery import shared_task

from analysis.models.sentiment_agents_model import SentimentAgentModel
from analysis.models.sentiment_chat_model import SentimentChatModel
from analysis.services import SentimentMessageService
from chats.models import ContentChatModel


@shared_task
def run_sentiment_analysis(message, session_id, timestamp, sentiment_model=None):
    content = ContentChatModel.objects.get(chat=session_id, created_at=timestamp)

    if not sentiment_model:
        SentimentChatModel.objects.create(content_chat=content)
    SentimentAgentModel.objects.get(id=sentiment_model)
    context = f"""
    ##Palabas de Ejemplo:
    Palabras NEGATIVAS: {sentiment_model.negatives}
    Palabras POSITIVAS: {sentiment_model.positives}
    Palabras NEUTRAS: {sentiment_model.neutrals}
    """
    sent = SentimentMessageService.run(text=message, context=context)
    SentimentChatModel.objects.create(
        content_chat=content, actitude=sent.sentimient, cause=sent.cause
    )
