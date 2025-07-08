from rest_framework import serializers

from communication.models.telegram.telegram_chat_model import (
    TelegramChatModel,
    TelegramMessageModel,
    TelegramUserModel,
)


class TelegramUserModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramUserModel
        fields = "__all__"
        read_only_fields = ("id",)


class TelegramChatModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramChatModel
        fields = "__all__"
        read_only_fields = ("id",)


class TelegramMessageModelSerializer(serializers.ModelSerializer):
    from_user = TelegramUserModelSerializer(read_only=True)
    chat = TelegramChatModelSerializer(read_only=True)

    class Meta:
        model = TelegramMessageModel
        fields = "__all__"
        read_only_fields = ("id",)
