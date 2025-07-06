import logging
import re

from agents.models import AgentModel
from agents.services.agent_factory_service import AgentFactoryService
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

        agent_factory = AgentFactoryService(
            agent_model=self.__agent_model,
            session_id=session_id,
            user_id=session_id,
        )
        self._agent = agent_factory.get_agent()

    def send_message(
        self, message: str, session_id: str, clean_respose: bool = True
    ) -> str:
        """Send a message to the agent and get a response."""
        response = self._agent.run(
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
