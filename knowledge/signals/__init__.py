"""
Ejemplo de cómo usar el sistema de signals centralizado desde main
para trackear cambios en modelos de Knowledge.
"""

import logging

from knowledge.models import KnowledgeModel
from main.signals import create_model_handler, track_model_changes

logger = logging.getLogger(__name__)


@track_model_changes(KnowledgeModel)
def handle_knowledge_changes(
    sender, instance, created, updated_fields, change_type, **kwargs
):
    """
    Handler para cambios en KnowledgeModel.
    """
    if created:
        logger.info(f"📚 Nueva base de conocimiento creada: {instance}")
        # Lógica específica para cuando se crea una base de conocimiento
        # Por ejemplo: indexar contenido, procesar embeddings, etc.

    else:
        logger.info(f"📝 Base de conocimiento actualizada: {instance}")

        if updated_fields:
            logger.info("Campos modificados en knowledge:")
            for field_info in updated_fields:
                logger.info(
                    f"  - {field_info['field_verbose_name']}: "
                    f"'{field_info['old_value']}' → '{field_info['new_value']}'"
                )

        # Lógica específica para actualizaciones
        for field_info in updated_fields:
            field_name = field_info["field"]

            if field_name == "content":  # Asumiendo que hay un campo content
                logger.info(
                    f"📄 Contenido de {instance} ha cambiado - reindexar necesario"
                )
                # Aquí podrías disparar tareas de reindexación

            elif field_name == "title":  # Asumiendo que hay un campo title
                logger.info(
                    f"🏷️ Título de knowledge cambió a: {field_info['new_value']}"
                )


@track_model_changes(KnowledgeModel)
def knowledge_cache_invalidation(
    sender, instance, created, updated_fields, change_type, **kwargs
):
    """
    Invalida cache específico de knowledge cuando hay cambios.
    """
    cache_keys = []

    if created:
        cache_keys.extend(
            [
                "knowledge_list",
                "knowledge_count",
                (
                    f"agent_knowledge_{instance.pk}"
                    if hasattr(instance, "agent_id")
                    else None
                ),
            ]
        )
    else:
        cache_keys.extend(
            [f"knowledge_{instance.pk}", f"knowledge_{instance.pk}_content"]
        )

    # Limpiar cache
    for cache_key in filter(None, cache_keys):
        logger.info(f"🗑️ Invalidando cache de knowledge: {cache_key}")
        # cache.delete(cache_key)
