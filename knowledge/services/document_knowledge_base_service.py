from agno.embedder.ollama import OllamaEmbedder
from agno.knowledge.combined import CombinedKnowledgeBase
from agno.vectordb.pgvector import PgVector

from agents.models import AgentModel
from knowledge.services.csv_document_service import CSVDocumentService
from knowledge.services.docx_document_service import DocxDocumentService
from knowledge.services.json_document_service import JSONDocumentService
from knowledge.services.markdown_document_service import MarkdownDocumentService
from knowledge.services.pdf_document_service import PDFDocumentService
from knowledge.services.plain_document_service import PlainDocumentService
from knowledge.services.website_service import WebsiteService
from main.settings import IA_DB, IA_MODEL_EMBEDDING


class DocumentKnowledgeBaseService:

    def __init__(self, agent: str):
        self.agent_model = AgentModel.objects.get(name=agent)

    def get_knowledge_base(self):
        """
        Obtiene una base de conocimiento combinada de todas las fuentes disponibles.

        Returns:
            CombinedKnowledgeBase: Base de conocimiento combinada
        """
        # Verificar si algún modelo de conocimiento necesita recreación
        recreate = self.agent_model.knoledge_text_models.filter(recreate=True).exists()

        # Clasificar los documentos por tipo
        plain_texts = []
        website_urls = []
        csv_files = []
        json_files = []
        pdf_files = []
        docx_files = []
        markdown_files = []

        # Categorizar los modelos de conocimiento
        for knowledge in self.agent_model.knoledge_text_models.all():
            if knowledge.category == "plain_document":
                plain_texts.append(knowledge.text)
            elif knowledge.category == "website":
                website_urls.append(knowledge.url)
            elif knowledge.category == "document":
                file_ext = (
                    knowledge.path.split(".")[-1].lower() if knowledge.path else ""
                )
                if file_ext == "csv":
                    csv_files.append(knowledge.path)
                elif file_ext == "json":
                    json_files.append(knowledge.path)
                elif file_ext == "pdf":
                    pdf_files.append(knowledge.path)
                elif file_ext in ["doc", "docx"]:
                    docx_files.append(knowledge.path)
                elif file_ext in ["md", "markdown"]:
                    markdown_files.append(knowledge.path)

        # Obtener bases de conocimiento para cada tipo de documento
        knowledge_sources = []

        # Documentos de texto plano
        if plain_texts:
            knowledge_base_plain = PlainDocumentService.get_knowledge_base(
                self.agent_model, plain_texts
            )
            knowledge_sources.append(knowledge_base_plain)

        # Sitios web
        if website_urls:
            knowledge_base_web = WebsiteService.get_knowledge_base(
                self.agent_model, website_urls
            )
            if knowledge_base_web:  # WebsiteService puede devolver None si no hay URLs
                knowledge_sources.append(knowledge_base_web)

        # Archivos CSV
        csv_knowledge_collection = CSVDocumentService.get_knowledge_base(
            self.agent_model, csv_files
        )
        knowledge_sources.extend(csv_knowledge_collection)

        # Archivos JSON
        json_knowledge_collection = JSONDocumentService.get_knowledge_base(
            self.agent_model, json_files
        )
        knowledge_sources.extend(json_knowledge_collection)

        # Archivos PDF
        pdf_knowledge_collection = PDFDocumentService.get_knowledge_base(
            self.agent_model, pdf_files
        )
        knowledge_sources.extend(pdf_knowledge_collection)

        # Archivos DOCX
        docx_knowledge_collection = DocxDocumentService.get_knowledge_base(
            self.agent_model, docx_files
        )
        knowledge_sources.extend(docx_knowledge_collection)

        # Archivos Markdown
        markdown_knowledge_collection = MarkdownDocumentService.get_knowledge_base(
            self.agent_model, markdown_files
        )
        knowledge_sources.extend(markdown_knowledge_collection)

        # Combinar todas las bases de conocimiento
        combined_knowledge = CombinedKnowledgeBase(
            sources=knowledge_sources,
            vector_db=PgVector(
                table_name=f"ia_combined_documents_{self.agent_model.name}",
                db_url=IA_DB,
                embedder=OllamaEmbedder(id=IA_MODEL_EMBEDDING, dimensions=3072),
            ),
        )

        # Cargar la base de conocimiento
        combined_knowledge.load(recreate=recreate)

        return combined_knowledge
