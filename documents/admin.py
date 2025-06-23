from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import DocumentModel


@admin.register(DocumentModel)
class DocumentModelAdmin(admin.ModelAdmin):
    """
    Admin para gestionar documentos.
    Proporciona una interfaz completa para CRUD de documentos.
    """

    list_display = [
        "title",
        "document_type_display",
        "tenant",
        "uploaded_by",
        "file_size_display",
        "is_active",
        "is_processed",
        "created_at",
        "file_link",
        # "file_to_knowledge",
    ]

    list_filter = [
        "document_type",
        "is_active",
        "is_processed",
        "tenant",
        "created_at",
        "updated_at",
    ]

    search_fields = [
        "title",
        "description",
        "original_filename",
        "tenant__name",
        "uploaded_by__username",
        "uploaded_by__email",
    ]

    readonly_fields = [
        "file_size",
        "original_filename",
        "created_at",
        "updated_at",
        "processed_at",
        "file_info_display",
        "file_preview",
    ]

    fieldsets = (
        (
            "Información General",
            {"fields": ("title", "description", "tenant", "uploaded_by")},
        ),
        (
            "Archivo",
            {
                "fields": (
                    "file",
                    "file_info_display",
                    "file_preview",
                ),
                "description": "El tipo de documento se detecta automáticamente. Solo especifique uno si desea sobreescribir la detección automática.",
            },
        ),
        ("Estado", {"fields": ("is_active", "is_processed", "processed_at")}),
        (
            "Metadatos (Solo lectura)",
            {
                "fields": (
                    "file_size",
                    "original_filename",
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    ordering = ["-created_at"]

    # Configuración de paginación
    list_per_page = 25

    # Acciones personalizadas
    actions = ["mark_as_processed", "mark_as_unprocessed", "deactivate_documents"]

    def file_size_display(self, obj):
        """Muestra el tamaño del archivo en formato legible"""
        return obj.get_file_size_display()

    file_size_display.short_description = "Tamaño"
    file_size_display.admin_order_field = "file_size"

    def file_link(self, obj):
        """Crea un enlace para descargar el archivo"""
        if obj.file:
            return format_html(
                '<a href="{}" target="_blank" class="button">Descargar</a>',
                obj.file.url,
            )
        return "No hay archivo"

    file_link.short_description = "Archivo"
    file_link.allow_tags = True

    def document_type_display(self, obj):
        """Muestra el tipo de documento con indicador de auto-detección"""
        if not obj.document_type:
            return format_html('<span style="color: red;">No detectado</span>')

        if obj.is_document_type_auto_detected():
            return format_html(
                '{} <span style="color: green; font-size: 0.8em;">●</span>',
                obj.get_document_type_display(),
            )
        else:
            return format_html(
                '{} <span style="color: blue; font-size: 0.8em;">●</span>',
                obj.get_document_type_display(),
            )

    document_type_display.short_description = "Tipo (● Auto / ● Manual)"
    document_type_display.admin_order_field = "document_type"

    # def file_to_knowledge(self, obj):
    #     # TODO: Implementar la lógica para generar Knowledge desde el archivo
    #     """Crea un enlace para descargar el archivo"""
    #     if obj.file:
    #         return format_html(
    #             '<a target="_blank" class="button" disabled>Knowledge</a>',
    #             obj.file.url,
    #         )
    #     return "No hay archivo"

    # file_to_knowledge.short_description = "Generar Knowledge"
    # file_to_knowledge.allow_tags = True

    def file_info_display(self, obj):
        """Muestra información detallada del archivo"""
        if not obj.file:
            return "No hay archivo"

        # Información básica del archivo
        info = f"""
        <strong>Nombre original:</strong> {obj.original_filename}<br>
        <strong>Tamaño:</strong> {obj.get_file_size_display()}<br>
        <strong>Extensión:</strong> {obj.file_extension}<br>
        <strong>Ruta:</strong> {obj.file.name}<br>
        """

        # Información sobre auto-detección
        if obj.document_type:
            if obj.is_document_type_auto_detected():
                info += f'<strong>Tipo:</strong> {obj.get_document_type_display()} <span style="color: green;">(Auto-detectado)</span><br>'
            else:
                info += f'<strong>Tipo:</strong> {obj.get_document_type_display()} <span style="color: blue;">(Manual)</span><br>'
        else:
            info += '<strong>Tipo:</strong> <span style="color: red;">No detectado</span><br>'

        return mark_safe(info)

    file_info_display.short_description = "Información del archivo"

    def file_preview(self, obj):
        """Vista previa del archivo si es una imagen o enlace de descarga"""
        if not obj.file:
            return "No hay archivo"

        file_ext = obj.file_extension

        if file_ext in [".jpg", ".jpeg", ".png", ".gif", ".webp"]:
            return format_html(
                '<img src="{}" style="max-width: 200px; max-height: 200px;" />',
                obj.file.url,
            )
        else:
            return format_html(
                '<a href="{}" target="_blank" class="button">Ver archivo</a>',
                obj.file.url,
            )

    file_preview.short_description = "Vista previa"
