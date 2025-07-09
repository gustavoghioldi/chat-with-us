from django.contrib import admin

from communication.models.telegram.telegram_communication_model import (
    TelegramCommunicationModel,
)


@admin.register(TelegramCommunicationModel)
class TelegramCommunicationModelAdmin(admin.ModelAdmin):
    list_display = ("id", "created_at", "updated_at")
    search_fields = ("id",)
    readonly_fields = ("created_at", "updated_at")
