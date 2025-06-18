from django.contrib import admin
from django.db import models
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from agents.models import AgentModel

# class KnowledgeInline(admin.TabularInline):
#     """Inline elegante para mostrar los Knowledge Models asociados"""
#     model = AgentModel.knoledge_text_models.through
#     extra = 1
#     verbose_name = "Knowledge Model"
#     verbose_name_plural = "Knowledge Models Asociados"

#     def get_queryset(self, request):
#         qs = super().get_queryset(request)
#         return qs.select_related('knowledgemodel')


# Register your models here.
@admin.register(AgentModel)
class AgentAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "get_knowledge_summary",
        "get_knowledge_categories",
        "get_api_tools_summary",
        "agent_model_id",
        "tenant",
        "created_at",
    )
    list_display_links = ("name",)
    search_fields = ("name", "instructions", "agent_model_id")
    list_filter = (
        "created_at",
        "updated_at",
        "tenant",
        "knoledge_text_models__category",
    )
    ordering = ("-created_at",)
    filter_horizontal = ("knoledge_text_models", "api_call_models")
    # inlines = [KnowledgeInline]

    fieldsets = (
        (
            "🤖 Información del Agente",
            {
                "fields": (
                    "name",
                    "instructions",
                    "description",
                    "agent_model_id",
                    "tenant",
                ),
                "description": "Configuración básica del agente de IA",
            },
        ),
        (
            "📚 Base de Conocimiento",
            {
                "fields": ("knoledge_text_models",),
                "description": "Selecciona los modelos de conocimiento que utilizará este agente para responder preguntas",
                "classes": ("wide",),
            },
        ),
        (
            "🛠️ Api Tool",
            {
                "fields": ("api_call_models",),
                "description": "Selecciona los modelos de Api Tool que utilizará este agente para responder preguntas",
                "classes": ("wide",),
            },
        ),
        (
            "📅 Metadatos",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )
    readonly_fields = ("created_at", "updated_at")

    def get_knowledge_summary(self, obj):
        """Muestra un resumen elegante de los knowledge models"""
        count = obj.knoledge_text_models.count()
        if count == 0:
            return format_html(
                '<span style="color: #dc3545; font-weight: 500;">❌ Sin modelos</span>'
            )
        elif count <= 3:
            return format_html(
                '<span style="color: #28a745; font-weight: 500;">✅ {} modelo{}</span>',
                count,
                "s" if count != 1 else "",
            )
        else:
            return format_html(
                '<span style="color: #007bff; font-weight: 500;">🚀 {} modelos</span>',
                count,
            )

    get_knowledge_summary.short_description = "Knowledge Models"
    get_knowledge_summary.admin_order_field = "knowledge_count"

    def get_knowledge_categories(self, obj):
        """Muestra las categorías como badges elegantes"""
        categories = obj.knoledge_text_models.values_list(
            "category", flat=True
        ).distinct()
        if not categories:
            return format_html('<span style="color: #6c757d;">—</span>')

        badges = []
        for category in categories:
            if category == "website":
                badge = '<span style="background: linear-gradient(135deg, #007bff, #0056b3); color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 500; margin-right: 4px;">🌐 Web</span>'
            elif category == "plain_document":
                badge = '<span style="background: linear-gradient(135deg, #28a745, #1e7e34); color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 500; margin-right: 4px;">📄 Doc</span>'
            else:
                badge = f'<span style="background: linear-gradient(135deg, #6c757d, #495057); color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 500; margin-right: 4px;">📎 {category}</span>'
            badges.append(badge)

        return mark_safe("".join(badges))

    get_knowledge_categories.short_description = "Categorías"

    def get_api_tools_summary(self, obj):
        """Muestra un resumen elegante de los API tools"""
        count = obj.api_call_models.count()
        if count == 0:
            return format_html(
                '<span style="color: #dc3545; font-weight: 500;">❌ Sin tools</span>'
            )
        elif count <= 3:
            return format_html(
                '<span style="color: #28a745; font-weight: 500;">✅ {} tool{}</span>',
                count,
                "s" if count != 1 else "",
            )
        else:
            return format_html(
                '<span style="color: #007bff; font-weight: 500;">🚀 {} tools</span>',
                count,
            )

    get_api_tools_summary.short_description = "API Tools"
    get_api_tools_summary.admin_order_field = "api_tools_count"

    def get_queryset(self, request):
        """Optimiza las consultas para mejor rendimiento"""
        qs = super().get_queryset(request)
        return (
            qs.prefetch_related("knoledge_text_models", "api_call_models")
            .select_related("tenant")
            .annotate(
                knowledge_count=models.Count("knoledge_text_models"),
                api_tools_count=models.Count("api_call_models"),
            )
        )

    def changelist_view(self, request, extra_context=None):
        """Mejora el título de la página de lista"""
        extra_context = extra_context or {}
        extra_context["title"] = "🤖 Gestión de Agentes IA"
        return super().changelist_view(request, extra_context)

    def change_view(self, request, object_id, form_url="", extra_context=None):
        """Agrega información contextual en la vista de edición"""
        extra_context = extra_context or {}
        if object_id:
            try:
                obj = self.get_object(request, object_id)
                if obj:
                    knowledge_stats = {
                        "total": obj.knoledge_text_models.count(),
                        "websites": obj.knoledge_text_models.filter(
                            category="website"
                        ).count(),
                        "documents": obj.knoledge_text_models.filter(
                            category="plain_document"
                        ).count(),
                    }
                    api_tools_stats = {
                        "total": obj.api_call_models.count(),
                        "get_methods": obj.api_call_models.filter(method="GET").count(),
                        "post_methods": obj.api_call_models.filter(
                            method="POST"
                        ).count(),
                        "other_methods": obj.api_call_models.exclude(
                            method__in=["GET", "POST"]
                        ).count(),
                    }
                    extra_context["knowledge_stats"] = knowledge_stats
                    extra_context["api_tools_stats"] = api_tools_stats
            except Exception:
                pass
        return super().change_view(request, object_id, form_url, extra_context)
