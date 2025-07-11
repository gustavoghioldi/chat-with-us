from rest_framework.response import Response
from rest_framework.views import APIView

from agents.services.agent_service import AgentService
from api.permissions_classes.is_tenant_authenticated import IsTenantAuthenticated
from api.serializers.chat_serializer import ChatSerializer
from chats.services import ChatService
from quota.services.quota_service import QuotaService


class ChatView(APIView):
    permission_classes = [IsTenantAuthenticated]

    def post(self, request):
        serializer = ChatSerializer(data=request.data)
        if serializer.is_valid():
            message = serializer.validated_data["message"]
            session_id = serializer.validated_data.get("session_id")
            agent = serializer.validated_data["agent"]
            agent_service = AgentService(agent, session_id)
            # Verificar que el agente pertenezca al tenant autenticado
            if hasattr(request, "tenant") and request.tenant:
                if agent_service.get_agent_model().tenant != request.tenant:
                    return Response(
                        {"error": "El agente no pertenece al tenant autenticado"},
                        status=403,
                    )
            # Validación y consumo de tokens + ejecución del mensaje
            try:
                text, session_id = QuotaService.process_agent_request(
                    agent=agent_service,
                    tenant=request.tenant,
                    prompt=message,
                    session_id=session_id
                )
            except Exception as e:
                return Response({"error": str(e)}, status=403)

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