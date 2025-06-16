from rest_framework import serializers


class KnowledgeJsonSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    content = serializers.ListField(
        child=serializers.JSONField(),
        allow_empty=False,
        required=True,
        max_length=1000,
    )
