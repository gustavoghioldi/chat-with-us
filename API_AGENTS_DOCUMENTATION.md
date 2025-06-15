# API REST para AgentModel

## Descripción General

Esta API REST permite manejar completamente el modelo `AgentModel` con todas las operaciones CRUD y funcionalidades adicionales.

## Configuración

### Autenticación
- **Requerida**: Sí
- **Tipos soportados**: Session Authentication, Basic Authentication
- **Permisos**: `IsAuthenticated`

### Paginación
- **Tipo**: Page Number Pagination
- **Tamaño de página por defecto**: 20 registros

## Endpoints Disponibles

### 1. Listar Agentes
```
GET /api/v1/agents/
```
**Descripción**: Obtiene una lista paginada de todos los agentes.

**Parámetros de consulta opcionales**:
- `tenant`: Filtrar por ID de tenant
- `agent_model_id`: Filtrar por ID del modelo de IA
- `search`: Buscar en nombre e instrucciones
- `ordering`: Ordenar por campos (ej: `name`, `-created_at`)
- `page`: Número de página
- `page_size`: Tamaño de página (máx. 100)

**Respuesta exitosa (200)**:
```json
{
    "count": 25,
    "next": "http://localhost:8000/api/v1/agents/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "name": "Agente de Ventas",
            "agent_model_id": "llama3.2:3b",
            "tenant_name": "Empresa ABC",
            "knowledge_count": 3,
            "created_at": "2025-06-14T10:30:00Z",
            "updated_at": "2025-06-14T15:45:00Z"
        }
    ]
}
```

### 2. Crear Agente
```
POST /api/v1/agents/
```
**Descripción**: Crea un nuevo agente.

**Cuerpo de la solicitud**:
```json
{
    "name": "Nuevo Agente",
    "instructions": "Instrucciones detalladas para el agente",
    "agent_model_id": "llama3.2:3b",
    "tenant": 1,
    "knoledge_text_models": [1, 2, 3]
}
```

**Respuesta exitosa (201)**:
```json
{
    "id": 2,
    "name": "Nuevo Agente",
    "instructions": "Instrucciones detalladas para el agente",
    "knoledge_text_models": [1, 2, 3],
    "agent_model_id": "llama3.2:3b",
    "tenant": 1,
    "created_at": "2025-06-14T16:00:00Z",
    "updated_at": "2025-06-14T16:00:00Z"
}
```

### 3. Obtener Agente Específico
```
GET /api/v1/agents/{id}/
```
**Descripción**: Obtiene los detalles completos de un agente específico.

**Respuesta exitosa (200)**:
```json
{
    "id": 1,
    "name": "Agente de Ventas",
    "instructions": "Especializado en ventas y atención al cliente...",
    "knoledge_text_models": [1, 2, 3],
    "agent_model_id": "llama3.2:3b",
    "tenant": 1,
    "created_at": "2025-06-14T10:30:00Z",
    "updated_at": "2025-06-14T15:45:00Z"
}
```

### 4. Actualizar Agente Completo
```
PUT /api/v1/agents/{id}/
```
**Descripción**: Actualiza completamente un agente (requiere todos los campos).

**Cuerpo de la solicitud**:
```json
{
    "name": "Agente Actualizado",
    "instructions": "Nuevas instrucciones",
    "agent_model_id": "llama3.2:3b",
    "tenant": 1,
    "knoledge_text_models": [1, 2]
}
```

### 5. Actualizar Agente Parcial
```
PATCH /api/v1/agents/{id}/
```
**Descripción**: Actualiza parcialmente un agente (solo campos enviados).

**Cuerpo de la solicitud**:
```json
{
    "name": "Nuevo Nombre",
    "instructions": "Instrucciones actualizadas"
}
```

### 6. Eliminar Agente
```
DELETE /api/v1/agents/{id}/
```
**Descripción**: Elimina un agente permanentemente.

**Respuesta exitosa (204)**: Sin contenido

### 7. Agentes por Tenant
```
GET /api/v1/agents/by-tenant/{tenant_id}/
```
**Descripción**: Obtiene todos los agentes que pertenecen a un tenant específico.

**Respuesta exitosa (200)**:
```json
[
    {
        "id": 1,
        "name": "Agente de Ventas",
        "agent_model_id": "llama3.2:3b",
        "tenant_name": "Empresa ABC",
        "knowledge_count": 3,
        "created_at": "2025-06-14T10:30:00Z",
        "updated_at": "2025-06-14T15:45:00Z"
    }
]
```

### 8. Agregar Conocimiento a Agente
```
POST /api/v1/agents/{id}/add_knowledge/
```
**Descripción**: Agrega modelos de conocimiento a un agente existente.

**Cuerpo de la solicitud**:
```json
{
    "knowledge_ids": [4, 5, 6]
}
```

**Respuesta exitosa (200)**: Agente actualizado con nuevos conocimientos

### 9. Remover Conocimiento de Agente
```
POST /api/v1/agents/{id}/remove_knowledge/
```
**Descripción**: Remueve modelos de conocimiento de un agente.

**Cuerpo de la solicitud**:
```json
{
    "knowledge_ids": [4, 5]
}
```

**Respuesta exitosa (200)**: Agente actualizado sin los conocimientos removidos

### 10. Búsqueda Avanzada
```
GET /api/v1/agents/search/?q={query}&tenant_id={tenant_id}
```
**Descripción**: Búsqueda avanzada de agentes por texto.

**Parámetros requeridos**:
- `q`: Texto a buscar en nombre e instrucciones

**Parámetros opcionales**:
- `tenant_id`: Filtrar por tenant específico

**Respuesta exitosa (200)**: Lista de agentes que coinciden con la búsqueda

## Códigos de Error Comunes

### 400 Bad Request
```json
{
    "error": "Mensaje de error descriptivo"
}
```

### 401 Unauthorized
```json
{
    "detail": "Authentication credentials were not provided."
}
```

### 404 Not Found
```json
{
    "detail": "Not found."
}
```

### 422 Validation Error
```json
{
    "name": ["Ya existe un agente con este nombre."],
    "instructions": ["Este campo es requerido."]
}
```

## Ejemplos de Uso

### Usando curl

#### Crear un agente:
```bash
curl -X POST http://localhost:8000/api/v1/agents/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic dXNlcjpwYXNzd29yZA==" \
  -d '{
    "name": "Agente de Soporte",
    "instructions": "Ayuda con consultas técnicas",
    "agent_model_id": "llama3.2:3b",
    "tenant": 1
  }'
```

#### Listar agentes con filtros:
```bash
curl "http://localhost:8000/api/v1/agents/?tenant=1&search=ventas&ordering=-created_at" \
  -H "Authorization: Basic dXNlcjpwYXNzd29yZA=="
```

#### Agregar conocimiento a un agente:
```bash
curl -X POST http://localhost:8000/api/v1/agents/1/add_knowledge/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic dXNlcjpwYXNzd29yZA==" \
  -d '{"knowledge_ids": [1, 2, 3]}'
```

### Usando JavaScript (fetch)

```javascript
// Obtener lista de agentes
const response = await fetch('/api/v1/agents/', {
  headers: {
    'Authorization': 'Basic ' + btoa('user:password'),
    'Content-Type': 'application/json'
  }
});
const data = await response.json();

// Crear nuevo agente
const newAgent = await fetch('/api/v1/agents/', {
  method: 'POST',
  headers: {
    'Authorization': 'Basic ' + btoa('user:password'),
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    name: 'Agente de Marketing',
    instructions: 'Especializado en estrategias de marketing',
    agent_model_id: 'llama3.2:3b',
    tenant: 1
  })
});
```

### Usando Python (requests)

```python
import requests

# Configurar autenticación
auth = ('user', 'password')
base_url = 'http://localhost:8000/api/v1/agents/'

# Obtener todos los agentes
response = requests.get(base_url, auth=auth)
agents = response.json()

# Crear nuevo agente
new_agent_data = {
    'name': 'Agente de Recursos Humanos',
    'instructions': 'Maneja consultas de RRHH',
    'agent_model_id': 'llama3.2:3b',
    'tenant': 1,
    'knoledge_text_models': [1, 2]
}
response = requests.post(base_url, json=new_agent_data, auth=auth)
created_agent = response.json()

# Búsqueda avanzada
search_params = {'q': 'ventas', 'tenant_id': 1}
response = requests.get(f"{base_url}search/", params=search_params, auth=auth)
search_results = response.json()
```

## Características Técnicas

### Optimizaciones
- **Consultas optimizadas**: Uso de `select_related` y `prefetch_related`
- **Filtrado eficiente**: Implementación de `DjangoFilterBackend`
- **Búsqueda indexada**: Búsqueda en campos `name` e `instructions`
- **Paginación**: Reduce la carga de datos en respuestas grandes

### Validaciones
- **Nombres únicos**: No se permiten agentes con el mismo nombre
- **Relaciones válidas**: Validación de existencia de tenant y knowledge models
- **Campos requeridos**: Validación de campos obligatorios

### Seguridad
- **Autenticación requerida**: Todos los endpoints requieren autenticación
- **Validación de entrada**: Sanitización de datos de entrada
- **Manejo de errores**: Respuestas de error consistentes y seguras
