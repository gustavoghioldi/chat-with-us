from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.permissions_classes.is_tenant_authenticated import IsTenantAuthenticated
from api.serializers.knowledge_csv_serializer import KnowledgeCSVSerializer
from api.serializers.knowledge_json_serializer import KnowledgeJsonSerializer
from api.serializers.knowledge_text_serializer import KnowledgeTextSerializer
from api.serializers.knowledge_web_scraping_serializer import (
    KnowledgeWebScrapingSerializer,
)
from knowledge.models import KnowledgeModel
from knowledge.services.content_formatter_service import ContentFormatterService


class KnowledgeViewSet(viewsets.ModelViewSet):
    """
    ViewSet para manejar operaciones CRUD del modelo KnowledgeModel.

    El serializer se selecciona automáticamente según el tipo especificado en la URL:
    - /api/v1/knowledge/text/ -> KnowledgeTextSerializer
    - /api/v1/knowledge/json/ -> KnowlegdeJsonSerializer
    - /api/v1/knowledge/csv/ -> KnowledgeCSVSerializer
    - /api/v1/knowledge/web-scraping/ -> KnowledegeWebScrapingSerializer
    """

    queryset = KnowledgeModel.objects.all()
    permission_classes = [IsTenantAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["category", "tenant"]
    search_fields = ["name", "description", "text"]
    ordering_fields = ["name", "created_at", "updated_at"]
    ordering = ["-created_at"]

    # Mapeo de tipos de knowledge a serializers
    SERIALIZER_MAPPING = {
        "text": KnowledgeTextSerializer,
        "json": KnowledgeJsonSerializer,
        "csv": KnowledgeCSVSerializer,
        "web-scraping": KnowledgeWebScrapingSerializer,
    }

    # Mapeo de tipos a categorías del modelo
    CATEGORY_MAPPING = {
        "text": "plain_document",
        "json": "plain_document",
        "csv": "plain_document",
        "web-scraping": "website",
    }

    def get_serializer_class(self):
        """Seleccionar el serializer según el tipo en la URL."""
        knowledge_type = self.kwargs.get("knowledge_type")

        if knowledge_type in self.SERIALIZER_MAPPING:
            return self.SERIALIZER_MAPPING[knowledge_type]

        # Serializer por defecto si no se especifica tipo
        return KnowledgeTextSerializer

    def get_queryset(self):
        """
        Optimizar consultas y filtrar por tenant automáticamente.

        Solo retorna modelos de conocimiento que pertenecen al tenant autenticado.
        """
        queryset = KnowledgeModel.objects.select_related("tenant")

        # Filtrar por tenant si está disponible en la request
        if hasattr(self.request, "tenant") and self.request.tenant:
            queryset = queryset.filter(tenant=self.request.tenant)

        return queryset

    def create(self, request, *args, **kwargs):
        """Crear un nuevo modelo de conocimiento."""
        knowledge_type = self.kwargs.get("knowledge_type")
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data)

        if serializer.is_valid():
            # Preparar datos para crear el modelo
            validated_data = serializer.validated_data
            knowledge_data = {
                "name": validated_data["name"],
                "category": self.CATEGORY_MAPPING.get(knowledge_type, "plain_document"),
                "tenant": (
                    request.tenant
                    if hasattr(request, "tenant") and request.tenant
                    else None
                ),
            }

            # Procesar contenido según el tipo
            if knowledge_type == "text":
                knowledge_data["text"] = validated_data["content"]
                knowledge_data["description"] = (
                    f"Documento de texto: {validated_data['name']}"
                )

            elif knowledge_type == "json":
                # Convertir el contenido JSON a formato Markdown usando el servicio
                markdown_content = ContentFormatterService.json_to_markdown(
                    validated_data["content"], validated_data["name"]
                )
                knowledge_data["text"] = markdown_content
                knowledge_data["description"] = (
                    f"Datos JSON convertidos a Markdown: {validated_data['name']}"
                )

            elif knowledge_type == "csv":
                # Convertir el contenido CSV a formato Markdown usando el servicio
                markdown_content = ContentFormatterService.csv_to_markdown(
                    validated_data["content"], validated_data["name"]
                )
                knowledge_data["text"] = markdown_content
                knowledge_data["description"] = (
                    f"Datos CSV convertidos a Markdown: {validated_data['name']}"
                )

            elif knowledge_type == "web-scraping":
                knowledge_data["url"] = validated_data["url"]
                knowledge_data["description"] = (
                    f"Web scraping de: {validated_data['url']}"
                )
                # Aquí podrías agregar lógica de scraping
                knowledge_data["text"] = (
                    f"Configuración de scraping - URL: {validated_data['url']}, Max depth: {validated_data.get('max_depth', 1)}, Max links: {validated_data.get('max_links', 1)}"
                )

            # Crear el modelo
            knowledge = KnowledgeModel.objects.create(**knowledge_data)

            return Response(
                {
                    "id": knowledge.id,
                    "name": knowledge.name,
                    "category": knowledge.category,
                    "type": knowledge_type,
                    "created_at": knowledge.created_at,
                    "message": f'Modelo de conocimiento "{knowledge.name}" creado exitosamente.',
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """Actualizar un modelo de conocimiento."""
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        knowledge_type = self.kwargs.get("knowledge_type")

        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data, partial=partial)

        if serializer.is_valid():
            validated_data = serializer.validated_data

            # Actualizar campos básicos
            if "name" in validated_data:
                instance.name = validated_data["name"]

            # Actualizar contenido según el tipo
            if knowledge_type == "text" and "content" in validated_data:
                instance.text = validated_data["content"]

            elif knowledge_type == "json" and "content" in validated_data:
                # Convertir el contenido JSON a formato Markdown usando el servicio
                markdown_content = ContentFormatterService.json_to_markdown(
                    validated_data["content"], validated_data.get("name", instance.name)
                )
                instance.text = markdown_content

            elif knowledge_type == "csv" and "content" in validated_data:
                # Convertir el contenido CSV a formato Markdown usando el servicio
                markdown_content = ContentFormatterService.csv_to_markdown(
                    validated_data["content"], validated_data.get("name", instance.name)
                )
                instance.text = markdown_content

            elif knowledge_type == "web-scraping":
                if "url" in validated_data:
                    instance.url = validated_data["url"]
                # Actualizar configuración de scraping
                max_depth = validated_data.get("max_depth", 1)
                max_links = validated_data.get("max_links", 1)
                instance.text = f"Configuración de scraping - URL: {instance.url}, Max depth: {max_depth}, Max links: {max_links}"

            instance.save()

            return Response(
                {
                    "id": instance.id,
                    "name": instance.name,
                    "category": instance.category,
                    "type": knowledge_type,
                    "updated_at": instance.updated_at,
                    "message": f'Modelo de conocimiento "{instance.name}" actualizado exitosamente.',
                }
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # :smartphone:
    def retrieve(self, request, *args, **kwargs):
        """Obtener un modelo de conocimiento específico."""
        instance = self.get_object()
        knowledge_type = self.kwargs.get("knowledge_type")

        # Preparar la respuesta según el tipo
        response_data = {
            "id": instance.id,
            "name": instance.name,
            "category": instance.category,
            "type": knowledge_type,
            "tenant": instance.tenant.name if instance.tenant else None,
            "created_at": instance.created_at,
            "updated_at": instance.updated_at,
        }

        # Agregar contenido específico según el tipo
        if knowledge_type == "text":
            response_data["content"] = instance.text

        elif knowledge_type == "json":
            try:
                import json

                response_data["content"] = (
                    json.loads(instance.text) if instance.text else []
                )
            except json.JSONDecodeError:
                response_data["content"] = []

        elif knowledge_type == "csv":
            response_data["content"] = instance.text

        elif knowledge_type == "web-scraping":
            response_data["url"] = instance.url
            response_data["description"] = instance.description

        return Response(response_data)

    def list(self, request, *args, **kwargs):
        """Listar modelos de conocimiento con filtros opcionales."""
        knowledge_type = self.kwargs.get("knowledge_type")
        queryset = self.filter_queryset(self.get_queryset())

        # Filtrar por categoría según el tipo si se especifica
        if knowledge_type:
            category = self.CATEGORY_MAPPING.get(knowledge_type)
            if category:
                queryset = queryset.filter(category=category)

        page = self.paginate_queryset(queryset)

        if page is not None:
            data = self._serialize_list(page, knowledge_type)
            return self.get_paginated_response(data)

        data = self._serialize_list(queryset, knowledge_type)
        return Response(data)

    def _serialize_list(self, queryset, knowledge_type):
        """Serializar lista de modelos para la respuesta."""
        return [
            {
                "id": item.id,
                "name": item.name,
                "category": item.category,
                "type": knowledge_type,
                "tenant": item.tenant.name if item.tenant else None,
                "created_at": item.created_at,
                "updated_at": item.updated_at,
                "has_content": bool(item.text or item.url),
            }
            for item in queryset
        ]
