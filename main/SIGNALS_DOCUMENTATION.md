# Sistema Genérico de Signals - Documentación

## 📍 Ubicación

El sistema de signals está centralizado en `/main/signals.py` y es accesible desde cualquier app del proyecto.

## 🚀 Cómo usar desde cualquier app

### Opción 1: Usando el decorator (Recomendado)

```python
# En cualquier archivo signals.py de tu app
from main.signals import track_model_changes
from .models import TuModelo

@track_model_changes(TuModelo)
def handle_tu_modelo_changes(sender, instance, created, updated_fields, change_type, **kwargs):
    if created:
        print(f"✅ Nuevo {sender._meta.verbose_name} creado: {instance}")
    else:
        print(f"🔄 {sender._meta.verbose_name} actualizado: {instance}")
        for field_info in updated_fields:
            print(f"  - {field_info['field']}: '{field_info['old_value']}' → '{field_info['new_value']}'")
```

### Opción 2: Para múltiples modelos

```python
from main.signals import track_model_changes
from .models import Modelo1, Modelo2, Modelo3

@track_model_changes(Modelo1, Modelo2, Modelo3)
def handle_multiple_models(sender, instance, created, updated_fields, change_type, **kwargs):
    model_name = sender._meta.verbose_name
    if created:
        print(f"🆕 {model_name} creado: {instance}")
    else:
        print(f"📝 {model_name} actualizado: {instance}")
```

### Opción 3: Usando la función helper

```python
from main.signals import create_model_handler
from .models import TuModelo

def my_handler(sender, instance, created, updated_fields, change_type, **kwargs):
    # Tu lógica aquí
    pass

# Conectar el handler
create_model_handler([TuModelo], my_handler)
```

## 🔧 Configuración por app

### 1. Crear archivo signals.py en tu app

```python
# tu_app/signals.py
from main.signals import track_model_changes
from .models import TuModelo
import logging

logger = logging.getLogger(__name__)

@track_model_changes(TuModelo)
def handle_tu_modelo_changes(sender, instance, created, updated_fields, change_type, **kwargs):
    # Tu lógica específica aquí
    pass
```

### 2. Registrar en apps.py

```python
# tu_app/apps.py
from django.apps import AppConfig

class TuAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tu_app'

    def ready(self):
        # Importar signals para que se registren
        import tu_app.signals
```

## 📊 Argumentos disponibles en los handlers

- **`sender`**: La clase del modelo que cambió
- **`instance`**: La instancia del objeto que cambió
- **`created`**: `True` si fue creado, `False` si fue actualizado
- **`updated_fields`**: Lista de diccionarios con información de campos cambiados
- **`change_type`**: `'created'` o `'updated'`

## 📋 Estructura de `updated_fields`

```python
[
    {
        'field': 'nombre_del_campo',
        'old_value': valor_anterior,
        'new_value': valor_nuevo,
        'field_verbose_name': 'Nombre Legible del Campo'
    }
]
```

## 🎯 Ejemplos por app

### Agents App
```python
# agents/signals.py
from main.signals import track_model_changes
from .models import AgentModel

@track_model_changes(AgentModel)
def handle_agent_changes(sender, instance, created, updated_fields, change_type, **kwargs):
    if created:
        print(f"🤖 Nuevo agente: {instance.name}")
    else:
        for field_info in updated_fields:
            if field_info['field'] == 'instructions':
                print(f"📝 Instrucciones del agente {instance.name} han cambiado")
```

### Knowledge App
```python
# knowledge/signals.py
from main.signals import track_model_changes
from .models import KnowledgeModel

@track_model_changes(KnowledgeModel)
def handle_knowledge_changes(sender, instance, created, updated_fields, change_type, **kwargs):
    if created:
        print(f"📚 Nueva base de conocimiento: {instance}")
    else:
        print(f"📝 Base de conocimiento actualizada: {instance}")
```

### Tenants App
```python
# tenants/signals.py
from main.signals import track_model_changes
from .models import TenantModel

@track_model_changes(TenantModel)
def handle_tenant_changes(sender, instance, created, updated_fields, change_type, **kwargs):
    if created:
        print(f"🏢 Nuevo tenant: {instance}")
        # Configurar tenant inicial
    else:
        print(f"🔄 Tenant actualizado: {instance}")
        # Invalidar cache del tenant
```

## ⚡ Auto-registro

El sistema se registra automáticamente cuando Django inicia porque:

1. `main/__init__.py` importa `main.signals`
2. Los decoradores `@receiver` se registran automáticamente
3. Cada app importa sus signals en `apps.py` → `ready()`

## 🎨 Casos de uso comunes

### Logging de auditoría
```python
@track_model_changes(TuModelo)
def audit_logger(sender, instance, created, updated_fields, change_type, **kwargs):
    # Guardar en tabla de auditoría
    pass
```

### Invalidación de cache
```python
@track_model_changes(TuModelo)
def invalidate_cache(sender, instance, created, updated_fields, change_type, **kwargs):
    # Invalidar cache relacionado
    pass
```

### Notificaciones
```python
@track_model_changes(TuModelo)
def send_notifications(sender, instance, created, updated_fields, change_type, **kwargs):
    # Enviar notificaciones por email/slack
    pass
```

### Validaciones post-guardado
```python
@track_model_changes(TuModelo)
def post_save_validation(sender, instance, created, updated_fields, change_type, **kwargs):
    # Validaciones adicionales
    pass
```

## 🔍 Debug y troubleshooting

Para verificar que los signals están funcionando, puedes usar logging:

```python
import logging
logger = logging.getLogger(__name__)

@track_model_changes(TuModelo)
def debug_handler(sender, instance, created, updated_fields, change_type, **kwargs):
    logger.info(f"Signal recibido: {sender._meta.verbose_name} - {change_type}")
    if updated_fields:
        logger.info(f"Campos modificados: {[f['field'] for f in updated_fields]}")
```
