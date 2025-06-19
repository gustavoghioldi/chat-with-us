"""
Signals para monitoreo de cambios en modelos de conocimiento.
"""

import logging

from django.dispatch import receiver

from knowledge.signals.emites.knowledge_recreated_change_emit import (
    KnowledgeRecreatedChangeEmit,
    signal,
)

logger = logging.getLogger(__name__)


@receiver(signal)
def handle_knowledge_change_recreate_receiver(sender, **kwargs):
    pass
