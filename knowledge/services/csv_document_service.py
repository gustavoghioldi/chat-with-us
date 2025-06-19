from agno.embedder.ollama import OllamaEmbedder
from agno.knowledge.csv import CSVKnowledgeBase
from agno.vectordb.pgvector import PgVector

from main.settings import IA_DB, IA_MODEL


class CSVDocumentService:
    """Servicio para gestionar documentos CSV."""

    @staticmethod
    def get_knowledge_base(agent_model, file_paths):
        """
        Crea una base de conocimiento para archivos CSV.

        Args:
            agent_model: Modelo del agente
            file_paths: Lista de rutas a archivos CSV

        Returns:
            list: Lista de bases de conocimiento para archivos CSV
        """
        if not file_paths:
            return []

        knowledge_collection = []

        for path in file_paths:
            knowledge_collection.append(
                CSVKnowledgeBase(
                    path=path,
                    vector_db=PgVector(
                        table_name=f"ia_csv_documents_{agent_model.name}",
                        db_url=IA_DB,
                        embedder=OllamaEmbedder(id=IA_MODEL, dimensions=3072),
                    ),
                )
            )

        return knowledge_collection
