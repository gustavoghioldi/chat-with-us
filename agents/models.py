from knowledge.models import KnowledgeModel
from main.models import AppModel, models


# Create your models here.
class AgentModel(AppModel):
    name = models.CharField(max_length=255, unique=True)
    instructions = models.TextField()
    knoledge_text_models = models.ManyToManyField(KnowledgeModel, blank=True)
    agent_model_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="ID del modelo de IA utilizado por el agente",
    )
    tenant = models.ForeignKey(
        "tenants.TenantModel",
        on_delete=models.CASCADE,
        related_name="agents",
        help_text="Inquilino al que pertenece el agente",
        null=True,
        blank=True,
        default=None,
    )

    def __str__(self):
        return self.name
