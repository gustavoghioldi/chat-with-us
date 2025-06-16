from rest_framework import serializers

class KnowledgeTextViewSerializer(serializers.Serializer):
    """Serializer para la vista de texto de conocimiento."""

    name = serializers.CharField(max_length=255, required=True)
    content = serializers.CharField(required=True, allow_blank=False)