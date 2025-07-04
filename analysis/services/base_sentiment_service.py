from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from agno.agent import Agent
from agno.models.ollama import Ollama

from main.settings import IA_MODEL


class BaseSentimentService(ABC):
    """
    Clase base abstracta para servicios de análisis de sentimientos.

    Proporciona la funcionalidad común para crear y configurar agentes
    de análisis de sentimientos utilizando el framework Agno.
    """

    def __init__(self):
        """Inicializa el servicio base de análisis de sentimientos."""
        self.model = Ollama(id=IA_MODEL)

    @abstractmethod
    def get_agent_description(self) -> str:
        """
        Retorna la descripción específica del agente.

        Returns:
            str: Descripción del agente de análisis
        """
        pass

    @abstractmethod
    def get_agent_instructions(self) -> str:
        """
        Retorna las instrucciones específicas del agente.

        Returns:
            str: Instrucciones para el agente de análisis
        """
        pass

    @abstractmethod
    def get_response_model(self) -> Any:
        """
        Retorna el modelo de respuesta estructurada.

        Returns:
            Any: Clase del modelo de respuesta (SentimentScript o SentimentChatScript)
        """
        pass

    def build_context(self, context: Optional[str] = None, **kwargs) -> str:
        """
        Construye el contexto para el análisis de sentimientos.

        Args:
            context: Contexto base proporcionado
            **kwargs: Argumentos adicionales para construir el contexto

        Returns:
            str: Contexto formateado para el agente
        """
        if context:
            return context
        return ""

    def create_agent(self, context: str, response_model: Any) -> Agent:
        """
        Crea y configura un agente de análisis de sentimientos.

        Args:
            context: Contexto para el análisis
            response_model: Modelo de respuesta estructurada

        Returns:
            Agent: Agente configurado para análisis de sentimientos
        """
        return Agent(
            model=self.model,
            description=self.get_agent_description(),
            instructions=self.get_agent_instructions(),
            context=context,
            response_model=response_model,
        )

    def analyze_sentiment(self, text: str, context: str) -> Any:
        """
        Ejecuta el análisis de sentimiento.

        Args:
            text: Texto a analizar
            context: Contexto para el análisis

        Returns:
            Any: Resultado del análisis de sentimientos
        """
        response_model = self.get_response_model()
        agent = self.create_agent(context, response_model)

        # Ejecutar el agente de forma síncrona
        response = agent.run(text)
        return response.content

    @abstractmethod
    def run(self, *args, **kwargs) -> Any:
        """
        Método principal para ejecutar el análisis de sentimientos.

        Args:
            *args: Argumentos posicionales específicos de cada implementación
            **kwargs: Argumentos con nombre específicos de cada implementación

        Returns:
            Any: Resultado del análisis de sentimientos
        """
        pass
