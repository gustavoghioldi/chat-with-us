"""Signal handlers específicos para la app agents."""

import logging

from main.signals import track_model_changes

from .models import AgentModel

# Configurar logger
logger = logging.getLogger(__name__)


@track_model_changes(AgentModel)
def handle_agent_changes(
    sender, instance, created, updated_fields, change_type, **kwargs
):
    """
    Handler específico para cambios en AgentModel.
    """
    if created:
        logger.info(f"✅ Nuevo agente creado: {instance.name}")
        # Aquí puedes agregar lógica específica para cuando se crea un agente

    else:
        logger.info(f"🔄 Agente actualizado: {instance.name}")

        if updated_fields:
            logger.info("Campos modificados:")
            for field_info in updated_fields:
                logger.info(
                    f"  - {field_info['field_verbose_name']} ({field_info['field']}): "
                    f"'{field_info['old_value']}' → '{field_info['new_value']}'"
                )

        # Aquí puedes agregar lógica específica para cuando se actualiza un agente

    # Ejemplo de lógica adicional basada en campos específicos
    if not created and updated_fields:
        for field_info in updated_fields:
            if field_info["field"] == "instructions":
                logger.info(
                    f"📝 Las instrucciones del agente {instance.name} han cambiado"
                )
                # Lógica específica para cambio de instrucciones

            elif field_info["field"] == "name":
                logger.info(
                    f"🏷️ El nombre del agente ha cambiado de '{field_info['old_value']}' a '{field_info['new_value']}'"
                )
                # Lógica específica para cambio de nombre


@track_model_changes(AgentModel)
def log_agent_changes(sender, instance, created, updated_fields, change_type, **kwargs):
    """
    Logger genérico para cambios en AgentModel.
    """
    model_name = sender._meta.verbose_name

    if created:
        logger.info(f"🆕 {model_name} creado: {instance}")
    else:
        if updated_fields:
            field_names = [f["field"] for f in updated_fields]
            logger.info(
                f"📝 {model_name} actualizado: {instance}. Campos: {', '.join(field_names)}"
            )
        else:
            logger.info(f"💾 {model_name} guardado sin cambios: {instance}")
