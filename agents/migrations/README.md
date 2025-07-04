# Agents - Migrations

## Descripción

Este directorio contiene las migraciones de base de datos para el módulo de agentes, que gestionan los cambios en el esquema de la base de datos de manera versionada y controlada.

## Estructura de Migraciones

```
migrations/
├── __init__.py
├── 0001_initial.py                           # Migración inicial
├── 0002_agentmodel_knoledge_text_models.py   # Campos de conocimiento y texto
├── 0003_agentmodel_agent_model_id_agentmodel_tenant.py  # ID del modelo y tenant
├── 0004_agentmodel_description.py           # Campo descripción
├── 0005_agentmodel_api_call_models.py       # Modelos de llamadas API
├── 0006_agentmodel_max_tokens_agentmodel_temperature_and_more.py  # Tokens y temperatura
└── 0007_agentmodel_analize_sentiment.py     # Análisis de sentimientos
```

## Evolución del Modelo

### 0001_initial.py
- **Propósito**: Migración inicial del modelo AgentModel
- **Cambios**: Creación de la estructura base del agente
- **Modelos**: AgentModel base

### 0002_agentmodel_knoledge_text_models.py
- **Propósito**: Incorporación de capacidades de conocimiento
- **Cambios**: Adición de campos para gestión de conocimiento y modelos de texto
- **Campos agregados**:
  - `knowledge_text_models`: Relación con modelos de texto
  - Campos relacionados con procesamiento de conocimiento

### 0003_agentmodel_agent_model_id_agentmodel_tenant.py
- **Propósito**: Implementación de multi-tenancy y identificación de modelos
- **Cambios**:
  - Adición de `agent_model_id` para identificación única
  - Implementación de `tenant` para aislamiento de datos
- **Impacto**: Permite múltiples clientes en la misma instancia

### 0004_agentmodel_description.py
- **Propósito**: Mejora de metadatos del agente
- **Cambios**: Campo `description` para documentación de agentes
- **Beneficios**: Mejor documentación y gestión de agentes

### 0005_agentmodel_api_call_models.py
- **Propósito**: Integración con APIs externas
- **Cambios**: Modelos para gestión de llamadas API
- **Funcionalidades**: Configuración de endpoints, autenticación, parámetros

### 0006_agentmodel_max_tokens_agentmodel_temperature_and_more.py
- **Propósito**: Configuración avanzada de modelos LLM
- **Cambios**:
  - `max_tokens`: Control de longitud de respuestas
  - `temperature`: Control de creatividad
  - Otros parámetros de configuración de LLM
- **Impacto**: Mayor control sobre el comportamiento del modelo

### 0007_agentmodel_analize_sentiment.py
- **Propósito**: Capacidades de análisis de sentimientos
- **Cambios**: Campo `analyze_sentiment` para activar análisis
- **Integración**: Conecta con el módulo de análisis

## Mejores Prácticas

### Gestión de Migraciones
```python
# Aplicar migraciones
python manage.py migrate agents

# Verificar estado de migraciones
python manage.py showmigrations agents

# Crear nueva migración
python manage.py makemigrations agents
```

### Rollback y Reversión
```python
# Rollback a migración específica
python manage.py migrate agents 0006

# Rollback completo
python manage.py migrate agents zero
```

### Validación de Migraciones
```python
# Verificar migraciones sin aplicar
python manage.py migrate --plan

# Verificar SQL generado
python manage.py sqlmigrate agents 0007
```

## Consideraciones de Datos

### Migración de Datos Sensibles
- **Agentes existentes**: Validar compatibilidad con nuevos campos
- **Configuraciones**: Preservar configuraciones personalizadas
- **Relaciones**: Mantener integridad referencial

### Backup y Recuperación
```python
# Backup antes de migración
python manage.py dumpdata agents > agents_backup.json

# Restaurar si es necesario
python manage.py loaddata agents_backup.json
```

## Testing de Migraciones

### Pruebas de Migración
```python
# tests/test_migrations.py
from django.test import TestCase
from django.db import connection
from django.core.management import call_command

class MigrationTestCase(TestCase):
    def test_migration_forward_backward(self):
        """Test migración y rollback"""
        # Aplicar migración
        call_command('migrate', 'agents', '0007')

        # Verificar esquema
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM information_schema.columns WHERE table_name = 'agents_agentmodel'")
            columns = [row[3] for row in cursor.fetchall()]
            self.assertIn('analize_sentiment', columns)
```

### Validación de Integridad
```python
def test_data_integrity_after_migration(self):
    """Verificar integridad de datos después de migración"""
    # Crear agente de prueba
    agent = AgentModel.objects.create(
        name="Test Agent",
        description="Test Description",
        max_tokens=1000,
        temperature=0.7,
        analize_sentiment=True
    )

    # Verificar que se guardó correctamente
    self.assertEqual(agent.max_tokens, 1000)
    self.assertTrue(agent.analize_sentiment)
```

## Monitoreo y Mantenimiento

### Logs de Migración
```python
# Habilitar logs detallados
LOGGING = {
    'loggers': {
        'django.db.backends': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
    },
}
```

### Métricas de Performance
- **Tiempo de migración**: Monitorear duración de migraciones
- **Impacto en base de datos**: Verificar locks y performance
- **Rollback preparedness**: Tiempo de reversión si es necesario

## Documentación de Cambios

### Changelog
- **v0.1.0**: Migración inicial (0001)
- **v0.2.0**: Capacidades de conocimiento (0002)
- **v0.3.0**: Multi-tenancy (0003)
- **v0.4.0**: Descripción de agentes (0004)
- **v0.5.0**: APIs externas (0005)
- **v0.6.0**: Configuración LLM (0006)
- **v0.7.0**: Análisis de sentimientos (0007)

### Dependencias
- Módulo `analysis` para análisis de sentimientos
- Módulo `tenants` para gestión de multi-tenancy
- Módulo `knowledge` para gestión de conocimiento

## Troubleshooting

### Problemas Comunes
1. **Conflictos de migración**: Resolver con `--merge`
2. **Datos faltantes**: Verificar datos de prueba
3. **Constraints**: Validar integridad referencial
4. **Performance**: Optimizar migraciones largas

### Comandos de Diagnóstico
```bash
# Verificar consistencia
python manage.py check

# Validar migraciones
python manage.py migrate --check

# Verificar SQL
python manage.py sqlmigrate agents 0007
```
