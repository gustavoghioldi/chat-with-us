from django.db import models

from main.models import AppModel


# Create your models here.
class TenantModel(AppModel):
    """Tenant model to represent a client in the system.

    Each tenant can have multiple associated applications and users.
    """

    name = models.CharField(
        max_length=255, unique=True, help_text="Nombre del inquilino"
    )
    description = models.TextField(
        blank=True, null=True, help_text="Descripción del inquilino"
    )
    model = models.CharField(
        max_length=50,
        choices=[
            ("ollama", "OLLAMA"),
            ("bedrock", "BEDROCK"),
        ],
        default="ollama",
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Tenant"
        verbose_name_plural = "Tenants"
        ordering = ["name"]  # Ordenar por nombre de tenant
