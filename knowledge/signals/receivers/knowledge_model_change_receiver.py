"""
Signals para monitoreo de cambios en modelos de conocimiento.
"""

import logging

from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone

from knowledge.models import KnowledgeModel
from knowledge.signals.emites.knowledge_recreated_change_emit import (
    KnowledgeRecreatedChangeEmit,
)

# Configurar logger
logger = logging.getLogger(__name__)


@receiver(pre_save, sender=KnowledgeModel)
def handle_knowledge_change_receiver(sender, instance, **kwargs):
    KnowledgeRecreatedChangeEmit.emit(sender, instance, instance.recreate)
