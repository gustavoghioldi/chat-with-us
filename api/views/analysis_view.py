"""
Analysis API Views

Vistas relacionadas con el análisis de sentimientos y métricas de chat.
"""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from analysis.models import SentimentAgentModel, SentimentChatModel
from api.permissions_classes.is_tenant_authenticated import IsTenantAuthenticated


class SentimentAnalysisViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet de solo lectura para análisis de sentimientos.

    Endpoints disponibles:
    - GET /api/v1/analysis/sentiment/ - Listar análisis de sentimientos
    - GET /api/v1/analysis/sentiment/{id}/ - Obtener análisis específico
    - GET /api/v1/analysis/sentiment/stats/ - Estadísticas generales
    """

    queryset = SentimentChatModel.objects.all()
    permission_classes = [IsTenantAuthenticated]

    @action(detail=False, methods=["get"])
    def stats(self, request):
        """
        Obtiene estadísticas de sentimientos por tenant.

        Ejemplo de implementación que usa IsTenantAuthenticated.
        """
        # TODO: Implementar lógica de filtrado por tenant
        # El permission_class se encargará de la autenticación

        stats = {
            "total_analyses": self.get_queryset().count(),
            "positive": self.get_queryset().filter(actitude="POSITIVO").count(),
            "negative": self.get_queryset().filter(actitude="NEGATIVO").count(),
            "neutral": self.get_queryset().filter(actitude="NEUTRO").count(),
        }

        return Response(stats, status=status.HTTP_200_OK)


# Ejemplo de cómo implementar IsTenantAuthenticated en vistas futuras:
"""
from rest_framework import viewsets
from api.permissions_classes.is_tenant_authenticated import IsTenantAuthenticated

class MiNuevaViewSet(viewsets.ModelViewSet):
    queryset = MiModelo.objects.all()
    permission_classes = [IsTenantAuthenticated]  # ← Siempre agregar esta línea

    # ... resto de la configuración
"""
