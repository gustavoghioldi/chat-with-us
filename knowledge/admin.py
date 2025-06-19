from django.contrib import admin, messages
from django.http import HttpResponseRedirect
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

    def has_change_permission(self, request, obj=None):
        """Deshabilitar permisos de edición para el modelo Knowledge."""
        return False

    def get_readonly_fields(self, request, obj=None):
        """Hacer que todos los campos sean de solo lectura."""
        if obj:  # Solo cuando se está editando un objeto existente
            # Obtener todos los campos del modelo
            return [field.name for field in obj._meta.fields] + [
                "formatted_text_preview"
            ]
        return self.readonly_fields

    fieldsets = (
        (
            "📝 Información Básica",
            {"fields": ("name", "description", "category", "tenant")},
        ),
        (
            "🌐 Contenido Web",
            {
                "fields": ("url",),
                "description": "Para contenido web o scraping",
            },
        ),
        (
            "📁 Contenido Documentos",
            {
                "fields": ("document",),
                "description": "Para contenido en documentos o archivos",
            },
        ),
        (
            "📄 Contenido de Texto",
            {
                "fields": ("text", "formatted_text_preview"),
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
            path(
                "mark-for-recreate/<int:object_id>/",
                self.admin_site.admin_view(self.mark_for_recreate),
                name="knowledge_mark_for_recreate",
            ),
        ]
        return custom_urls + urls

    def mark_for_recreate(self, request, object_id):
        """Marca un modelo de conocimiento para ser recreado."""
        try:
            knowledge = KnowledgeModel.objects.get(id=object_id)
            # Establecer recreate=True y guardar desencadenará el signal
            knowledge.recreate = True
            knowledge.save(update_fields=["recreate"])

            # El signal manejará la actualización del documento si es necesario

            self.message_user(
                request,
                f"✅ El modelo '{knowledge.name}' ha sido marcado para recreación.",
                messages.SUCCESS,
            )
        except KnowledgeModel.DoesNotExist:
            self.message_user(
                request, "❌ No se encontró el modelo de conocimiento.", messages.ERROR
            )

        # Redirigir de vuelta a la vista de detalle
        return HttpResponseRedirect(
            reverse(
                "admin:knowledge_knowledgemodel_change",
                args=[object_id],
            )
        )

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

    def change_view(self, request, object_id, form_url="", extra_context=None):
        """Personalizar la vista de cambio para mostrar secciones según la categoría."""
        extra_context = extra_context or {}
        obj = self.get_object(request, object_id)
        if obj:
            extra_context["content_category"] = obj.category
            extra_context["needs_recreate"] = not obj.recreate
            extra_context["mark_for_recreate_url"] = reverse(
                "admin:knowledge_mark_for_recreate", args=[obj.id]
            )
        return super().change_view(request, object_id, form_url, extra_context)

    def changelist_view(self, request, extra_context=None):
        """Personalizar la vista de lista para agregar botones de subida e importación."""
        extra_context = extra_context or {}
        extra_context["upload_url"] = reverse("admin:knowledge_upload_file")
        extra_context["import_documents_url"] = reverse(
            "admin:knowledge_import_documents"
        )
        return super().changelist_view(request, extra_context)
