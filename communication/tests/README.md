# Tests para TelegramCommunicationService

Esta carpeta contiene los tests unitarios específicos para el `TelegramCommunicationService`.

## Estructura de Tests

### `test_telegram_communication_service.py`
**Tests principales del servicio**

#### `TelegramCommunicationServiceTests`
- ✅ `test_send_message_success()` - Envío exitoso de mensaje
- ✅ `test_send_message_failure()` - Manejo de errores en envío
- ✅ `test_send_message_with_special_characters()` - Caracteres especiales
- ✅ `test_get_updates_success()` - Obtención exitosa de updates
- ✅ `test_get_updates_empty_result()` - Updates vacíos
- ✅ `test_get_updates_failure()` - Errores en obtención de updates
- ✅ `test_get_updates_malformed_response()` - Respuestas malformadas
- ✅ `test_service_initialization()` - Inicialización del servicio
- ✅ `test_send_message_with_empty_message()` - Mensajes vacíos
- ✅ `test_send_message_with_long_message()` - Mensajes largos
- ✅ `test_send_message_network_error()` - Errores de red en envío
- ✅ `test_get_updates_network_error()` - Errores de red en updates

#### `TelegramCommunicationServiceIntegrationTests`
- Tests de integración con modelos reales (expandible)

### `test_telegram_service_edge_cases.py`
**Tests para casos edge y rendimiento**

#### `TelegramCommunicationServiceEdgeCaseTests`
- ✅ `test_send_message_with_unicode_characters()` - Caracteres Unicode y emojis
- ✅ `test_send_message_with_markdown_injection()` - Problemas con Markdown
- ✅ `test_send_message_with_negative_chat_id()` - IDs negativos (grupos)
- ✅ `test_send_message_timeout_handling()` - Manejo de timeouts
- ✅ `test_get_updates_with_large_response()` - Respuestas grandes
- ✅ `test_get_updates_with_malformed_update()` - Updates malformados
- ✅ `test_service_initialization_with_none_model()` - Inicialización con None
- ✅ `test_send_message_with_empty_token()` - Token vacío
- ✅ `test_concurrent_send_messages()` - Envíos concurrentes

#### `TelegramCommunicationServicePerformanceTests`
- ✅ `test_send_message_performance()` - Rendimiento de envío
- ✅ `test_get_updates_performance_with_large_dataset()` - Rendimiento con datasets grandes
- ✅ `test_memory_usage_with_large_messages()` - Uso de memoria

## Ejecutar los Tests

### Todos los tests de la aplicación communication
```bash
python manage.py test communication
```

### Solo tests del TelegramCommunicationService
```bash
python manage.py test communication.tests.test_telegram_communication_service
```

### Solo tests de casos edge
```bash
python manage.py test communication.tests.test_telegram_service_edge_cases
```

### Test específico
```bash
python manage.py test communication.tests.test_telegram_communication_service.TelegramCommunicationServiceTests.test_send_message_success
```

### Con verbosidad
```bash
python manage.py test communication --verbosity=2
```

### Con cobertura (si tienes coverage instalado)
```bash
coverage run --source='.' manage.py test communication
coverage report -m
coverage html  # Genera reporte HTML
```

## Mocks y Patching

Los tests usan extensively mocking para:

- **`requests.post`** - Simular llamadas HTTP para envío de mensajes
- **`requests.get`** - Simular llamadas HTTP para obtener updates
- **`TelegramCommunicationModel`** - Mock del modelo de comunicación
- **Respuestas de API** - Simular diferentes tipos de respuesta de Telegram

## Casos de Prueba Cubiertos

### ✅ Casos Exitosos
- Envío de mensajes normales
- Obtención de updates
- Mensajes con caracteres especiales
- Múltiples updates

### ✅ Casos de Error
- Errores HTTP (400, 401, 500)
- Errores de red (timeout, connection)
- Respuestas malformadas
- Tokens inválidos

### ✅ Casos Edge
- Mensajes muy largos
- Caracteres Unicode y emojis
- Chat IDs negativos (grupos)
- Datasets grandes
- Concurrencia

### ✅ Rendimiento
- Tiempo de ejecución
- Manejo de memoria
- Volumen de datos

## Estructura de Datos de Test

### Mensaje de Test Típico
```python
{
    "update_id": 123456,
    "message": {
        "message_id": 1,
        "from": {
            "id": 987654321,
            "is_bot": False,
            "first_name": "Juan",
            "last_name": "Pérez",
            "language_code": "es"
        },
        "chat": {
            "id": 123456789,
            "type": "private"
        },
        "date": 1609459200,
        "text": "Mensaje de prueba"
    }
}
```

### Respuesta de API Exitosa
```python
{
    "ok": True,
    "result": [...]
}
```

### Respuesta de API con Error
```python
{
    "ok": False,
    "error_code": 400,
    "description": "Bad Request: chat not found"
}
```

## Agregar Nuevos Tests

Para agregar nuevos tests:

1. **Test unitario simple** → Agregar a `TelegramCommunicationServiceTests`
2. **Caso edge** → Agregar a `TelegramCommunicationServiceEdgeCaseTests`
3. **Test de rendimiento** → Agregar a `TelegramCommunicationServicePerformanceTests`
4. **Test de integración** → Agregar a `TelegramCommunicationServiceIntegrationTests`

### Ejemplo de Nuevo Test
```python
@patch('communication.services.telegram_communication_service.requests.post')
def test_my_new_functionality(self, mock_post):
    # Setup
    mock_response = Mock()
    mock_response.status_code = 200
    mock_post.return_value = mock_response

    # Execute
    result = self.service.my_new_method()

    # Assert
    self.assertIsNotNone(result)
    mock_post.assert_called_once()
```

## Notas Importantes

- **Mocking**: Todos los tests usan mocks para evitar llamadas reales a la API de Telegram
- **Aislamiento**: Cada test es independiente y no afecta a otros
- **Cobertura**: Los tests cubren tanto casos exitosos como de error
- **Rendimiento**: Se incluyen tests básicos de rendimiento
- **Mantenimiento**: Tests fáciles de mantener y extender
