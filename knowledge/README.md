# Módulo de Knowledge (Base de Conocimiento)

## Descripción General
Este módulo gestiona la base de conocimiento del sistema, permitiendo almacenar, organizar y consultar información estructurada desde diferentes fuentes. El módulo se integra con el sistema de documentos y agentes para proporcionar respuestas basadas en conocimiento.

## Estructura del Módulo

- **models.py**: Define el modelo principal `KnowledgeModel` que representa una unidad de conocimiento con diferentes categorías (documento, web, texto plano).
- **admin.py**: Configuración para administrar la base de conocimiento en el panel de administración de Django, con interfaces especializadas según el tipo de contenido.
- **views.py**: Vistas generales para la gestión del conocimiento.
- **tests.py**: Pruebas unitarias y de integración para el módulo.

### Carpeta `forms/`
Contiene formularios personalizados para:
- `DocumentSelectionForm`: Selección de documentos existentes para importar al conocimiento
- `FileUploadForm`: Carga de archivos para crear nuevas entradas de conocimiento

### Carpeta `migrations/`
Contiene las migraciones de la base de datos para los modelos de conocimiento.

### Carpeta `services/`
Servicios especializados para procesar diferentes tipos de conocimiento:
- `document_knowledge_base_service.py`: Servicio principal para gestionar la base de conocimiento
- `plain_document_service.py`: Manejo de documentos de texto plano
- `website_service.py`: Extracción y procesamiento de contenido web
- `csv_document_service.py`: Procesamiento de archivos CSV
- `json_document_service.py`: Procesamiento de archivos JSON
- `pdf_document_service.py`: Extracción y procesamiento de contenido de PDFs
- `docx_document_service.py`: Extracción y procesamiento de documentos Word
- `markdown_document_service.py`: Procesamiento de archivos Markdown

### Carpeta `signals/`
Define señales para reaccionar a eventos en el sistema de conocimiento:
- Emisores de eventos para cambios en el estado de recreación
- Receptores que reaccionan a estos cambios
- Gestión automática del estado de procesamiento de documentos asociados

### Carpeta `views/admin/`
Vistas especializadas para el panel de administración:
- `import_documents_view.py`: Vista para importar documentos existentes
- `upload_file_view.py`: Vista para cargar nuevos archivos

## Funcionalidades Principales

1. **Gestión multi-fuente**: Capacidad de almacenar conocimiento de diversas fuentes (documentos, sitios web, texto plano).
2. **Procesamiento especializado**: Servicios específicos para cada tipo de documento (PDF, DOCX, CSV, JSON, etc.).
3. **Integración con documentos**: Relación con `DocumentModel` para reutilización de documentos.
4. **Recreación bajo demanda**: Mecanismo para marcar y recrear bases de conocimiento cuando cambian los datos fuente.
5. **Interfaz administrativa**: Panel especializado para gestionar el conocimiento con visualización apropiada según el tipo.

## Flujo de Trabajo

1. El administrador importa conocimiento desde documentos existentes o carga nuevos.
2. El sistema procesa el contenido según su tipo usando servicios especializados.
3. El conocimiento queda disponible para que los agentes lo consulten.
4. Cuando hay cambios en las fuentes (documentos), se marca el conocimiento para recreación.
5. El sistema automáticamente mantiene la consistencia entre documentos y conocimiento mediante signals.
