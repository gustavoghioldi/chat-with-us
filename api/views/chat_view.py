from rest_framework.views import APIView
from api.serializers.chat_serializer import ChatSerializer
from rest_framework.response import Response
from agents.services.agent_service import AgentService
from chats.services import ChatService
# Create your views here.

class ChatView(APIView):
    def post(self, request):
        serializer = ChatSerializer(data=request.data)
        if serializer.is_valid():
            agent = serializer.validated_data['agent']
            message = serializer.validated_data['message']
            session_id = serializer.validated_data['session_id']
            agent_service = AgentService(agent)
            response = {
                'agent': agent,
                'message': message,
                'session_id': session_id,
                'response': agent_service.send_message(message, session_id),
            }
            chat_service = ChatService(session_id)
            chat_service.append_content(request=message, response=response['response'])
            return Response(response, status=200)
        else:
            return Response(serializer.errors, status=400)