import re
import logging
from textwrap import dedent
from agno.agent import Agent
from agno.models.ollama import Ollama
from agents.models import AgentModel
from main.settings import IA_MODEL
from agno.agent import Agent
from agents.services.agent_storage_service import AgentSessionService
from knowledge.services.document_knowledge_base_service import DocumentKnowledgeBaseService
logger = logging.getLogger(__name__)

class AgentService:
    def __init__(self, agent_name:str)->None:
        agent_model = AgentModel.objects.get(name=agent_name)

        knowledge_service =  DocumentKnowledgeBaseService(agent_name)

        storage_service = AgentSessionService()

        self.__agent = Agent(
            model= Ollama(id=IA_MODEL),
            instructions=dedent(
                f"""
                {agent_model.instructions}
                """
            ),
            knowledge=knowledge_service.get_knowledge_base(),
            storage = storage_service.get_storage(),
            add_history_to_messages=True,
            num_history_responses=3,
            debug_mode=True,
            
            )
        
            

    def send_message(self, message: str, session_id:str, clean_respose:bool=True) -> str:
        """
        Send a message to the agent and get a response.
        """
        response = self.__agent.run(message, session_id=str(session_id))
        if clean_respose:
            response = self.__clean_response(response.content), response.session_id
        return response[0] , response[1]
    
    def __clean_response(self, response:str)-> str:
        return re.sub(r"<think>.*?</think>", "", response, flags=re.DOTALL).strip()

