"""Admin configuration for the tenants app."""

from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.urls import path, reverse
from django.utils.html import format_html

from tenants.helpers import generate_cwu_token
from tenants.models import TenantModel, UserProfile


@admin.register(TenantModel)
class TenantAdmin(admin.ModelAdmin):
    list_display = ("name", "model", "view_token_button", "regenerate_token_button")
    readonly_fields = ("cwu_token",)
    search_fields = ("name", "description")  # Para el autocomplete

    def get_urls(self):
        """Agregar URLs personalizadas para el admin."""
        urls = super().get_urls()
        custom_urls = [
            path(
                "regenerate-token/<int:tenant_id>/",
                self.admin_site.admin_view(self.regenerate_token),
                name="tenant_regenerate_token",
            ),
        ]
        return custom_urls + urls

    def regenerate_token(self, request, tenant_id):
        """Vista para regenerar el token de un tenant."""
        try:
            tenant = TenantModel.objects.get(pk=tenant_id)
            old_token = tenant.cwu_token
            tenant.cwu_token = generate_cwu_token()
            tenant.save()

            messages.success(
                request,
                f"Token regenerado exitosamente para {tenant.name}. Nuevo token: {tenant.cwu_token}",
            )
        except TenantModel.DoesNotExist:
            messages.error(request, "Tenant no encontrado.")

        return HttpResponseRedirect(
            request.META.get("HTTP_REFERER", "/admin/tenants/tenantmodel/")
        )

    def view_token_button(self, obj):
        """Botón para ver el token completo."""
        if obj.cwu_token:
            return format_html(
                '<button type="button" class="button" onclick="alert(\'Token: {}\')">Ver Token</button>',
                obj.cwu_token,
            )
        return "-"

    view_token_button.short_description = "Ver Token"
    view_token_button.allow_tags = True

    def regenerate_token_button(self, obj):
        """Botón para regenerar el token."""
        url = reverse("admin:tenant_regenerate_token", args=[obj.pk])
        return format_html(
            '<a href="{}" class="button" onclick="return confirm(\'¿Estás seguro de que quieres regenerar el token? Esta acción no se puede deshacer.\')">Regenerar Token</a>',
            url,
        )

    regenerate_token_button.short_description = "Regenerar Token"
    regenerate_token_button.allow_tags = True


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "tenant", "created_at", "updated_at")
    list_filter = ("tenant", "created_at")
    search_fields = (
        "user__username",
        "user__email",
        "user__first_name",
        "user__last_name",
        "tenant__name",
    )
    raw_id_fields = ("user",)
    autocomplete_fields = ("tenant",)

    def get_queryset(self, request):
        """Optimizar consultas con select_related."""
        return super().get_queryset(request).select_related("user", "tenant")
