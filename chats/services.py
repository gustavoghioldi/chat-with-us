
from django.utils import timezone
from chats.models import ChatModel
from chats.dtos import ChatContentDTO
from dataclasses import  asdict
from agents.models import AgentModel

class ChatService:
    def __init__(self, chat_id: str)->None:
        self.__chat_model: ChatModel = ChatModel.objects.get(session_id=chat_id)

    @staticmethod
    def new(agent_name: str)-> str:
        agent: AgentModel = AgentModel.objects.get(name = agent_name)
        return ChatModel.objects.create(agent = agent, content={"data":[]}).pk

    def append_content(self, request:str, response:str)->None:
        content : ChatContentDTO = ChatContentDTO(datetime=timezone.now().isoformat(), request=request, response=response)
        self.__chat_model.content["data"].append(asdict(content))
        self.__chat_model.save()
