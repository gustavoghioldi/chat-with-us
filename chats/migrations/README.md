# Chats - Migrations

## Descripción

Este directorio contiene las migraciones de base de datos para el módulo de chats, que gestiona los cambios en el esquema de la base de datos para funcionalidades de conversación, contenido de mensajes y relaciones con agentes.

## Estructura de Migraciones

```
migrations/
├── __init__.py
├── 0001_initial.py                              # Migración inicial
├── 0002_alter_chatmodel_content.py             # Modificación contenido v1
├── 0003_alter_chatmodel_content.py             # Modificación contenido v2
├── 0004_alter_chatmodel_content.py             # Modificación contenido v3
├── 0005_remove_chatmodel_content_contentchatmodel.py  # Separación de contenido
├── 0006_chatmodel_agent_instance.py            # Instancia de agente
└── 0007_remove_chatmodel_agent_instance.py     # Eliminación instancia agente
```

## Evolución del Modelo

### 0001_initial.py
- **Propósito**: Migración inicial del módulo de chats
- **Cambios**: Creación de la estructura base para gestión de conversaciones
- **Modelos**: ChatModel base
- **Campos iniciales**:
  - Identificación única del chat
  - Contenido del mensaje
  - Metadatos básicos
  - Timestamps

### 0002_alter_chatmodel_content.py
- **Propósito**: Primera iteración de mejora del campo contenido
- **Cambios**: Modificación del campo `content` en ChatModel
- **Mejoras**:
  - Ajuste de tipo de campo
  - Validación mejorada
  - Soporte para contenido extendido

### 0003_alter_chatmodel_content.py
- **Propósito**: Segunda iteración de mejora del campo contenido
- **Cambios**: Refinamiento adicional del campo `content`
- **Optimizaciones**:
  - Performance mejorada
  - Soporte para contenido rico
  - Validación adicional

### 0004_alter_chatmodel_content.py
- **Propósito**: Tercera iteración de mejora del campo contenido
- **Cambios**: Ajuste final del campo `content`
- **Estabilización**: Configuración final del manejo de contenido

### 0005_remove_chatmodel_content_contentchatmodel.py
- **Propósito**: Separación de contenido en modelo dedicado
- **Cambios**:
  - Eliminación del campo `content` de ChatModel
  - Creación del modelo `ContentChatModel`
- **Arquitectura**: Normalización de datos y mejor gestión de contenido

### 0006_chatmodel_agent_instance.py
- **Propósito**: Asociación directa con instancias de agentes
- **Cambios**: Adición del campo `agent_instance` a ChatModel
- **Funcionalidad**: Rastreo de qué agente específico manejó el chat

### 0007_remove_chatmodel_agent_instance.py
- **Propósito**: Eliminación de la instancia de agente directa
- **Cambios**: Eliminación del campo `agent_instance`
- **Razón**: Simplificación de la arquitectura o cambio de enfoque

## Arquitectura de Modelos

### ChatModel (Estado Final)
```python
class ChatModel(models.Model):
    chat_id = models.UUIDField(default=uuid.uuid4, unique=True)
    user_id = models.CharField(max_length=255)
    agent = models.ForeignKey(AgentModel, on_delete=models.CASCADE)
    session_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Chat"
        verbose_name_plural = "Chats"
        indexes = [
            models.Index(fields=['chat_id']),
            models.Index(fields=['user_id']),
            models.Index(fields=['created_at']),
        ]
```

### ContentChatModel
```python
class ContentChatModel(models.Model):
    chat = models.ForeignKey(ChatModel, on_delete=models.CASCADE, related_name='contents')
    content = models.TextField()
    content_type = models.CharField(max_length=50, choices=CONTENT_TYPES)
    sender = models.CharField(max_length=20, choices=SENDER_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Contenido de Chat"
        verbose_name_plural = "Contenidos de Chat"
        ordering = ['timestamp']
```

## Mejores Prácticas

### Gestión de Migraciones
```python
# Aplicar migraciones
python manage.py migrate chats

# Verificar estado de migraciones
python manage.py showmigrations chats

# Crear nueva migración
python manage.py makemigrations chats
```

### Migración de Contenido
```python
# Comando especializado para migración de contenido
python manage.py migrate_chat_content

# Verificar integridad después de migración
python manage.py validate_chat_integrity
```

## Gestión de Datos

### Migración de Contenido Histórico
```python
# migration_script.py
from django.db import migrations

def migrate_chat_content(apps, schema_editor):
    """Migrar contenido de chat del campo directo al modelo separado"""
    ChatModel = apps.get_model('chats', 'ChatModel')
    ContentChatModel = apps.get_model('chats', 'ContentChatModel')

    for chat in ChatModel.objects.all():
        if hasattr(chat, 'content') and chat.content:
            # Crear registro de contenido separado
            ContentChatModel.objects.create(
                chat=chat,
                content=chat.content,
                content_type='text',
                sender='user',
                timestamp=chat.created_at
            )

def reverse_migrate_chat_content(apps, schema_editor):
    """Revertir migración de contenido"""
    ChatModel = apps.get_model('chats', 'ChatModel')
    ContentChatModel = apps.get_model('chats', 'ContentChatModel')

    for chat in ChatModel.objects.all():
        first_content = chat.contents.first()
        if first_content:
            chat.content = first_content.content
            chat.save()

class Migration(migrations.Migration):
    dependencies = [
        ('chats', '0004_alter_chatmodel_content'),
    ]

    operations = [
        migrations.RunPython(
            migrate_chat_content,
            reverse_migrate_chat_content
        ),
    ]
```

### Validación de Integridad
```python
def validate_chat_integrity(apps, schema_editor):
    """Validar integridad de datos de chat"""
    ChatModel = apps.get_model('chats', 'ChatModel')
    ContentChatModel = apps.get_model('chats', 'ContentChatModel')

    # Verificar que todos los chats tienen contenido
    chats_without_content = ChatModel.objects.filter(contents__isnull=True)
    if chats_without_content.exists():
        raise ValueError(f"Encontrados {chats_without_content.count()} chats sin contenido")

    # Verificar integridad de contenido
    invalid_content = ContentChatModel.objects.filter(content__isnull=True)
    if invalid_content.exists():
        raise ValueError(f"Encontrados {invalid_content.count()} contenidos inválidos")
```

## Testing de Migraciones

### Pruebas de Migración
```python
# tests/test_migrations.py
from django.test import TestCase
from django.db import connection
from django.core.management import call_command

class ChatMigrationTestCase(TestCase):
    def test_content_separation(self):
        """Test separación de contenido en modelo dedicado"""
        from chats.models import ChatModel, ContentChatModel
        from agents.models import AgentModel

        # Crear agente de prueba
        agent = AgentModel.objects.create(name="Test Agent")

        # Crear chat
        chat = ChatModel.objects.create(
            user_id="test_user",
            agent=agent
        )

        # Crear contenido
        content = ContentChatModel.objects.create(
            chat=chat,
            content="Test message",
            content_type="text",
            sender="user"
        )

        # Verificar relación
        self.assertEqual(chat.contents.count(), 1)
        self.assertEqual(chat.contents.first().content, "Test message")

    def test_agent_instance_removal(self):
        """Test que el campo agent_instance fue eliminado"""
        from chats.models import ChatModel

        # Verificar que el campo agent_instance no existe
        self.assertFalse(hasattr(ChatModel, 'agent_instance'))

        # Verificar que el campo agent sí existe
        self.assertTrue(hasattr(ChatModel, 'agent'))
```

### Validación de Datos
```python
def test_data_integrity_after_migration(self):
    """Verificar integridad de datos después de migración"""
    from chats.models import ChatModel, ContentChatModel
    from agents.models import AgentModel

    # Crear agente y chat
    agent = AgentModel.objects.create(name="Test Agent")
    chat = ChatModel.objects.create(
        user_id="test_user",
        agent=agent,
        session_id="test_session"
    )

    # Crear múltiples contenidos
    content1 = ContentChatModel.objects.create(
        chat=chat,
        content="Hello",
        content_type="text",
        sender="user"
    )

    content2 = ContentChatModel.objects.create(
        chat=chat,
        content="Hi there!",
        content_type="text",
        sender="agent"
    )

    # Verificar integridad
    self.assertEqual(chat.contents.count(), 2)
    self.assertEqual(chat.contents.filter(sender="user").count(), 1)
    self.assertEqual(chat.contents.filter(sender="agent").count(), 1)
```

## Configuración de Chats

### Settings para Chats
```python
# settings/base.py
CHAT_SETTINGS = {
    'MAX_MESSAGE_LENGTH': 10000,
    'SUPPORTED_CONTENT_TYPES': ['text', 'image', 'file', 'audio'],
    'SESSION_TIMEOUT': 1800,  # 30 minutos
    'MESSAGE_RETENTION_DAYS': 365,
    'ENABLE_MESSAGE_ENCRYPTION': True,
    'REAL_TIME_UPDATES': True,
}
```

### Configuración de WebSocket
```python
# Para chats en tiempo real
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('127.0.0.1', 6379)],
        },
    },
}
```

## Comandos de Gestión

### Comandos de Migración
```python
# management/commands/migrate_chat_data.py
from django.core.management.base import BaseCommand
from chats.services import ChatMigrationService

class Command(BaseCommand):
    help = 'Migrar datos de chat históricos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-id',
            type=str,
            help='ID del usuario para migrar'
        )
        parser.add_argument(
            '--validate-only',
            action='store_true',
            help='Solo validar sin migrar'
        )

    def handle(self, *args, **options):
        service = ChatMigrationService()

        if options['validate_only']:
            issues = service.validate_chat_data()
            if issues:
                self.stdout.write(
                    self.style.ERROR(f'Encontrados {len(issues)} problemas')
                )
                for issue in issues:
                    self.stdout.write(f'  - {issue}')
            else:
                self.stdout.write(
                    self.style.SUCCESS('Datos de chat validados correctamente')
                )
        else:
            if options['user_id']:
                result = service.migrate_user_chats(options['user_id'])
            else:
                result = service.migrate_all_chats()

            self.stdout.write(
                self.style.SUCCESS(
                    f'Migrados {result["migrated"]} chats'
                )
            )
```

### Limpieza de Datos
```python
# management/commands/cleanup_old_chats.py
class Command(BaseCommand):
    help = 'Limpiar chats antiguos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=365,
            help='Días de antigüedad para limpieza'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simular limpieza sin ejecutar'
        )

    def handle(self, *args, **options):
        from chats.services import ChatCleanupService

        service = ChatCleanupService()

        if options['dry_run']:
            count = service.count_old_chats(options['days'])
            self.stdout.write(
                self.style.WARNING(f'Se eliminarían {count} chats')
            )
        else:
            deleted = service.cleanup_old_chats(options['days'])
            self.stdout.write(
                self.style.SUCCESS(f'Eliminados {deleted} chats antiguos')
            )
```

## Monitoreo y Métricas

### Métricas de Conversación
```python
# Comando para generar métricas
python manage.py chat_metrics --period=daily

# Análisis de patrones de conversación
python manage.py analyze_conversation_patterns --days=30
```

### Monitoreo de Performance
```python
# Análisis de performance de chats
python manage.py analyze_chat_performance

# Optimización de consultas
python manage.py optimize_chat_queries
```

## Seguridad y Privacidad

### Protección de Datos
```python
# Encriptación de mensajes sensibles
python manage.py encrypt_sensitive_messages

# Anonimización de datos
python manage.py anonymize_chat_data --user-id=123
```

### Auditoría
```python
# Logs de acceso a chats
LOGGING = {
    'loggers': {
        'chats.access': {
            'level': 'INFO',
            'handlers': ['file'],
            'propagate': False,
        },
        'chats.security': {
            'level': 'WARNING',
            'handlers': ['security_file'],
            'propagate': False,
        },
    },
}
```

## Troubleshooting

### Problemas Comunes
1. **Contenido perdido**: Verificar migración de contenido
2. **Relaciones rotas**: Validar foreign keys
3. **Performance**: Optimizar consultas de contenido
4. **Duplicados**: Verificar integridad de datos

### Comandos de Diagnóstico
```bash
# Verificar integridad de chats
python manage.py check chats

# Validar contenido de chats
python manage.py validate_chat_content

# Análisis de duplicados
python manage.py find_duplicate_chats
```

## Integración con Otros Módulos

### Agentes
- Asociación directa con agentes
- Historial de conversaciones por agente
- Análisis de efectividad

### Análisis
- Análisis de sentimientos de conversaciones
- Métricas de satisfacción
- Patrones de conversación

### Tenants
- Aislamiento de chats por tenant
- Configuraciones específicas
- Reporting por cliente

## Roadmap

### Próximas Funcionalidades
- Soporte para multimedia
- Conversaciones grupales
- Traducción automática
- Análisis de intenciones

### Mejoras Planificadas
- Optimización de storage
- Búsqueda avanzada
- Archivado automático
- Métricas en tiempo real

## Extensibilidad

### Nuevos Tipos de Contenido
```python
# Ejemplo de nuevo tipo de contenido
class MediaContentModel(models.Model):
    chat = models.ForeignKey(ChatModel, on_delete=models.CASCADE)
    media_type = models.CharField(max_length=50)
    media_url = models.URLField()
    thumbnail_url = models.URLField(blank=True)

    class Meta:
        verbose_name = "Contenido Multimedia"
        verbose_name_plural = "Contenidos Multimedia"
```

### Plugins de Procesamiento
- Sistema de plugins para procesamiento de mensajes
- Filtros de contenido
- Validaciones personalizadas
