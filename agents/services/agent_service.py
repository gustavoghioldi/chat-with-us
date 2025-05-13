import re
import os
import logging
from textwrap import dedent

from agno.agent import Agent
from agno.embedder.ollama import OllamaEmbedder
from agno.models.ollama import Ollama

from agents.models import AgentModel
from main.settings import IA_MODEL
from agno.agent import Agent
from agno.document.base import Document
from agno.knowledge.document import DocumentKnowledgeBase
from agno.vectordb.pgvector import PgVector
from agents.services.agent_storage_service import AgentSessionService

logger = logging.getLogger(__name__)



class AgentService:
    def __init__(self, agent_name:str)->None:
        agent_model = AgentModel.objects.get(name=agent_name)
        
  
        documents = [Document(content=agent_model.knoledge_text_models.all()[0].text)]
        db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"
        
        knowledge_base = DocumentKnowledgeBase(
            documents=documents,
            vector_db=PgVector(
                table_name="ia_documents",
                db_url=db_url,
                embedder=OllamaEmbedder(id="llama3.2:3b", dimensions=3072),
            ),
        )
        knowledge_base.load(recreate=False)

        storage_service = AgentSessionService()
        

        self.__agent = Agent(
            model= Ollama(id="llama3.2:3b"),
            instructions=dedent(
                f"""
                {agent_model.instructions}
                """
            ),
            knowledge=knowledge_base,
            storage = storage_service.get_storage(),
            add_history_to_messages=True,
            num_history_responses=3
            )
        
            

    def send_message(self, message: str, session_id:str, clean_respose:bool=True) -> str:
        """
        Send a message to the agent and get a response.
        """
        response = self.__agent.run(message, session_id=str(session_id))
        if clean_respose:
            response = self.__clean_response(response.content)
        return response
    
    def __clean_response(self, response:str)-> str:
        return re.sub(r"<think>.*?</think>", "", response, flags=re.DOTALL).strip()

