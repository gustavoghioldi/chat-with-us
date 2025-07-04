# Models - Analysis

## Descripción General
Este directorio contiene los modelos de datos para el módulo de análisis, definiendo la estructura de las tablas que almacenan los resultados de análisis de sentimientos y métricas del sistema.

## Modelos Principales

### sentiment_chat_model.py
Define el modelo `SentimentChatModel` para almacenar análisis de sentimientos de conversaciones.

#### Campos Principales:
- **chat**: Relación ForeignKey con el modelo de chat
- **message**: Relación ForeignKey con el mensaje analizado
- **sentiment_score**: Puntuación del sentimiento (-1.0 a 1.0)
- **sentiment_label**: Etiqueta del sentimiento (positivo, negativo, neutral)
- **confidence**: Nivel de confianza del análisis (0.0 a 1.0)
- **analysis_timestamp**: Timestamp del análisis
- **model_version**: Versión del modelo utilizado para el análisis
- **tenant**: Relación con el tenant (herencia de AppModel)

#### Funcionalidades:
- Validación de rangos de puntuación y confianza
- Métodos para obtener estadísticas agregadas
- Índices optimizados para consultas frecuentes
- Soft delete para auditoría

### sentiment_agents_model.py
Define el modelo `SentimentAgentsModel` para análisis de interacciones con agentes.

#### Campos Principales:
- **agent**: Relación ForeignKey con el agente
- **interaction**: Relación ForeignKey con la interacción
- **user_message_sentiment**: Sentimiento del mensaje del usuario
- **agent_response_sentiment**: Sentimiento de la respuesta del agente
- **interaction_satisfaction**: Nivel de satisfacción de la interacción
- **response_time**: Tiempo de respuesta del agente
- **conversation_flow_score**: Puntuación del flujo de conversación
- **escalation_required**: Indica si se requiere escalamiento
- **tenant**: Relación con el tenant (herencia de AppModel)

#### Métricas Calculadas:
- **sentiment_trend**: Tendencia del sentimiento a lo largo del tiempo
- **agent_performance**: Métricas de rendimiento del agente
- **user_satisfaction**: Satisfacción general del usuario
- **conversation_quality**: Calidad de la conversación

## Otros Modelos

### analysis_report_model.py
Modelo para almacenar reportes de análisis generados:

#### Campos:
- **report_type**: Tipo de reporte (daily, weekly, monthly)
- **date_range**: Rango de fechas del reporte
- **data**: Datos del reporte en formato JSON
- **generated_by**: Usuario que generó el reporte
- **status**: Estado del reporte (pending, completed, failed)
- **tenant**: Relación con el tenant

### metric_summary_model.py
Modelo para almacenar resúmenes de métricas:

#### Campos:
- **metric_type**: Tipo de métrica (sentiment, satisfaction, performance)
- **period**: Período de la métrica (hour, day, week, month)
- **value**: Valor de la métrica
- **metadata**: Metadatos adicionales en JSON
- **calculated_at**: Timestamp del cálculo
- **tenant**: Relación con el tenant

## Relaciones entre Modelos

### Diagrama de Relaciones
```
SentimentChatModel
├── chat (ForeignKey)
├── message (ForeignKey)
├── tenant (ForeignKey)
└── user (ForeignKey - through chat)

SentimentAgentsModel
├── agent (ForeignKey)
├── interaction (ForeignKey)
├── tenant (ForeignKey)
└── user (ForeignKey - through interaction)

AnalysisReportModel
├── tenant (ForeignKey)
├── generated_by (ForeignKey - User)
└── related_data (JSON references)

MetricSummaryModel
├── tenant (ForeignKey)
└── source_models (JSON references)
```

## Funcionalidades Comunes

### Validación de Datos
```python
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

class SentimentChatModel(AppModel):
    sentiment_score = models.FloatField(
        validators=[MinValueValidator(-1.0), MaxValueValidator(1.0)],
        help_text="Puntuación del sentimiento entre -1.0 y 1.0"
    )

    confidence = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Nivel de confianza entre 0.0 y 1.0"
    )

    def clean(self):
        super().clean()
        if self.sentiment_score < -1.0 or self.sentiment_score > 1.0:
            raise ValidationError("La puntuación debe estar entre -1.0 y 1.0")
```

### Métodos de Agregación
```python
class SentimentChatModel(AppModel):
    # ... campos ...

    @classmethod
    def get_average_sentiment(cls, chat_id=None, date_range=None):
        """Obtiene el sentimiento promedio"""
        queryset = cls.objects.filter(tenant=get_current_tenant())

        if chat_id:
            queryset = queryset.filter(chat_id=chat_id)

        if date_range:
            queryset = queryset.filter(
                analysis_timestamp__range=date_range
            )

        return queryset.aggregate(
            avg_sentiment=models.Avg('sentiment_score'),
            avg_confidence=models.Avg('confidence')
        )

    @classmethod
    def get_sentiment_distribution(cls, **filters):
        """Obtiene la distribución de sentimientos"""
        queryset = cls.objects.filter(tenant=get_current_tenant(), **filters)

        return queryset.values('sentiment_label').annotate(
            count=models.Count('id'),
            avg_score=models.Avg('sentiment_score')
        )
```

### Índices Optimizados
```python
class SentimentChatModel(AppModel):
    # ... campos ...

    class Meta:
        indexes = [
            models.Index(fields=['tenant', 'analysis_timestamp']),
            models.Index(fields=['chat', 'analysis_timestamp']),
            models.Index(fields=['sentiment_label', 'tenant']),
            models.Index(fields=['sentiment_score', 'confidence']),
        ]

        # Índice compuesto para consultas frecuentes
        constraints = [
            models.UniqueConstraint(
                fields=['message', 'tenant'],
                name='unique_message_analysis_per_tenant'
            )
        ]
```

## Managers Personalizados

### SentimentManager
```python
class SentimentManager(models.Manager):
    def positive(self):
        """Filtra sentimientos positivos"""
        return self.filter(sentiment_score__gt=0.1)

    def negative(self):
        """Filtra sentimientos negativos"""
        return self.filter(sentiment_score__lt=-0.1)

    def neutral(self):
        """Filtra sentimientos neutrales"""
        return self.filter(sentiment_score__gte=-0.1, sentiment_score__lte=0.1)

    def high_confidence(self):
        """Filtra análisis con alta confianza"""
        return self.filter(confidence__gte=0.8)

    def recent(self, days=7):
        """Filtra análisis recientes"""
        from django.utils import timezone
        from datetime import timedelta

        cutoff = timezone.now() - timedelta(days=days)
        return self.filter(analysis_timestamp__gte=cutoff)

class SentimentChatModel(AppModel):
    # ... campos ...

    objects = SentimentManager()

    def get_sentiment_display(self):
        """Devuelve representación legible del sentimiento"""
        if self.sentiment_score > 0.1:
            return "Positivo"
        elif self.sentiment_score < -0.1:
            return "Negativo"
        else:
            return "Neutral"
```

## Propiedades Calculadas

### Propiedades del Modelo
```python
class SentimentAgentsModel(AppModel):
    # ... campos ...

    @property
    def sentiment_improvement(self):
        """Calcula mejora del sentimiento durante la interacción"""
        if self.user_message_sentiment and self.agent_response_sentiment:
            return self.agent_response_sentiment - self.user_message_sentiment
        return None

    @property
    def is_escalation_needed(self):
        """Determina si se necesita escalamiento"""
        return (
            self.user_message_sentiment < -0.5 and
            self.interaction_satisfaction < 0.3
        )

    @property
    def performance_category(self):
        """Categoriza el rendimiento de la interacción"""
        if self.interaction_satisfaction >= 0.8:
            return "Excelente"
        elif self.interaction_satisfaction >= 0.6:
            return "Bueno"
        elif self.interaction_satisfaction >= 0.4:
            return "Regular"
        else:
            return "Deficiente"
```

## Señales de Modelos

### Señales Post-Save
```python
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=SentimentChatModel)
def update_chat_sentiment_summary(sender, instance, created, **kwargs):
    """Actualiza resumen de sentimientos del chat"""
    if created:
        # Actualizar métricas agregadas del chat
        update_chat_metrics.delay(instance.chat.id)

@receiver(post_save, sender=SentimentAgentsModel)
def update_agent_performance(sender, instance, created, **kwargs):
    """Actualiza métricas de rendimiento del agente"""
    if created:
        # Actualizar métricas del agente
        update_agent_metrics.delay(instance.agent.id)
```

## Migraciones Personalizadas

### Data Migrations
```python
# migrations/0003_populate_initial_metrics.py
from django.db import migrations
from django.utils import timezone

def populate_initial_metrics(apps, schema_editor):
    """Popula métricas iniciales"""
    SentimentChatModel = apps.get_model('analysis', 'SentimentChatModel')
    MetricSummaryModel = apps.get_model('analysis', 'MetricSummaryModel')

    # Crear métricas iniciales
    for tenant in get_all_tenants():
        MetricSummaryModel.objects.create(
            tenant=tenant,
            metric_type='sentiment',
            period='day',
            value=0.0,
            calculated_at=timezone.now()
        )

class Migration(migrations.Migration):
    dependencies = [
        ('analysis', '0002_initial_models'),
    ]

    operations = [
        migrations.RunPython(populate_initial_metrics),
    ]
```

## Consultas Optimizadas

### QuerySets Eficientes
```python
class SentimentChatModel(AppModel):
    # ... campos ...

    @classmethod
    def get_chat_sentiment_trend(cls, chat_id, days=30):
        """Obtiene tendencia de sentimiento de un chat"""
        from django.utils import timezone
        from datetime import timedelta

        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)

        return cls.objects.filter(
            chat_id=chat_id,
            analysis_timestamp__range=(start_date, end_date)
        ).extra(
            select={'day': 'DATE(analysis_timestamp)'}
        ).values('day').annotate(
            avg_sentiment=models.Avg('sentiment_score'),
            message_count=models.Count('id')
        ).order_by('day')

    @classmethod
    def get_agent_comparison(cls, agent_ids, date_range=None):
        """Compara rendimiento entre agentes"""
        queryset = cls.objects.filter(
            interaction__agent_id__in=agent_ids
        )

        if date_range:
            queryset = queryset.filter(
                analysis_timestamp__range=date_range
            )

        return queryset.values(
            'interaction__agent__name'
        ).annotate(
            avg_sentiment=models.Avg('agent_response_sentiment'),
            avg_satisfaction=models.Avg('interaction_satisfaction'),
            total_interactions=models.Count('id')
        ).order_by('-avg_satisfaction')
```

## Ejemplo de Uso

### Crear Análisis de Sentimiento
```python
from analysis.models import SentimentChatModel
from chats.models import ChatModel, MessageModel

# Crear análisis de sentimiento para un mensaje
message = MessageModel.objects.get(id=123)
sentiment_analysis = SentimentChatModel.objects.create(
    chat=message.chat,
    message=message,
    sentiment_score=0.7,
    sentiment_label='positive',
    confidence=0.85,
    model_version='v1.0',
    tenant=get_current_tenant()
)

# Obtener estadísticas de sentimiento
stats = SentimentChatModel.get_average_sentiment(
    chat_id=message.chat.id,
    date_range=(start_date, end_date)
)
```

## Mejores Prácticas

### Performance
1. **Índices**: Crear índices apropiados para consultas frecuentes
2. **Agregaciones**: Usar agregaciones de base de datos en lugar de Python
3. **Prefetch**: Usar select_related y prefetch_related
4. **Cacheo**: Cachear resultados de análisis complejos

### Mantenimiento
1. **Soft Delete**: Implementar soft delete para auditoría
2. **Archivado**: Archivar datos antiguos regularmente
3. **Validación**: Validar datos antes de insertar
4. **Monitoring**: Monitorear rendimiento de consultas
