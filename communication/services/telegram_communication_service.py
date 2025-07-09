import requests

from communication.models.telegram.telegram_communication_model import (
    TelegramCommunicationModel,
)


class TelegramCommunicationService:
    def __init__(self, telegram_communication_model: TelegramCommunicationModel):
        self.telegram_communication_model: TelegramCommunicationModel = (
            telegram_communication_model
        )

    def send_message(self, chat_id: int, message: str) -> None:
        url = f"https://api.telegram.org/bot{self.telegram_communication_model.token}/sendMessage"
        payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            raise Exception(f"Failed to send message: {response.text}")

    def get_updates(self, offset=0) -> dict:
        url = f"https://api.telegram.org/bot{self.telegram_communication_model.token}/getUpdates?limit=100&offset={offset}"
        response = requests.get(url)

        if response.status_code != 200:
            raise Exception(f"Failed to get updates: {response.text}")

        return response.json()
