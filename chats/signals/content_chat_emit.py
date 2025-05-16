from django.dispatch import Signal

# Definir un signal personalizado
new_chat_text = Signal()

class NewChatTextSignal:
    @staticmethod
    def emit(sender, message, session_id, timestamp):
        new_chat_text.send(sender, message=message, session_id=session_id, timestamp=timestamp)