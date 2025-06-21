from django.dispatch import Signal

signal = Signal()


class DocumentUpdateEmitter:
    @staticmethod
    def emit(sender, instance, **kwargs):
        signal.send(sender=sender, instance=instance, **kwargs)
