from typing import Literal

from pydantic import BaseModel, Field


class SentimientScript(BaseModel):
    """
    Script base para análisis de sentimientos.

    Define la estructura común para respuestas de análisis de sentimientos.
    """

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
