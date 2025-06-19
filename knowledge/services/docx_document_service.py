from agno.embedder.ollama import OllamaEmbedder
from agno.knowledge.docx import DocxKnowledgeBase
from agno.vectordb.pgvector import PgVector

from main.settings import IA_DB, IA_MODEL


class DocxDocumentService:
    """Servicio para gestionar documentos DOCX."""

    @staticmethod
    def get_knowledge_base(agent_model, file_paths):
        """
        Crea una base de conocimiento para archivos DOCX.

        Args:
            agent_model: Modelo del agente
            file_paths: Lista de rutas a archivos DOCX

        Returns:
            list: Lista de bases de conocimiento para archivos DOCX
        """
        if not file_paths:
            return []

        knowledge_collection = []

        for path in file_paths:
            knowledge_collection.append(
                DocxKnowledgeBase(
                    path=path,
                    vector_db=PgVector(
                        table_name=f"ia_docx_documents_{agent_model.name}",
                        db_url=IA_DB,
                        embedder=OllamaEmbedder(id=IA_MODEL, dimensions=3072),
                    ),
                )
            )

        return knowledge_collection
