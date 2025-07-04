# Documents - Migrations

## Descripción

Este directorio contiene las migraciones de base de datos para el módulo de documentos, que gestiona los cambios en el esquema de la base de datos para funcionalidades de gestión de documentos, tipos de archivo y metadatos.

## Estructura de Migraciones

```
migrations/
├── __init__.py
├── 0001_initial.py                              # Migración inicial
├── 0002_alter_documentmodel_document_type.py    # Modificación tipo documento v1
├── 0003_alter_documentmodel_document_type.py    # Modificación tipo documento v2
└── 0004_alter_documentmodel_document_type_and_more.py  # Modificación tipo y campos adicionales
```

## Evolución del Modelo

### 0001_initial.py
- **Propósito**: Migración inicial del módulo de documentos
- **Cambios**: Creación de la estructura base para gestión de documentos
- **Modelos**: DocumentModel base
- **Campos iniciales**:
  - Identificación única del documento
  - Nombre y descripción
  - Tipo de documento
  - Ruta del archivo
  - Metadatos básicos
  - Timestamps

### 0002_alter_documentmodel_document_type.py
- **Propósito**: Primera iteración de mejora del campo tipo de documento
- **Cambios**: Modificación del campo `document_type` en DocumentModel
- **Mejoras**:
  - Ampliación de tipos soportados
  - Validación mejorada
  - Categorización más específica

### 0003_alter_documentmodel_document_type.py
- **Propósito**: Segunda iteración de mejora del campo tipo de documento
- **Cambios**: Refinamiento adicional del campo `document_type`
- **Optimizaciones**:
  - Tipos de documento específicos
  - Validación de formato
  - Soporte para nuevos formatos

### 0004_alter_documentmodel_document_type_and_more.py
- **Propósito**: Mejora integral del modelo de documentos
- **Cambios**:
  - Ajuste final del campo `document_type`
  - Modificación de campos adicionales
- **Funcionalidades**:
  - Campos de metadatos extendidos
  - Validación mejorada
  - Soporte para múltiples formatos

## Arquitectura de Modelos

### DocumentModel (Estado Final)
```python
class DocumentModel(models.Model):
    DOCUMENT_TYPES = [
        ('pdf', 'PDF'),
        ('docx', 'Word Document'),
        ('txt', 'Text File'),
        ('md', 'Markdown'),
        ('html', 'HTML'),
        ('json', 'JSON'),
        ('csv', 'CSV'),
        ('xlsx', 'Excel'),
        ('pptx', 'PowerPoint'),
        ('image', 'Image'),
        ('audio', 'Audio'),
        ('video', 'Video'),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPES)
    file_path = models.FileField(upload_to='documents/')
    file_size = models.BigIntegerField()
    mime_type = models.CharField(max_length=100)
    checksum = models.CharField(max_length=64)  # SHA-256

    # Metadatos
    metadata = models.JSONField(default=dict)
    tags = models.JSONField(default=list)

    # Procesamiento
    is_processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True, blank=True)
    processing_error = models.TextField(blank=True)

    # Auditoría
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Documento"
        verbose_name_plural = "Documentos"
        indexes = [
            models.Index(fields=['document_type']),
            models.Index(fields=['uploaded_at']),
            models.Index(fields=['is_processed']),
        ]
```

## Mejores Prácticas

### Gestión de Migraciones
```python
# Aplicar migraciones
python manage.py migrate documents

# Verificar estado de migraciones
python manage.py showmigrations documents

# Crear nueva migración
python manage.py makemigrations documents
```

### Validación de Tipos
```python
# Validar tipos de documentos después de migración
python manage.py validate_document_types

# Migrar documentos existentes
python manage.py migrate_document_metadata
```

## Gestión de Datos

### Migración de Tipos de Documento
```python
# migration_script.py
from django.db import migrations

def migrate_document_types(apps, schema_editor):
    """Migrar tipos de documento a nueva estructura"""
    DocumentModel = apps.get_model('documents', 'DocumentModel')

    # Mapeo de tipos antiguos a nuevos
    type_mapping = {
        'document': 'pdf',
        'text': 'txt',
        'spreadsheet': 'xlsx',
        'presentation': 'pptx',
        'image_file': 'image',
        'audio_file': 'audio',
        'video_file': 'video',
    }

    for document in DocumentModel.objects.all():
        old_type = document.document_type
        if old_type in type_mapping:
            document.document_type = type_mapping[old_type]
            document.save()

def validate_document_integrity(apps, schema_editor):
    """Validar integridad de documentos después de migración"""
    DocumentModel = apps.get_model('documents', 'DocumentModel')

    # Verificar que todos los documentos tienen tipo válido
    valid_types = [choice[0] for choice in DocumentModel.DOCUMENT_TYPES]
    invalid_docs = DocumentModel.objects.exclude(document_type__in=valid_types)

    if invalid_docs.exists():
        raise ValueError(f"Encontrados {invalid_docs.count()} documentos con tipos inválidos")

class Migration(migrations.Migration):
    dependencies = [
        ('documents', '0003_alter_documentmodel_document_type'),
    ]

    operations = [
        migrations.RunPython(migrate_document_types),
        migrations.RunPython(validate_document_integrity),
    ]
```

### Migración de Metadatos
```python
def migrate_document_metadata(apps, schema_editor):
    """Migrar metadatos de documentos"""
    DocumentModel = apps.get_model('documents', 'DocumentModel')

    import os
    import mimetypes

    for document in DocumentModel.objects.all():
        if document.file_path:
            # Actualizar metadatos basados en archivo
            file_path = document.file_path.path
            if os.path.exists(file_path):
                # Tamaño del archivo
                document.file_size = os.path.getsize(file_path)

                # Tipo MIME
                mime_type, _ = mimetypes.guess_type(file_path)
                document.mime_type = mime_type or 'application/octet-stream'

                # Metadatos específicos por tipo
                if document.document_type == 'pdf':
                    document.metadata['pages'] = get_pdf_pages(file_path)
                elif document.document_type == 'image':
                    document.metadata['dimensions'] = get_image_dimensions(file_path)

                document.save()
```

## Testing de Migraciones

### Pruebas de Migración
```python
# tests/test_migrations.py
from django.test import TestCase
from django.db import connection
from django.core.management import call_command
from django.core.files.uploadedfile import SimpleUploadedFile

class DocumentMigrationTestCase(TestCase):
    def test_document_type_evolution(self):
        """Test evolución de tipos de documento"""
        from documents.models import DocumentModel
        from django.contrib.auth.models import User

        # Crear usuario de prueba
        user = User.objects.create_user(username='testuser')

        # Crear documento con tipo válido
        document = DocumentModel.objects.create(
            name="Test Document",
            description="Test description",
            document_type="pdf",
            file_path="test.pdf",
            file_size=1024,
            mime_type="application/pdf",
            uploaded_by=user
        )

        # Verificar campos requeridos
        self.assertEqual(document.document_type, "pdf")
        self.assertEqual(document.file_size, 1024)
        self.assertEqual(document.mime_type, "application/pdf")

    def test_metadata_structure(self):
        """Test estructura de metadatos"""
        from documents.models import DocumentModel
        from django.contrib.auth.models import User

        user = User.objects.create_user(username='testuser')

        document = DocumentModel.objects.create(
            name="Test Document",
            document_type="pdf",
            file_path="test.pdf",
            file_size=1024,
            mime_type="application/pdf",
            uploaded_by=user,
            metadata={'pages': 10, 'author': 'Test Author'},
            tags=['test', 'document']
        )

        # Verificar estructura de metadatos
        self.assertIsInstance(document.metadata, dict)
        self.assertIsInstance(document.tags, list)
        self.assertEqual(document.metadata['pages'], 10)
        self.assertIn('test', document.tags)
```

### Validación de Integridad
```python
def test_data_integrity_after_migration(self):
    """Verificar integridad de datos después de migración"""
    from documents.models import DocumentModel
    from django.contrib.auth.models import User

    user = User.objects.create_user(username='testuser')

    # Crear documento con todos los campos
    document = DocumentModel.objects.create(
        name="Complete Document",
        description="Complete test document",
        document_type="docx",
        file_path="test.docx",
        file_size=2048,
        mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        checksum="abc123def456",
        metadata={'word_count': 500, 'language': 'es'},
        tags=['document', 'word', 'test'],
        uploaded_by=user
    )

    # Verificar integridad completa
    self.assertEqual(document.name, "Complete Document")
    self.assertEqual(document.document_type, "docx")
    self.assertEqual(document.file_size, 2048)
    self.assertEqual(document.metadata['word_count'], 500)
    self.assertEqual(len(document.tags), 3)
```

## Configuración de Documentos

### Settings para Documentos
```python
# settings/base.py
DOCUMENT_SETTINGS = {
    'MAX_FILE_SIZE': 100 * 1024 * 1024,  # 100MB
    'ALLOWED_EXTENSIONS': ['.pdf', '.docx', '.txt', '.md', '.html'],
    'UPLOAD_PATH': 'documents/',
    'ENABLE_VIRUS_SCAN': True,
    'ENABLE_OCR': True,
    'OCR_LANGUAGES': ['es', 'en'],
    'THUMBNAIL_GENERATION': True,
    'AUTOMATIC_TAGGING': True,
    'DUPLICATE_DETECTION': True,
}
```

### Configuración de Procesamiento
```python
# Para procesamiento asíncrono
CELERY_ROUTES = {
    'documents.tasks.process_document': {'queue': 'document_processing'},
    'documents.tasks.generate_thumbnail': {'queue': 'image_processing'},
    'documents.tasks.extract_text': {'queue': 'text_extraction'},
}
```

## Comandos de Gestión

### Comandos de Migración
```python
# management/commands/migrate_document_data.py
from django.core.management.base import BaseCommand
from documents.services import DocumentMigrationService

class Command(BaseCommand):
    help = 'Migrar datos de documentos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--document-type',
            type=str,
            help='Tipo de documento específico a migrar'
        )
        parser.add_argument(
            '--update-metadata',
            action='store_true',
            help='Actualizar metadatos de documentos existentes'
        )
        parser.add_argument(
            '--validate-files',
            action='store_true',
            help='Validar existencia de archivos'
        )

    def handle(self, *args, **options):
        service = DocumentMigrationService()

        if options['validate_files']:
            missing_files = service.validate_file_existence()
            if missing_files:
                self.stdout.write(
                    self.style.ERROR(f'Archivos faltantes: {len(missing_files)}')
                )
                for file in missing_files:
                    self.stdout.write(f'  - {file}')
            else:
                self.stdout.write(
                    self.style.SUCCESS('Todos los archivos están presentes')
                )

        if options['update_metadata']:
            updated = service.update_document_metadata()
            self.stdout.write(
                self.style.SUCCESS(f'Metadatos actualizados: {updated}')
            )

        if options['document_type']:
            result = service.migrate_document_type(options['document_type'])
        else:
            result = service.migrate_all_documents()

        self.stdout.write(
            self.style.SUCCESS(f'Migrados {result["migrated"]} documentos')
        )
```

### Procesamiento de Documentos
```python
# management/commands/process_documents.py
class Command(BaseCommand):
    help = 'Procesar documentos pendientes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forzar reprocesamiento de documentos ya procesados'
        )
        parser.add_argument(
            '--document-id',
            type=int,
            help='ID de documento específico a procesar'
        )

    def handle(self, *args, **options):
        from documents.services import DocumentProcessingService

        service = DocumentProcessingService()

        if options['document_id']:
            result = service.process_document(options['document_id'], options['force'])
        else:
            result = service.process_pending_documents(options['force'])

        self.stdout.write(
            self.style.SUCCESS(f'Procesados {result["processed"]} documentos')
        )

        if result.get('errors'):
            self.stdout.write(
                self.style.ERROR(f'Errores: {len(result["errors"])}')
            )
            for error in result['errors']:
                self.stdout.write(f'  - {error}')
```

## Monitoreo y Métricas

### Métricas de Documentos
```python
# Comando para generar métricas
python manage.py document_metrics --period=daily

# Análisis de tipos de documentos
python manage.py analyze_document_types

# Estadísticas de procesamiento
python manage.py processing_stats --days=30
```

### Limpieza de Datos
```python
# Limpiar documentos huérfanos
python manage.py cleanup_orphaned_documents

# Eliminar archivos sin registro
python manage.py cleanup_unused_files

# Optimizar almacenamiento
python manage.py optimize_document_storage
```

## Seguridad y Validación

### Validación de Archivos
```python
# Escaneo de virus
python manage.py scan_documents --all

# Validación de integridad
python manage.py validate_document_integrity

# Verificación de checksums
python manage.py verify_checksums
```

### Protección de Datos
```python
# Encriptación de documentos sensibles
python manage.py encrypt_sensitive_documents

# Auditoría de acceso
python manage.py audit_document_access --days=30
```

## Troubleshooting

### Problemas Comunes
1. **Archivos faltantes**: Verificar rutas y permisos
2. **Tipos MIME incorrectos**: Actualizar detección automática
3. **Metadatos corruptos**: Regenerar metadatos
4. **Documentos duplicados**: Ejecutar detección de duplicados

### Comandos de Diagnóstico
```bash
# Verificar integridad del módulo
python manage.py check documents

# Validar configuración
python manage.py validate_document_settings

# Análisis de storage
python manage.py analyze_document_storage
```

## Integración con Otros Módulos

### Knowledge
- Documentos como fuente de conocimiento
- Extracción automática de texto
- Indexación para búsqueda

### Agents
- Acceso a documentos por agentes
- Procesamiento contextual
- Generación de respuestas basadas en documentos

### Tenants
- Aislamiento de documentos por tenant
- Cuotas de almacenamiento
- Configuraciones específicas

## Roadmap

### Próximas Funcionalidades
- Versionado de documentos
- Colaboración en tiempo real
- Conversión automática de formatos
- Análisis de contenido con IA

### Mejoras Planificadas
- Optimización de storage
- Búsqueda semántica
- Integración con servicios cloud
- API REST completa

## Extensibilidad

### Nuevos Tipos de Documento
```python
# Ejemplo de nuevo tipo de documento
class SpecialDocumentModel(models.Model):
    document = models.ForeignKey(DocumentModel, on_delete=models.CASCADE)
    special_metadata = models.JSONField()
    processing_config = models.JSONField()

    class Meta:
        verbose_name = "Documento Especial"
        verbose_name_plural = "Documentos Especiales"
```

### Procesadores Personalizados
- Sistema de plugins para procesamiento
- Extractores de metadatos específicos
- Validadores personalizados
