"""
Configurador para agentes que utilizan modelos Google Gemini.
"""

from agno.agent import Agent
from agno.models.google import Gemini

from .base_configurator import BaseAgentConfigurator


class GeminiConfigurator(BaseAgentConfigurator):
    """Configurador específico para modelos Google Gemini"""

    def configure(self) -> Agent:
        """
        Configura un agente con modelo Google Gemini.

        Returns:
            Agent: Instancia configurada del agente con Gemini

        Raises:
            ValueError: Si la configuración es inválida
        """
        # Validar configuración básica y específica
        self._validate_configuration()

        # Configurar el modelo Gemini usando agno.models.google.Gemini
        model = Gemini(
            id=self.agent_model.agent_model_id,
            api_key=self.agent_model.tenant.ai_token,
            # max_tokens=self.agent_model.max_tokens,
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
        Validación específica para Google Gemini.

        Raises:
            ValueError: Si la configuración específica de Gemini es inválida
        """
        # Llamar validación base
        super()._validate_configuration()

        # Validar tenant
        if not self.agent_model.tenant:
            raise ValueError("El agente debe tener un tenant asignado para usar Gemini")

        # Validar que el tenant esté configurado para Gemini
        if self.agent_model.tenant.model != "gemini":
            raise ValueError(
                f"El tenant '{self.agent_model.tenant.name}' no está configurado "
                "para usar Google Gemini. Verifique el campo 'model' en el tenant."
            )

        # Validar que el tenant tenga configurado el token de Gemini
        if not self.agent_model.tenant.ai_token:
            raise ValueError(
                f"El tenant '{self.agent_model.tenant.name}' no tiene configurado "
                "un token de Google Gemini. Configure el campo 'ai_token' en el tenant."
            )

        # Validar que el API key no esté vacío
        api_key = self.agent_model.tenant.ai_token.strip()
        if not api_key:
            raise ValueError("El token de Google Gemini no puede estar vacío")

        # Validar modelo ID (opcional, usará gemini-pro por defecto)
        if self.agent_model.agent_model_id:
            valid_models = ["gemini-2.0-flash-lite"]
            if self.agent_model.agent_model_id not in valid_models:
                print(
                    f"⚠️ Modelo '{self.agent_model.agent_model_id}' no está en la lista de modelos válidos conocidos: {valid_models}"
                )

        # Validar límites específicos de Gemini para algunos parámetros
        if self.agent_model.max_tokens > 8192:
            print(
                f"⚠️ max_tokens ({self.agent_model.max_tokens}) es muy alto para algunos modelos Gemini. Se recomienda <= 8192"
            )

    @classmethod
    def get_supported_models(cls) -> list:
        """
        Retorna la lista de modelos Gemini soportados.

        Returns:
            list: Lista de IDs de modelos soportados
        """
        return [
            "gemini-pro",
            "gemini-pro-vision",
            "gemini-1.5-pro",
            "gemini-1.5-flash",
            "gemini-ultra",
        ]

    @classmethod
    def get_default_model(cls) -> str:
        """
        Retorna el modelo por defecto para Gemini.

        Returns:
            str: ID del modelo por defecto
        """
        return "gemini-pro"
