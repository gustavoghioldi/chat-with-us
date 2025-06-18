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
        "document_type",
        "tenant",
        "uploaded_by",
        "file_size_display",
        "is_active",
        "is_processed",
        "created_at",
        "file_link",
        "file_to_knowledge",
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
            {"fields": ("file", "document_type", "file_info_display", "file_preview")},
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

    def file_to_knowledge(self, obj):
        # TODO: Implementar la lógica para generar Knowledge desde el archivo
        """Crea un enlace para descargar el archivo"""
        if obj.file:
            return format_html(
                '<a target="_blank" class="button" disabled>Knowledge</a>',
                obj.file.url,
            )
        return "No hay archivo"

    file_to_knowledge.short_description = "Generar Knowledge"
    file_to_knowledge.allow_tags = True

    def file_info_display(self, obj):
        """Muestra información detallada del archivo"""
        if not obj.file:
            return "No hay archivo"

        info = f"""
        <strong>Nombre original:</strong> {obj.original_filename}<br>
        <strong>Tamaño:</strong> {obj.get_file_size_display()}<br>
        <strong>Extensión:</strong> {obj.file_extension}<br>
        <strong>Ruta:</strong> {obj.file.name}
        """
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

    # Acciones personalizadas
    @admin.action(description="Marcar como procesado")
    def mark_as_processed(self, request, queryset):
        """Marca los documentos seleccionados como procesados"""
        from django.utils import timezone

        updated = queryset.update(is_processed=True, processed_at=timezone.now())
        self.message_user(
            request, f"{updated} documento(s) marcado(s) como procesado(s)."
        )

    @admin.action(description="Marcar como no procesado")
    def mark_as_unprocessed(self, request, queryset):
        """Marca los documentos seleccionados como no procesados"""
        updated = queryset.update(is_processed=False, processed_at=None)
        self.message_user(
            request, f"{updated} documento(s) marcado(s) como no procesado(s)."
        )

    @admin.action(description="Desactivar documentos")
    def deactivate_documents(self, request, queryset):
        """Desactiva los documentos seleccionados"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} documento(s) desactivado(s).")

    def get_queryset(self, request):
        """Optimiza las consultas con select_related"""
        return super().get_queryset(request).select_related("tenant", "uploaded_by")

    def save_model(self, request, obj, form, change):
        """Auto-asigna el usuario que sube el archivo si no está especificado"""
        if not change and not obj.uploaded_by:
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)
