from django.dispatch import receiver
from analysis.tasks import run_sentiment_analysis
from chats.signals.content_chat_emit import new_chat_text

@receiver(new_chat_text)
def handler(sender, **kwargs):
    run_sentiment_analysis.delay(
        message=kwargs['message'],
        session_id=kwargs['session_id'],
        timestamp=kwargs['timestamp']
    )