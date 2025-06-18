from datetime import datetime

from agno.document.base import Document
from agno.embedder.ollama import OllamaEmbedder
from agno.knowledge.combined import CombinedKnowledgeBase
from agno.knowledge.csv import CSVKnowledgeBase
from agno.knowledge.document import DocumentKnowledgeBase
from agno.knowledge.docx import DocxKnowledgeBase
from agno.knowledge.json import JSONKnowledgeBase
from agno.knowledge.markdown import MarkdownKnowledgeBase
from agno.knowledge.pdf import PDFKnowledgeBase
from agno.knowledge.website import WebsiteKnowledgeBase
from agno.vectordb.pgvector import PgVector

from agents.models import AgentModel
from main.settings import IA_DB, IA_MODEL, IA_MODEL_EMBEDDING


class DocumentKnowledgeBaseService:

    def __init__(self, agent: str):
        self.agent_model = AgentModel.objects.get(name=agent)

    def get_knowledge_base(self):
        # Verificar si algún modelo de conocimiento necesita recreación
        recreate = self.agent_model.knoledge_text_models.filter(recreate=True).exists()
        documents = []
        sites = []
        files_csv = []
        files_json = []
        files_pdf = []
        files_docx = []
        files_markdown = []

        for k in self.agent_model.knoledge_text_models.all():
            if k.category == "plain_document":
                documents.append(Document(content=k.text))
            if k.category == "website":
                sites.append(k.url)
            if k.category == "document":
                file_ext = k.path.split(".")[-1].lower()
                if file_ext == "csv":
                    files_csv.append(k.path)
                elif file_ext == "json":
                    files_json.append(k.path)
                elif file_ext == "pdf":
                    files_pdf.append(k.path)
                elif file_ext in ["doc", "docx"]:
                    files_docx.append(k.path)
                elif file_ext in ["md", "markdown"]:
                    files_markdown.append(k.path)

        # CSV Knowledge Base
        knowledge_csv_collection = []
        for i in files_csv:
            knowledge_csv_collection.append(
                CSVKnowledgeBase(
                    path=i,
                    vector_db=PgVector(
                        table_name=f"ia_csv_documents_{self.agent_model.name}",
                        db_url=IA_DB,
                        embedder=OllamaEmbedder(id=IA_MODEL, dimensions=3072),
                    ),
                )
            )

        # JSON Knowledge Base
        knowledge_json_collection = []
        for i in files_json:
            knowledge_json_collection.append(
                JSONKnowledgeBase(
                    path=i,
                    vector_db=PgVector(
                        table_name=f"ia_json_documents_{self.agent_model.name}",
                        db_url=IA_DB,
                        embedder=OllamaEmbedder(id=IA_MODEL, dimensions=3072),
                    ),
                )
            )

        # PDF Knowledge Base
        knowledge_pdf_collection = []
        for i in files_pdf:
            knowledge_pdf_collection.append(
                PDFKnowledgeBase(
                    path=i,
                    vector_db=PgVector(
                        table_name=f"ia_pdf_documents_{self.agent_model.name}",
                        db_url=IA_DB,
                        embedder=OllamaEmbedder(id=IA_MODEL, dimensions=3072),
                    ),
                )
            )

        # DOCX Knowledge Base
        knowledge_docx_collection = []
        for i in files_docx:
            knowledge_docx_collection.append(
                DocxKnowledgeBase(
                    path=i,
                    vector_db=PgVector(
                        table_name=f"ia_docx_documents_{self.agent_model.name}",
                        db_url=IA_DB,
                        embedder=OllamaEmbedder(id=IA_MODEL, dimensions=3072),
                    ),
                )
            )

        # Markdown Knowledge Base
        knowledge_markdown_collection = []
        for i in files_markdown:
            knowledge_markdown_collection.append(
                MarkdownKnowledgeBase(
                    path=i,
                    vector_db=PgVector(
                        table_name=f"ia_markdown_documents_{self.agent_model.name}",
                        db_url=IA_DB,
                        embedder=OllamaEmbedder(id=IA_MODEL, dimensions=3072),
                    ),
                )
            )

        knowledge_base_documents = DocumentKnowledgeBase(
            documents=documents,
            vector_db=PgVector(
                table_name=f"ia_documents_{self.agent_model.name}",
                db_url=IA_DB,
                embedder=OllamaEmbedder(id=IA_MODEL, dimensions=3072),
            ),
        )

        knowledge_base_web = WebsiteKnowledgeBase(
            urls=sites,
            vector_db=PgVector(
                table_name=f"ia_website_documents_{self.agent_model.name}",
                db_url="postgresql+psycopg://ai:ai@localhost:5532/ai",
            ),
            embedder=OllamaEmbedder(id=IA_MODEL, dimensions=3072),
        )

        combined_knowledge = CombinedKnowledgeBase(
            sources=[
                knowledge_base_web,
                knowledge_base_documents,
            ]
            + knowledge_csv_collection
            + knowledge_json_collection
            + knowledge_pdf_collection
            + knowledge_docx_collection
            + knowledge_markdown_collection,
            vector_db=PgVector(
                table_name=f"ia_combined_documents_{self.agent_model.name}",
                db_url=IA_DB,
                embedder=OllamaEmbedder(id=IA_MODEL_EMBEDDING, dimensions=3072),
            ),
        )

        combined_knowledge.load(recreate=recreate)

        return combined_knowledge
