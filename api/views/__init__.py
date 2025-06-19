"""
API Views Module

Este módulo contiene todas las vistas de la API REST del proyecto Chat With Us.
Todas las vistas implementan IsTenantAuthenticated para control de acceso basado en tenant.

Vistas disponibles:
- AgentModelViewSet: CRUD para modelos de agentes IA
- ChatView: Endpoint para interacciones de chat
- KnowledgeViewSet: CRUD para modelos de conocimiento
- AnalysisView: (Futuro) Análisis de sentimientos
- TenantsView: (Futuro) Gestión de tenants
- UserProfileView: (Futuro) Gestión de perfiles de usuario
"""

from .agents_view import AgentModelViewSet
from .chat_view import ChatView
from .knowledge_crud_view import KnowledgeViewSet

__all__ = [
    "AgentModelViewSet",
    "ChatView",
    "KnowledgeViewSet",
]
