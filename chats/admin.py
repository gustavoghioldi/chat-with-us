from django.contrib import admin

from chats.models import ChatModel

@admin.register(ChatModel)
class ChatAdmin(admin.ModelAdmin):
    change_form_template = 'admin/chats/change_form.html'
    list_display = ('agent', 'session_id', 'created_at', 'updated_at')
    search_fields = ('agent__name',)
    list_filter = ('agent',)
    ordering = ('-created_at',)
    fields = ('agent', 'session_id', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at', 'agent', 'session_id')