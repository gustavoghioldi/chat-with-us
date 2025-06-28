"""
Configurador para agentes que utilizan modelos OpenAI.
"""

from agno.agent import Agent
from agno.models.openai import OpenAIChat

from .base_configurator import BaseAgentConfigurator


class OpenAIConfigurator(BaseAgentConfigurator):
    """Configurador específico para modelos OpenAI"""

    def configure(self) -> Agent:
        """
        Configura un agente con modelo OpenAI.

        Returns:
            Agent: Instancia configurada del agente con OpenAI

        Raises:
            ValueError: Si la configuración es inválida
        """
        # Validar configuración básica y específica
        self._validate_configuration()

        # Configuración específica de OpenAI
        model = OpenAIChat(
            id=self.agent_model.agent_model_id,
            api_key=self.agent_model.tenant.ai_token,
            max_tokens=self.agent_model.max_tokens,
            temperature=self.agent_model.temperature,
            top_p=self.agent_model.top_p,
        )

        # Obtener configuración común
        agent_config = self._get_common_agent_config()
        agent_config["model"] = model

        # Crear y retornar el agente
        return Agent(**agent_config)

    def _validate_configuration(self):
        """
        Validación específica para OpenAI.

        Raises:
            ValueError: Si la configuración específica de OpenAI es inválida
        """
        # Llamar validación base
        super()._validate_configuration()

        # Validar tenant
        if not self.agent_model.tenant:
            raise ValueError("El agente debe tener un tenant asignado para usar OpenAI")

        # Validar que el tenant esté configurado para OpenAI
        if self.agent_model.tenant.model != "openai":
            raise ValueError(
                f"El tenant '{self.agent_model.tenant.name}' no está configurado "
                "para usar OpenAI. Verifique el campo 'model' en el tenant."
            )

        # Validar que el tenant tenga configurado el token de OpenAI
        if not self.agent_model.tenant.ai_token:
            raise ValueError(
                f"El tenant '{self.agent_model.tenant.name}' no tiene configurado "
                "un token de OpenAI. Configure el campo 'ai_token' en el tenant."
            )

        # Validar modelo ID
        if not self.agent_model.agent_model_id:
            raise ValueError(
                "El campo 'agent_model_id' es requerido para usar OpenAI. "
                "Especifique el ID del modelo (ej: 'gpt-3.5-turbo', 'gpt-4')."
            )

        # Validar que el API key no esté vacío
        api_key = self.agent_model.tenant.ai_token.strip()
        if not api_key:
            raise ValueError("El token de OpenAI no puede estar vacío")

        # Validar formato básico del API key (OpenAI keys empiezan con 'sk-')
        if not api_key.startswith("sk-"):
            raise ValueError(
                "El token de OpenAI parece tener un formato inválido. "
                "Los tokens de OpenAI deben empezar con 'sk-'."
            )
