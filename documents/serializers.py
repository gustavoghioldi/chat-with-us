from django.contrib.auth.models import User
from rest_framework import serializers

from tenants.models import TenantModel

from .models import DocumentModel


class DocumentModelSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo DocumentModel.
    Proporciona serialización completa para operaciones CRUD.
    """

    # Campos calculados
    file_size_display = serializers.CharField(
        read_only=True, source="get_file_size_display"
    )
    file_url = serializers.CharField(read_only=True, source="get_absolute_url")
    file_extension = serializers.CharField(read_only=True)

    # Información del usuario
    uploaded_by_username = serializers.CharField(
        read_only=True, source="uploaded_by.username"
    )
    uploaded_by_email = serializers.CharField(
        read_only=True, source="uploaded_by.email"
    )

    # Información del tenant
    tenant_name = serializers.CharField(read_only=True, source="tenant.name")

    class Meta:
        model = DocumentModel
        fields = [
            "id",
            "title",
            "description",
            "file",
            "document_type",
            "file_size",
            "file_size_display",
            "file_url",
            "file_extension",
            "original_filename",
            "tenant",
            "tenant_name",
            "uploaded_by",
            "uploaded_by_username",
            "uploaded_by_email",
            "is_active",
            "is_processed",
            "processed_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "file_size",
            "original_filename",
            "file_size_display",
            "file_url",
            "file_extension",
            "uploaded_by_username",
            "uploaded_by_email",
            "tenant_name",
            "processed_at",
            "created_at",
            "updated_at",
        ]

    def validate_file(self, value):
        """Validación personalizada del archivo"""
        from .services import DocumentService

        validation_result = DocumentService.validate_file(value)

        if not validation_result["is_valid"]:
            raise serializers.ValidationError(validation_result["errors"])

        # Agregar advertencias como información adicional
        if validation_result["warnings"]:
            # En un contexto real, podrías loggear estas advertencias
            pass

        return value

    def create(self, validated_data):
        """Crear documento usando el servicio"""
        from .services import DocumentService

        # El tenant y uploaded_by deben ser proporcionados por la vista
        tenant = validated_data.pop("tenant")
        uploaded_by = validated_data.pop("uploaded_by")

        return DocumentService.create_document(
            tenant=tenant, uploaded_by=uploaded_by, **validated_data
        )


class DocumentListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listar documentos.
    Incluye solo los campos esenciales para mejor performance.
    """

    file_size_display = serializers.CharField(
        read_only=True, source="get_file_size_display"
    )
    uploaded_by_username = serializers.CharField(
        read_only=True, source="uploaded_by.username"
    )
    tenant_name = serializers.CharField(read_only=True, source="tenant.name")

    class Meta:
        model = DocumentModel
        fields = [
            "id",
            "title",
            "document_type",
            "file_size_display",
            "uploaded_by_username",
            "tenant_name",
            "is_active",
            "is_processed",
            "created_at",
        ]


class DocumentUploadSerializer(serializers.ModelSerializer):
    """
    Serializer específico para subir documentos.
    Optimizado para el proceso de carga de archivos.
    """

    class Meta:
        model = DocumentModel
        fields = ["title", "description", "file", "document_type"]

    def validate_file(self, value):
        """Validación del archivo en el upload"""
        from .services import DocumentService

        validation_result = DocumentService.validate_file(value)

        if not validation_result["is_valid"]:
            raise serializers.ValidationError(
                {
                    "errors": validation_result["errors"],
                    "file_info": validation_result["file_info"],
                }
            )

        return value


class DocumentStatsSerializer(serializers.Serializer):
    """
    Serializer para estadísticas de documentos.
    """

    total_documents = serializers.IntegerField(read_only=True)
    active_documents = serializers.IntegerField(read_only=True)
    processed_documents = serializers.IntegerField(read_only=True)
    unprocessed_documents = serializers.IntegerField(read_only=True)
    documents_by_type = serializers.DictField(read_only=True)
    total_size_bytes = serializers.IntegerField(read_only=True)
    total_size_mb = serializers.FloatField(read_only=True)


class BulkUpdateSerializer(serializers.Serializer):
    """
    Serializer para actualizaciones masivas de documentos.
    """

    document_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1,
        help_text="Lista de IDs de documentos a actualizar",
    )
    is_active = serializers.BooleanField(
        required=False, help_text="Estado activo de los documentos"
    )
    is_processed = serializers.BooleanField(
        required=False, help_text="Estado procesado de los documentos"
    )

    def validate(self, data):
        """Validar que al menos un campo de actualización esté presente"""
        if not any(["is_active" in data, "is_processed" in data]):
            raise serializers.ValidationError(
                "Debe proporcionar al menos un campo para actualizar"
            )
        return data
