# Módulo de Documentos

## Descripción

Este módulo proporciona funcionalidad completa para que los usuarios puedan subir, gestionar y organizar documentos en el sistema. Cada documento está asociado a un tenant específico y al usuario que lo subió.

## Características

### Modelo DocumentModel

- **Almacenamiento organizado**: Los archivos se guardan organizados por tenant con nombres únicos
- **Nombres únicos**: Timestamp automático agregado antes de la extensión para evitar duplicados
- **Tipos de archivo soportados**: PDF, Word (DOC/DOCX), TXT, CSV, Excel (XLS/XLSX), JSON, Markdown
- **Metadatos automáticos**: Captura automática del tamaño, nombre original y tipo de archivo
- **Soft delete**: Los documentos se pueden desactivar sin eliminar físicamente
- **Auditoría completa**: Timestamps de creación, actualización y procesamiento

### Administración Django

El admin de Django incluye:

- **Interfaz completa**: CRUD completo con filtros, búsqueda y ordenamiento
- **Vista previa**: Enlaces de descarga y vista previa de archivos
- **Acciones masivas**: Marcar como procesado/no procesado, activar/desactivar
- **Información detallada**: Metadatos del archivo, estadísticas de tamaño
- **Filtros avanzados**: Por tipo, estado, tenant, usuario, fechas

### API REST

Endpoints disponibles:

- `GET /api/v1/documents/` - Listar documentos
- `POST /api/v1/documents/` - Subir nuevo documento
- `GET /api/v1/documents/{id}/` - Obtener documento específico
- `PUT/PATCH /api/v1/documents/{id}/` - Actualizar documento
- `DELETE /api/v1/documents/{id}/` - Eliminar documento (soft delete)
- `POST /api/v1/documents/{id}/mark_processed/` - Marcar como procesado
- `GET /api/v1/documents/stats/` - Estadísticas de documentos
- `POST /api/v1/documents/bulk_update/` - Actualización masiva
- `POST /api/v1/documents/validate_file/` - Validar archivo antes de subir
- `GET /api/v1/documents/types/` - Obtener tipos disponibles

### Servicios

La clase `DocumentService` proporciona:

- **Creación de documentos**: Con validación automática
- **Filtrado avanzado**: Por tenant, usuario, tipo, estado
- **Validación de archivos**: Tamaño, extensión, tipo MIME
- **Estadísticas**: Conteos, distribución por tipo, tamaño total
- **Operaciones masivas**: Actualización de múltiples documentos

## Configuración

### Settings necesarios

```python
# En settings/base.py
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Límites de archivos
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
FILE_UPLOAD_PERMISSIONS = 0o644
```

### URLs

```python
# En api/urls.py
path("v1/", include("documents.urls")),
```

### Estructura de archivos

Los documentos se guardan en:
```
media/
  documents/
    tenant_name/
      archivo_20250618_143052_123.pdf
      documento_20250618_143055_456.docx
    otro_tenant/
      reporte_20250618_143100_789.txt
```

**Formato de nombres de archivo:**
- `nombre_original_YYYYMMDD_HHMMSS_microsegundos.extension`
- Ejemplo: `reporte_anual_20250618_143052_123.pdf`
- El timestamp incluye fecha, hora y microsegundos para garantizar unicidad
- Los nombres se limpian automáticamente (espacios → guiones bajos, solo caracteres alfanuméricos)

## Uso

### Desde el Admin

1. Ir a Django Admin → Documentos
2. Hacer clic en "Agregar documento"
3. Completar título, descripción, seleccionar archivo
4. Seleccionar tenant y usuario
5. El tipo se detecta automáticamente

### Desde la API

#### Subir documento

```bash
curl -X POST http://localhost:8000/api/v1/documents/ \
  -H "Authorization: Bearer <token>" \
  -F "title=Mi Documento" \
  -F "description=Descripción opcional" \
  -F "file=@/path/to/file.pdf"
```

#### Listar documentos

```bash
curl -X GET http://localhost:8000/api/v1/documents/ \
  -H "Authorization: Bearer <token>"
```

#### Filtrar documentos

```bash
curl -X GET "http://localhost:8000/api/v1/documents/?document_type=pdf&is_active=true" \
  -H "Authorization: Bearer <token>"
```

#### Obtener estadísticas

```bash
curl -X GET http://localhost:8000/api/v1/documents/stats/ \
  -H "Authorization: Bearer <token>"
```

## Comandos de Management

### Limpiar documentos antiguos

```bash
# Ver qué se eliminaría (dry run)
python manage.py cleanup_documents --days=90 --dry-run

# Eliminar documentos inactivos más antiguos que 30 días
python manage.py cleanup_documents --days=30 --inactive-only

# Eliminación física (hard delete)
python manage.py cleanup_documents --days=180 --hard-delete

# Limpiar tenant específico
python manage.py cleanup_documents --tenant-id=1 --days=60
```

## Validaciones

### Tipos de archivo permitidos

- **Documentos**: PDF, DOC, DOCX
- **Texto**: TXT, MD
- **Datos**: CSV, JSON
- **Hojas de cálculo**: XLS, XLSX

### Límites

- **Tamaño máximo**: 50MB por archivo
- **Extensiones**: Solo las permitidas en `DOCUMENT_TYPES`
- **Validación MIME**: Verificación del tipo real del archivo

## Seguridad

- **Aislamiento por tenant**: Los usuarios solo ven documentos de su tenant
- **Validación de archivos**: Verificación de tipo y tamaño
- **Permisos**: Autenticación requerida para todas las operaciones
- **Estructura segura**: Archivos organizados por tenant/usuario

## Testing

Ejecutar tests:

```bash
python manage.py test documents
```

Los tests cubren:
- Creación y validación de modelos
- Servicios de documentos
- Validación de archivos
- Estadísticas y operaciones masivas

## Extensiones Futuras

- **Versionado de documentos**: Mantener historial de versiones
- **OCR**: Extracción de texto de imágenes y PDFs
- **Vista previa**: Generación de thumbnails
- **Compartir**: Funcionalidad para compartir entre usuarios
- **Categorización**: Sistema de tags o categorías
- **Búsqueda de contenido**: Indexación del contenido de archivos
