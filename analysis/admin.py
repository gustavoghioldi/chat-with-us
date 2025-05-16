from django.contrib import admin
from analysis.models.sentiment_chat_model import SentimentChatModel

@admin.register(SentimentChatModel)
class SentimentAdmin(admin.ModelAdmin):
    pass