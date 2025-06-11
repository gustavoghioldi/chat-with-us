from agents.models import AgentModel
from chats.models import ChatModel, ContentChatModel


class ChatService:
    def __init__(self, chat_id: str) -> None:
        self.__chat_model: ChatModel = ChatModel.objects.get(session_id=chat_id)

    @staticmethod
    def new(agent_name: str) -> str:
        agent: AgentModel = AgentModel.objects.get(name=agent_name)
        return ChatModel.objects.create(agent=agent).pk

    def append_content(self, session_id: str, request: str, response: str) -> None:
        chat: ChatModel = ChatModel.objects.get(session_id=session_id)
        ContentChatModel.objects.create(chat=chat, request=request, response=response)
