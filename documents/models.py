import os
from datetime import datetime

from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils import timezone

from main.models import AppModel
from tenants.models import TenantModel


def user_document_upload_path(instance, filename):
    """
    Genera la ruta donde se guardará el documento.
    Estructura: documents/tenant_name/filename_timestamp.extension

    El timestamp se agrega antes de la extensión para evitar nombres duplicados.
    Formato: documents/tenant_name/archivo_20250618_143052_123456.pdf
    """
    tenant_name = instance.tenant.name if instance.tenant else "no_tenant"

    # Limpiar el nombre del tenant para usar como directorio
    tenant_dir = "".join(
        c for c in tenant_name if c.isalnum() or c in (" ", "-", "_")
    ).rstrip()
    tenant_dir = tenant_dir.replace(" ", "_")

    # Separar nombre y extensión del archivo
    name, ext = os.path.splitext(filename)

    # Limpiar el nombre del archivo
    clean_name = "".join(
        c for c in name if c.isalnum() or c in (" ", "-", "_")
    ).rstrip()
    clean_name = clean_name.replace(" ", "_")

    # Generar timestamp único
    now = timezone.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S_%f")[
        :-3
    ]  # Incluir microsegundos (primeros 3 dígitos)

    # Construir nombre final: nombre_timestamp.extension
    final_filename = f"{clean_name}_{timestamp}{ext.lower()}"

    return f"documents/{tenant_dir}/{final_filename}"


class DocumentModel(AppModel):
    """
    Modelo para almacenar documentos subidos por usuarios.
    Cada documento está asociado a un tenant y usuario específico.
    """

    # Tipos de documento permitidos
    DOCUMENT_TYPES = [
        ("pdf", "PDF"),
        ("doc", "Word Document (DOC)"),
        ("docx", "Word Document (DOCX)"),
        ("txt", "Text File"),
        ("csv", "CSV File"),
        ("xlsx", "Excel File (XLSX)"),
        ("xls", "Excel File (XLS)"),
        ("json", "JSON File"),
        ("md", "Markdown File"),
    ]

    # Mapeo extendido de extensiones a tipos de documento
    EXTENSION_MAPPING = {
        "pdf": "pdf",
        "doc": "doc",
        "docx": "docx",
        "txt": "txt",
        "csv": "csv",
        "xlsx": "xlsx",
        "xls": "xls",
        "json": "json",
        "md": "md",
        "markdown": "md",  # Alias para markdown
    }

    # Información básica del documento
    title = models.CharField(
        max_length=255, help_text="Título descriptivo del documento"
    )
    description = models.TextField(
        blank=True, null=True, help_text="Descripción opcional del documento"
    )

    # Archivo
    file = models.FileField(
        upload_to=user_document_upload_path,
        validators=[
            FileExtensionValidator(
                allowed_extensions=[
                    "pdf",
                    "doc",
                    "docx",
                    "txt",
                    "csv",
                    "xlsx",
                    "xls",
                    "json",
                    "md",
                ]
            )
        ],
        help_text="Archivo del documento",
    )

    # Tipo de documento
    document_type = models.CharField(
        max_length=10,
        choices=DOCUMENT_TYPES,
        blank=True,  # Permitir que esté vacío para auto-detección
        help_text="Tipo de documento (se detecta automáticamente si no se especifica)",
    )

    # Metadatos del archivo
    file_size = models.PositiveIntegerField(
        default=0, help_text="Tamaño del archivo en bytes", editable=False
    )
    original_filename = models.CharField(
        max_length=255,
        blank=True,
        help_text="Nombre original del archivo",
        editable=False,
    )

    # Relaciones
    tenant = models.ForeignKey(
        TenantModel,
        on_delete=models.CASCADE,
        related_name="documents",
        help_text="Tenant al que pertenece el documento",
    )
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="uploaded_documents",
        help_text="Usuario que subió el documento",
    )

    # Estados del documento
    is_active = models.BooleanField(
        default=True, help_text="Indica si el documento está activo"
    )
    is_processed = models.BooleanField(
        default=False, help_text="Indica si el documento ha sido procesado"
    )

    # Campos de auditoría adicionales
    processed_at = models.DateTimeField(
        blank=True, null=True, help_text="Fecha y hora en que se procesó el documento"
    )

    class Meta:
        verbose_name = "Documento"
        verbose_name_plural = "Documentos"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["tenant", "uploaded_by"]),
            models.Index(fields=["document_type"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.title} - {self.tenant.name}"

    def save(self, *args, **kwargs):
        """Override save para capturar metadatos del archivo y gestionar estado de procesamiento"""
        # Verificar si es una actualización
        is_update = self.pk is not None

        # Si es una actualización, verificar si hay cambios relevantes
        if is_update:
            try:
                old_instance = DocumentModel.objects.get(pk=self.pk)
                # Si hay cambio en el archivo, resetear el estado de procesamiento
                if self.file and (
                    not old_instance.file or self.file.name != old_instance.file.name
                ):
                    self.is_processed = False
                    self.processed_at = None

                # Si cambió el estado de is_processed a True, actualizar processed_at
                if self.is_processed and not old_instance.is_processed:
                    from django.utils import timezone

                    self.processed_at = timezone.now()
                # Si cambió el estado de is_processed a False, resetear processed_at
                elif not self.is_processed and old_instance.is_processed:
                    self.processed_at = None

            except DocumentModel.DoesNotExist:
                pass

        if self.file:
            # Guardar el nombre original del archivo
            if hasattr(self.file, "name"):
                self.original_filename = os.path.basename(self.file.name)

            # Guardar el tamaño del archivo
            if hasattr(self.file, "size") and self.file.size:
                self.file_size = self.file.size

            # Auto-detectar tipo de documento basado en la extensión
            if not self.document_type:
                ext = os.path.splitext(self.file.name)[1].lower().lstrip(".")
                detected_type = self.EXTENSION_MAPPING.get(ext)
                if detected_type:
                    self.document_type = detected_type

        super().save(*args, **kwargs)

    def get_file_size_display(self):
        """Retorna el tamaño del archivo en formato legible"""
        if not self.file_size:
            return "0 bytes"

        size = float(self.file_size)
        for unit in ["bytes", "KB", "MB", "GB"]:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"

    def is_document_type_auto_detected(self):
        """Indica si el tipo de documento fue detectado automáticamente"""
        if not self.file or not self.document_type:
            return False

        ext = os.path.splitext(self.file.name)[1].lower().lstrip(".")
        return self.EXTENSION_MAPPING.get(ext) == self.document_type

    def get_supported_extensions(self):
        """Retorna las extensiones soportadas"""
        return list(self.EXTENSION_MAPPING.keys())

    def get_absolute_url(self):
        """Retorna la URL del archivo"""
        if self.file:
            return self.file.url
        return None

    @property
    def file_extension(self):
        """Retorna la extensión del archivo"""
        if self.file:
            return os.path.splitext(self.file.name)[1].lower()
        return None
