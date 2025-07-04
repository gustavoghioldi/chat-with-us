# Management Commands - Comandos de Gestión

## Descripción General
Este directorio contiene comandos de gestión personalizados de Django que proporcionan funcionalidades específicas para el mantenimiento, inicialización y administración del sistema.

## Estructura de Comandos

### Comandos de Inicialización
Comandos para configurar el sistema inicial:

#### `init_system.py`
Inicializa el sistema con datos básicos:
- Crea usuario administrador por defecto
- Configura tenants iniciales
- Crea agentes básicos de demostración
- Configura herramientas por defecto

```bash
python manage.py init_system
python manage.py init_system --skip-admin  # Omite creación de admin
python manage.py init_system --tenant=demo  # Solo para tenant específico
```

#### `setup_demo_data.py`
Configura datos de demostración:
- Crea agentes de ejemplo
- Configura conocimientos de muestra
- Genera chats de prueba
- Crea documentos de ejemplo

```bash
python manage.py setup_demo_data
python manage.py setup_demo_data --tenant=demo
```

### Comandos de Mantenimiento

#### `cleanup_old_data.py`
Limpia datos antiguos del sistema:
- Elimina chats antiguos
- Limpia logs caducados
- Elimina archivos temporales
- Purga datos de análisis antiguos

```bash
python manage.py cleanup_old_data
python manage.py cleanup_old_data --days=30
python manage.py cleanup_old_data --type=chats
python manage.py cleanup_old_data --tenant=specific_tenant
```

#### `backup_data.py`
Realiza respaldos de datos:
- Respaldo completo de base de datos
- Respaldo de archivos multimedia
- Respaldo de configuraciones
- Respaldo incremental

```bash
python manage.py backup_data
python manage.py backup_data --tenant=all
python manage.py backup_data --type=database
python manage.py backup_data --output=/path/to/backup
```

#### `optimize_database.py`
Optimiza la base de datos:
- Actualiza estadísticas de tablas
- Reorganiza índices
- Limpia transacciones huérfanas
- Optimiza consultas lentas

```bash
python manage.py optimize_database
python manage.py optimize_database --analyze
python manage.py optimize_database --reindex
```

### Comandos de Importación/Exportación

#### `import_knowledge.py`
Importa conocimientos desde archivos:
- Importa desde CSV, JSON, XML
- Procesamiento en lote
- Validación de datos
- Generación de reportes

```bash
python manage.py import_knowledge --file=data.csv
python manage.py import_knowledge --directory=/path/to/files
python manage.py import_knowledge --tenant=specific_tenant
```

#### `export_data.py`
Exporta datos del sistema:
- Exporta chats, agentes, conocimientos
- Múltiples formatos (CSV, JSON, XML)
- Filtros por fecha y tenant
- Exportación incremental

```bash
python manage.py export_data --type=chats
python manage.py export_data --format=json
python manage.py export_data --tenant=demo --output=/path/to/export
```

### Comandos de Análisis

#### `generate_reports.py`
Genera reportes del sistema:
- Reportes de uso
- Análisis de rendimiento
- Estadísticas de agentes
- Métricas de satisfacción

```bash
python manage.py generate_reports
python manage.py generate_reports --type=usage
python manage.py generate_reports --period=monthly
python manage.py generate_reports --tenant=all
```

#### `analyze_sentiment.py`
Analiza sentimientos de chats:
- Análisis retroactivo
- Análisis por período
- Análisis por agente
- Generación de métricas

```bash
python manage.py analyze_sentiment
python manage.py analyze_sentiment --days=7
python manage.py analyze_sentiment --agent=specific_agent
```

### Comandos de Migración

#### `migrate_knowledge_base.py`
Migra bases de conocimiento:
- Migración entre versiones
- Actualización de formatos
- Corrección de datos
- Validación post-migración

```bash
python manage.py migrate_knowledge_base
python manage.py migrate_knowledge_base --version=2.0
python manage.py migrate_knowledge_base --validate-only
```

#### `migrate_tenant_data.py`
Migra datos entre tenants:
- Transferencia de agentes
- Migración de conocimientos
- Copia de configuraciones
- Validación de integridad

```bash
python manage.py migrate_tenant_data --from=old_tenant --to=new_tenant
python manage.py migrate_tenant_data --type=agents
```

### Comandos de Monitoreo

#### `health_check.py`
Verifica estado del sistema:
- Estado de servicios
- Conectividad de base de datos
- Estado de Redis/Celery
- Verificación de APIs externas

```bash
python manage.py health_check
python manage.py health_check --service=database
python manage.py health_check --verbose
```

#### `monitor_performance.py`
Monitorea rendimiento:
- Métricas de respuesta
- Uso de recursos
- Detección de cuellos de botella
- Alertas automáticas

```bash
python manage.py monitor_performance
python manage.py monitor_performance --duration=60
python manage.py monitor_performance --alert-threshold=90
```

### Comandos de Desarrollo

#### `create_test_data.py`
Crea datos de prueba:
- Datos realistas para testing
- Volumen configurable
- Diferentes escenarios
- Datos de stress testing

```bash
python manage.py create_test_data
python manage.py create_test_data --volume=large
python manage.py create_test_data --scenario=high_load
```

#### `validate_system.py`
Valida integridad del sistema:
- Validación de modelos
- Verificación de relaciones
- Validación de configuraciones
- Detección de inconsistencias

```bash
python manage.py validate_system
python manage.py validate_system --fix-issues
python manage.py validate_system --module=agents
```

## Estructura de un Comando

### Plantilla Base
```python
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

class Command(BaseCommand):
    help = 'Descripción del comando'

    def add_arguments(self, parser):
        parser.add_argument(
            '--tenant',
            type=str,
            help='Especifica el tenant',
            default=None
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Ejecuta sin hacer cambios reales',
        )

    def handle(self, *args, **options):
        try:
            tenant = options['tenant']
            dry_run = options['dry_run']

            if dry_run:
                self.stdout.write(
                    self.style.WARNING('Ejecutando en modo dry-run')
                )

            # Lógica del comando aquí

            self.stdout.write(
                self.style.SUCCESS('Comando ejecutado exitosamente')
            )

        except Exception as e:
            raise CommandError(f'Error al ejecutar comando: {str(e)}')
```

### Mejores Prácticas

#### Validación de Entrada
```python
def validate_tenant(self, tenant_name):
    """Valida que el tenant existe"""
    if not TenantModel.objects.filter(name=tenant_name).exists():
        raise CommandError(f'Tenant {tenant_name} no existe')
```

#### Logging
```python
import logging
logger = logging.getLogger(__name__)

def handle(self, *args, **options):
    logger.info(f'Iniciando comando: {self.__class__.__name__}')
    # Lógica del comando
    logger.info('Comando completado exitosamente')
```

#### Progreso y Feedback
```python
def handle(self, *args, **options):
    items = self.get_items_to_process()
    total = len(items)

    for i, item in enumerate(items):
        self.process_item(item)
        if i % 100 == 0:
            self.stdout.write(f'Procesados {i}/{total} items')

    self.stdout.write(
        self.style.SUCCESS(f'Procesados {total} items exitosamente')
    )
```

## Configuración de Comandos

### Variables de Entorno
```bash
# Para comandos de respaldo
BACKUP_DIRECTORY=/path/to/backups
BACKUP_RETENTION_DAYS=30

# Para comandos de limpieza
CLEANUP_BATCH_SIZE=1000
CLEANUP_CONCURRENT_JOBS=4

# Para comandos de importación
IMPORT_BATCH_SIZE=500
IMPORT_VALIDATION_LEVEL=strict
```

### Configuración en settings.py
```python
# Configuración para comandos de gestión
MANAGEMENT_COMMANDS = {
    'backup': {
        'retention_days': 30,
        'compression': True,
        'encryption': True,
    },
    'cleanup': {
        'batch_size': 1000,
        'concurrent_jobs': 4,
    },
    'import': {
        'batch_size': 500,
        'validation_level': 'strict',
    }
}
```

## Automatización

### Cron Jobs
```bash
# Respaldo diario
0 2 * * * /path/to/venv/bin/python /path/to/manage.py backup_data

# Limpieza semanal
0 3 * * 0 /path/to/venv/bin/python /path/to/manage.py cleanup_old_data

# Reportes mensuales
0 4 1 * * /path/to/venv/bin/python /path/to/manage.py generate_reports
```

### Celery Tasks
```python
# tasks.py
from celery import shared_task
from django.core.management import call_command

@shared_task
def run_cleanup_task():
    call_command('cleanup_old_data', days=30)

@shared_task
def run_backup_task():
    call_command('backup_data', tenant='all')
```

## Monitoreo y Alertas

### Logging de Comandos
- Logs de ejecución
- Métricas de rendimiento
- Alertas por errores
- Reportes de estado

### Notificaciones
- Email para comandos críticos
- Slack/Teams para alertas
- Dashboard de estado
- Reportes automatizados
