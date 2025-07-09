import logging

from agents.services.agent_service import AgentService
from api.serializers.chat_serializer import ChatSerializer
from chats.models import ChatModel
from chats.services import ChatService
from communication.models.telegram.telegram_chat_model import TelegramChatModel
from communication.services.telegram_communication_service import (
    TelegramCommunicationService,
)
from main.signals import track_model_changes

logger = logging.getLogger(__name__)
import uuid

# Log cuando el módulo se carga
logger.info("📡 Módulo telegram_new_message cargado")
print("📡 Módulo telegram_new_message cargado")


@track_model_changes(TelegramChatModel)
def handle_telegram_new_message(
    sender, instance: TelegramChatModel, created, updated_fields, change_type, **kwargs
):
    """
    Handler para nuevos mensajes de chat.
    """
    print(
        f"🔥 SIGNAL EJECUTADO - TelegramChatModel - Created: {created}, Instance ID: {instance.pk}"
    )
    logger.info(
        f"🔥 SIGNAL EJECUTADO - TelegramChatModel - Created: {created}, Instance ID: {instance.pk}"
    )

    if created:
        logger.info(f"✅ Nuevo mensaje de Telegram creado: {instance}")
        if not instance.error:
            ns = uuid.NAMESPACE_URL
            semilla = f"{instance.agent_id}-{instance.chat_id}"
            uuid_sha1 = uuid.uuid5(ns, semilla)

            agent_service = AgentService(instance.agent.name, uuid_sha1)

            response, id = agent_service.send_message(
                message=instance.text, session_id=uuid_sha1
            )

            ChatModel.objects.get_or_create(
                session_id=id,
                agent=instance.agent,
            )
            chat_service = ChatService(id)
            chat_service.append_content(
                session_id=id, request=instance.text, response=response
            )
            telegram_comm_service = TelegramCommunicationService(
                instance.telegram_communication
            )
            telegram_comm_service.send_message(instance.chat_id, response)
            print(f"🔔 Respuesta del agente: {response}")
            logger.info(f"🔔 Respuesta del agente: {response}")
            print(f"✅ Nuevo mensaje de Telegram es un texto {instance}")
            logger.info(f"✅ Nuevo mensaje de Telegram es un texto {instance}")
    else:
        print(f"🔄 Mensaje de Telegram actualizado: {instance}")
        logger.info(f"🔄 Mensaje de Telegram actualizado: {instance}")


# Log cuando el signal se conecta
logger.info(f"📡 Signal handle_telegram_new_message conectado para {TelegramChatModel}")
print(f"📡 Signal handle_telegram_new_message conectado para {TelegramChatModel}")
