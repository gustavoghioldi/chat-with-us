from rest_framework import serializers

from agents.models import AgentModel
from knowledge.models import KnowledgeModel
from tenants.models import TenantModel


class AgentModelSerializer(serializers.ModelSerializer):
    """Serializer para el modelo AgentModel."""

    knoledge_text_models = serializers.PrimaryKeyRelatedField(
        many=True, queryset=KnowledgeModel.objects.all(), required=False
    )
    tenant = serializers.PrimaryKeyRelatedField(
        queryset=TenantModel.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = AgentModel
        fields = [
            "id",
            "name",
            "instructions",
            "knoledge_text_models",
            "agent_model_id",
            "tenant",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ("id", "created_at", "updated_at")

    def validate_name(self, value):
        """Validar que el nombre sea único."""
        if AgentModel.objects.filter(name=value).exists():
            if self.instance and self.instance.name == value:
                return value
            raise serializers.ValidationError("Ya existe un agente con este nombre.")
        return value


class AgentModelCreateSerializer(AgentModelSerializer):
    """Serializer específico para la creación de agentes."""

    class Meta(AgentModelSerializer.Meta):
        fields = [
            "name",
            "instructions",
            "knoledge_text_models",
            "agent_model_id",
            "tenant",
        ]


class AgentModelListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listas de agentes."""

    tenant_name = serializers.CharField(source="tenant.name", read_only=True)
    knowledge_count = serializers.SerializerMethodField()

    class Meta:
        model = AgentModel
        fields = [
            "id",
            "name",
            "agent_model_id",
            "tenant_name",
            "knowledge_count",
            "created_at",
            "updated_at",
        ]

    def get_knowledge_count(self, obj):
        """Obtener el número de modelos de conocimiento asociados."""
        return obj.knoledge_text_models.count()
