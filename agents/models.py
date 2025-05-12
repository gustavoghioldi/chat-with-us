from main.models import AppModel, models
# Create your models here.
class AgentModel(AppModel):
    name = models.CharField(max_length=255, unique=True)
    instructions = models.TextField()

    def __str__(self):
        return self.name