from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from tenants.models import TenantModel

from .models import DocumentModel
from .serializers import (
    BulkUpdateSerializer,
    DocumentListSerializer,
    DocumentModelSerializer,
    DocumentStatsSerializer,
    DocumentUploadSerializer,
)
from .services import DocumentService


class DocumentModelViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar documentos.

    Proporciona operaciones CRUD completas más acciones personalizadas
    para gestión de documentos por tenant.
    """

    serializer_class = DocumentModelSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    # Filtros
    filterset_fields = ["document_type", "is_active", "is_processed", "uploaded_by"]
    search_fields = ["title", "description", "original_filename"]
    ordering_fields = ["created_at", "updated_at", "title", "file_size"]
    ordering = ["-created_at"]

    def get_queryset(self):
        """
        Filtrar documentos por tenant del usuario.
        Solo mostrar documentos del tenant al que pertenece el usuario.
        """
        # Aquí asumo que tienes una relación user -> tenant
        # Ajusta según tu implementación de tenants
        user = self.request.user

        # Obtener el tenant del usuario (ajustar según tu modelo)
        try:
            user_profile = user.userprofile
            tenant = user_profile.tenant
        except:
            # Si no hay relación con tenant, no mostrar documentos
            return DocumentModel.objects.none()

        return DocumentService.get_documents_by_tenant(tenant)

    def get_serializer_class(self):
        """Usar diferentes serializers según la acción"""
        if self.action == "list":
            return DocumentListSerializer
        elif self.action == "create":
            return DocumentUploadSerializer
        elif self.action == "bulk_update":
            return BulkUpdateSerializer
        elif self.action == "stats":
            return DocumentStatsSerializer
        return DocumentModelSerializer

    def perform_create(self, serializer):
        """Asignar tenant y usuario al crear documento"""
        user = self.request.user

        # Obtener tenant del usuario
        try:
            user_profile = user.userprofile
            tenant = user_profile.tenant
        except:
            raise ValidationError("Usuario no tiene tenant asignado")

        serializer.save(uploaded_by=user, tenant=tenant)

    def retrieve(self, request, pk=None):
        """Obtener un documento específico"""
        user = request.user
        try:
            user_profile = user.userprofile
            tenant = user_profile.tenant
        except:
            return Response(
                {"error": "Usuario no tiene tenant asignado"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        document = DocumentService.get_document_by_id(pk, tenant)
        if not document:
            return Response(
                {"error": "Documento no encontrado"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(document)
        return Response(serializer.data)

    def update(self, request, pk=None):
        """Actualizar documento"""
        user = request.user
        try:
            user_profile = user.userprofile
            tenant = user_profile.tenant
        except:
            return Response(
                {"error": "Usuario no tiene tenant asignado"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        document = DocumentService.get_document_by_id(pk, tenant)
        if not document:
            return Response(
                {"error": "Documento no encontrado"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(document, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """Eliminar documento (soft delete por defecto)"""
        user = request.user
        try:
            user_profile = user.userprofile
            tenant = user_profile.tenant
        except:
            return Response(
                {"error": "Usuario no tiene tenant asignado"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        document = DocumentService.get_document_by_id(pk, tenant)
        if not document:
            return Response(
                {"error": "Documento no encontrado"}, status=status.HTTP_404_NOT_FOUND
            )

        # Soft delete por defecto, hard delete si se especifica
        hard_delete = request.query_params.get("hard", "false").lower() == "true"

        success = DocumentService.delete_document(document, soft_delete=not hard_delete)
        if success:
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                {"error": "Error al eliminar documento"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["post"])
    def mark_processed(self, request, pk=None):
        """Marcar documento como procesado"""
        user = request.user
        try:
            user_profile = user.userprofile
            tenant = user_profile.tenant
        except:
            return Response(
                {"error": "Usuario no tiene tenant asignado"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        document = DocumentService.get_document_by_id(pk, tenant)
        if not document:
            return Response(
                {"error": "Documento no encontrado"}, status=status.HTTP_404_NOT_FOUND
            )

        updated_document = DocumentService.mark_as_processed(document)
        serializer = self.get_serializer(updated_document)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def stats(self, request):
        """Obtener estadísticas de documentos del tenant"""
        user = request.user
        try:
            user_profile = user.userprofile
            tenant = user_profile.tenant
        except:
            return Response(
                {"error": "Usuario no tiene tenant asignado"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        stats = DocumentService.get_document_stats(tenant)
        serializer = self.get_serializer(stats)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def bulk_update(self, request):
        """Actualización masiva de documentos"""
        user = request.user
        try:
            user_profile = user.userprofile
            tenant = user_profile.tenant
        except:
            return Response(
                {"error": "Usuario no tiene tenant asignado"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            validated_data = serializer.validated_data

            updated_count = DocumentService.bulk_update_status(
                document_ids=validated_data["document_ids"],
                tenant=tenant,
                is_active=validated_data.get("is_active"),
                is_processed=validated_data.get("is_processed"),
            )

            return Response(
                {
                    "updated_count": updated_count,
                    "message": f"Se actualizaron {updated_count} documento(s)",
                }
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"])
    def validate_file(self, request):
        """Validar archivo antes de subirlo"""
        file = request.FILES.get("file")
        if not file:
            return Response(
                {"error": "No se proporcionó archivo"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        validation_result = DocumentService.validate_file(file)
        return Response(validation_result)

    @action(detail=False, methods=["get"])
    def types(self, request):
        """Obtener tipos de documentos disponibles"""
        document_types = [
            {"value": choice[0], "label": choice[1]}
            for choice in DocumentModel.DOCUMENT_TYPES
        ]
        return Response({"document_types": document_types})
