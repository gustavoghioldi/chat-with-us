import uuid
from main.models import AppModel, models

from agents.models import AgentModel

class ChatModel(AppModel):
    agent = models.ForeignKey(AgentModel, on_delete=models.CASCADE)
    session_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    content = models.JSONField(blank=True, null=True, default=dict)
