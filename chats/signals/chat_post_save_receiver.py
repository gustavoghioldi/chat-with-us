from django.db.models.signals import post_save
from django.dispatch import receiver
from chats.models import ContentChatModel
from chats.signals.content_chat_emit import NewChatTextSignal

@receiver(post_save, sender=ContentChatModel)
def handler(sender, instance, created, **kwargs):
    if created:
        NewChatTextSignal.emit('content_chat', message=instance.request, session_id=instance.chat.session_id, timestamp=instance.created_at)    