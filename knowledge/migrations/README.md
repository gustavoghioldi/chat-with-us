# Knowledge - Migrations

## Descripción

Este directorio contiene las migraciones de base de datos para el módulo de conocimiento, que gestiona los cambios en el esquema de la base de datos para funcionalidades de gestión de conocimiento, documentos y bases de datos vectoriales.

## Estructura de Migraciones

```
migrations/
├── __init__.py
├── 0001_initial.py                              # Migración inicial
├── 0002_knowledgepdfmodel_and_more.py          # Modelo PDF y extensiones
├── 0003_knowledgemodel_delete_knowledgepdfmodel_and_more.py  # Consolidación de modelos
├── 0004_alter_knowledgemodel_category_and_more.py  # Modificación de categorías
├── 0005_knowledgemodel_tenant.py               # Implementación multi-tenant
├── 0006_knowledgemodel_recreate.py             # Campo de recreación
├── 0007_alter_knowledgemodel_category.py       # Ajuste de categorías
├── 0008_knowledgemodel_path.py                 # Campo de ruta
└── 0009_remove_knowledgemodel_path_knowledgemodel_document.py  # Referencia a documentos
```

## Evolución del Modelo

### 0001_initial.py
- **Propósito**: Migración inicial del módulo de conocimiento
- **Cambios**: Creación de la estructura base para gestión de conocimiento
- **Modelos**: KnowledgeModel base
- **Campos iniciales**:
  - Metadatos de conocimiento
  - Contenido y categorización
  - Timestamps básicos

### 0002_knowledgepdfmodel_and_more.py
- **Propósito**: Soporte específico para documentos PDF
- **Cambios**: Creación del modelo `KnowledgePDFModel`
- **Funcionalidades**:
  - Procesamiento específico de PDFs
  - Extracción de texto
  - Metadatos específicos de documentos PDF
- **Extensiones**: Campos adicionales para gestión de documentos

### 0003_knowledgemodel_delete_knowledgepdfmodel_and_more.py
- **Propósito**: Consolidación y simplificación del modelo
- **Cambios**:
  - Eliminación del modelo `KnowledgePDFModel`
  - Integración de funcionalidades en `KnowledgeModel`
- **Razón**: Simplificación de la arquitectura
- **Impacto**: Modelo unificado para todos los tipos de conocimiento

### 0004_alter_knowledgemodel_category_and_more.py
- **Propósito**: Refinamiento del sistema de categorías
- **Cambios**: Modificación de campos de categoría
- **Mejoras**:
  - Validación mejorada de categorías
  - Opciones de categorización extendidas
  - Mejor organización del conocimiento

### 0005_knowledgemodel_tenant.py
- **Propósito**: Implementación de multi-tenancy
- **Cambios**: Adición del campo `tenant`
- **Funcionalidades**:
  - Aislamiento de conocimiento por tenant
  - Seguridad mejorada
  - Gestión multi-cliente

### 0006_knowledgemodel_recreate.py
- **Propósito**: Control de recreación de conocimiento
- **Cambios**: Campo `recreate` para gestión de actualizaciones
- **Uso**: Indicar cuando el conocimiento debe ser reprocesado

### 0007_alter_knowledgemodel_category.py
- **Propósito**: Ajuste final del sistema de categorías
- **Cambios**: Refinamiento de opciones de categoría
- **Estabilización**: Configuración final de categorías

### 0008_knowledgemodel_path.py
- **Propósito**: Gestión de rutas de archivos
- **Cambios**: Campo `path` para ubicación de archivos
- **Funcionalidades**: Referencia directa a archivos del sistema

### 0009_remove_knowledgemodel_path_knowledgemodel_document.py
- **Propósito**: Migración a sistema de documentos
- **Cambios**:
  - Eliminación del campo `path`
  - Adición del campo `document`
- **Mejora**: Integración con el módulo de documentos

## Arquitectura de Modelos

### KnowledgeModel (Estado Final)
```python
class KnowledgeModel(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    tenant = models.ForeignKey(TenantModel, on_delete=models.CASCADE)
    document = models.ForeignKey(DocumentModel, on_delete=models.CASCADE, null=True, blank=True)
    recreate = models.BooleanField(default=False)
    vector_embedding = models.TextField(null=True, blank=True)  # JSON serializado

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Conocimiento"
        verbose_name_plural = "Conocimientos"
        indexes = [
            models.Index(fields=['tenant', 'category']),
            models.Index(fields=['created_at']),
        ]
```

## Mejores Prácticas

### Gestión de Migraciones
```python
# Aplicar migraciones
python manage.py migrate knowledge

# Verificar estado de migraciones
python manage.py showmigrations knowledge

# Crear nueva migración
python manage.py makemigrations knowledge
```

### Migración de Datos de Conocimiento
```python
# Comando personalizado para migrar conocimiento
python manage.py migrate_knowledge_data

# Recrear embeddings después de migración
python manage.py recreate_embeddings --all
```

## Gestión de Datos

### Migración de Datos Históricos
```python
# migration_script.py
from django.db import migrations
from django.db.models import Q

def migrate_knowledge_data(apps, schema_editor):
    """Migrar datos de conocimiento existentes"""
    KnowledgeModel = apps.get_model('knowledge', 'KnowledgeModel')
    DocumentModel = apps.get_model('documents', 'DocumentModel')

    for knowledge in KnowledgeModel.objects.filter(recreate=True):
        # Reprocesar conocimiento marcado para recreación
        knowledge.recreate = False
        knowledge.save()

def migrate_to_document_system(apps, schema_editor):
    """Migrar del sistema de paths al sistema de documentos"""
    KnowledgeModel = apps.get_model('knowledge', 'KnowledgeModel')
    DocumentModel = apps.get_model('documents', 'DocumentModel')

    for knowledge in KnowledgeModel.objects.exclude(path__isnull=True):
        # Crear documento correspondiente
        document = DocumentModel.objects.create(
            name=knowledge.title,
            file_path=knowledge.path,
            uploaded_by=knowledge.tenant.owner
        )

        # Actualizar referencia
        knowledge.document = document
        knowledge.save()

class Migration(migrations.Migration):
    dependencies = [
        ('knowledge', '0008_knowledgemodel_path'),
        ('documents', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(migrate_to_document_system),
    ]
```

### Validación de Embeddings
```python
def validate_embeddings(apps, schema_editor):
    """Validar integridad de embeddings vectoriales"""
    KnowledgeModel = apps.get_model('knowledge', 'KnowledgeModel')

    import json

    for knowledge in KnowledgeModel.objects.exclude(vector_embedding__isnull=True):
        try:
            embedding = json.loads(knowledge.vector_embedding)
            if not isinstance(embedding, list) or len(embedding) == 0:
                raise ValueError(f"Embedding inválido para conocimiento {knowledge.id}")
        except json.JSONDecodeError:
            raise ValueError(f"Embedding JSON inválido para conocimiento {knowledge.id}")
```

## Testing de Migraciones

### Pruebas de Migración
```python
# tests/test_migrations.py
from django.test import TestCase
from django.db import connection
from django.core.management import call_command

class KnowledgeMigrationTestCase(TestCase):
    def test_knowledge_model_evolution(self):
        """Test evolución del modelo de conocimiento"""
        from knowledge.models import KnowledgeModel

        # Verificar campos finales
        required_fields = ['title', 'content', 'category', 'tenant', 'document']

        for field in required_fields:
            self.assertTrue(hasattr(KnowledgeModel, field))

    def test_tenant_integration(self):
        """Test integración con sistema de tenants"""
        from knowledge.models import KnowledgeModel
        from tenants.models import TenantModel

        # Crear tenant de prueba
        tenant = TenantModel.objects.create(name="Test Tenant")

        # Crear conocimiento
        knowledge = KnowledgeModel.objects.create(
            title="Test Knowledge",
            content="Test content",
            category="general",
            tenant=tenant
        )

        self.assertEqual(knowledge.tenant, tenant)

    def test_document_integration(self):
        """Test integración con sistema de documentos"""
        from knowledge.models import KnowledgeModel
        from documents.models import DocumentModel
        from tenants.models import TenantModel

        # Crear dependencias
        tenant = TenantModel.objects.create(name="Test Tenant")
        document = DocumentModel.objects.create(
            name="Test Document",
            file_path="/test/path"
        )

        # Crear conocimiento con documento
        knowledge = KnowledgeModel.objects.create(
            title="Test Knowledge",
            content="Test content",
            category="document",
            tenant=tenant,
            document=document
        )

        self.assertEqual(knowledge.document, document)
```

### Validación de Datos
```python
def test_data_integrity_after_migration(self):
    """Verificar integridad de datos después de migración"""
    from knowledge.models import KnowledgeModel
    from tenants.models import TenantModel

    # Crear tenant
    tenant = TenantModel.objects.create(name="Test Tenant")

    # Crear conocimiento con embedding
    knowledge = KnowledgeModel.objects.create(
        title="Test Knowledge",
        content="Test content for embedding",
        category="general",
        tenant=tenant,
        vector_embedding='[0.1, 0.2, 0.3, 0.4, 0.5]'
    )

    # Verificar que se guardó correctamente
    self.assertEqual(knowledge.title, "Test Knowledge")
    self.assertIsNotNone(knowledge.vector_embedding)

    # Verificar que el embedding es válido JSON
    import json
    embedding = json.loads(knowledge.vector_embedding)
    self.assertIsInstance(embedding, list)
    self.assertEqual(len(embedding), 5)
```

## Configuración de Conocimiento

### Settings para Conocimiento
```python
# settings/base.py
KNOWLEDGE_SETTINGS = {
    'EMBEDDING_MODEL': 'sentence-transformers/all-MiniLM-L6-v2',
    'VECTOR_DIMENSION': 384,
    'SIMILARITY_THRESHOLD': 0.7,
    'CHUNK_SIZE': 1000,
    'CHUNK_OVERLAP': 200,
    'SUPPORTED_FORMATS': ['pdf', 'txt', 'docx', 'md'],
    'MAX_FILE_SIZE': 10 * 1024 * 1024,  # 10MB
}
```

### Configuración de Procesamiento
```python
# Para procesamiento de documentos
DOCUMENT_PROCESSING = {
    'ASYNC_PROCESSING': True,
    'QUEUE_NAME': 'knowledge_processing',
    'BATCH_SIZE': 50,
    'RETRY_ATTEMPTS': 3,
}
```

## Comandos de Gestión

### Comandos de Migración
```python
# management/commands/migrate_knowledge_data.py
from django.core.management.base import BaseCommand
from knowledge.services import KnowledgeMigrationService

class Command(BaseCommand):
    help = 'Migrar datos de conocimiento históricos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--tenant-id',
            type=int,
            help='ID del tenant para migrar'
        )
        parser.add_argument(
            '--recreate-embeddings',
            action='store_true',
            help='Recrear embeddings vectoriales'
        )

    def handle(self, *args, **options):
        service = KnowledgeMigrationService()

        if options['tenant_id']:
            result = service.migrate_tenant_data(options['tenant_id'])
        else:
            result = service.migrate_all_data()

        if options['recreate_embeddings']:
            embedding_result = service.recreate_embeddings()
            result.update(embedding_result)

        self.stdout.write(
            self.style.SUCCESS(
                f'Migración completada: {result["migrated"]} registros procesados'
            )
        )
```

### Validación de Conocimiento
```python
# management/commands/validate_knowledge_data.py
class Command(BaseCommand):
    help = 'Validar integridad de datos de conocimiento'

    def handle(self, *args, **options):
        from knowledge.validators import KnowledgeDataValidator

        validator = KnowledgeDataValidator()
        issues = validator.validate_all()

        if issues:
            self.stdout.write(
                self.style.ERROR(f'Encontrados {len(issues)} problemas')
            )
            for issue in issues:
                self.stdout.write(f'  - {issue}')
        else:
            self.stdout.write(
                self.style.SUCCESS('Datos de conocimiento validados correctamente')
            )
```

## Gestión de Embeddings

### Recreación de Embeddings
```python
# management/commands/recreate_embeddings.py
class Command(BaseCommand):
    help = 'Recrear embeddings vectoriales'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Recrear todos los embeddings'
        )
        parser.add_argument(
            '--tenant-id',
            type=int,
            help='Recrear embeddings para un tenant específico'
        )

    def handle(self, *args, **options):
        from knowledge.services import EmbeddingService

        service = EmbeddingService()

        if options['all']:
            count = service.recreate_all_embeddings()
        elif options['tenant_id']:
            count = service.recreate_tenant_embeddings(options['tenant_id'])
        else:
            count = service.recreate_marked_embeddings()

        self.stdout.write(
            self.style.SUCCESS(f'Recreados {count} embeddings')
        )
```

## Monitoreo y Mantenimiento

### Métricas de Conocimiento
```python
# Comando para generar métricas
python manage.py knowledge_metrics --tenant-id=1

# Limpiar conocimiento obsoleto
python manage.py cleanup_old_knowledge --days=365
```

### Optimización de Base de Datos
```python
# Comando para optimizar índices
python manage.py optimize_knowledge_indexes

# Análisis de uso de conocimiento
python manage.py analyze_knowledge_usage --period=monthly
```

## Seguridad y Privacidad

### Protección de Datos
```python
# Anonimización de conocimiento sensible
python manage.py anonymize_knowledge --tenant-id=1

# Eliminación segura de datos
python manage.py secure_delete_knowledge --knowledge-id=123
```

### Auditoría
```python
# Logs de acceso a conocimiento
LOGGING = {
    'loggers': {
        'knowledge.access': {
            'level': 'INFO',
            'handlers': ['file'],
            'propagate': False,
        },
    },
}
```

## Troubleshooting

### Problemas Comunes
1. **Embeddings corruptos**: Verificar formato JSON
2. **Relaciones rotas**: Validar foreign keys
3. **Documentos faltantes**: Verificar integridad referencial
4. **Performance**: Optimizar consultas vectoriales

### Comandos de Diagnóstico
```bash
# Verificar integridad de conocimiento
python manage.py check knowledge

# Verificar embeddings
python manage.py validate_embeddings

# Análisis de performance
python manage.py analyze_knowledge_performance
```

## Roadmap

### Próximas Funcionalidades
- Búsqueda semántica avanzada
- Clustering automático de conocimiento
- Versionado de conocimiento
- Análisis de relevancia

### Mejoras Planificadas
- Optimización de embeddings
- Búsqueda en tiempo real
- Integración con LLMs
- Dashboard de conocimiento
