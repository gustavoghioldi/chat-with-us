"""
Factory para crear servicios de procesamiento de documentos según el tipo de archivo.
"""

from abc import ABC, abstractmethod
from typing import List, Type


class BaseDocumentService(ABC):
    """Clase base abstracta para servicios de documentos"""

    @staticmethod
    @abstractmethod
    def get_knowledge_base(agent_model, file_paths, ia_token=None):
        """
        Crea una base de conocimiento para archivos del tipo específico.

        Args:
            agent_model: Modelo del agente
            file_paths: Lista de rutas a archivos
            ia_token: Token de IA para los servicios

        Returns:
            list: Lista de bases de conocimiento
        """
        pass


class DocumentServiceFactory:
    """Factory para crear servicios de procesamiento de documentos"""

    # Mapeo de extensiones a servicios
    _services = {}

    @classmethod
    def register_service(cls, extensions: List[str], service_class):
        """
        Registra un servicio para las extensiones especificadas.

        Args:
            extensions: Lista de extensiones de archivo (ej: ['pdf'])
            service_class: Clase del servicio de documentos (debe tener método get_knowledge_base)

        Raises:
            ValueError: Si la clase no implementa get_knowledge_base
        """
        # Verificar que la clase tenga el método get_knowledge_base usando duck typing
        if not hasattr(service_class, "get_knowledge_base"):
            raise ValueError(
                f"El servicio {service_class.__name__} debe implementar el método 'get_knowledge_base'"
            )

        # Verificar que get_knowledge_base sea un método estático o de clase
        if not callable(getattr(service_class, "get_knowledge_base")):
            raise ValueError(
                f"El método 'get_knowledge_base' en {service_class.__name__} debe ser callable"
            )

        for ext in extensions:
            cls._services[ext.lower()] = service_class

    @classmethod
    def get_service(cls, file_extension: str):
        """
        Obtiene el servicio apropiado para una extensión de archivo.

        Args:
            file_extension: Extensión del archivo (ej: 'pdf', 'docx')

        Returns:
            class: Clase del servicio apropiado

        Raises:
            ValueError: Si la extensión no es soportada
        """
        ext = file_extension.lower().lstrip(".")
        service_class = cls._services.get(ext)

        if not service_class:
            supported_extensions = ", ".join(cls._services.keys())
            raise ValueError(
                f"Extensión '{ext}' no soportada. "
                f"Extensiones soportadas: {supported_extensions}"
            )

        return service_class

    @classmethod
    def process_files_by_type(
        cls, agent_model, files_by_extension: dict, ia_token: str = None
    ) -> list:
        """
        Procesa archivos agrupados por extensión usando los servicios apropiados.

        Args:
            agent_model: Modelo del agente
            files_by_extension: Dict con extensión como clave y lista de archivos como valor
                                ej: {'pdf': ['/path/file1.pdf'], 'docx': ['/path/file2.docx']}
            ia_token: Token de IA para los servicios

        Returns:
            list: Lista de bases de conocimiento combinadas
        """
        knowledge_sources = []

        for extension, file_paths in files_by_extension.items():
            if not file_paths:
                continue

            try:
                service_class = cls.get_service(extension)
                knowledge_collection = service_class.get_knowledge_base(
                    agent_model, file_paths, ia_token
                )

                # Algunos servicios retornan una lista, otros un objeto
                if isinstance(knowledge_collection, list):
                    knowledge_sources.extend(knowledge_collection)
                elif knowledge_collection is not None:
                    knowledge_sources.append(knowledge_collection)

            except ValueError as e:
                # Log error pero continúa con otros tipos de archivo
                print(f"⚠️ Error procesando archivos {extension}: {e}")
                continue

        return knowledge_sources

    @classmethod
    def get_supported_extensions(cls) -> list:
        """
        Retorna la lista de extensiones soportadas.

        Returns:
            list: Lista de extensiones soportadas
        """
        return list(cls._services.keys())


# Auto-registro de servicios de documentos
def _register_default_services():
    """Registra los servicios de documentos por defecto"""
    try:
        from knowledge.services.csv_document_service import CSVDocumentService
        from knowledge.services.docx_document_service import DocxDocumentService
        from knowledge.services.json_document_service import JSONDocumentService
        from knowledge.services.markdown_document_service import MarkdownDocumentService
        from knowledge.services.pdf_document_service import PDFDocumentService
        from knowledge.services.plain_document_service import PlainDocumentService

        DocumentServiceFactory.register_service(["pdf"], PDFDocumentService)
        DocumentServiceFactory.register_service(["doc", "docx"], DocxDocumentService)
        DocumentServiceFactory.register_service(["csv"], CSVDocumentService)
        DocumentServiceFactory.register_service(["json"], JSONDocumentService)
        DocumentServiceFactory.register_service(
            ["md", "markdown"], MarkdownDocumentService
        )
        DocumentServiceFactory.register_service(["txt"], PlainDocumentService)

    except ImportError as e:
        print(f"⚠️ Error importando servicios de documentos: {e}")


# Registrar servicios por defecto al importar el módulo
_register_default_services()
