from analysis.tasks import run_sentiment_analysis
from chats.models import ContentChatModel
from main.signals import track_model_changes


@track_model_changes(ContentChatModel)
def handle_new_chat_text(
    sender, instance, created, updated_fields, change_type, **kwargs
):
    """
    Handler para nuevos mensajes de chat.
    """
    if created:
        run_sentiment_analysis(
            message=instance.request,
            session_id=instance.chat.session_id,
            timestamp=instance.created_at,
        )
