from django.contrib import admin
from django.utils.html import format_html

from analysis.models.sentiment_agents_model import SentimentAgentModel
from analysis.models.sentiment_chat_model import SentimentChatModel


@admin.register(SentimentChatModel)
class SentimentChatAdmin(admin.ModelAdmin):
    list_display = ("content_chat", "actitude", "cause", "created_at")
    list_filter = ("actitude", "created_at", "updated_at")
    search_fields = ("cause", "content_chat__request", "content_chat__response")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)

    fieldsets = (
        (
            "📊 Análisis de Sentimiento",
            {
                "fields": ("content_chat", "actitude", "cause"),
                "description": "Información del análisis de sentimiento realizado al contenido del chat",
            },
        ),
        (
            "📅 Metadatos",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def get_queryset(self, request):
        """Optimizar consultas con select_related."""
        return (
            super()
            .get_queryset(request)
            .select_related("content_chat", "content_chat__chat")
        )


@admin.register(SentimentAgentModel)
class SentimentAgentAdmin(admin.ModelAdmin):
    change_form_template = "admin/analysis/sentimentagentmodel/change_form.html"
    list_display = ("name", "tenant", "get_tokens_summary", "created_at", "updated_at")
    list_display_links = ("name",)
    search_fields = ("name", "description", "tenant__name")
    list_filter = ("created_at", "updated_at", "tenant")
    ordering = ("-created_at",)
    autocomplete_fields = ("tenant",)

    fieldsets = (
        (
            "🤖 Información del Agente de Sentimientos",
            {
                "fields": ("name", "description", "tenant"),
                "description": "Configuración básica del agente de análisis de sentimientos",
            },
        ),
        (
            "🎭 Configuración de Tokens",
            {
                "fields": ("positive_tokens", "negative_tokens", "neutral_tokens"),
                "description": "Define los tokens que utilizará el agente para clasificar sentimientos. Separa cada token con comas.",
                "classes": ("wide",),
            },
        ),
        (
            "📅 Metadatos",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )
    readonly_fields = ("created_at", "updated_at")

    def get_tokens_summary(self, obj):
        """Muestra un resumen elegante de los tokens configurados."""
        positive_count = (
            len(
                [
                    token.strip()
                    for token in obj.positive_tokens.split(",")
                    if token.strip()
                ]
            )
            if obj.positive_tokens
            else 0
        )
        negative_count = (
            len(
                [
                    token.strip()
                    for token in obj.negative_tokens.split(",")
                    if token.strip()
                ]
            )
            if obj.negative_tokens
            else 0
        )
        neutral_count = (
            len(
                [
                    token.strip()
                    for token in obj.neutral_tokens.split(",")
                    if token.strip()
                ]
            )
            if obj.neutral_tokens
            else 0
        )

        total_tokens = positive_count + negative_count + neutral_count

        if total_tokens == 0:
            return format_html(
                '<span style="color: #dc3545; font-weight: 500;">❌ Sin tokens configurados</span>'
            )

        return format_html(
            '<div style="display: flex; gap: 8px; flex-wrap: wrap;">'
            '<span style="background: linear-gradient(135deg, #28a745, #20c997); color: white; padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: 500;">😊 {} positivos</span>'
            '<span style="background: linear-gradient(135deg, #dc3545, #e74c3c); color: white; padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: 500;">😞 {} negativos</span>'
            '<span style="background: linear-gradient(135deg, #6c757d, #495057); color: white; padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: 500;">😐 {} neutrales</span>'
            "</div>",
            positive_count,
            negative_count,
            neutral_count,
        )

    get_tokens_summary.short_description = "Resumen de Tokens"
    get_tokens_summary.admin_order_field = "name"

    def get_queryset(self, request):
        """Optimizar consultas con select_related."""
        return super().get_queryset(request).select_related("tenant")

    def changelist_view(self, request, extra_context=None):
        """Mejora el título de la página de lista."""
        extra_context = extra_context or {}
        extra_context["title"] = "🎭 Gestión de Agentes de Sentimiento"
        return super().changelist_view(request, extra_context)

    def change_view(self, request, object_id, form_url="", extra_context=None):
        """Agrega información contextual en la vista de edición."""
        extra_context = extra_context or {}
        if object_id:
            try:
                obj = self.get_object(request, object_id)
                if obj:
                    # Estadísticas de tokens
                    positive_tokens = (
                        [
                            token.strip()
                            for token in obj.positive_tokens.split(",")
                            if token.strip()
                        ]
                        if obj.positive_tokens
                        else []
                    )
                    negative_tokens = (
                        [
                            token.strip()
                            for token in obj.negative_tokens.split(",")
                            if token.strip()
                        ]
                        if obj.negative_tokens
                        else []
                    )
                    neutral_tokens = (
                        [
                            token.strip()
                            for token in obj.neutral_tokens.split(",")
                            if token.strip()
                        ]
                        if obj.neutral_tokens
                        else []
                    )

                    tokens_stats = {
                        "positive_count": len(positive_tokens),
                        "negative_count": len(negative_tokens),
                        "neutral_count": len(neutral_tokens),
                        "total_count": len(positive_tokens)
                        + len(negative_tokens)
                        + len(neutral_tokens),
                        "positive_examples": positive_tokens[:5],  # Primeros 5 ejemplos
                        "negative_examples": negative_tokens[:5],
                        "neutral_examples": neutral_tokens[:5],
                    }
                    extra_context["tokens_stats"] = tokens_stats
            except Exception:
                pass
        return super().change_view(request, object_id, form_url, extra_context)
