import uuid

from agents.models import AgentModel
from main.models import AppModel, models


class ChatModel(AppModel):
    agent = models.ForeignKey(AgentModel, on_delete=models.CASCADE)
    session_id = models.UUIDField(primary_key=True, default=uuid.uuid4)


class ContentChatModel(AppModel):
    chat = models.ForeignKey(ChatModel, on_delete=models.CASCADE)
    request = models.TextField()
    response = models.TextField()
