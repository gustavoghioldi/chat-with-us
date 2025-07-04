# Analysis - Migrations

## Descripción

Este directorio contiene las migraciones de base de datos para el módulo de análisis, que gestiona los cambios en el esquema de la base de datos para funcionalidades de análisis de sentimientos y métricas de conversación.

## Estructura de Migraciones

```
migrations/
├── __init__.py
├── 0001_initial.py                              # Migración inicial
├── 0002_rename_sentimentmodel_sentimentchatmodel.py  # Renombrado de modelo
└── 0003_sentimentagentmodel.py                  # Modelo de sentimientos por agente
```

## Evolución del Modelo

### 0001_initial.py
- **Propósito**: Migración inicial del módulo de análisis
- **Cambios**: Creación de la estructura base para análisis de sentimientos
- **Modelos**: SentimentModel base
- **Campos iniciales**:
  - Campos de análisis básico
  - Relaciones con chats/conversaciones
  - Metadatos de análisis

### 0002_rename_sentimentmodel_sentimentchatmodel.py
- **Propósito**: Refactorización del modelo de sentimientos
- **Cambios**: Renombrado de `SentimentModel` a `SentimentChatModel`
- **Razón**: Mejor semántica y claridad en el propósito del modelo
- **Impacto**:
  - Mejor organización del código
  - Claridad en la función del modelo
  - Preparación para modelos adicionales

### 0003_sentimentagentmodel.py
- **Propósito**: Análisis de sentimientos a nivel de agente
- **Cambios**: Creación del modelo `SentimentAgentModel`
- **Funcionalidades**:
  - Análisis agregado por agente
  - Métricas de performance de agentes
  - Análisis temporal de sentimientos

## Arquitectura de Modelos

### SentimentChatModel
```python
# Modelo para análisis de sentimientos por chat
class SentimentChatModel(models.Model):
    chat = models.ForeignKey(ChatModel, on_delete=models.CASCADE)
    sentiment_score = models.FloatField()
    sentiment_label = models.CharField(max_length=20)
    confidence = models.FloatField()
    analyzed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Análisis de Sentimiento por Chat"
        verbose_name_plural = "Análisis de Sentimientos por Chat"
```

### SentimentAgentModel
```python
# Modelo para análisis de sentimientos por agente
class SentimentAgentModel(models.Model):
    agent = models.ForeignKey(AgentModel, on_delete=models.CASCADE)
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    avg_sentiment_score = models.FloatField()
    total_interactions = models.IntegerField()
    positive_interactions = models.IntegerField()
    negative_interactions = models.IntegerField()
    neutral_interactions = models.IntegerField()

    class Meta:
        verbose_name = "Análisis de Sentimiento por Agente"
        verbose_name_plural = "Análisis de Sentimientos por Agente"
```

## Mejores Prácticas

### Gestión de Migraciones
```python
# Aplicar migraciones
python manage.py migrate analysis

# Verificar estado de migraciones
python manage.py showmigrations analysis

# Crear nueva migración
python manage.py makemigrations analysis
```

### Migración de Datos Históricos
```python
# Comando personalizado para migrar datos históricos
python manage.py migrate_sentiment_data

# Recalcular métricas después de migración
python manage.py recalculate_sentiment_metrics
```

## Gestión de Datos

### Migración de Datos Sensibles
```python
# migration_script.py
from django.db import migrations
from django.db.models import Q

def migrate_sentiment_data(apps, schema_editor):
    """Migrar datos de sentimientos existentes"""
    OldModel = apps.get_model('analysis', 'SentimentModel')
    NewModel = apps.get_model('analysis', 'SentimentChatModel')

    for old_record in OldModel.objects.all():
        NewModel.objects.create(
            chat_id=old_record.chat_id,
            sentiment_score=old_record.sentiment_score,
            sentiment_label=old_record.sentiment_label,
            confidence=old_record.confidence
        )

class Migration(migrations.Migration):
    dependencies = [
        ('analysis', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(migrate_sentiment_data),
    ]
```

### Validación de Integridad
```python
def validate_sentiment_data(apps, schema_editor):
    """Validar integridad de datos después de migración"""
    SentimentChatModel = apps.get_model('analysis', 'SentimentChatModel')

    # Verificar que todos los sentimientos tienen valores válidos
    invalid_sentiments = SentimentChatModel.objects.filter(
        Q(sentiment_score__lt=-1) | Q(sentiment_score__gt=1)
    )

    if invalid_sentiments.exists():
        raise ValueError("Sentimientos con valores inválidos encontrados")
```

## Testing de Migraciones

### Pruebas de Migración
```python
# tests/test_migrations.py
from django.test import TestCase
from django.db import connection
from django.core.management import call_command

class AnalysisMigrationTestCase(TestCase):
    def test_sentiment_model_rename(self):
        """Test renombrado de modelo de sentimientos"""
        # Verificar que el modelo nuevo existe
        from analysis.models import SentimentChatModel
        self.assertTrue(hasattr(SentimentChatModel, 'sentiment_score'))

    def test_sentiment_agent_model_creation(self):
        """Test creación de modelo de sentimientos por agente"""
        from analysis.models import SentimentAgentModel

        # Verificar campos requeridos
        required_fields = [
            'agent', 'period_start', 'period_end',
            'avg_sentiment_score', 'total_interactions'
        ]

        for field in required_fields:
            self.assertTrue(hasattr(SentimentAgentModel, field))
```

### Validación de Datos
```python
def test_data_integrity_after_migration(self):
    """Verificar integridad de datos después de migración"""
    from analysis.models import SentimentChatModel, SentimentAgentModel
    from chats.models import ChatModel
    from agents.models import AgentModel

    # Crear datos de prueba
    chat = ChatModel.objects.create(content="Test chat")
    agent = AgentModel.objects.create(name="Test Agent")

    # Crear análisis de sentimiento
    sentiment_chat = SentimentChatModel.objects.create(
        chat=chat,
        sentiment_score=0.8,
        sentiment_label="positive",
        confidence=0.95
    )

    sentiment_agent = SentimentAgentModel.objects.create(
        agent=agent,
        period_start=timezone.now() - timedelta(days=1),
        period_end=timezone.now(),
        avg_sentiment_score=0.8,
        total_interactions=10,
        positive_interactions=8,
        negative_interactions=1,
        neutral_interactions=1
    )

    # Verificar que se guardaron correctamente
    self.assertEqual(sentiment_chat.sentiment_score, 0.8)
    self.assertEqual(sentiment_agent.total_interactions, 10)
```

## Configuración de Análisis

### Settings para Análisis
```python
# settings/base.py
ANALYSIS_SETTINGS = {
    'SENTIMENT_MODELS': {
        'default': 'transformers',
        'backup': 'textblob'
    },
    'BATCH_SIZE': 100,
    'CACHE_TIMEOUT': 3600,
    'ASYNC_PROCESSING': True
}
```

### Configuración de Celery
```python
# Para procesamiento asíncrono de análisis
CELERY_ROUTES = {
    'analysis.tasks.analyze_sentiment': {'queue': 'analysis'},
    'analysis.tasks.generate_agent_metrics': {'queue': 'metrics'},
}
```

## Monitoreo y Mantenimiento

### Métricas de Performance
```python
# Comando para generar métricas
python manage.py generate_sentiment_metrics --period=daily

# Limpiar datos antiguos
python manage.py cleanup_old_sentiment_data --days=90
```

### Logs de Análisis
```python
# Configuración de logging
LOGGING = {
    'loggers': {
        'analysis.migrations': {
            'level': 'INFO',
            'handlers': ['file', 'console'],
            'propagate': False,
        },
        'analysis.services': {
            'level': 'DEBUG',
            'handlers': ['file'],
            'propagate': False,
        },
    },
}
```

## Comandos de Gestión

### Comandos Personalizados
```python
# management/commands/migrate_sentiment_data.py
from django.core.management.base import BaseCommand
from analysis.services import SentimentMigrationService

class Command(BaseCommand):
    help = 'Migrar datos de sentimientos históricos'

    def handle(self, *args, **options):
        service = SentimentMigrationService()
        result = service.migrate_historical_data()

        self.stdout.write(
            self.style.SUCCESS(
                f'Migrados {result["migrated"]} registros de sentimientos'
            )
        )
```

### Validación de Datos
```python
# management/commands/validate_sentiment_data.py
class Command(BaseCommand):
    help = 'Validar integridad de datos de análisis'

    def handle(self, *args, **options):
        from analysis.validators import SentimentDataValidator

        validator = SentimentDataValidator()
        issues = validator.validate_all()

        if issues:
            self.stdout.write(
                self.style.ERROR(f'Encontrados {len(issues)} problemas')
            )
            for issue in issues:
                self.stdout.write(f'  - {issue}')
        else:
            self.stdout.write(
                self.style.SUCCESS('Datos de análisis validados correctamente')
            )
```

## Troubleshooting

### Problemas Comunes
1. **Datos duplicados**: Verificar constraints únicos
2. **Valores de sentimiento inválidos**: Validar rangos (-1 a 1)
3. **Relaciones rotas**: Verificar foreign keys
4. **Performance**: Optimizar queries de análisis

### Comandos de Diagnóstico
```bash
# Verificar estado de modelos
python manage.py check analysis

# Verificar migraciones pendientes
python manage.py showmigrations analysis

# Generar SQL para revisión
python manage.py sqlmigrate analysis 0003
```

## Seguridad y Privacidad

### Protección de Datos
- **Anonimización**: Datos sensibles anonimizados
- **Retención**: Políticas de retención de datos
- **Acceso**: Control de acceso a datos de análisis

### Cumplimiento
- **GDPR**: Derecho al olvido implementado
- **Auditoría**: Logs de acceso a datos de análisis
- **Encriptación**: Datos sensibles encriptados

## Roadmap

### Próximas Funcionalidades
- Análisis de emociones granular
- Métricas de satisfacción del cliente
- Análisis predictivo de sentimientos
- Integración con herramientas de BI

### Mejoras Planificadas
- Optimización de performance
- Análisis en tiempo real
- Dashboard de métricas
- Alertas automáticas
