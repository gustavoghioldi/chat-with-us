from rest_framework import serializers

from main.settings import KNOWKEDGE_TEXT_MAX_CHARS


class KnowledgeTextSerializer(serializers.Serializer):
    """Serializer para la vista de texto de conocimiento."""

    name = serializers.CharField(max_length=255, required=True)
    content = serializers.CharField(
        max_length=KNOWKEDGE_TEXT_MAX_CHARS, required=True, allow_blank=False
    )
