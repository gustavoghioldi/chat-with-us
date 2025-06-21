"""
Signals para monitoreo de cambios en modelos de conocimiento.
"""

import logging

from django.db.models.signals import pre_save
from django.dispatch import receiver

from documents.models import DocumentModel
from documents.signals.emiters.document_update_emit import DocumentUpdateEmitter

# Configurar logger
logger = logging.getLogger(__name__)


@receiver(pre_save, sender=DocumentModel)
def handler_document_update_receiver(sender, instance, **kwargs):
    DocumentUpdateEmitter.emit(sender, instance, kwargs=kwargs)
