import logging
import re
from textwrap import dedent

from agno.agent import Agent
from agno.models.ollama import Ollama

from agents.models import AgentModel
from agents.services.agent_storage_service import AgentSessionService
from knowledge.services.document_knowledge_base_service import (
    DocumentKnowledgeBaseService,
)
from main.settings import IA_MODEL
from tools.services.toolkit_service import ToolkitService

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
        toolkit = ToolkitService(agent_name)
        knowledge_service = DocumentKnowledgeBaseService(agent_name)
        knowledge = knowledge_service.get_knowledge_base()
        storage_service = AgentSessionService()

        self.__agent = Agent(
            name=self.__agent_model.name,
            model=Ollama(id=IA_MODEL),
            instructions=dedent(
                f"""
                {self.__agent_model.instructions}
                """
            ),
            description=dedent(
                f"""
                {self.__agent_model.description or "Agente creado para responder preguntas y realizar tareas específicas."}
                """
            ),
            tools=toolkit.get_toolkit(),
            show_tool_calls=True,
            knowledge=knowledge,
            search_knowledge=True if knowledge else False,
            storage=storage_service.get_storage(),
            add_history_to_messages=True,
            num_history_responses=3,
            debug_mode=True,
        )

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
