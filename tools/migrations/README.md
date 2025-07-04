# Tools - Migrations

## Descripción

Este directorio contiene las migraciones de base de datos para el módulo de herramientas, que gestiona los cambios en el esquema de la base de datos para funcionalidades de herramientas externas, llamadas a APIs y configuraciones de servicios.

## Estructura de Migraciones

```
migrations/
├── __init__.py
├── 0001_initial.py                                    # Migración inicial
└── 0002_rename_intructions_apicallmodel_instructions.py  # Corrección de nombre de campo
```

## Evolución del Modelo

### 0001_initial.py
- **Propósito**: Migración inicial del módulo de herramientas
- **Cambios**: Creación de la estructura base para gestión de herramientas
- **Modelos**: ApiCallModel y otros modelos base
- **Funcionalidades iniciales**:
  - Gestión de llamadas a APIs externas
  - Configuración de herramientas
  - Metadatos de integración
  - Campos de configuración básicos

### 0002_rename_intructions_apicallmodel_instructions.py
- **Propósito**: Corrección tipográfica en el nombre del campo
- **Cambios**: Renombrado de `intructions` a `instructions`
- **Razón**: Corrección ortográfica estándar
- **Impacto**: Mejora en la legibilidad y estándares del código

## Arquitectura de Modelos

### ApiCallModel
```python
class ApiCallModel(models.Model):
    name = models.CharField(max_length=255)
    endpoint = models.URLField()
    method = models.CharField(max_length=10, choices=HTTP_METHODS)
    headers = models.JSONField(default=dict)
    instructions = models.TextField()  # Corregido de 'intructions'
    parameters = models.JSONField(default=dict)
    authentication = models.JSONField(default=dict)
    timeout = models.IntegerField(default=30)
    retry_attempts = models.IntegerField(default=3)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Llamada a API"
        verbose_name_plural = "Llamadas a API"
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['endpoint']),
        ]
```

### ToolConfigModel
```python
class ToolConfigModel(models.Model):
    tool_name = models.CharField(max_length=255, unique=True)
    configuration = models.JSONField()
    is_active = models.BooleanField(default=True)
    version = models.CharField(max_length=50)
    description = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Configuración de Herramienta"
        verbose_name_plural = "Configuraciones de Herramientas"
```

## Mejores Prácticas

### Gestión de Migraciones
```python
# Aplicar migraciones
python manage.py migrate tools

# Verificar estado de migraciones
python manage.py showmigrations tools

# Crear nueva migración
python manage.py makemigrations tools
```

### Validación de Datos
```python
# Validar configuraciones de herramientas
python manage.py validate_tool_configs

# Verificar conectividad de APIs
python manage.py test_api_connections
```

## Gestión de Configuraciones

### Migración de Configuraciones
```python
# migration_script.py
from django.db import migrations
import json

def migrate_tool_configurations(apps, schema_editor):
    """Migrar configuraciones de herramientas existentes"""
    ApiCallModel = apps.get_model('tools', 'ApiCallModel')

    # Actualizar configuraciones existentes
    for api_call in ApiCallModel.objects.all():
        if hasattr(api_call, 'intructions'):  # Campo con typo
            # Migrar datos del campo con typo al campo correcto
            api_call.instructions = api_call.intructions
            api_call.save()

def validate_api_configurations(apps, schema_editor):
    """Validar configuraciones de APIs"""
    ApiCallModel = apps.get_model('tools', 'ApiCallModel')

    for api_call in ApiCallModel.objects.all():
        # Validar que las instrucciones no estén vacías
        if not api_call.instructions or api_call.instructions.strip() == '':
            raise ValueError(f"API {api_call.name} tiene instrucciones vacías")

        # Validar formato de headers
        if not isinstance(api_call.headers, dict):
            raise ValueError(f"API {api_call.name} tiene headers en formato inválido")

class Migration(migrations.Migration):
    dependencies = [
        ('tools', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(migrate_tool_configurations),
        migrations.RunPython(validate_api_configurations),
    ]
```

## Testing de Migraciones

### Pruebas de Migración
```python
# tests/test_migrations.py
from django.test import TestCase
from django.db import connection
from django.core.management import call_command

class ToolsMigrationTestCase(TestCase):
    def test_instructions_field_rename(self):
        """Test corrección del campo instructions"""
        from tools.models import ApiCallModel

        # Verificar que el campo correcto existe
        self.assertTrue(hasattr(ApiCallModel, 'instructions'))

        # Crear API call de prueba
        api_call = ApiCallModel.objects.create(
            name="Test API",
            endpoint="https://api.example.com/test",
            method="GET",
            instructions="Test instructions"
        )

        # Verificar que se guardó correctamente
        self.assertEqual(api_call.instructions, "Test instructions")

    def test_api_call_model_validation(self):
        """Test validación del modelo ApiCallModel"""
        from tools.models import ApiCallModel

        # Crear API call con datos válidos
        api_call = ApiCallModel.objects.create(
            name="Valid API",
            endpoint="https://api.example.com/valid",
            method="POST",
            instructions="Valid instructions",
            headers={"Content-Type": "application/json"},
            parameters={"param1": "value1"},
            authentication={"type": "bearer", "token": "test-token"}
        )

        # Verificar campos requeridos
        self.assertEqual(api_call.name, "Valid API")
        self.assertEqual(api_call.method, "POST")
        self.assertIsInstance(api_call.headers, dict)
        self.assertIsInstance(api_call.parameters, dict)
        self.assertIsInstance(api_call.authentication, dict)
```

### Validación de Integridad
```python
def test_data_integrity_after_migration(self):
    """Verificar integridad de datos después de migración"""
    from tools.models import ApiCallModel, ToolConfigModel

    # Crear configuración de herramienta
    tool_config = ToolConfigModel.objects.create(
        tool_name="test_tool",
        configuration={"setting1": "value1", "setting2": "value2"},
        version="1.0.0",
        description="Test tool configuration"
    )

    # Crear API call
    api_call = ApiCallModel.objects.create(
        name="Test API",
        endpoint="https://api.example.com/test",
        method="GET",
        instructions="Test instructions for API call",
        timeout=60,
        retry_attempts=5
    )

    # Verificar que se guardaron correctamente
    self.assertEqual(tool_config.tool_name, "test_tool")
    self.assertEqual(api_call.timeout, 60)
    self.assertEqual(api_call.retry_attempts, 5)
```

## Configuración de Herramientas

### Settings para Herramientas
```python
# settings/base.py
TOOLS_SETTINGS = {
    'DEFAULT_TIMEOUT': 30,
    'MAX_RETRY_ATTEMPTS': 3,
    'RATE_LIMIT': {
        'calls_per_minute': 60,
        'calls_per_hour': 1000,
    },
    'SUPPORTED_METHODS': ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'],
    'AUTHENTICATION_TYPES': ['bearer', 'basic', 'api_key', 'oauth2'],
    'VALIDATION_ENABLED': True,
}
```

### Configuración de Seguridad
```python
# Configuración de autenticación segura
TOOL_AUTHENTICATION = {
    'ENCRYPT_TOKENS': True,
    'TOKEN_EXPIRY': 3600,  # 1 hora
    'AUDIT_LOGGING': True,
    'IP_WHITELIST': ['127.0.0.1', '10.0.0.0/8'],
}
```

## Comandos de Gestión

### Comandos de Migración
```python
# management/commands/migrate_tool_configs.py
from django.core.management.base import BaseCommand
from tools.services import ToolMigrationService

class Command(BaseCommand):
    help = 'Migrar configuraciones de herramientas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--tool-name',
            type=str,
            help='Nombre de la herramienta específica a migrar'
        )
        parser.add_argument(
            '--validate-only',
            action='store_true',
            help='Solo validar configuraciones sin migrar'
        )

    def handle(self, *args, **options):
        service = ToolMigrationService()

        if options['validate_only']:
            issues = service.validate_configurations()
            if issues:
                self.stdout.write(
                    self.style.ERROR(f'Encontrados {len(issues)} problemas')
                )
                for issue in issues:
                    self.stdout.write(f'  - {issue}')
            else:
                self.stdout.write(
                    self.style.SUCCESS('Configuraciones validadas correctamente')
                )
        else:
            if options['tool_name']:
                result = service.migrate_tool_config(options['tool_name'])
            else:
                result = service.migrate_all_configs()

            self.stdout.write(
                self.style.SUCCESS(
                    f'Migradas {result["migrated"]} configuraciones'
                )
            )
```

### Validación de APIs
```python
# management/commands/validate_api_calls.py
class Command(BaseCommand):
    help = 'Validar configuraciones de llamadas a API'

    def add_arguments(self, parser):
        parser.add_argument(
            '--test-connectivity',
            action='store_true',
            help='Probar conectividad a las APIs'
        )

    def handle(self, *args, **options):
        from tools.validators import ApiCallValidator

        validator = ApiCallValidator()

        if options['test_connectivity']:
            results = validator.test_connectivity()
            for api_name, result in results.items():
                if result['success']:
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ {api_name}: Conectividad OK')
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(f'✗ {api_name}: {result["error"]}')
                    )
        else:
            issues = validator.validate_configurations()
            if issues:
                self.stdout.write(
                    self.style.ERROR(f'Encontrados {len(issues)} problemas')
                )
                for issue in issues:
                    self.stdout.write(f'  - {issue}')
            else:
                self.stdout.write(
                    self.style.SUCCESS('Configuraciones de API validadas correctamente')
                )
```

## Monitoreo y Mantenimiento

### Métricas de Uso
```python
# Comando para generar métricas de uso
python manage.py tool_usage_metrics --period=daily

# Análisis de performance de APIs
python manage.py analyze_api_performance --days=7
```

### Limpieza de Datos
```python
# Limpiar configuraciones obsoletas
python manage.py cleanup_tool_configs --inactive-days=90

# Archivar llamadas API antiguas
python manage.py archive_old_api_calls --days=365
```

## Seguridad y Auditoría

### Protección de Credenciales
```python
# Comando para encriptar credenciales
python manage.py encrypt_tool_credentials

# Rotación de tokens
python manage.py rotate_api_tokens --tool-name=external_api
```

### Logs de Auditoría
```python
# Configuración de logging
LOGGING = {
    'loggers': {
        'tools.api_calls': {
            'level': 'INFO',
            'handlers': ['file', 'console'],
            'propagate': False,
        },
        'tools.security': {
            'level': 'WARNING',
            'handlers': ['security_file'],
            'propagate': False,
        },
    },
}
```

## Troubleshooting

### Problemas Comunes
1. **Timeouts de API**: Ajustar configuración de timeout
2. **Credenciales inválidas**: Verificar autenticación
3. **Rate limiting**: Implementar backoff exponencial
4. **Formato de datos**: Validar serialización JSON

### Comandos de Diagnóstico
```bash
# Verificar configuración de herramientas
python manage.py check tools

# Probar conectividad específica
python manage.py test_api_connection --api-name=external_service

# Análisis de errores
python manage.py analyze_tool_errors --last-days=7
```

## Integración con Otros Módulos

### Agentes
- Los agentes pueden usar herramientas configuradas
- Integración con sistema de instrucciones
- Validación de permisos por agente

### Análisis
- Métricas de uso de herramientas
- Análisis de performance
- Logs de actividad

### Tenants
- Configuraciones específicas por tenant
- Aislamiento de herramientas
- Facturación por uso

## Roadmap

### Próximas Funcionalidades
- Herramientas de IA/ML integradas
- Marketplace de herramientas
- Configuración visual de workflows
- Monitoreo en tiempo real

### Mejoras Planificadas
- Optimización de performance
- Mejor gestión de errores
- Interfaz de administración mejorada
- Documentación automática de APIs

## Extensibilidad

### Nuevas Herramientas
```python
# Ejemplo de nueva herramienta
class CustomToolModel(models.Model):
    name = models.CharField(max_length=255)
    configuration = models.JSONField()
    api_call = models.ForeignKey(ApiCallModel, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Herramienta Personalizada"
        verbose_name_plural = "Herramientas Personalizadas"
```

### Plugins
- Sistema de plugins para herramientas externas
- Interfaz estándar para nuevas integraciones
- Validación automática de plugins
