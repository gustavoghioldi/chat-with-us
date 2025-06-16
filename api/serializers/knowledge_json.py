from rest_framework import serializers

class KnowlegdeJsonSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    content = serializers.JSONField()