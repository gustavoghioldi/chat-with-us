from django.contrib import admin

from knowledge.models import KnowledgeModel


# Register your models here.
@admin.register(KnowledgeModel)
class KnowledgeAdmin(admin.ModelAdmin):
    change_form_template = "admin/knowledge/change_form.html"
    list_display = ("name", "category")
    search_fields = ("name", "url", "description")
    list_filter = ("category",)
    ordering = ("-created_at",)
    fields = ("name", "category", "url", "text", "description")
    readonly_fields = ("created_at", "updated_at")
