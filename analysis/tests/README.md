# Test Unitarios - ChatAnalysisView

Este archivo contiene tests unitarios completos para la vista `ChatAnalysisView` que fue migrada desde la app `api` hacia la app `analysis`.

## Descripción

La `ChatAnalysisView` es responsable de analizar el sentimiento de chats utilizando agentes de análisis específicos del tenant.

## Tests Incluidos

### 1. **test_chat_analysis_success**
- ✅ Verifica el flujo exitoso de análisis de sentimientos
- Mockea el servicio `SentimentChatService` y permisos
- Valida estructura de respuesta completa

### 2. **test_chat_analysis_invalid_data**
- ✅ Valida manejo de datos de entrada inválidos (chat vacío)
- Verifica respuesta 400 con mensaje de error apropiado

### 3. **test_chat_analysis_missing_analyzer_name**
- ✅ Verifica manejo cuando falta el campo `analyzer_name`
- Confirma validación de campos requeridos

### 4. **test_chat_analysis_nonexistent_analyzer**
- ✅ Prueba comportamiento con analizador inexistente
- Valida error de validación correspondiente

### 5. **test_chat_analysis_service_error**
- ✅ Simula error en el servicio de análisis
- Verifica respuesta 500 con manejo apropiado de excepciones

### 6. **test_chat_analysis_different_sentiments**
- ✅ Prueba respuestas para diferentes tipos de sentimientos (POSITIVE, NEGATIVE, NEUTRAL)
- Usa `subTest` para validar cada sentimiento individualmente

### 7. **test_chat_analysis_empty_chat_text**
- ✅ Valida manejo de texto con solo espacios en blanco
- Confirma validación de campos no vacíos

### 8. **test_chat_analysis_long_text**
- ✅ Prueba validación de máximo de caracteres (5000)
- Verifica límites de longitud del campo

### 9. **test_chat_analysis_response_serialization_error**
- ✅ Simula error en serialización de respuesta
- Prueba con sentimiento inválido que causa fallo en validación

### 10. **test_chat_analysis_method_not_allowed**
- ✅ Verifica que solo el método POST está permitido
- Confirma respuesta 405 para otros métodos HTTP

### 11. **test_chat_analysis_validates_json_format**
- ✅ Valida manejo de JSON malformado
- Verifica respuesta 400 para errores de parseo

### 12. **test_chat_analysis_timestamp_format**
- ✅ Verifica formato correcto del timestamp en respuesta
- Valida que es un string numérico dentro de rango temporal válido

## Configuración de Test

### Datos de Prueba
- **Tenant**: Test Tenant con modelo "ollama"
- **SentimentAgent**: test_analyzer con tokens de ejemplo
- **Mock Results**: Resultado simulado con sentimiento POSITIVE

### Mocks Utilizados
- `SentimentChatService.run`: Servicio principal de análisis
- `IsTenantAuthenticated.has_permission`: Sistema de permisos

## Cobertura

Los tests cubren:
- ✅ Flujos exitosos y de error
- ✅ Validación de entrada y salida
- ✅ Manejo de excepciones
- ✅ Permisos y autenticación
- ✅ Serialización y deserialización
- ✅ Métodos HTTP permitidos
- ✅ Límites y validaciones de campos

## Ejecución

```bash
# Ejecutar todos los tests
python manage.py test analysis.tests.test_chat_analysis_view

# Ejecutar un test específico
python manage.py test analysis.tests.test_chat_analysis_view.ChatAnalysisViewTestCase.test_chat_analysis_success

# Ejecutar con verbosidad
python manage.py test analysis.tests.test_chat_analysis_view -v 2
```

## Endpoint Actual

**POST** `/api/v1/analysis/chat`

### Request
```json
{
    "chat": "Texto del chat a analizar",
    "analyzer_name": "nombre_del_analizador"
}
```

### Response
```json
{
    "sentimient": "POSITIVE|NEGATIVE|NEUTRAL",
    "cause": "Descripción del motivo",
    "log": "Log del análisis",
    "timestamp": "1234567890"
}
```

## Notas

- Los tests utilizan mocking para aislar la lógica de la vista
- Se valida tanto el happy path como los casos de error
- Todos los tests pasan exitosamente ✅
- La migración desde `api` hacia `analysis` fue completada exitosamente
