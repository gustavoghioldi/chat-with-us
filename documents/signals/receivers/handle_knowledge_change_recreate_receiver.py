"""
Signals para monitoreo de cambios en modelos de conocimiento.
"""

import logging

from django.dispatch import receiver

from knowledge.models import KnowledgeModel
from knowledge.signals.emites.knowledge_recreated_change_emit import signal

logger = logging.getLogger(__name__)


@receiver(signal)
def handle_knowledge_change_recreate_receiver(sender, **kwargs):
    if not kwargs.get("recreate"):
        knowledge: KnowledgeModel = kwargs.get("instance")
        if knowledge.document:
            # Marcar el documento como procesado
            knowledge.document.is_processed = True
            # La fecha de procesamiento se actualizará automáticamente en el save
            # No necesitamos establecer processed_at manualmente
            knowledge.document.save(update_fields=["is_processed"])
