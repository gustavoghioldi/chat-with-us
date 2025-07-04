# Analysis Views

Esta carpeta contiene las vistas relacionadas con el análisis de sentimientos y contenido.

## ChatAnalysisView

Vista para analizar el sentimiento de chats usando agentes de análisis específicos del tenant.

### Endpoint
- `POST /api/v1/analysis/chat/` - Analiza el sentimiento de un chat

### Uso
```python
from analysis.views.chat_analysis_view import ChatAnalysisView
```

### Migración
Este archivo fue movido desde `api/views/chat_analysis_view.py` para mantener la funcionalidad relacionada con análisis dentro de la app `analysis`.
