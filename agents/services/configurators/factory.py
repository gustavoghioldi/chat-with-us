"""
Factory para crear configuradores de agentes según el tipo de modelo.
"""

from typing import Type

from agents.models import AgentModel

from .base_configurator import BaseAgentConfigurator
from .gemini_configurator import GeminiConfigurator
from .ollama_configurator import OllamaConfigurator


class AgentConfiguratorFactory:
    """Factory para crear configuradores de agentes"""

    # Mapeo de modelos a configuradores
    _configurators = {
        "ollama": OllamaConfigurator,
        "gemini": GeminiConfigurator,
    }

    @classmethod
    def create_configurator(
        cls, agent_model: AgentModel, knowledge_base=None, storage_service=None
    ) -> BaseAgentConfigurator:
        """
        Crea el configurador apropiado según el modelo del tenant.

        Args:
            agent_model: Instancia del modelo de agente
            knowledge_base: Base de conocimiento opcional
            storage_service: Servicio de almacenamiento opcional

        Returns:
            BaseAgentConfigurator: Configurador específico para el modelo

        Raises:
            ValueError: Si el modelo no es soportado o el tenant no está configurado
        """
        if not agent_model.tenant:
            raise ValueError("El agente debe tener un tenant asignado")

        model_type = agent_model.tenant.model

        if not model_type:
            raise ValueError(
                f"El tenant '{agent_model.tenant.name}' no tiene configurado "
                "un tipo de modelo. Configure el campo 'model' en el tenant."
            )

        configurator_class = cls._configurators.get(model_type)

        if not configurator_class:
            supported_models = ", ".join(cls._configurators.keys())
            raise ValueError(
                f"Modelo '{model_type}' no soportado. "
                f"Modelos soportados: {supported_models}"
            )

        return configurator_class(
            agent_model=agent_model,
            knowledge_base=knowledge_base,
            storage_service=storage_service,
        )

    @classmethod
    def get_supported_models(cls) -> list:
        """
        Retorna la lista de modelos soportados.

        Returns:
            list: Lista de modelos soportados
        """
        return list(cls._configurators.keys())

    @classmethod
    def register_configurator(
        cls, model_type: str, configurator_class: Type[BaseAgentConfigurator]
    ):
        """
        Registra un nuevo configurador para un tipo de modelo.

        Args:
            model_type: Tipo de modelo (ej: 'claude', 'gemini')
            configurator_class: Clase del configurador

        Raises:
            ValueError: Si la clase no hereda de BaseAgentConfigurator
        """
        if not issubclass(configurator_class, BaseAgentConfigurator):
            raise ValueError("El configurador debe heredar de BaseAgentConfigurator")

        cls._configurators[model_type] = configurator_class
