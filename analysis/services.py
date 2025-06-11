from typing import Literal

from agno.agent import Agent
from agno.models.ollama import Ollama
from pydantic import BaseModel, Field

from main.settings import IA_MODEL


class SentimientScript(BaseModel):
    sentimient: Literal["POSITIVO", "NEGATIVO", "NEUTRO"] = Field(
        ...,
        description="Clasifica el mensaje del usuario segun su sentimiento, en: POSITIVO, NEGATIVO o NEUTRO",
        examples=["POSITIVO", "NEGATIVO", "NEUTRO"],
    )
    cause: str = Field(..., description="justifica la clasificacion del sentimiento")


class SentimentMessageService:
    @staticmethod
    def run(text) -> SentimientScript:
        structured_output_agent = Agent(
            model=Ollama(id=IA_MODEL),
            description="analizas los sentimientos de las frases enviadas por el usuario",
            response_model=SentimientScript,
        )

        # Run the agent synchronously
        response = structured_output_agent.run(text)
        return response.content
