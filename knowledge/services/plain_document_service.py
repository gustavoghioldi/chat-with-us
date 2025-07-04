from agno.document.base import Document
from agno.embedder.google import GeminiEmbedder
from agno.knowledge.document import DocumentKnowledgeBase
from agno.vectordb.pgvector import PgVector

from main.settings import IA_DB, IA_MODEL


class PlainDocumentService:
    """Servicio para gestionar documentos de texto plano."""

    @staticmethod
    def get_knowledge_base(agent_model, documents, ia_token=None):
        """
        Crea una base de conocimiento para documentos de texto plano.

        Args:
            agent_model: Modelo del agente
            documents: Lista de contenidos de texto
            ia_token: Token de IA para el embedder

        Returns:
            DocumentKnowledgeBase: Base de conocimiento para documentos planos
        """
        document_objects = [Document(content=text) for text in documents]

        return DocumentKnowledgeBase(
            documents=document_objects,
            vector_db=PgVector(
                table_name=f"ia_documents_{agent_model.name}",
                db_url=IA_DB,
                embedder=GeminiEmbedder(api_key=ia_token),
            ),
        )
