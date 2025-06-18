from agno.embedder.ollama import OllamaEmbedder
from agno.knowledge.pdf import PDFKnowledgeBase
from agno.vectordb.pgvector import PgVector

from main.settings import IA_DB, IA_MODEL


class PDFDocumentService:
    """Servicio para gestionar documentos PDF."""

    @staticmethod
    def get_knowledge_base(agent_model, file_paths):
        """
        Crea una base de conocimiento para archivos PDF.

        Args:
            agent_model: Modelo del agente
            file_paths: Lista de rutas a archivos PDF

        Returns:
            list: Lista de bases de conocimiento para archivos PDF
        """
        if not file_paths:
            return []

        knowledge_collection = []

        for path in file_paths:
            knowledge_collection.append(
                PDFKnowledgeBase(
                    path=path,
                    vector_db=PgVector(
                        table_name=f"ia_pdf_documents_{agent_model.name}",
                        db_url=IA_DB,
                        embedder=OllamaEmbedder(id=IA_MODEL, dimensions=3072),
                    ),
                )
            )

        return knowledge_collection
