# Serializers - Analysis

## Descripción General
Este directorio contiene los serializadores para el módulo de análisis, que convierten los modelos de datos a representaciones JSON y viceversa, facilitando la comunicación entre el frontend y la API REST.

## Estructura de Serializadores

### chat_analysis_serializer.py
Contiene serializadores para análisis de chat y sentimientos.

#### ChatAnalysisRequestSerializer
Valida las solicitudes de análisis de chat:
```python
class ChatAnalysisRequestSerializer(serializers.Serializer):
    chat_id = serializers.IntegerField()
    message_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
    analysis_type = serializers.ChoiceField(
        choices=['sentiment', 'content', 'full'],
        default='sentiment'
    )
    force_reanalysis = serializers.BooleanField(default=False)
```

#### ChatAnalysisResponseSerializer
Estructura las respuestas de análisis:
```python
class ChatAnalysisResponseSerializer(serializers.Serializer):
    chat_id = serializers.IntegerField()
    analysis_results = serializers.ListField()
    summary = serializers.DictField()
    timestamp = serializers.DateTimeField()
```

### SentimentAnalysisSerializer
Para análisis específicos de sentimientos:
```python
class SentimentAnalysisSerializer(serializers.ModelSerializer):
    sentiment_display = serializers.CharField(source='get_sentiment_display', read_only=True)
    confidence_level = serializers.SerializerMethodField()

    class Meta:
        model = SentimentChatModel
        fields = [
            'id', 'sentiment_score', 'sentiment_label',
            'sentiment_display', 'confidence', 'confidence_level',
            'analysis_timestamp', 'model_version'
        ]

    def get_confidence_level(self, obj):
        if obj.confidence >= 0.8:
            return 'Alto'
        elif obj.confidence >= 0.6:
            return 'Medio'
        else:
            return 'Bajo'
```

## Uso de Serializadores

### Análisis de Chat
```python
from analysis.serializers.chat_analysis_serializer import (
    ChatAnalysisRequestSerializer,
    ChatAnalysisResponseSerializer
)

# Validar solicitud
request_serializer = ChatAnalysisRequestSerializer(data=request.data)
if request_serializer.is_valid():
    # Procesar análisis
    results = process_chat_analysis(request_serializer.validated_data)

    # Serializar respuesta
    response_serializer = ChatAnalysisResponseSerializer(results)
    return Response(response_serializer.data)
```

### Análisis de Sentimientos
```python
from analysis.serializers import SentimentAnalysisSerializer

# Serializar múltiples análisis
sentiments = SentimentChatModel.objects.filter(chat_id=chat_id)
serializer = SentimentAnalysisSerializer(sentiments, many=True)
return Response(serializer.data)
```

## Validación Personalizada

### Validación de Chat IDs
```python
def validate_chat_id(self, value):
    """Valida que el chat exista y pertenezca al tenant"""
    try:
        chat = ChatModel.objects.get(
            id=value,
            tenant=self.context['request'].user.tenant
        )
        return value
    except ChatModel.DoesNotExist:
        raise serializers.ValidationError("Chat no encontrado")
```

### Validación de Permisos
```python
def validate_message_ids(self, value):
    """Valida que los mensajes pertenezcan al tenant"""
    tenant = self.context['request'].user.tenant
    valid_ids = MessageModel.objects.filter(
        id__in=value,
        chat__tenant=tenant
    ).values_list('id', flat=True)

    if len(valid_ids) != len(value):
        raise serializers.ValidationError(
            "Algunos mensajes no son válidos o no tienes permisos"
        )
    return value
```

## Formateo de Respuestas

### Análisis Completo
```python
class ComprehensiveAnalysisSerializer(serializers.Serializer):
    chat_summary = serializers.DictField()
    sentiment_trend = serializers.ListField()
    key_insights = serializers.ListField()
    recommendations = serializers.ListField()

    def to_representation(self, instance):
        """Formato personalizado de respuesta"""
        data = super().to_representation(instance)

        # Agregar metadatos
        data['metadata'] = {
            'analysis_date': timezone.now().isoformat(),
            'model_version': settings.SENTIMENT_MODEL_VERSION,
            'confidence_threshold': 0.7
        }

        return data
```

## Migración y Compatibilidad

### Historial de Migración
Este archivo fue movido desde `api/serializers/chat_analysis_serializer.py` para mantener la funcionalidad relacionada con análisis dentro de la app `analysis`.

### Compatibilidad hacia atrás
```python
# Para mantener compatibilidad con imports antiguos
from analysis.serializers.chat_analysis_serializer import *

# Alias para compatibilidad
ChatAnalysisSerializer = ChatAnalysisRequestSerializer
```

## Mejores Prácticas

### Performance
1. **Campos Selectivos**: Solo serializar campos necesarios
2. **Lazy Loading**: Evitar N+1 queries con select_related
3. **Paginación**: Implementar paginación para grandes datasets

### Validación
1. **Validación Temprana**: Validar datos antes del procesamiento
2. **Mensajes Claros**: Proporcionar mensajes de error descriptivos
3. **Contexto de Request**: Usar contexto para validaciones de permisos

### Seguridad
1. **Filtrado por Tenant**: Asegurar aislamiento de datos
2. **Validación de Permisos**: Verificar permisos en cada operación
3. **Sanitización**: Limpiar datos de entrada
