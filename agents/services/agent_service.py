import logging
import re
from textwrap import dedent

from agents.models import AgentModel
from agents.services.agent_service_configure import AgentServiceConfigure
from agents.services.agent_storage_service import AgentSessionService
from knowledge.services.document_knowledge_base_service import (
    DocumentKnowledgeBaseService,
)
from tools.kit.obtener_datos_de_factura import *

logger = logging.getLogger(__name__)


class AgentService:
    def __init__(self, agent_name: str, session_id=None) -> None:
        # Obtener el agente directamente de la base de datos
        try:
            self.__agent_model = AgentModel.objects.select_related("tenant").get(
                name=agent_name
            )
        except AgentModel.DoesNotExist:
            raise AgentModel.DoesNotExist(f"Agent {agent_name} not found")
        # toolkit = [obtener_datos_de_factura]
        agent_service_configure = AgentServiceConfigure(self.__agent_model)
        self.__agent = agent_service_configure.configure()

    def send_message(
        self, message: str, session_id: str, clean_respose: bool = True
    ) -> str:
        """Send a message to the agent and get a response."""
        response = self.__agent.run(
            message, session_id=str(session_id), user_id=str(session_id)
        )
        if clean_respose:
            response = self.__clean_response(response.content), response.session_id
        return response[0], response[1]

    def __clean_response(self, response: str) -> str:
        return re.sub(r"<think>.*?</think>", "", response, flags=re.DOTALL).strip()

    def get_agent_model(self) -> Agent:
        """Get the agent instance."""
        return self.__agent_model
