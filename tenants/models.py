from django.db import models

from main.models import AppModel
# Create your models here.
class TenantModel(AppModel):
    """
    Modelo para representar un inquilino (tenant) en el sistema.
    Cada inquilino puede tener múltiples aplicaciones asociadas.
    """
    name = models.CharField(max_length=255, unique=True, help_text="Nombre del inquilino")
    description = models.TextField(blank=True, null=True, help_text="Descripción del inquilino")
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Tenant"
        verbose_name_plural = "Tenants"
        ordering = ['name']  # Ordenar por nombre de tenant