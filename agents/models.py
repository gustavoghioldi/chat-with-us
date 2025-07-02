from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator

from knowledge.models import KnowledgeModel
from main.models import AppModel, models
from tools.models.api_call_model import ApiCallModel


# Create your models here.
class AgentModel(AppModel):
    name = models.CharField(max_length=255, unique=True)
    instructions = models.TextField()
    description = models.TextField(
        blank=True,
        null=True,
        default="Agente creado para responder preguntas y realizar tareas específicas.",
        help_text="Descripción del agente, opcional",
    )
    knoledge_text_models = models.ManyToManyField(KnowledgeModel, blank=True)
    api_call_models = models.ManyToManyField(ApiCallModel, blank=True)
    max_tokens = models.PositiveIntegerField(
        default=100,
        help_text="Número máximo de tokens a predecir en la respuesta del agente",
    )
    temperature = models.FloatField(
        default=0.7,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Controla la aleatoriedad de las respuestas del agente (0.0 a 1.0)",
    )
    top_p = models.FloatField(
        default=0.9,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Controla la diversidad de las respuestas del agente (0.0 a 1.0)",
    )

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

    analize_sentiment = models.ForeignKey(
        "analysis.SentimentAgentModel",
        default=None,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="agents",
        help_text="Agente de análisis de sentimientos asociado al agente",
    )

    def __str__(self):
        return self.name

    def clean(self):
        """
        Validaciones personalizadas para el modelo AgentModel.
        """
        super().clean()

        # Validar temperature
        if self.temperature is not None:
            if self.temperature < 0.0 or self.temperature > 1.0:
                raise ValidationError(
                    {
                        "temperature": "El valor de temperatura debe estar entre 0.0 y 1.0"
                    }
                )

        # Validar top_p
        if self.top_p is not None:
            if self.top_p < 0.0 or self.top_p > 1.0:
                raise ValidationError(
                    {"top_p": "El valor de top_p debe estar entre 0.0 y 1.0"}
                )

    def save(self, *args, **kwargs):
        """
        Override del método save para ejecutar validaciones completas.
        """
        self.full_clean()  # Ejecuta las validaciones del modelo
        super().save(*args, **kwargs)
