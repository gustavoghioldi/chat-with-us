from typing import Literal

from agno.agent import Agent
from agno.models.ollama import Ollama
from pydantic import BaseModel, Field

from analysis.models.sentiment_agents_model import SentimentAgentModel
from main.settings import IA_MODEL


class SentimientScript(BaseModel):
    sentimient: Literal["POSITIVE", "NEGATIVE", "NEUTRAL"] = Field(
        ...,
        description="Clasifica el mensaje del usuario segun su sentimiento, en: POSITIVE, NEGATIVE o NEUTRAL",
        examples=["POSITIVE", "NEGATIVE", "NEUTRAL"],
    )
    cause: str = Field(
        ..., description="justifica la clasificacion del sentimiento", max_length=500
    )
    log: str = Field(
        ...,
        description="Log del analisis realizado, incluyendo el texto analizado y el sentimiento detectado",
        examples=["Analizado 55 caracteres de texto, sentimiento detectado: NEUTRO"],
        max_length=500,
    )


class sentimentChatScript(SentimientScript):
    sentimient: Literal["POSITIVE", "NEGATIVE", "NEUTRAL"] = Field(
        ...,
        description="totalmente el chat en: POSITIVE, NEGATIVE o NEUTRAL",
        examples=["POSITIVE", "NEGATIVE", "NEUTRAL"],
    )


class SentimentMessageService:
    @staticmethod
    def run(text, context) -> SentimientScript:
        structured_output_agent = Agent(
            model=Ollama(id=IA_MODEL),
            description="Eres un analista de los sentimientos de las frases enviadas por el usuario",
            instructions=(
                "Analiza el sentimiento del mensaje del usuario y clasificalo como POSITIVO, NEGATIVO o NEUTRO. "
                "Proporciona una justificación para la clasificación."
            ),
            context=context,
            response_model=SentimientScript,
        )

        # Run the agent synchronously
        response = structured_output_agent.run(text)
        return response.content


class SentimentChatService:
    @staticmethod
    def run(text, analyzer_name) -> sentimentChatScript:
        sentiment_model = SentimentAgentModel.objects.get(name=analyzer_name)
        context = f"""
            ##Palabras de Ejemplo:
            Frases de sentimientos NEGATIVAS: {sentiment_model.negative_tokens}
            Frases de sentimientos POSITIVAS: {sentiment_model.positive_tokens}
            Frases de sentimientos NEUTRAS: {sentiment_model.neutral_tokens}
        """
        structured_output_agent = Agent(
            model=Ollama(id=IA_MODEL),
            description="Eres un analista de los sentimientos del chat enviado por el usuario",
            instructions=(
                "Analiza el sentimiento del chat del usuario y clasificalo como POSITIVO, NEGATIVO o NEUTRO. "
                "Proporciona una justificación para la clasificación."
            ),
            context=context,
            response_model=sentimentChatScript,
        )

        # Run the agent synchronously
        response = structured_output_agent.run(text)
        return response.content
