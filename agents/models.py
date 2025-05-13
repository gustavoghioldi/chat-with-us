from main.models import AppModel, models
from knowledge.models import KnowledgeModel
# Create your models here.
class AgentModel(AppModel):
    name = models.CharField(max_length=255, unique=True)
    instructions = models.TextField()
    knoledge_text_models = models.ManyToManyField(KnowledgeModel, blank=True)

    def __str__(self):
        return self.name