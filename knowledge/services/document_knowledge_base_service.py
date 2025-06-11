from agno.document.base import Document
from agno.embedder.ollama import OllamaEmbedder
from agno.knowledge.document import DocumentKnowledgeBase
from agno.vectordb.pgvector import PgVector

from agents.models import AgentModel
from main.settings import IA_DB, IA_MODEL


class DocumentKnowledgeBaseService:

    def __init__(self, agent: str):
        self.agent_model = AgentModel.objects.get(name=agent)

    def get_knowledge_base(self):
        documents = []
        for k in self.agent_model.knoledge_text_models.all():
            documents.append(Document(content=k.text))

        knowledge_base = DocumentKnowledgeBase(
            documents=documents,
            vector_db=PgVector(
                table_name="ia_documents",
                db_url=IA_DB,
                embedder=OllamaEmbedder(id=IA_MODEL, dimensions=3072),
            ),
        )
        knowledge_base.load(recreate=False)
        return knowledge_base
