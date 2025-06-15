from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from agents.models import AgentModel
from api.permissions_classes.is_tenant_authenticated import IsTenantAuthenticated
from api.serializers.agent_serializer import (
    AgentModelCreateSerializer,
    AgentModelListSerializer,
    AgentModelSerializer,
)


class AgentModelViewSet(viewsets.ModelViewSet):
    """
    ViewSet para manejar operaciones CRUD del modelo AgentModel.

    Endpoints disponibles:
    - GET /api/agents/ - Listar todos los agentes
    - POST /api/agents/ - Crear un nuevo agente
    - GET /api/agents/{id}/ - Obtener un agente específico
    - PUT /api/agents/{id}/ - Actualizar completamente un agente
    - PATCH /api/agents/{id}/ - Actualizar parcialmente un agente
    - DELETE /api/agents/{id}/ - Eliminar un agente
    - GET /api/agents/by-tenant/{tenant_id}/ - Obtener agentes por tenant
    """

    queryset = AgentModel.objects.all()
    serializer_class = AgentModelSerializer
    permission_classes = [IsTenantAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["tenant", "agent_model_id"]
    search_fields = ["name", "instructions"]
    ordering_fields = ["name", "created_at", "updated_at"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        """Seleccionar el serializer apropiado según la acción."""
        if self.action == "create":
            return AgentModelCreateSerializer
        elif self.action == "list":
            return AgentModelListSerializer
        return AgentModelSerializer

    def get_queryset(self):
        """Optimizar consultas con select_related y prefetch_related."""
        return AgentModel.objects.select_related("tenant").prefetch_related(
            "knoledge_text_models"
        )

    def create(self, request, *args, **kwargs):
        """Crear un nuevo agente."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        agent = serializer.save()

        # Retornar el agente creado con el serializer completo
        response_serializer = AgentModelSerializer(agent)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """Actualizar un agente."""
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        agent = serializer.save()

        # Retornar el agente actualizado
        response_serializer = AgentModelSerializer(agent)
        return Response(response_serializer.data)

    @action(detail=False, methods=["get"], url_path="by-tenant/(?P<tenant_id>[^/.]+)")
    def by_tenant(self, request, tenant_id=None):
        """Obtener agentes filtrados por tenant."""
        try:
            agents = self.get_queryset().filter(tenant_id=tenant_id)
            page = self.paginate_queryset(agents)

            if page is not None:
                serializer = AgentModelListSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = AgentModelListSerializer(agents, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {"error": f"Error al obtener agentes por tenant: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=True, methods=["post"])
    def add_knowledge(self, request, pk=None):
        """Agregar modelos de conocimiento a un agente."""
        agent = self.get_object()
        knowledge_ids = request.data.get("knowledge_ids", [])

        if not knowledge_ids:
            return Response(
                {"error": "Se requiere una lista de knowledge_ids"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            agent.knoledge_text_models.add(*knowledge_ids)
            serializer = AgentModelSerializer(agent)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {"error": f"Error al agregar conocimiento: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=True, methods=["post"])
    def remove_knowledge(self, request, pk=None):
        """Remover modelos de conocimiento de un agente."""
        agent: AgentModel = self.get_object()
        knowledge_ids = request.data.get("knowledge_ids", [])

        if not knowledge_ids:
            return Response(
                {"error": "Se requiere una lista de knowledge_ids"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            agent.knoledge_text_models.remove(*knowledge_ids)
            serializer = AgentModelSerializer(agent)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {"error": f"Error al remover conocimiento: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=False, methods=["get"])
    def search(self, request):
        """Búsqueda avanzada de agentes."""
        query = request.query_params.get("q", "")
        tenant_id = request.query_params.get("tenant_id", "")

        if not query:
            return Response(
                {"error": 'Se requiere el parámetro de búsqueda "q"'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        agents = self.get_queryset().filter(
            Q(name__icontains=query) | Q(instructions__icontains=query)
        )

        if tenant_id:
            agents = agents.filter(tenant_id=tenant_id)

        page = self.paginate_queryset(agents)
        if page is not None:
            serializer = AgentModelListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = AgentModelListSerializer(agents, many=True)
        return Response(serializer.data)
