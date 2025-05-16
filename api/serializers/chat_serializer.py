from rest_framework import serializers
from chats.services import ChatService

class ChatSerializer(serializers.Serializer):
    agent = serializers.CharField(max_length=100)
    message = serializers.CharField(max_length=200)
    session_id = serializers.UUIDField(required=False)
    
    def validate(self, attrs):
        if not "session_id" in attrs:
            attrs["session_id"] = ChatService.new(attrs["agent"])
            attrs["new"] = True
    
        return super().validate(attrs)
