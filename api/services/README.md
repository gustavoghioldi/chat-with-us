# Servicios de API

## Descripción General
Este directorio contiene los servicios de negocio para la API REST del sistema. Los servicios encapsulan la lógica de negocio compleja y proporcionan una interfaz limpia para las vistas de la API.

## Estructura de Archivos

### `s3_upload_service.py`
Servicio para manejo de carga de archivos a Amazon S3.

```python
import boto3
from django.conf import settings
from botocore.exceptions import ClientError
import logging

class S3UploadService:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        self.bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        self.logger = logging.getLogger(__name__)

    def upload_file(self, file_obj, key, bucket_name=None):
        """
        Sube un archivo a S3.

        Args:
            file_obj: Objeto de archivo a subir
            key: Clave (path) del archivo en S3
            bucket_name: Nombre del bucket (opcional)

        Returns:
            dict: Resultado de la operación con URL del archivo
        """
        bucket = bucket_name or self.bucket_name

        try:
            self.s3_client.upload_fileobj(
                file_obj,
                bucket,
                key,
                ExtraArgs={'ACL': 'private'}
            )

            file_url = f"https://{bucket}.s3.amazonaws.com/{key}"

            self.logger.info(f"File uploaded successfully: {key}")
            return {
                'success': True,
                'url': file_url,
                'key': key,
                'bucket': bucket
            }

        except ClientError as e:
            self.logger.error(f"Error uploading file: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def delete_file(self, key, bucket_name=None):
        """
        Elimina un archivo de S3.

        Args:
            key: Clave del archivo a eliminar
            bucket_name: Nombre del bucket (opcional)

        Returns:
            dict: Resultado de la operación
        """
        bucket = bucket_name or self.bucket_name

        try:
            self.s3_client.delete_object(Bucket=bucket, Key=key)
            self.logger.info(f"File deleted successfully: {key}")
            return {'success': True}

        except ClientError as e:
            self.logger.error(f"Error deleting file: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_file_url(self, key, bucket_name=None, expires_in=3600):
        """
        Genera una URL firmada para acceder a un archivo.

        Args:
            key: Clave del archivo
            bucket_name: Nombre del bucket (opcional)
            expires_in: Tiempo de expiración en segundos

        Returns:
            str: URL firmada
        """
        bucket = bucket_name or self.bucket_name

        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket, 'Key': key},
                ExpiresIn=expires_in
            )
            return url

        except ClientError as e:
            self.logger.error(f"Error generating presigned URL: {e}")
            return None

    def list_files(self, prefix='', bucket_name=None):
        """
        Lista archivos en S3 con un prefijo específico.

        Args:
            prefix: Prefijo para filtrar archivos
            bucket_name: Nombre del bucket (opcional)

        Returns:
            list: Lista de archivos encontrados
        """
        bucket = bucket_name or self.bucket_name

        try:
            response = self.s3_client.list_objects_v2(
                Bucket=bucket,
                Prefix=prefix
            )

            files = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    files.append({
                        'key': obj['Key'],
                        'size': obj['Size'],
                        'last_modified': obj['LastModified'],
                        'etag': obj['ETag']
                    })

            return files

        except ClientError as e:
            self.logger.error(f"Error listing files: {e}")
            return []

    def upload_multiple_files(self, files_data):
        """
        Sube múltiples archivos a S3.

        Args:
            files_data: Lista de diccionarios con 'file_obj' y 'key'

        Returns:
            dict: Resultado de las operaciones
        """
        results = []

        for file_data in files_data:
            result = self.upload_file(
                file_data['file_obj'],
                file_data['key'],
                file_data.get('bucket_name')
            )
            results.append(result)

        successful = sum(1 for r in results if r['success'])
        failed = len(results) - successful

        return {
            'total': len(results),
            'successful': successful,
            'failed': failed,
            'results': results
        }

    def validate_file(self, file_obj, max_size=None, allowed_extensions=None):
        """
        Valida un archivo antes de subirlo.

        Args:
            file_obj: Objeto de archivo a validar
            max_size: Tamaño máximo en bytes
            allowed_extensions: Lista de extensiones permitidas

        Returns:
            dict: Resultado de la validación
        """
        errors = []

        # Validar tamaño
        if max_size and file_obj.size > max_size:
            errors.append(f"File size ({file_obj.size}) exceeds maximum allowed size ({max_size})")

        # Validar extensión
        if allowed_extensions:
            file_extension = file_obj.name.split('.')[-1].lower()
            if file_extension not in allowed_extensions:
                errors.append(f"File extension '.{file_extension}' is not allowed")

        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
```

## Patrones de Servicios

### 1. Servicio Base
```python
class BaseService:
    """
    Clase base para todos los servicios.
    """

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def handle_error(self, error, context=None):
        """
        Manejo centralizado de errores.
        """
        self.logger.error(f"Error in {context}: {error}")
        return {
            'success': False,
            'error': str(error),
            'context': context
        }

    def validate_input(self, data, schema):
        """
        Validación de entrada usando un schema.
        """
        # Implementar validación
        pass
```

### 2. Servicio con Cache
```python
from django.core.cache import cache

class CachedService(BaseService):
    """
    Servicio con capacidades de cache.
    """

    def get_cached_data(self, key, fetch_function, timeout=300):
        """
        Obtiene datos del cache o los calcula si no existen.
        """
        data = cache.get(key)
        if data is None:
            data = fetch_function()
            cache.set(key, data, timeout)
        return data

    def invalidate_cache(self, pattern):
        """
        Invalida cache basado en un patrón.
        """
        # Implementar invalidación de cache
        pass
```

### 3. Servicio Asíncrono
```python
import asyncio
from asgiref.sync import sync_to_async

class AsyncService(BaseService):
    """
    Servicio con capacidades asíncronas.
    """

    async def process_async(self, data):
        """
        Procesa datos de forma asíncrona.
        """
        # Implementar procesamiento asíncrono
        pass

    def process_sync(self, data):
        """
        Wrapper síncrono para procesamiento asíncrono.
        """
        return asyncio.run(self.process_async(data))
```

## Casos de Uso Comunes

### 1. Carga de Archivos
```python
from api.services.s3_upload_service import S3UploadService

# Uso en vista
def upload_file_view(request):
    s3_service = S3UploadService()

    # Validar archivo
    validation = s3_service.validate_file(
        request.FILES['file'],
        max_size=5 * 1024 * 1024,  # 5MB
        allowed_extensions=['pdf', 'doc', 'docx']
    )

    if not validation['valid']:
        return Response({'errors': validation['errors']}, status=400)

    # Subir archivo
    result = s3_service.upload_file(
        request.FILES['file'],
        f"uploads/{request.user.id}/{request.FILES['file'].name}"
    )

    if result['success']:
        return Response({'url': result['url']}, status=201)
    else:
        return Response({'error': result['error']}, status=500)
```

### 2. Procesamiento por Lotes
```python
class BatchProcessingService(BaseService):
    def process_batch(self, items, batch_size=100):
        """
        Procesa elementos en lotes.
        """
        results = []

        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            batch_result = self.process_batch_items(batch)
            results.extend(batch_result)

        return results

    def process_batch_items(self, items):
        """
        Procesa un lote de elementos.
        """
        # Implementar procesamiento
        pass
```

### 3. Integración con APIs Externas
```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class ExternalAPIService(BaseService):
    def __init__(self):
        super().__init__()
        self.session = requests.Session()

        # Configurar reintentos
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def make_request(self, method, url, **kwargs):
        """
        Realiza una petición HTTP con manejo de errores.
        """
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return {
                'success': True,
                'data': response.json(),
                'status_code': response.status_code
            }
        except requests.exceptions.RequestException as e:
            return self.handle_error(e, f"{method} {url}")
```

## Integración con Celery

### Servicio para Tareas Asíncronas
```python
from celery import shared_task

class AsyncTaskService(BaseService):
    @shared_task
    def process_long_running_task(self, data):
        """
        Procesa una tarea de larga duración.
        """
        try:
            # Procesamiento pesado
            result = self.heavy_processing(data)
            return {
                'success': True,
                'result': result
            }
        except Exception as e:
            return self.handle_error(e, "Long running task")

    def heavy_processing(self, data):
        """
        Procesamiento pesado que toma tiempo.
        """
        # Implementar lógica pesada
        pass
```

## Testing

### Test de Servicios
```python
from django.test import TestCase
from unittest.mock import patch, MagicMock

class S3UploadServiceTest(TestCase):
    def setUp(self):
        self.service = S3UploadService()

    @patch('boto3.client')
    def test_upload_file_success(self, mock_boto_client):
        # Configurar mock
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3

        # Ejecutar
        result = self.service.upload_file(
            file_obj=MagicMock(),
            key='test-key'
        )

        # Verificar
        self.assertTrue(result['success'])
        self.assertIn('url', result)

    @patch('boto3.client')
    def test_upload_file_error(self, mock_boto_client):
        # Configurar mock para error
        mock_s3 = MagicMock()
        mock_s3.upload_fileobj.side_effect = ClientError(
            error_response={'Error': {'Code': 'NoSuchBucket'}},
            operation_name='upload_fileobj'
        )
        mock_boto_client.return_value = mock_s3

        # Ejecutar
        result = self.service.upload_file(
            file_obj=MagicMock(),
            key='test-key'
        )

        # Verificar
        self.assertFalse(result['success'])
        self.assertIn('error', result)
```

## Configuración

### Variables de Entorno
```bash
# AWS S3
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_STORAGE_BUCKET_NAME=your_bucket_name
AWS_S3_REGION_NAME=us-east-1

# Cache
REDIS_URL=redis://localhost:6379/0

# APIs Externas
EXTERNAL_API_KEY=your_api_key
EXTERNAL_API_URL=https://api.example.com
```

### Settings Django
```python
# settings.py
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME', 'us-east-1')

# Cache
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

## Mejores Prácticas

1. **Separación de Responsabilidades**: Cada servicio debe tener una responsabilidad específica
2. **Manejo de Errores**: Siempre manejar y registrar errores apropiadamente
3. **Logging**: Implementar logging detallado para debugging
4. **Validación**: Validar entrada antes del procesamiento
5. **Testing**: Escribir tests unitarios con mocks
6. **Documentación**: Documentar métodos y parámetros claramente

## Monitoreo y Métricas

### Métricas de Servicio
```python
import time
from functools import wraps

def monitor_performance(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            # Registrar métrica de éxito
            return result
        except Exception as e:
            # Registrar métrica de error
            raise
        finally:
            duration = time.time() - start_time
            # Registrar métrica de duración
    return wrapper
```

### Logging Estructurado
```python
import structlog

logger = structlog.get_logger()

class MonitoredService(BaseService):
    def process_data(self, data):
        logger.info(
            "Processing data",
            service=self.__class__.__name__,
            data_size=len(data),
            user_id=getattr(data, 'user_id', None)
        )
        # Procesar datos
```

## Extensibilidad

Para agregar nuevos servicios:

1. Heredar de `BaseService`
2. Implementar métodos específicos
3. Agregar validaciones apropiadas
4. Implementar manejo de errores
5. Escribir tests unitarios
6. Documentar el servicio

```python
class NewService(BaseService):
    """
    Descripción del nuevo servicio.
    """

    def __init__(self):
        super().__init__()
        # Inicialización específica

    def process(self, data):
        """
        Procesa los datos.
        """
        # Implementar lógica específica
        pass
```
