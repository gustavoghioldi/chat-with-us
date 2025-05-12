from django.contrib import admin

from agents.models import AgentModel

# Register your models here.
@admin.register(AgentModel)
class AgentAdmin(admin.ModelAdmin):
    list_display = ('name', 'instructions', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('created_at', 'updated_at')
    ordering = ('-created_at',)