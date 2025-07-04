# Analysis Serializers

Esta carpeta contiene los serializadores relacionados con el análisis de sentimientos y contenido.

## ChatAnalysisSerializer

Serializadores para las solicitudes y respuestas de análisis de chat.

### Clases
- `ChatAnalysisRequestSerializer` - Valida las solicitudes de análisis
- `ChatAnalysisResponseSerializer` - Estructura las respuestas de análisis

### Uso
```python
from analysis.serializers.chat_analysis_serializer import (
    ChatAnalysisRequestSerializer,
    ChatAnalysisResponseSerializer
)
```

### Migración
Este archivo fue movido desde `api/serializers/chat_analysis_serializer.py` para mantener la funcionalidad relacionada con análisis dentro de la app `analysis`.
