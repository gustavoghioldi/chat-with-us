from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import DocumentModelViewSet

# Configurar router para ViewSets
router = DefaultRouter()
router.register(r"documents", DocumentModelViewSet, basename="documents")

app_name = "documents"

urlpatterns = [
    path("", include(router.urls)),
]
