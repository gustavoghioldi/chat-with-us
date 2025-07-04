from django import forms
from django.contrib import admin
from django.db import models
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from agents.models import AgentModel


class AgentAdminForm(forms.ModelForm):
    """Formulario personalizado para el admin de AgentModel con validaciones mejoradas"""

    class Meta:
        model = AgentModel
        fields = "__all__"
        widgets = {
            "temperature": forms.NumberInput(
                attrs={
                    "step": "0.05",
                    "min": "0.0",
                    "max": "1.0",
                    "class": "form-control",
                    "placeholder": "0.7 (recomendado: 0.3-0.8)",
                    "title": "Valor entre 0.0 y 1.0 que controla la aleatoriedad de las respuestas",
                }
            ),
            "top_p": forms.NumberInput(
                attrs={
                    "step": "0.05",
                    "min": "0.0",
                    "max": "1.0",
                    "class": "form-control",
                    "placeholder": "0.9 (recomendado: 0.8-0.95)",
                    "title": "Valor entre 0.0 y 1.0 que controla la diversidad de las respuestas",
                }
            ),
            "max_tokens": forms.NumberInput(
                attrs={
                    "min": "50",
                    "max": "10000",
                    "class": "form-control",
                    "placeholder": "100 (recomendado: 50-200)",
                    "title": "Número máximo de tokens en la respuesta (50-10000)",
                }
            ),
        }

    def clean_temperature(self):
        """Validación adicional para temperature"""
        temperature = self.cleaned_data.get("temperature")
        if temperature is not None:
            if temperature < 0.0 or temperature > 1.0:
                raise forms.ValidationError(
                    "El valor de temperature debe estar entre 0.0 y 1.0"
                )
        return temperature

    def clean_top_p(self):
        """Validación adicional para top_p"""
        top_p = self.cleaned_data.get("top_p")
        if top_p is not None:
            if top_p < 0.0 or top_p > 1.0:
                raise forms.ValidationError(
                    "El valor de top_p debe estar entre 0.0 y 1.0"
                )
        return top_p

    def clean_max_tokens(self):
        """Validación adicional para max_tokens"""
        max_tokens = self.cleaned_data.get("max_tokens")
        if max_tokens is not None:
            if max_tokens < 1:
                raise forms.ValidationError("El número de tokens debe ser mayor a 0")
            if max_tokens > 10000:
                raise forms.ValidationError(
                    "El número de tokens no puede ser mayor a 10,000"
                )
        return max_tokens


# Register your models here.
@admin.register(AgentModel)
class AgentAdmin(admin.ModelAdmin):
    form = AgentAdminForm
    list_display = (
        "name",
        "get_knowledge_summary",
        "get_knowledge_categories",
        "get_api_tools_summary",
        "get_config_summary",
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
        "temperature",
        "max_tokens",
    )
    ordering = ("-created_at",)
    filter_horizontal = ("knoledge_text_models", "api_call_models")

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
            "⚙️ Configuraciones",
            {
                "fields": (
                    "temperature",
                    "top_p",
                    "max_tokens",
                ),
                "description": "Parámetros de configuración para el comportamiento del agente de IA",
                "classes": ("wide",),
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

    class Media:
        css = {"all": ("admin/css/agents_admin.css",)}
        js = ("admin/js/agents_admin.js",)

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
                badge = f'<span style="background: linear-gradient(135deg, #007bff, #0056b3); color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 500; margin-right: 4px;">🌐 {category}</span>'
            elif category == "plain_document":
                badge = f'<span style="background: linear-gradient(135deg, #28a745, #1e7e34); color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 500; margin-right: 4px;">📄 plain</span>'
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

    def get_config_summary(self, obj):
        """Muestra un resumen elegante de la configuración del agente"""
        config_info = f"🌡️ {obj.temperature} | 🎯 {obj.top_p} | 📊 {obj.max_tokens}"

        # Determinar el color basado en los valores
        temp_status = (
            "🟢"
            if 0.3 <= obj.temperature <= 0.8
            else "🟡" if obj.temperature < 0.3 or obj.temperature > 0.8 else "🔴"
        )
        top_p_status = "🟢" if 0.8 <= obj.top_p <= 0.95 else "🟡"
        tokens_status = (
            "🟢"
            if 50 <= obj.max_tokens <= 200
            else "🟡" if obj.max_tokens < 50 else "🔴"
        )

        return format_html(
            '<span style="font-family: monospace; font-size: 11px; background: #f8f9fa; padding: 2px 6px; border-radius: 4px; border-left: 3px solid #007bff;">'
            "{} T:{} | {} P:{} | {} M:{}"
            "</span>",
            temp_status,
            obj.temperature,
            top_p_status,
            obj.top_p,
            tokens_status,
            obj.max_tokens,
        )

    get_config_summary.short_description = "Configuración"

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

                    # Agregar estadísticas de configuración
                    config_stats = {
                        "temperature": {
                            "value": obj.temperature,
                            "status": (
                                "optimal"
                                if 0.3 <= obj.temperature <= 0.8
                                else (
                                    "warning"
                                    if obj.temperature < 0.3 or obj.temperature > 0.8
                                    else "danger"
                                )
                            ),
                            "description": "Controla la creatividad/aleatoriedad de las respuestas",
                        },
                        "top_p": {
                            "value": obj.top_p,
                            "status": (
                                "optimal" if 0.8 <= obj.top_p <= 0.95 else "warning"
                            ),
                            "description": "Controla la diversidad de tokens considerados",
                        },
                        "max_tokens": {
                            "value": obj.max_tokens,
                            "status": (
                                "optimal"
                                if 50 <= obj.max_tokens <= 200
                                else "warning" if obj.max_tokens < 50 else "danger"
                            ),
                            "description": "Número máximo de tokens en la respuesta",
                        },
                    }
                    extra_context["config_stats"] = config_stats
            except Exception:
                pass
        return super().change_view(request, object_id, form_url, extra_context)
