# Settings - Configuración del Proyecto

## Descripción General
Este directorio contiene la configuración modular del proyecto Django, organizada por ambientes para facilitar el mantenimiento y despliegue en diferentes entornos.

## Estructura de Archivos

### `__init__.py`
Archivo de inicialización que selecciona automáticamente la configuración apropiada basándose en la variable de entorno `DJANGO_ENV`.

```python
import os

ENV = os.environ.get("DJANGO_ENV", "development")

if ENV == "production":
    from .production import *
else:
    from .development import *
```

### `base.py`
Configuración base común a todos los ambientes. Incluye:

#### Configuración de Django
- **INSTALLED_APPS**: Aplicaciones instaladas
- **MIDDLEWARE**: Middleware del proyecto
- **ROOT_URLCONF**: Configuración de URLs raíz
- **TEMPLATES**: Configuración de plantillas
- **WSGI_APPLICATION**: Aplicación WSGI

#### Configuración de Base de Datos
- **DATABASES**: Configuración de bases de datos
- **DEFAULT_AUTO_FIELD**: Campo auto por defecto
- **DATABASE_ROUTERS**: Routers de base de datos (si aplica)

#### Configuración Internacional
- **LANGUAGE_CODE**: Código de idioma ('es-es')
- **TIME_ZONE**: Zona horaria ('UTC')
- **USE_I18N**: Internacionalización habilitada
- **USE_TZ**: Uso de timezone habilitado

#### Configuración de Archivos Estáticos
- **STATIC_URL**: URL para archivos estáticos
- **STATIC_ROOT**: Directorio para archivos estáticos en producción
- **MEDIA_URL**: URL para archivos multimedia
- **MEDIA_ROOT**: Directorio para archivos multimedia

#### Configuración de Seguridad
- **SECRET_KEY**: Clave secreta (desde variables de entorno)
- **ALLOWED_HOSTS**: Hosts permitidos
- **CSRF_TRUSTED_ORIGINS**: Orígenes confiables para CSRF

#### Configuración de Autenticación
- **AUTH_USER_MODEL**: Modelo de usuario personalizado
- **LOGIN_URL**: URL de login
- **LOGIN_REDIRECT_URL**: URL de redirección después del login
- **LOGOUT_REDIRECT_URL**: URL de redirección después del logout

#### Configuración de REST Framework
```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],
}
```

#### Configuración de Celery
```python
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
```

### `development.py`
Configuración específica para el ambiente de desarrollo:

#### Configuraciones de Desarrollo
```python
from .base import *

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# Base de datos de desarrollo
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'barbadb'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'barba'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5632'),
    }
}

# Logging para desarrollo
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'logs/django.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'main': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
```

#### Herramientas de Desarrollo
- **Django Debug Toolbar**: Habilitado para debug
- **CORS Settings**: Configuración permisiva para desarrollo
- **Email Backend**: Backend de email para desarrollo (console)

### `production.py`
Configuración específica para el ambiente de producción:

#### Configuraciones de Producción
```python
from .base import *

DEBUG = False
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

# Configuración de seguridad
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# Configuración de sesiones
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_AGE = 1800  # 30 minutos

# Configuración de CSRF
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True

# Base de datos de producción
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'CONN_MAX_AGE': 60,
        'OPTIONS': {
            'sslmode': 'require',
        },
    }
}
```

#### Configuración de Caché
```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://localhost:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

#### Logging para Producción
- **File Logging**: Logs en archivos
- **Error Logging**: Logs de errores separados
- **Rotation**: Rotación de logs
- **Sentry Integration**: Integración con Sentry para error tracking

## Variables de Entorno

### Variables Comunes
```bash
# Django
SECRET_KEY=your-secret-key-here
DJANGO_ENV=development|production
DEBUG=True|False
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com

# Base de datos
DB_NAME=barbadb
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5632

# Redis
REDIS_URL=redis://localhost:6379/0

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# AI Services
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
```

### Variables de Producción
```bash
# Seguridad
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-password
EMAIL_USE_TLS=True

# Monitoreo
SENTRY_DSN=your-sentry-dsn
```

## Configuración por Módulos

### Configuración de Aplicaciones
```python
INSTALLED_APPS = [
    # Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third party apps
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'django_celery_beat',
    'django_celery_results',

    # Local apps
    'main',
    'agents',
    'analysis',
    'api',
    'chats',
    'crews',
    'documents',
    'knowledge',
    'tenants',
    'tools',
]
```

### Configuración de Middleware
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'tenants.middleware.TenantMiddleware',  # Custom middleware
]
```

## Mejores Prácticas

### Gestión de Configuraciones
1. **Separación por Ambientes**: Mantener configuraciones separadas
2. **Variables de Entorno**: Usar variables de entorno para datos sensibles
3. **Configuración Base**: Mantener configuración común en base.py
4. **Documentación**: Documentar todas las configuraciones

### Seguridad
1. **Secret Key**: Nunca hardcodear la secret key
2. **Debug Mode**: Desactivar DEBUG en producción
3. **HTTPS**: Forzar HTTPS en producción
4. **Headers de Seguridad**: Configurar headers de seguridad apropiados

### Performance
1. **Database Connections**: Optimizar conexiones de base de datos
2. **Caching**: Implementar caching apropiado
3. **Static Files**: Configurar servicio de archivos estáticos
4. **Logging**: Configurar logging eficiente

### Monitoreo
1. **Error Tracking**: Implementar tracking de errores
2. **Performance Monitoring**: Monitorear rendimiento
3. **Health Checks**: Implementar verificaciones de estado
4. **Alerting**: Configurar alertas para problemas críticos
