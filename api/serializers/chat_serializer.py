from rest_framework import serializers
from chats.models import ChatModel
from agents.models import AgentModel
class ChatSerializer(serializers.Serializer):
    agent = serializers.CharField(max_length=100)
    message = serializers.CharField(max_length=200)
    session_id = serializers.UUIDField(required=False)
    
    def validate(self, attrs):
        if not "session_id" in attrs:
            agent = AgentModel.objects.get(name = attrs["agent"])
            attrs["session_id"] = ChatModel.objects.create(agent = agent).pk
        return super().validate(attrs)