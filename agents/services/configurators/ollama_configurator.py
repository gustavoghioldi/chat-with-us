"""
Configurador para agentes que utilizan modelos Ollama.
"""

from agno.agent import Agent
from agno.models.ollama import Ollama

from main.settings import IA_MODEL

from .base_configurator import BaseAgentConfigurator


class OllamaConfigurator(BaseAgentConfigurator):
    """Configurador específico para modelos Ollama"""

    def configure(self) -> Agent:
        """
        Configura un agente con modelo Ollama.

        Returns:
            Agent: Instancia configurada del agente con Ollama

        Raises:
            ValueError: Si la configuración es inválida
        """
        # Validar configuración básica
        self._validate_configuration()

        # Configuración específica de Ollama
        model = Ollama(
            id=IA_MODEL,
            options={
                "max_tokens": self.agent_model.max_tokens,
                "temperature": self.agent_model.temperature,
                "top_p": self.agent_model.top_p,
            },
        )

        # Obtener configuración común
        agent_config = self._get_common_agent_config()
        agent_config["model"] = model

        # Crear y retornar el agente
        return Agent(**agent_config)

    def _validate_configuration(self):
        """
        Validación específica para Ollama.

        Raises:
            ValueError: Si la configuración específica de Ollama es inválida
        """
        # Llamar validación base
        super()._validate_configuration()

        # Validaciones específicas de Ollama
        if not IA_MODEL:
            raise ValueError("IA_MODEL no está configurado en settings para Ollama")

        # Validar que el tenant esté configurado correctamente para Ollama
        if self.agent_model.tenant and self.agent_model.tenant.model != "ollama":
            raise ValueError(
                f"El tenant '{self.agent_model.tenant.name}' no está configurado "
                "para usar Ollama. Verifique el campo 'model' en el tenant."
            )
