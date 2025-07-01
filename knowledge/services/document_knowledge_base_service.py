from agno.embedder.google import GeminiEmbedder
from agno.embedder.ollama import OllamaEmbedder
from agno.knowledge.combined import CombinedKnowledgeBase
from agno.vectordb.pgvector import PgVector

from agents.models import AgentModel
from knowledge.services.document_service_factory import DocumentServiceFactory
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

        # Agrupar archivos por extensión para usar el factory
        files_by_extension = {}
        plain_texts = []
        website_urls = []

        # Categorizar los modelos de conocimiento
        for knowledge in self.agent_model.knoledge_text_models.all():
            if knowledge.category == "plain_document":
                plain_texts.append(knowledge.text)
            elif knowledge.category == "website":
                website_urls.append(knowledge.url)
            elif (
                knowledge.category == "document"
                and knowledge.document
                and knowledge.document.file
            ):
                file_path = knowledge.document.file.path
                file_ext = knowledge.document.file.name.split(".")[-1].lower()

                # Agrupar archivos por extensión
                if file_ext not in files_by_extension:
                    files_by_extension[file_ext] = []
                files_by_extension[file_ext].append(file_path)

        # Obtener bases de conocimiento usando factories y servicios específicos
        knowledge_sources = []

        # Documentos de texto plano (usando servicio específico)
        if plain_texts:
            knowledge_base_plain = PlainDocumentService.get_knowledge_base(
                self.agent_model, plain_texts
            )
            knowledge_sources.append(knowledge_base_plain)

        # Sitios web (usando servicio específico)
        if website_urls:
            knowledge_base_web = WebsiteService.get_knowledge_base(
                self.agent_model, website_urls, self.agent_model.tenant.ai_token
            )
            if knowledge_base_web:  # WebsiteService puede devolver None si no hay URLs
                knowledge_sources.append(knowledge_base_web)

        # Procesar archivos usando el DocumentServiceFactory
        if files_by_extension:
            document_knowledge_sources = DocumentServiceFactory.process_files_by_type(
                self.agent_model, files_by_extension
            )
            knowledge_sources.extend(document_knowledge_sources)

        # Combinar todas las bases de conocimiento
        combined_knowledge = CombinedKnowledgeBase(
            sources=knowledge_sources,
            vector_db=PgVector(
                table_name=f"ia_combined_documents_{self.agent_model.name}",
                db_url=IA_DB,
                # embedder=OllamaEmbedder(id=IA_MODEL_EMBEDDING, dimensions=3072),
                embedder=GeminiEmbedder(api_key=self.agent_model.tenant.ai_token),
            ),
            num_documents=1,
        )

        # Cargar la base de conocimiento
        if (
            not combined_knowledge.vector_db.search(
                "ia_combined_documents_GeminiTestAgent", limit=1
            )
            or recreate
        ):
            combined_knowledge.load(recreate=recreate)

        # Usa este código para que se emitan las señales:
        for knowledge in self.agent_model.knoledge_text_models.filter(recreate=True):
            knowledge.recreate = False
            knowledge.save()

        return combined_knowledge
