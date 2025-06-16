from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views.agents_view import AgentModelViewSet
from api.views.chat_view import ChatView
from api.views.knowledge_crud_view import KnowledgeViewSet

# Configurar router para ViewSets
router = DefaultRouter()
router.register(r"agents", AgentModelViewSet, basename="agents")

urlpatterns = [
    path("v1/chat", ChatView.as_view(), name="api-chat"),
    path("v1/", include(router.urls)),
    # URLs específicas para Knowledge con tipos
    path(
        "v1/knowledge/<str:knowledge_type>/",
        KnowledgeViewSet.as_view({"get": "list", "post": "create"}),
        name="knowledge-list-create",
    ),
    path(
        "v1/knowledge/<str:knowledge_type>/<int:pk>/",
        KnowledgeViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="knowledge-detail",
    ),
]
