from rest_framework.views import APIView
from agents.models import AgentModel
from api.serializers.chat_serializer import ChatSerializer
from rest_framework.response import Response
from agents.services import AgentService
# Create your views here.

class ChatView(APIView):
    def post(self, request):
        serializer = ChatSerializer(data=request.data)
        if serializer.is_valid():
            agent = serializer.validated_data['agent']
            message = serializer.validated_data['message']
            session_id = serializer.validated_data['session_id']
            agent_models = AgentModel.objects.get(name=agent)
            agent_service = AgentService(agent_models)
            response = {
                'agent': agent,
                'message': message,
                'session_id': session_id,
                'response': agent_service.send_message(message),
            }
            
            return Response(response, status=200)
        else:
            return Response(serializer.errors, status=400)