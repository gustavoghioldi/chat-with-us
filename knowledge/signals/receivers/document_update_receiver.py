"""
Signals para monitoreo de cambios en modelos de conocimiento.
"""

import logging

from django.dispatch import receiver

from documents.signals.emiters.document_update_emit import signal

logger = logging.getLogger(__name__)


@receiver(signal)
def document_update_receiver(sender, instance, **kwargs):
    instance.knowledge_models.update(recreate=True)
