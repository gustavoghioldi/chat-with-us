from rest_framework import serializers

class KnowledegeWebScrapingSerializer(serializers.Serializer):
    """Serializer para la vista de web scraping de conocimiento."""

    name = serializers.CharField(max_length=255, required=True)
    url = serializers.URLField(required=True, allow_blank=False)
    max_depth = serializers.IntegerField(
        required=False,
        default=1,
        help_text="Profundidad máxima de scraping, por defecto 1",
    )
    max_links = serializers.IntegerField(
        required=False,
        default=1,
        help_text="Número máximo de enlaces a seguir, por defecto 1",
    )