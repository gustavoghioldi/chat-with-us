from main.models import AppModel, models


class SentimentAgentModel(AppModel):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    negative_tokens = models.TextField(
        help_text="Lista de tokens negativos, separados por comas."
    )
    positive_tokens = models.TextField(
        help_text="Lista de tokens positivos, separados por comas."
    )
    neutral_tokens = models.TextField(
        help_text="Lista de tokens neutrales, separados por comas."
    )
    tenant = models.ForeignKey(
        "tenants.TenantModel", on_delete=models.CASCADE, related_name="sentiment_agents"
    )

    class Meta:
        verbose_name = "Agente de Sentimiento"
        verbose_name_plural = "Agentes de Sentimiento"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.tenant.name if self.tenant else 'Sin tenant'})"

    def get_positive_tokens_list(self):
        """Retorna la lista de tokens positivos."""
        if not self.positive_tokens:
            return []
        return [
            token.strip() for token in self.positive_tokens.split(",") if token.strip()
        ]

    def get_negative_tokens_list(self):
        """Retorna la lista de tokens negativos."""
        if not self.negative_tokens:
            return []
        return [
            token.strip() for token in self.negative_tokens.split(",") if token.strip()
        ]

    def get_neutral_tokens_list(self):
        """Retorna la lista de tokens neutrales."""
        if not self.neutral_tokens:
            return []
        return [
            token.strip() for token in self.neutral_tokens.split(",") if token.strip()
        ]

    def get_total_tokens_count(self):
        """Retorna el número total de tokens configurados."""
        return (
            len(self.get_positive_tokens_list())
            + len(self.get_negative_tokens_list())
            + len(self.get_neutral_tokens_list())
        )
