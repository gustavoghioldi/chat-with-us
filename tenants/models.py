from django.contrib.auth.models import User
from django.db import models

from main.models import AppModel
from tenants.helpers import generate_cwu_token


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
            ("gemini", "GEMINI"),
        ],
        default="ollama",
    )

    ai_token = models.CharField(
        max_length=255, blank=True, null=True, default=None, help_text="Token de AI"
    )
    cwu_token = models.CharField(
        max_length=36,
        default=generate_cwu_token,
        help_text="Token único del tenant que comienza con 'cwu_'",
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Tenant"
        verbose_name_plural = "Tenants"
        ordering = ["name"]


class UserProfile(AppModel):
    """Perfil de usuario para extender el modelo User de Django con información del tenant."""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
        help_text="Usuario de Django asociado",
    )
    tenant = models.ForeignKey(
        TenantModel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
        help_text="Tenant asignado al usuario",
    )

    def __str__(self):
        tenant_name = self.tenant.name if self.tenant else "Sin tenant"
        return f"{self.user.username} - {tenant_name}"

    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuario"
        ordering = ["user__username"]
