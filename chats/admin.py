from django.contrib import admin

from analysis.models.sentiment_chat_model import SentimentChatModel
from chats.models import ChatModel, ContentChatModel


@admin.register(ChatModel)
class ChatAdmin(admin.ModelAdmin):
    change_form_template = "admin/chats/change_form.html"
    list_display = ("agent", "session_id", "created_at", "updated_at")
    search_fields = ("agent__name",)
    list_filter = ("agent",)
    ordering = ("-created_at",)
    fields = ("agent", "session_id", "created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at", "agent", "session_id")

    def get_form(self, request, obj=..., change=..., **kwargs):
        form = super().get_form(request, obj=obj, change=change, **kwargs)
        form.content_chats = ContentChatModel.objects.filter(chat=obj)
        return form

    def change_view(self, request, object_id, form_url="", extra_context=None):
        extra_context = extra_context or {}
        extra_context["content_chats"] = SentimentChatModel.objects.filter(
            content_chat__chat=object_id
        )
        return super(ChatAdmin, self).change_view(
            request,
            object_id,
            form_url,
            extra_context=extra_context,
        )
