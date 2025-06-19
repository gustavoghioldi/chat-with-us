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
    path = models.CharField(max_length=255, blank=True, null=True)
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

    def save(self, *args, **kwargs):
        """
        Sobrescribir el método save para establecer recreate=True en cada edición.
        """
        # Si el objeto ya existe (no es una creación), establecer recreate=True
        if self.pk is not None:
            self.recreate = True
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
