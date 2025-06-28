"""
Configurador base para servicios de agentes IA.
"""

from abc import ABC, abstractmethod

from agno.agent import Agent

from agents.models import AgentModel


class BaseAgentConfigurator(ABC):
    """Clase base abstracta para configuradores de agentes"""

    def __init__(
        self, agent_model: AgentModel, knowledge_base=None, storage_service=None
    ):
        self.agent_model = agent_model
        self.knowledge_base = knowledge_base
        self.storage_service = storage_service

    @abstractmethod
    def configure(self) -> Agent:
        """
        Configura y retorna una instancia de Agent.

        Returns:
            Agent: Instancia configurada del agente

        Raises:
            NotImplementedError: Si el método no está implementado
            ValueError: Si la configuración es inválida
        """
        pass

    def _get_common_agent_config(self) -> dict:
        """
        Retorna la configuración común para todos los tipos de agentes.

        Returns:
            dict: Configuración común del agente
        """
        from textwrap import dedent

        return {
            "name": self.agent_model.name,
            "instructions": dedent(
                f"""
                {self.agent_model.instructions}
            """
            ),
            "description": dedent(
                f"""
                {self.agent_model.description or "Agente creado para responder preguntas y realizar tareas específicas."}
            """
            ),
            "knowledge": self.knowledge_base,
            "search_knowledge": True if self.knowledge_base else False,
            "storage": (
                self.storage_service.get_storage() if self.storage_service else None
            ),
            "add_history_to_messages": True,
            "num_history_responses": 3,
            "debug_mode": True,
        }

    def _validate_configuration(self):
        """
        Valida la configuración básica del agente.

        Raises:
            ValueError: Si la configuración es inválida
        """
        if not self.agent_model:
            raise ValueError("El modelo de agente es requerido")

        if not self.agent_model.name:
            raise ValueError("El nombre del agente es requerido")

        if not self.agent_model.instructions:
            raise ValueError("Las instrucciones del agente son requeridas")

        # Validar parámetros de configuración
        if not (0.0 <= self.agent_model.temperature <= 1.0):
            raise ValueError("La temperatura debe estar entre 0.0 y 1.0")

        if not (0.0 <= self.agent_model.top_p <= 1.0):
            raise ValueError("El valor top_p debe estar entre 0.0 y 1.0")

        if self.agent_model.max_tokens <= 0:
            raise ValueError("max_tokens debe ser mayor a 0")
