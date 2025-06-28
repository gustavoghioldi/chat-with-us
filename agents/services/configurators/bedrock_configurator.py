"""
Configurador para agentes que utilizan modelos AWS Bedrock.
"""

from agno.agent import Agent

from .base_configurator import BaseAgentConfigurator


class BedrockConfigurator(BaseAgentConfigurator):
    """Configurador específico para modelos AWS Bedrock"""

    def configure(self) -> Agent:
        """
        Configura un agente con modelo AWS Bedrock.

        Returns:
            Agent: Instancia configurada del agente con Bedrock

        Raises:
            NotImplementedError: Bedrock aún no está implementado
            ValueError: Si la configuración es inválida
        """
        # Validar configuración básica
        self._validate_configuration()

        # TODO: Implementar configuración de AWS Bedrock
        raise NotImplementedError(
            "La configuración de AWS Bedrock aún no está implementada. "
            "Se requiere implementar la integración con AWS Bedrock en agno."
        )

    def _validate_configuration(self):
        """
        Validación específica para AWS Bedrock.

        Raises:
            ValueError: Si la configuración específica de Bedrock es inválida
        """
        # Llamar validación base
        super()._validate_configuration()

        # Validar tenant
        if not self.agent_model.tenant:
            raise ValueError(
                "El agente debe tener un tenant asignado para usar Bedrock"
            )

        # Validar que el tenant esté configurado para Bedrock
        if self.agent_model.tenant.model != "bedrock":
            raise ValueError(
                f"El tenant '{self.agent_model.tenant.name}' no está configurado "
                "para usar AWS Bedrock. Verifique el campo 'model' en el tenant."
            )

        # TODO: Implementar validaciones específicas de Bedrock
        # - Validar AWS credentials
        # - Validar región de AWS
        # - Validar modelo específico de Bedrock
        # - Validar permisos de IAM
