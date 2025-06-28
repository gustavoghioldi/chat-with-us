from agno.embedder.google import GeminiEmbedder
from agno.knowledge.markdown import MarkdownKnowledgeBase
from agno.vectordb.pgvector import PgVector

from main.settings import IA_DB, IA_MODEL


class MarkdownDocumentService:
    """Servicio para gestionar documentos Markdown."""

    @staticmethod
    def get_knowledge_base(agent_model, file_paths, ia_token=None):
        """
        Crea una base de conocimiento para archivos Markdown.

        Args:
            agent_model: Modelo del agente
            file_paths: Lista de rutas a archivos Markdown
            ia_token: Token de IA para el embedder

        Returns:
            list: Lista de bases de conocimiento para archivos Markdown
        """
        if not file_paths:
            return []

        knowledge_collection = []

        for path in file_paths:
            knowledge_collection.append(
                MarkdownKnowledgeBase(
                    path=path,
                    vector_db=PgVector(
                        table_name=f"ia_markdown_documents_{agent_model.name}",
                        db_url=IA_DB,
                        embedder=GeminiEmbedder(api_key=ia_token),
                    ),
                )
            )

        return knowledge_collection
