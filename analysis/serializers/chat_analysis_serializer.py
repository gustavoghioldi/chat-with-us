import time

from rest_framework import serializers

from analysis.models.sentiment_agents_model import SentimentAgentModel


class ChatAnalysisRequestSerializer(serializers.Serializer):
    """Serializer para la solicitud de análisis de chat"""

    chat = serializers.CharField(max_length=5000, help_text="Texto del chat a analizar")
    analyzer_name = serializers.SlugRelatedField(
        queryset=SentimentAgentModel.objects.all(),
        slug_field="name",
        help_text="Nombre del agente de sentimiento a utilizar para el análisis",
    )

    def validate_chat(self, value):
        """Validar que el chat no esté vacío"""
        if not value.strip():
            raise serializers.ValidationError("El chat no puede estar vacío")
        return value


class ChatAnalysisResponseSerializer(serializers.Serializer):
    """Serializer para la respuesta del análisis de chat"""

    VALUATION_CHOICES = [
        ("POSITIVE", "Positivo"),
        ("NEGATIVE", "Negativo"),
        ("NEUTRAL", "Neutral"),
    ]

    sentimient = serializers.ChoiceField(
        choices=VALUATION_CHOICES,
        default="NEUTRAL",
        help_text="Valoración del sentimiento del chat",
    )
    cause = serializers.CharField(max_length=500, help_text="Motivo de la valoración")
    log = serializers.CharField(max_length=500, help_text="Log del análisis realizado")
    timestamp = serializers.CharField(help_text="Timestamp del análisis")
