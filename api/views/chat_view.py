from rest_framework.response import Response
from rest_framework.views import APIView

from agents.services.agent_service import AgentService
from api.serializers.chat_serializer import ChatSerializer
from chats.services import ChatService
from chats.signals.content_chat_emit import new_chat_text

# Create your views here.


class ChatView(APIView):
    def post(self, request):
        serializer = ChatSerializer(data=request.data)
        if serializer.is_valid():
            agent = serializer.validated_data["agent"]
            message = serializer.validated_data["message"]
            session_id = serializer.validated_data.get("session_id")
            agent_service = AgentService(agent)
            text, session_id = agent_service.send_message(message, session_id)
            response = {
                "agent": agent,
                "message": message,
                "session_id": session_id,
                "response": text,
            }
            chat_service = ChatService(session_id)
            chat_service.append_content(
                session_id=session_id, request=message, response=response["response"]
            )
            return Response(response, status=200)
        else:
            return Response(serializer.errors, status=400)
