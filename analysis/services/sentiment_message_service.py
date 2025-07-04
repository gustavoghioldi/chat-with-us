from analysis.services.base_sentiment_service import BaseSentimentService
from analysis.services.scripts.sentiment_script import SentimientScript


class SentimentMessageService(BaseSentimentService):
    """
    Servicio para análisis de sentimientos de mensajes individuales.

    Utiliza un agente de IA para analizar el sentimiento de mensajes cortos
    basándose en el contexto proporcionado.
    """

    def get_agent_description(self) -> str:
        """
        Retorna la descripción específica del agente para mensajes individuales.

        Returns:
            str: Descripción del agente de análisis de mensajes
        """
        return (
            "Eres un analista de los sentimientos de las frases enviadas por el usuario"
        )

    def get_agent_instructions(self) -> str:
        """
        Retorna las instrucciones específicas del agente para mensajes individuales.

        Returns:
            str: Instrucciones para el agente de análisis de mensajes
        """
        return (
            "Analiza el sentimiento del mensaje del usuario y clasificalo como POSITIVO, NEGATIVO o NEUTRO. "
            "Proporciona una justificación para la clasificación."
        )

    def get_response_model(self) -> type:
        """
        Retorna el modelo de respuesta estructurada para mensajes individuales.

        Returns:
            type: Clase SentimientScript para la respuesta
        """
        return SentimientScript

    @staticmethod
    def run(text: str, context: str) -> SentimientScript:
        """
        Ejecuta el análisis de sentimiento para un mensaje.

        Args:
            text: Texto del mensaje a analizar
            context: Contexto adicional para el análisis

        Returns:
            SentimientScript: Resultado del análisis con sentimiento, causa y log
        """
        service = SentimentMessageService()
        return service.analyze_sentiment(text, context)
