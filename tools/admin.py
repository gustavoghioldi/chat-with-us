from django.contrib import admin

from tools.models.api_call_model import ApiCallModel


@admin.register(ApiCallModel)
class ApiCallAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "url",
        "method",
        "username",
        "tenant",
        "created_at",
    )
    list_display_links = ("name",)
    search_fields = ("name", "url", "method", "username")
    list_filter = (
        "created_at",
        "updated_at",
        "tenant",
        "method",
    )
    ordering = ("-created_at",)

    fieldsets = (
        (
            "🔗 Información de la API",
            {
                "fields": ("name", "url", "method", "headers", "body"),
                "description": "Configuración básica de la llamada a la API",
            },
        ),
        (
            "🔐 Autenticación",
            {
                "fields": ("username", "password", "api_key"),
                "description": "Opciones de autenticación para la llamada a la API",
                "classes": ("collapse",),
            },
        ),
        (
            "⚙️ Configuración Avanzada",
            {
                "fields": ("verify_ssl", "timeout"),
                "description": "Configuraciones avanzadas para la llamada a la API",
                "classes": ("collapse",),
            },
        ),
        (
            "⚙️ Instrucciones",
            {
                "fields": ("instructions",),
                "description": "Instrucciones para hacer la llamada a la API",
                "classes": ("collapse",),
            },
        ),
        (
            "📅 Metadatos",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    readonly_fields = ("created_at", "updated_at")
