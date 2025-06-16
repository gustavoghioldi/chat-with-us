from agno.document.base import Document
from agno.embedder.ollama import OllamaEmbedder
from agno.knowledge.combined import CombinedKnowledgeBase
from agno.knowledge.document import DocumentKnowledgeBase
from agno.knowledge.website import WebsiteKnowledgeBase
from agno.vectordb.pgvector import PgVector

from agents.models import AgentModel
from main.settings import IA_DB, IA_MODEL


class DocumentKnowledgeBaseService:

    def __init__(self, agent: str):
        self.agent_model = AgentModel.objects.get(name=agent)

    def get_knowledge_base(self):
        # Verificar si algún modelo de conocimiento necesita recreación
        recreate = self.agent_model.knoledge_text_models.filter(recreate=True).exists()
        documents = []
        sites = []

        for k in self.agent_model.knoledge_text_models.all():
            if k.category == "plain_document":
                documents.append(Document(content=k.text))
            if k.category == "website":
                sites.append(k.url)

        knowledge_base_documents = DocumentKnowledgeBase(
            documents=documents,
            # vector_db=PgVector(
            #     table_name="ia_documents",
            #     db_url=IA_DB,
            #     embedder=OllamaEmbedder(id=IA_MODEL, dimensions=3072),
            # ),
        )

        knowledge_base_web = WebsiteKnowledgeBase(
            urls=sites,
            max_depth=1,
            max_links=1,
            # vector_db=PgVector(
            #     table_name="ia_website_documents",
            #     db_url="postgresql+psycopg://ai:ai@localhost:5532/ai",
            # ),
            embedder=OllamaEmbedder(id=IA_MODEL, dimensions=3072),
        )

        combined_knowledge = CombinedKnowledgeBase(
            sources=[
                knowledge_base_web,
                knowledge_base_documents,
            ],
            vector_db=PgVector(
                table_name=f"{self.agent_model.tenant.name}_{self.agent_model.name}_ia_combined_documents",
                db_url=IA_DB,
                embedder=OllamaEmbedder(id=IA_MODEL, dimensions=3072),
            ),
        )

        combined_knowledge.load(recreate=recreate)  # TODO: dar TTL o forzar

        # Marcar todos los modelos de conocimiento utilizados como procesados (recreate=False)
        self.agent_model.knoledge_text_models.update(recreate=False)

        return combined_knowledge
