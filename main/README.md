# Main - Configuración Principal del Proyecto

## Descripción General
Este directorio contiene la configuración principal del proyecto Django, incluyendo settings, URLs raíz, configuración de Celery, y otros archivos de configuración del sistema.

## Estructura del Directorio

### Archivos Principales

- **asgi.py**: Configuración ASGI para aplicaciones asíncronas
- **wsgi.py**: Configuración WSGI para despliegue en producción
- **urls.py**: URLs principales del proyecto
- **celery.py**: Configuración de Celery para tareas asíncronas
- **models.py**: Modelos base utilizados por toda la aplicación
- **signals.py**: Señales globales del sistema
- **SIGNALS_DOCUMENTATION.md**: Documentación detallada del sistema de señales

### Carpeta `settings/`
Contiene la configuración modular del proyecto:
- **__init__.py**: Selector automático de configuración según ambiente
- **base.py**: Configuración base común a todos los ambientes
- **development.py**: Configuración específica para desarrollo
- **production.py**: Configuración específica para producción

### Carpeta `management/`
Contiene comandos de gestión personalizados de Django:
- Comandos para inicialización de datos
- Comandos para mantenimiento del sistema
- Comandos para migraciones específicas

## Configuración por Ambientes

### Desarrollo (development.py)
```python
# Configuraciones típicas para desarrollo
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Base de datos local
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'barbadb_dev',
        # ... otras configuraciones
    }
}

# Logging verbose para desarrollo
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

### Producción (production.py)
```python
# Configuraciones para producción
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com']

# Configuración de seguridad
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True

# Configuración de caché
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

## Configuración de Base de Datos

### PostgreSQL con pgvector
- **Base de datos principal**: Datos de la aplicación
- **Base de datos AI**: Embeddings y datos vectoriales
- **Configuración de conexiones**: Pool de conexiones optimizado

### Configuración de Vectores
```python
# Configuración para pgvector
VECTOR_DATABASE = {
    'ENGINE': 'django.db.backends.postgresql',
    'NAME': 'ai_db',
    'USER': 'ai_user',
    'PASSWORD': 'ai_password',
    'HOST': 'localhost',
    'PORT': '5532',
    'OPTIONS': {
        'OPTIONS': '-c search_path=public,vector'
    }
}
```

## Configuración de Celery

### Configuración Base
```python
# celery.py
from celery import Celery
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')

app = Celery('main')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
```

### Configuración de Tareas
- **Procesamiento de documentos**: Tareas asíncronas para procesamiento
- **Análisis de sentimientos**: Análisis en background
- **Notificaciones**: Envío de notificaciones
- **Mantenimiento**: Tareas de limpieza y mantenimiento

## Modelos Base

### AppModel
Modelo base que incluye:
- **created_at**: Fecha de creación
- **updated_at**: Fecha de última actualización
- **tenant**: Relación con tenant (multi-tenancy)
- **is_active**: Estado activo/inactivo

```python
class AppModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tenant = models.ForeignKey(TenantModel, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True
```

## Sistema de Señales

### Señales Globales
- **post_save**: Acciones después de guardar modelos
- **pre_delete**: Acciones antes de eliminar modelos
- **user_logged_in**: Acciones cuando un usuario inicia sesión
- **custom_signals**: Señales personalizadas del sistema

### Documentación de Señales
Ver `SIGNALS_DOCUMENTATION.md` para información detallada sobre:
- Señales disponibles
- Parámetros de cada señal
- Ejemplos de uso
- Mejores prácticas

## URLs Principales

### Estructura de URLs
```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('api.urls')),
    path('agents/', include('agents.urls')),
    path('chats/', include('chats.urls')),
    path('documents/', include('documents.urls')),
    path('knowledge/', include('knowledge.urls')),
    path('analysis/', include('analysis.urls')),
]
```

### Configuración de API
- **Versioning**: Versionado de APIs
- **Throttling**: Límites de tasa
- **Authentication**: Autenticación y autorización
- **Documentation**: Documentación automática con Swagger

## Configuración de Seguridad

### Autenticación
- **Django Authentication**: Sistema de autenticación por defecto
- **Token Authentication**: Autenticación por tokens
- **JWT Support**: Soporte para JWT tokens
- **Multi-factor Authentication**: Autenticación de múltiples factores

### Autorización
- **Role-based Access Control**: Control de acceso basado en roles
- **Tenant-based Isolation**: Aislamiento por tenant
- **Permission System**: Sistema de permisos granular

## Logging y Monitoreo

### Configuración de Logs
- **Application Logs**: Logs de la aplicación
- **Error Logs**: Logs de errores
- **Security Logs**: Logs de seguridad
- **Performance Logs**: Logs de rendimiento

### Monitoreo
- **Health Checks**: Verificaciones de estado
- **Metrics Collection**: Recolección de métricas
- **Alerting**: Sistema de alertas
- **Performance Monitoring**: Monitoreo de rendimiento

## Comandos de Gestión

### Comandos Personalizados
- **init_system**: Inicialización del sistema
- **backup_data**: Respaldo de datos
- **cleanup_old_data**: Limpieza de datos antiguos
- **generate_reports**: Generación de reportes

### Uso de Comandos
```bash
# Inicializar sistema
python manage.py init_system

# Respaldo de datos
python manage.py backup_data --tenant=all

# Limpieza de datos
python manage.py cleanup_old_data --days=30
```

## Configuración de Desarrollo

### Variables de Entorno
```bash
# .env para desarrollo
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:pass@localhost/db
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
```

### Docker Configuration
- **docker-compose.yml**: Configuración para desarrollo
- **Dockerfile**: Imagen de la aplicación
- **docker-entrypoint.sh**: Script de inicialización

## Mejores Prácticas

1. **Configuración por Ambientes**: Separar configuraciones por ambiente
2. **Variables de Entorno**: Usar variables de entorno para configuración sensible
3. **Logging Estructurado**: Usar logging estructurado y significativo
4. **Monitoring**: Implementar monitoreo proactivo
5. **Security**: Seguir mejores prácticas de seguridad
6. **Performance**: Optimizar configuraciones para rendimiento
