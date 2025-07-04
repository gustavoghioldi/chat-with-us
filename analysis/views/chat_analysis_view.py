import logging
import time
from typing import Any, Dict

from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.exceptions import ParseError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from analysis.models.sentiment_agents_model import SentimentAgentModel
from analysis.serializers.chat_analysis_serializer import (
    ChatAnalysisRequestSerializer,
    ChatAnalysisResponseSerializer,
)
from analysis.services import SentimentChatService
from api.permissions_classes.is_tenant_authenticated import IsTenantAuthenticated

logger = logging.getLogger(__name__)


class ChatAnalysisView(APIView):
    """
    API endpoint para analizar el sentimiento y contenido de un chat.

    Este endpoint permite analizar el sentimiento de un texto usando
    un agente de análisis de sentimientos específico del tenant.
    """

    permission_classes = [IsTenantAuthenticated]

    def post(self, request) -> Response:
        """
        Analizar un chat y devolver su valoración de sentimiento.

        Args:
            request: Objeto de solicitud HTTP con datos del chat

        Returns:
            Response: Respuesta con análisis de sentimiento

        Request body:
        {
            "chat": "Texto del chat a analizar",
            "analyzer_name": "Nombre del agente de sentimiento"
        }

        Response:
        {
            "sentimient": "POSITIVE|NEGATIVE|NEUTRAL",
            "cause": "Descripción del motivo",
            "log": "Log del análisis",
            "timestamp": "Timestamp del análisis"
        }
        """
        try:
            # Validar y obtener datos de entrada
            validated_data = self._validate_request_data(request.data)
            if "error" in validated_data:
                return validated_data["error"]

            chat_text = validated_data["chat"]
            analyzer = validated_data["analyzer_name"]

            # Realizar análisis del chat
            analysis_result = self._perform_chat_analysis(chat_text, analyzer)

            # Preparar y validar respuesta
            response_data = self._prepare_response_data(analysis_result)

            return Response(response_data, status=status.HTTP_200_OK)

        except SentimentAgentModel.DoesNotExist:
            logger.error(
                f"Agente de sentimiento no encontrado: {request.data.get('analyzer_name')}"
            )
            return Response(
                {"error": "Agente de sentimiento no encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except ParseError as e:
            logger.error(f"Error de parseo JSON: {str(e)}")
            return Response(
                {"error": "Formato JSON inválido"}, status=status.HTTP_400_BAD_REQUEST
            )
        except ValidationError as e:
            logger.error(f"Error de validación: {str(e)}")
            return Response(
                {"error": "Error de validación", "details": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            logger.error(
                f"Error inesperado en análisis de chat: {str(e)}", exc_info=True
            )
            return Response(
                {"error": "Error interno del servidor"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _validate_request_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validar los datos de entrada de la solicitud.

        Args:
            data: Datos de la solicitud

        Returns:
            Dict con datos validados o error
        """
        request_serializer = ChatAnalysisRequestSerializer(data=data)
        if not request_serializer.is_valid():
            logger.warning(f"Datos de solicitud inválidos: {request_serializer.errors}")
            return {
                "error": Response(
                    {
                        "error": "Datos de solicitud inválidos",
                        "details": request_serializer.errors,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            }
        return request_serializer.validated_data

    def _perform_chat_analysis(
        self, chat_text: str, analyzer: SentimentAgentModel
    ) -> Any:
        """
        Realizar el análisis de sentimiento del chat.

        Args:
            chat_text: Texto del chat a analizar
            analyzer: Instancia del agente de sentimiento

        Returns:
            Resultado del análisis

        Raises:
            Exception: Si hay error en el análisis
        """
        try:
            logger.info(f"Iniciando análisis de chat con agente: {analyzer.name}")

            analysis_result = SentimentChatService.run(
                text=chat_text, analyzer_name=analyzer.name
            )

            logger.info(
                f"Análisis completado exitosamente para agente: {analyzer.name}"
            )
            return analysis_result

        except Exception as e:
            logger.error(f"Error en análisis de chat: {str(e)}", exc_info=True)
            raise

    def _prepare_response_data(self, analysis_result: Any) -> Dict[str, Any]:
        """
        Preparar y validar los datos de respuesta.

        Args:
            analysis_result: Resultado del análisis

        Returns:
            Dict con datos de respuesta validados

        Raises:
            ValidationError: Si la respuesta no es válida
        """
        analysis_result_dict = {
            "sentimient": analysis_result.sentimient,
            "cause": analysis_result.cause,
            "log": analysis_result.log,
            "timestamp": str(int(time.time())),
        }

        response_serializer = ChatAnalysisResponseSerializer(data=analysis_result_dict)
        if not response_serializer.is_valid():
            logger.error(f"Error al serializar respuesta: {response_serializer.errors}")
            raise ValidationError(
                f"Error al preparar respuesta: {response_serializer.errors}"
            )

        return response_serializer.data
