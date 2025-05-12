import re
import os
import logging
from textwrap import dedent

from agno.agent import Agent
from agno.models.openai import OpenAIChat

from main.settings import IA_MODEL

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from agents.models import AgentModel

logger = logging.getLogger(__name__)

class AgentService:
    def __init__(self, agent_model:"AgentModel"):
        self.__agent = Agent(
            model= OpenAIChat(IA_MODEL),
            instructions=dedent(
                f"""
                {agent_model.instructions}
                """
            ),
            )
        
    def send_message(self, message: str, clean_respose:bool=True) -> str:
        """
        Send a message to the agent and get a response.
        """
        response = self.__agent.run(message)
        if clean_respose:
            response = self.__clean_response(response.content)
        return response
    
    def __clean_response(self, response:str)-> str:
        return re.sub(r"<think>.*?</think>", "", response, flags=re.DOTALL).strip()

