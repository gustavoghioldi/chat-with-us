from agno.embedder.ollama import OllamaEmbedder
from agno.knowledge.website import WebsiteKnowledgeBase
from agno.vectordb.pgvector import PgVector

from main.settings import IA_DB, IA_MODEL


class WebsiteService:
    """Servicio para gestionar documentos de sitios web."""

    @staticmethod
    def get_knowledge_base(agent_model, urls):
        """
        Crea una base de conocimiento para sitios web.

        Args:
            agent_model: Modelo del agente
            urls: Lista de URLs

        Returns:
            WebsiteKnowledgeBase: Base de conocimiento para sitios web
        """
        if not urls:
            return None

        return WebsiteKnowledgeBase(
            urls=urls,
            vector_db=PgVector(
                table_name=f"ia_website_documents_{agent_model.name}",
                db_url=IA_DB,
                embedder=OllamaEmbedder(id=IA_MODEL, dimensions=3072),
            ),
        )
