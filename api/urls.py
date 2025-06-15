from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views.agents_view import AgentModelViewSet
from api.views.chat_view import ChatView

# Configurar router para ViewSets
router = DefaultRouter()
router.register(r"agents", AgentModelViewSet, basename="agents")

urlpatterns = [
    path("v1/chat", ChatView.as_view(), name="api-chat"),
    path("v1/", include(router.urls)),
]
