from rest_framework import serializers

from communication.models.telegram.telegram_chat_model import TelegramChatModel


class TelegramChatModelSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = TelegramChatModel

    def to_internal_value(self, data):
        _data = {}
        _data["update_id"] = data.get("update_id")
        _data["text"] = data.get("message").get("text")
        _data["chat_id"] = data.get("message").get("chat").get("id")
        _data["is_bot"] = data.get("message").get("from").get("is_bot")
        _data["date"] = data.get("message").get("date")
        _data["first_name"] = data.get("message").get("from").get("first_name")
        _data["last_name"] = data.get("message").get("from").get("last_name")
        _data["language_code"] = data.get("message").get("from").get("language_code")
        _data["message_id"] = data.get("message").get("message_id")
        _data["agent"] = data.get("agent").pk
        _data["telegram_communication"] = data.get("telegram_communication")
        return super().to_internal_value(_data)

    def validate(self, attrs):
        return super().validate(attrs)

    def create(self, validated_data):
        return super().create(validated_data)
