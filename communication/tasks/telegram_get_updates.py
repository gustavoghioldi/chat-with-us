import logging

from celery import group, shared_task

from communication.models.telegram.telegram_chat_model import TelegramChatModel
from communication.models.telegram.telegram_communication_model import (
    TelegramCommunicationModel,
)
from communication.serializers.telegram_serializers import TelegramChatModelSerializer
from communication.services.telegram_communication_service import (
    TelegramCommunicationService,
)

# Importar signals para asegurar que estén cargados en Celery workers
try:
    import agents.signals.telegram_new_message  # noqa: F401
except ImportError:
    logging.warning("No se pudieron cargar los signals de agents")

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def process_telegram_update(self, update, comm_model: TelegramCommunicationModel):
    # Asegurar que los signals estén cargados
    try:
        import agents.signals.telegram_new_message  # noqa: F401

        logger.info("Signals cargados exitosamente en la tarea")
    except ImportError as e:
        logger.warning(f"No se pudieron cargar los signals: {e}")

    try:
        message_data = update.get("message", {})
        has_text = message_data.get("text")
        update["agent"] = comm_model.agent
        update["telegram_communication"] = comm_model.pk
        if has_text:
            # Procesar mensaje con texto usando serializer
            serializer = TelegramChatModelSerializer(data=update)
            if serializer.is_valid():
                logger.info(
                    f"Guardando mensaje con texto via serializer, update_id: {update.get('update_id')}"
                )
                instance = serializer.save()
                logger.info(
                    f"Mensaje guardado via serializer - ID: {instance.pk}, update_id: {update.get('update_id')}"
                )
                logger.info(f"Processing text update {update.get('update_id')}")
                logger.info(f"Update {update.get('update_id')} saved OK.")
                return {"update_id": update.get("update_id"), "status": "ok"}
            else:
                logger.error(f"Invalid update data: {serializer.errors}")
                return {
                    "update_id": update.get("update_id"),
                    "status": "invalid",
                    "errors": serializer.errors,
                }
        else:
            # Procesar mensaje sin texto (multimedia, etc.)
            return _process_non_text_message(update, comm_model)

    except Exception as e:
        logger.error(f"Error processing update {update.get('update_id')}: {e}")
        return {
            "update_id": update.get("update_id"),
            "status": "error",
            "error": str(e),
        }


def _process_non_text_message(update, comm_model):
    """
    Procesa mensajes que no contienen texto (multimedia, etc.)
    """
    try:
        message_data = update.get("message", {})
        telegram_communication_service = TelegramCommunicationService(comm_model)

        # Determinar el tipo de mensaje y respuesta
        if message_data.get("voice"):
            message = "No se pueden procesar mensajes de voz en este momento."
        elif message_data.get("photo"):
            message = "No se pueden procesar fotos en este momento."
        elif message_data.get("document"):
            message = "No se pueden procesar documentos en este momento."
        elif message_data.get("poll"):
            message = "No se pueden procesar encuestas en este momento."
        elif message_data.get("video"):
            message = "No se pueden procesar videos en este momento."
        else:
            message = "No se puede procesar este tipo de mensaje en este momento."

        # Crear el modelo usando get_or_create
        telegram_chat, created = TelegramChatModel.objects.get_or_create(
            update_id=update.get("update_id"),
            defaults={
                "error": message,
                "chat_id": message_data.get("chat", {}).get("id"),
                "is_bot": message_data.get("from", {}).get("is_bot", False),
                "date": message_data.get("date"),
                "first_name": message_data.get("from", {}).get("first_name", ""),
                "last_name": message_data.get("from", {}).get("last_name", ""),
                "language_code": message_data.get("from", {}).get("language_code", ""),
                "message_id": message_data.get("message_id"),
                "agent": comm_model.agent,
            },
        )

        logger.info(
            f"TelegramChatModel created={created}, id={telegram_chat.pk}, update_id={update.get('update_id')}"
        )

        # Enviar respuesta automática si se creó un nuevo chat
        if created:
            chat_id = message_data.get("chat", {}).get("id")
            if chat_id:
                telegram_communication_service.send_message(chat_id, message)
                logger.info(
                    f"Created new TelegramChatModel for non-text message. Update ID: {update.get('update_id')}"
                )

        return {
            "update_id": update.get("update_id"),
            "status": "processed_non_text",
            "created": created,
            "message": message,
        }

    except Exception as e:
        logger.error(
            f"Error processing non-text message {update.get('update_id')}: {e}"
        )
        raise e
    except Exception as e:
        logger.error(f"Error processing update {update.get('update_id')}: {e}")
        return {
            "update_id": update.get("update_id"),
            "status": "error",
            "error": str(e),
        }


@shared_task(bind=True)
def fetch_telegram_updates_for_model(self, comm_model_id):
    try:
        comm_model = TelegramCommunicationModel.objects.get(pk=comm_model_id)
        service = TelegramCommunicationService(comm_model)
        updates = service.get_updates()
        ok = updates.get("ok", None)
        result = updates.get("result", None)
        logger.info(f"comm_model {comm_model.pk} - ok: {ok}, result: {result}")
        logger.info(
            f"Fetched {len(result) if result else 0} updates from Telegram for comm_model {comm_model.pk}."
        )
        if ok and result:
            job = group(
                process_telegram_update.s(update, comm_model) for update in result
            )
            job_result = job.apply_async()
            logger.info(f"Dispatched {len(result)} subtasks for processing updates.")
            return job_result.id
        return updates
    except Exception as e:
        logger.error(
            f"Error fetching Telegram updates for comm_model {comm_model_id}: {e}"
        )
        self.retry(exc=e, countdown=60, max_retries=3)


@shared_task(bind=True)
def check_telegram_updates(self):
    """
    Celery task to check for new updates from Telegram for all TelegramCommunicationModel instances.
    Each model is processed in a separate task.
    """
    try:
        comm_model_ids = list(
            TelegramCommunicationModel.objects.values_list("pk", flat=True)
        )
        job = group(
            fetch_telegram_updates_for_model.s(comm_id) for comm_id in comm_model_ids
        )
        result = job.apply_async()
        logger.info(f"Dispatched {len(comm_model_ids)} subtasks for Telegram updates.")
        return result.id
    except Exception as e:
        logger.error(f"Error dispatching Telegram update tasks: {e}")
        self.retry(exc=e, countdown=60, max_retries=3)
