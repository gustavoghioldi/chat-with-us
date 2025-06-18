from django.contrib import admin
from django.urls import path, reverse
from django.utils.html import format_html

from knowledge.models import KnowledgeModel
from knowledge.views.admin.import_documents_view import import_documents_view
from knowledge.views.admin.upload_file_view import upload_file_view


@admin.register(KnowledgeModel)
class KnowledgeAdmin(admin.ModelAdmin):
    change_form_template = "admin/knowledge/change_form.html"
    list_display = ("name", "category", "tenant", "created_at")
    search_fields = ("name", "url", "description", "text")
    list_filter = ("category", "tenant", "created_at")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at", "formatted_text_preview")

    fieldsets = (
        (
            "📝 Información Básica",
            {"fields": ("name", "description", "category", "tenant")},
        ),
        (
            "🌐 Contenido Web",
            {
                "fields": ("url",),
                "classes": ("collapse",),
                "description": "Para contenido web o scraping",
            },
        ),
        (
            "📁 Contenido Documentos",
            {
                "fields": ("path",),
                "classes": ("collapse",),
                "description": "Para contenido en documentos o archivos",
            },
        ),
        (
            "📄 Contenido de Texto",
            {
                "fields": ("text", "formatted_text_preview"),
                "classes": ("collapse",),
                "description": "Contenido transformado a Markdown",
            },
        ),
        (
            "🕒 Metadatos",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                    "recreate",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    def get_urls(self):
        """Agregar URLs personalizadas para la carga de archivos y selección de documentos."""
        urls = super().get_urls()
        custom_urls = [
            path(
                "upload-file/",
                self.admin_site.admin_view(upload_file_view),
                name="knowledge_upload_file",
            ),
            path(
                "import-documents/",
                self.admin_site.admin_view(import_documents_view),
                name="knowledge_import_documents",
            ),
        ]
        return custom_urls + urls

    def formatted_text_preview(self, obj):
        """Vista previa del texto formateado."""
        if obj.text:
            preview = obj.text[:500] + "..." if len(obj.text) > 500 else obj.text
            return format_html(
                '<pre style="white-space: pre-wrap; max-height: 300px; overflow-y: auto;">{}</pre>',
                preview,
            )
        return "Sin contenido"

    formatted_text_preview.short_description = "🔍 Vista Previa del Contenido"

    def changelist_view(self, request, extra_context=None):
        """Personalizar la vista de lista para agregar botones de subida e importación."""
        extra_context = extra_context or {}
        extra_context["upload_url"] = reverse("admin:knowledge_upload_file")
        extra_context["import_documents_url"] = reverse(
            "admin:knowledge_import_documents"
        )
        return super().changelist_view(request, extra_context)
