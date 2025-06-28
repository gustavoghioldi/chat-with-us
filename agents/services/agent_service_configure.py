from agents.models import AgentModel
from agents.services.agent_storage_service import AgentSessionService
from agents.services.configurators.factory import AgentConfiguratorFactory
from knowledge.services.document_knowledge_base_service import (
    DocumentKnowledgeBaseService,
)


class AgentServiceConfigure:
    """
    Servicio principal para configurar agentes IA.

    Utiliza el patrón Factory para delegar la configuración específica
    a configuradores especializados según el tipo de modelo.
    """

    def __init__(self, agent_model: AgentModel):
        self.__agent_model: AgentModel = agent_model
        knowledge_service = DocumentKnowledgeBaseService(agent_model.name)
        self.__knowledge = knowledge_service.get_knowledge_base()
        self.storage_service = AgentSessionService()

    def configure(self):
        """
        Configura el agente utilizando el configurador apropiado.

        Returns:
            Agent: Instancia configurada del agente

        Raises:
            ValueError: Si la configuración es inválida
        """
        # Usar factory para crear el configurador apropiado
        configurator = AgentConfiguratorFactory.create_configurator(
            agent_model=self.__agent_model,
            knowledge_base=self.__knowledge,
            storage_service=self.storage_service,
        )

        # Configurar y retornar el agente
        return configurator.configure()
