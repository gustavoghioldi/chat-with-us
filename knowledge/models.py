from documents.models import DocumentModel
from main.models import AppModel, models

# Create your models here.


class KnowledgeModel(AppModel):
    CHOICES = [
        ("plain_document", "plain_document"),
        ("website", "website"),
        ("document", "document"),
    ]

    name = models.CharField(max_length=255, unique=True)
    url = models.URLField(blank=True)
    document = models.ForeignKey(
        DocumentModel,
        on_delete=models.SET_NULL,
        related_name="knowledge_models",
        null=True,
        blank=True,
        help_text="Documento asociado a este modelo de conocimiento",
    )
    text = models.TextField(blank=True)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, choices=CHOICES)
    tenant = models.ForeignKey(
        "tenants.TenantModel",
        on_delete=models.CASCADE,
        related_name="knowledge_models",
        help_text="Tenant asociado a este modelo de conocimiento",
        null=True,
        blank=True,
        default=None,
    )
    recreate = models.BooleanField(
        default=True,
        help_text="Indica si el modelo de conocimiento necesita ser recreado",
    )

    def __str__(self):
        return self.name
