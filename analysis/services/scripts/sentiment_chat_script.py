from typing import Literal

from pydantic import Field

from analysis.services.scripts.sentiment_script import SentimientScript


class SentimentChatScript(SentimientScript):
    """
    Script específico para análisis de sentimientos de chats completos.

    Extiende SentimientScript con configuraciones específicas para análisis de chat.
    """

    sentimient: Literal["POSITIVE", "NEGATIVE", "NEUTRAL"] = Field(
        ...,
        description="Analiza totalmente el chat en: POSITIVE, NEGATIVE o NEUTRAL",
        examples=["POSITIVE", "NEGATIVE", "NEUTRAL"],
    )
