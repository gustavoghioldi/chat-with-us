from django.urls import path

from api.views.chat_view import ChatView

urlpatterns = [
    path("v1/chat", ChatView.as_view(), name="api-chat"),
]
