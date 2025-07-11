# Módulo de Quotas

## Descripción General

El módulo **quota** gestiona el control y registro del uso de tokens por tenant en el sistema. Permite definir planes de tokens, llevar el control de consumo, bloquear tenants que exceden su cuota y registrar todas las transacciones relacionadas con el uso de tokens. Es fundamental para implementar límites de uso, monetización y control de recursos en arquitecturas multi-tenant.

---

## Estructura del Módulo

- **models/**  
  - `tenant_quota_model.py`: Modelo principal que almacena la cuota, tokens usados y estado de bloqueo por tenant.
  - `token_plan_model.py`: Define los planes de tokens disponibles (límite mensual, descripción, etc).
  - `token_ledger_model.py`: Registro histórico de todas las transacciones de tokens (consumo, recarga, reset, etc).

- **services/**  
  - `quota_service.py`: Lógica centralizada para validar, consumir y registrar el uso de tokens, así como bloquear/desbloquear tenants.

- **admins/**  
  - Archivos para la administración de los modelos en el panel de Django Admin.

- **enums/**  
  - Enumeraciones para tipos de transacción, direcciones y mensajes de sistema.

- **signals/**  
  - `post_save_tenant_quota_signal.py`: Signal para desbloquear automáticamente un tenant cuando se realiza una recarga o reset.

- **migrations/**  
  - Migraciones de base de datos para los modelos de quota.

- **docs/**  
  - Documentación y diagramas de flujo del módulo.

---

## Principales Funcionalidades

1. **Definición de Planes de Tokens**
   - Permite crear y administrar diferentes planes de tokens para los tenants.

2. **Control de Consumo**
   - Lleva el registro de tokens usados por cada tenant y bloquea automáticamente cuando se excede el límite.

3. **Registro de Transacciones**
   - Cada consumo, recarga o reset de tokens queda registrado en el ledger para trazabilidad y auditoría.

4. **Bloqueo y Desbloqueo Automático**
   - Si un tenant excede su cuota, se bloquean futuros requests.
   - Al recargar o resetear tokens, el tenant se desbloquea automáticamente mediante signals.

5. **Integración con Otros Módulos**
   - El servicio de quota puede ser llamado desde cualquier app para validar y registrar el consumo de tokens antes de ejecutar operaciones costosas.

---

## Flujo de Trabajo

1. Un usuario realiza una acción que consume tokens (por ejemplo, enviar un prompt a un agente).
2. El servicio `QuotaService` valida si el tenant tiene tokens disponibles.
3. Si el tenant está bloqueado, se retorna un mensaje de sistema y no se procesa la acción.
4. Si hay tokens disponibles, se ejecuta la acción, se calcula el consumo real y se actualiza el uso de tokens.
5. Se registra la transacción en el ledger.
6. Si el consumo excede el límite, el tenant se bloquea para futuros requests.
7. Una recarga o reset de tokens desbloquea automáticamente al tenant.

---

## Ejemplo de Uso

```python
from quota.services.quota_service import QuotaService

text, session_id = QuotaService.process_agent_request(
    agent=agent_service,
    tenant=request.tenant,
    prompt=message,
    session_id=session_id
)