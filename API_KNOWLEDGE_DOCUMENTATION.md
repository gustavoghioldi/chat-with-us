# API REST para KnowledgeModel

## Descripción General

Esta API REST permite manejar completamente el modelo `KnowledgeModel` con operaciones CRUD específicas según el tipo de contenido. El serializer se selecciona automáticamente según el parámetro de tipo en la URL.

## Tipos de Knowledge Soportados

### 1. **Text** (`/api/v1/knowledge/text/`)
- **Serializer**: `KnowledgeTextSerializer`
- **Descripción**: Para documentos de texto plano
- **Categoría**: `plain_document`

### 2. **JSON** (`/api/v1/knowledge/json/`)
- **Serializer**: `KnowledgeJsonSerializer`
- **Descripción**: Para datos estructurados en formato JSON
- **Categoría**: `plain_document`

### 3. **CSV** (`/api/v1/knowledge/csv/`)
- **Serializer**: `KnowledgeCSVSerializer`
- **Descripción**: Para datos tabulares en formato CSV
- **Categoría**: `plain_document`

### 4. **Web Scraping** (`/api/v1/knowledge/web-scraping/`)
- **Serializer**: `KnowledgeWebScrapingSerializer`
- **Descripción**: Para configuración de scraping de sitios web
- **Categoría**: `website`

## Endpoints Disponibles

### 1. Listar Knowledge por Tipo
```
GET /api/v1/knowledge/{type}/
```

**Tipos válidos**: `text`, `json`, `csv`, `web-scraping`

**Parámetros de consulta opcionales**:
- `category`: Filtrar por categoría
- `tenant`: Filtrar por ID de tenant
- `search`: Buscar en nombre, descripción y texto
- `ordering`: Ordenar por campos (ej: `name`, `-created_at`)

**Respuesta exitosa (200)**:
```json
{
    "count": 10,
    "next": "http://localhost:8000/api/v1/knowledge/text/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "name": "Manual de Usuario",
            "category": "plain_document",
            "type": "text",
            "tenant": "Empresa ABC",
            "created_at": "2025-06-16T10:30:00Z",
            "updated_at": "2025-06-16T15:45:00Z",
            "has_content": true
        }
    ]
}
```

### 2. Crear Knowledge por Tipo
```
POST /api/v1/knowledge/{type}/
```

#### **Crear Knowledge de Texto**
```
POST /api/v1/knowledge/text/
```
**Cuerpo de la solicitud**:
```json
{
    "name": "Manual de Procedimientos",
    "content": "Este es el contenido del manual con todas las instrucciones..."
}
```

#### **Crear Knowledge de JSON**
```
POST /api/v1/knowledge/json/
```
**Cuerpo de la solicitud**:
```json
{
    "name": "Datos de Productos",
    "content": [
        {"id": 1, "name": "Producto A", "price": 29.99},
        {"id": 2, "name": "Producto B", "price": 39.99}
    ]
}
```

#### **Crear Knowledge de CSV**
```
POST /api/v1/knowledge/csv/
```
**Cuerpo de la solicitud**:
```json
{
    "name": "Lista de Empleados",
    "content": "name,position,salary\nJuan Pérez,Developer,50000\nMaría García,Designer,45000"
}
```

#### **Crear Knowledge de Web Scraping**
```
POST /api/v1/knowledge/web-scraping/
```
**Cuerpo de la solicitud**:
```json
{
    "name": "Scraping de Noticias",
    "url": "https://example.com/news",
    "max_depth": 2,
    "max_links": 50
}
```

**Respuesta exitosa para todos (201)**:
```json
{
    "id": 15,
    "name": "Manual de Procedimientos",
    "category": "plain_document",
    "type": "text",
    "created_at": "2025-06-16T16:00:00Z",
    "message": "Modelo de conocimiento \"Manual de Procedimientos\" creado exitosamente."
}
```

### 3. Obtener Knowledge Específico
```
GET /api/v1/knowledge/{type}/{id}/
```

**Respuesta exitosa (200) - Ejemplo para texto**:
```json
{
    "id": 1,
    "name": "Manual de Usuario",
    "category": "plain_document",
    "type": "text",
    "tenant": "Empresa ABC",
    "created_at": "2025-06-16T10:30:00Z",
    "updated_at": "2025-06-16T15:45:00Z",
    "content": "Contenido completo del manual..."
}
```

**Respuesta exitosa (200) - Ejemplo para JSON**:
```json
{
    "id": 2,
    "name": "Datos de Productos",
    "category": "plain_document",
    "type": "json",
    "tenant": "Empresa ABC",
    "created_at": "2025-06-16T10:30:00Z",
    "updated_at": "2025-06-16T15:45:00Z",
    "content": [
        {"id": 1, "name": "Producto A", "price": 29.99}
    ]
}
```

**Respuesta exitosa (200) - Ejemplo para Web Scraping**:
```json
{
    "id": 3,
    "name": "Scraping de Noticias",
    "category": "website",
    "type": "web-scraping",
    "tenant": "Empresa ABC",
    "created_at": "2025-06-16T10:30:00Z",
    "updated_at": "2025-06-16T15:45:00Z",
    "url": "https://example.com/news",
    "description": "Web scraping de: https://example.com/news"
}
```

### 4. Actualizar Knowledge Completo
```
PUT /api/v1/knowledge/{type}/{id}/
```

**Ejemplo para actualizar texto**:
```json
{
    "name": "Manual Actualizado",
    "content": "Nuevo contenido del manual..."
}
```

### 5. Actualizar Knowledge Parcial
```
PATCH /api/v1/knowledge/{type}/{id}/
```

**Ejemplo para actualizar solo el nombre**:
```json
{
    "name": "Nuevo Nombre"
}
```

### 6. Eliminar Knowledge
```
DELETE /api/v1/knowledge/{type}/{id}/
```

**Respuesta exitosa (204)**: Sin contenido

## Validaciones por Tipo

### **Text Knowledge**
- **Límite de caracteres**: Configurado por `KNOWKEDGE_TEXT_MAX_CHARS` en settings
- **Campos requeridos**: `name`, `content`

### **JSON Knowledge**
- **Límite de objetos**: Máximo 1,000 objetos en la lista
- **Formato**: Debe ser una lista válida de objetos JSON
- **Campos requeridos**: `name`, `content`

### **CSV Knowledge**
- **Formato válido**: Debe ser CSV válido con estructura consistente
- **Límite de filas**: Máximo configurado por `KNOWKEDGE_CSV_MAX_ROWS`
- **Validaciones**:
  - Número consistente de columnas
  - Encabezados no vacíos
  - Formato CSV válido
- **Campos requeridos**: `name`, `content`

### **Web Scraping Knowledge**
- **URL válida**: Debe ser una URL válida y accesible
- **Parámetros opcionales**: `max_depth`, `max_links`
- **Campos requeridos**: `name`, `url`

## Códigos de Error

### 400 Bad Request
```json
{
    "content": ["El CSV no puede tener más de 10,000 filas. Actualmente tiene 15,000 filas."]
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
    "name": ["Este campo es requerido."],
    "content": ["Formato CSV inválido: line contains NULL byte"]
}
```

## Ejemplos de Uso

### Usando curl

#### Crear knowledge de texto:
```bash
curl -X POST http://localhost:8000/api/v1/knowledge/text/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic dXNlcjpwYXNzd29yZA==" \
  -d '{
    "name": "Manual de API",
    "content": "Este manual describe cómo usar la API..."
  }'
```

#### Crear knowledge de JSON:
```bash
curl -X POST http://localhost:8000/api/v1/knowledge/json/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic dXNlcjpwYXNzd29yZA==" \
  -d '{
    "name": "Catálogo de Productos",
    "content": [
      {"id": 1, "name": "Laptop", "price": 999.99},
      {"id": 2, "name": "Mouse", "price": 29.99}
    ]
  }'
```

#### Obtener knowledge específico:
```bash
curl http://localhost:8000/api/v1/knowledge/text/1/ \
  -H "Authorization: Basic dXNlcjpwYXNzd29yZA=="
```

### Usando JavaScript (fetch)

```javascript
// Crear knowledge de CSV
const csvData = {
  name: 'Empleados 2025',
  content: 'name,department,salary\nJuan,IT,50000\nMaría,HR,45000'
};

const response = await fetch('/api/v1/knowledge/csv/', {
  method: 'POST',
  headers: {
    'Authorization': 'Basic ' + btoa('user:password'),
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(csvData)
});

const result = await response.json();
```

### Usando Python (requests)

```python
import requests

# Configurar autenticación
auth = ('user', 'password')
base_url = 'http://localhost:8000/api/v1/knowledge/'

# Crear knowledge de web scraping
scraping_data = {
    'name': 'Noticias Tech',
    'url': 'https://techcrunch.com',
    'max_depth': 3,
    'max_links': 100
}

response = requests.post(
    f"{base_url}web-scraping/",
    json=scraping_data,
    auth=auth
)
created_knowledge = response.json()

# Listar todos los knowledge de texto
response = requests.get(f"{base_url}text/", auth=auth)
text_knowledge = response.json()

# Actualizar knowledge
update_data = {'name': 'Nuevo Nombre'}
response = requests.patch(
    f"{base_url}text/1/",
    json=update_data,
    auth=auth
)
```

## Características Técnicas

### Selección Automática de Serializers
- La vista selecciona automáticamente el serializer correcto según el parámetro `knowledge_type` en la URL
- Mapeo dinámico entre tipos y serializers
- Fallback al serializer de texto por defecto

### Procesamiento de Contenido
- **Texto**: Se almacena directamente en el campo `text`
- **JSON**: Se convierte a string con formato indentado
- **CSV**: Se almacena como texto plano después de validación
- **Web Scraping**: Se almacena configuración y se puede extender para ejecutar scraping

### Optimizaciones
- Consultas optimizadas con `select_related('tenant')`
- Filtrado eficiente por categoría y tenant
- Paginación automática para listas grandes

### Seguridad
- Autenticación requerida para todos los endpoints
- Validación específica por tipo de contenido
- Manejo robusto de errores y excepciones

Esta API proporciona una interfaz uniforme para manejar diferentes tipos de conocimiento mientras mantiene validaciones específicas para cada formato.
