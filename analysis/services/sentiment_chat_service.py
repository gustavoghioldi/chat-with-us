from analysis.models.sentiment_agents_model import SentimentAgentModel
from analysis.services.base_sentiment_service import BaseSentimentService
from analysis.services.scripts.sentiment_chat_script import SentimentChatScript


class SentimentChatService(BaseSentimentService):
    """
    Servicio para análisis de sentimientos de chats completos.

    Utiliza un agente de IA configurado con tokens específicos del tenant
    para analizar el sentimiento de conversaciones completas.
    """

    def get_agent_description(self) -> str:
        """
        Retorna la descripción específica del agente para chats completos.

        Returns:
            str: Descripción del agente de análisis de chats
        """
        return "Eres un analista de los sentimientos del chat enviado por el usuario"

    def get_agent_instructions(self) -> str:
        """
        Retorna las instrucciones específicas del agente para chats completos.

        Returns:
            str: Instrucciones para el agente de análisis de chats
        """
        return (
            "Analiza el sentimiento del chat del usuario y clasificalo como POSITIVO, NEGATIVO o NEUTRO. "
            "Proporciona una justificación para la clasificación."
        )

    def get_response_model(self) -> type:
        """
        Retorna el modelo de respuesta estructurada para chats completos.

        Returns:
            type: Clase SentimentChatScript para la respuesta
        """
        return SentimentChatScript

    def build_context(
        self, context: str = None, sentiment_model: SentimentAgentModel = None
    ) -> str:
        """
        Construye el contexto específico para análisis de chats con tokens del modelo.

        Args:
            context: Contexto base (no utilizado en esta implementación)
            sentiment_model: Modelo de sentimiento con tokens específicos

        Returns:
            str: Contexto formateado con ejemplos de tokens
        """
        if sentiment_model:
            return f"""
            ##Palabras de Ejemplo:
            Frases de sentimientos NEGATIVAS: {sentiment_model.negative_tokens}
            Frases de sentimientos POSITIVAS: {sentiment_model.positive_tokens}
            Frases de sentimientos NEUTRAS: {sentiment_model.neutral_tokens}
        """
        return ""

    @staticmethod
    def run(text: str, analyzer_name: str) -> SentimentChatScript:
        """
        Ejecuta el análisis de sentimiento para un chat completo.

        Args:
            text: Texto del chat a analizar
            analyzer_name: Nombre del agente de sentimiento a utilizar

        Returns:
            SentimentChatScript: Resultado del análisis con sentimiento, causa y log

        Raises:
            SentimentAgentModel.DoesNotExist: Si el analizador no existe
        """
        sentiment_model = SentimentAgentModel.objects.get(name=analyzer_name)

        service = SentimentChatService()
        context = service.build_context(sentiment_model=sentiment_model)

        return service.analyze_sentiment(text, context)
