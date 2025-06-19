from django.dispatch import Signal

from knowledge.models import KnowledgeModel

signal = Signal()


class KnowledgeRecreatedChangeEmit:
    @staticmethod
    def emit(sender, instance: KnowledgeModel, recreate: bool) -> None:
        signal.send(sender, instance=instance, recreate=recreate)
