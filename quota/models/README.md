# Modelos del Módulo Quota

Este módulo contiene los modelos principales para la gestión de cuotas y control de uso de tokens por tenant en el sistema.  
A continuación se explica, de forma sencilla y contextual, el propósito de cada modelo.

---

## 1. TokenPlanModel

**¿Qué representa?**  
Un plan de tokens es la “membresía” o “paquete” que define cuántos tokens puede consumir un tenant en un período (por ejemplo, por mes).

**¿Para qué sirve?**  
Permite ofrecer distintos niveles de servicio: por ejemplo, un plan básico con pocos tokens y un plan premium con muchos más.

**Campos principales:**
- `name`: Nombre del plan (ej: "Básico", "Premium").
- `total_amount`: Cantidad máxima de tokens permitidos en el ciclo.
- `description`: Descripción opcional del plan.

---

## 2. TenantQuotaModel

**¿Qué representa?**  
Es el “contador” de tokens usados por cada tenant y el vínculo entre el tenant y su plan de tokens.

**¿Para qué sirve?**  
Permite saber cuántos tokens ha consumido un tenant, si está bloqueado por exceder su cuota y cuándo fue el último reset de su contador.

**Campos principales:**
- `tenant`: El tenant (cliente o usuario) al que pertenece la cuota.
- `plan`: El plan de tokens asignado.
- `tokens_used`: Cuántos tokens lleva consumidos en el ciclo.
- `is_blocked`: Si el tenant está bloqueado por exceder su cuota.
- `last_reset`: Fecha del último reset de tokens.

---

## 3. TokenLedgerModel

**¿Qué representa?**  
Es el “historial” o “libro contable” de todas las transacciones de tokens de cada tenant.

**¿Para qué sirve?**  
Permite auditar, analizar y entender cómo y cuándo se consumieron, recargaron o resetearon los tokens.  
Cada vez que un tenant consume, recarga o se le resetean los tokens, se crea un registro aquí.

**Campos principales:**
- `tenant`: El tenant al que pertenece la transacción.
- `transaction_type`: Tipo de transacción (consumo, recarga, reset, etc.).
- `amount`: Cantidad de tokens involucrados en la transacción.
- `total_remaining`: Tokens restantes después de la transacción.
- `direction`: Si la transacción suma o resta tokens.
- `created_at`: Fecha y hora de la transacción.

---

## Resumen visual

- **TokenPlanModel**: Define los límites de cada plan.
- **TenantQuotaModel**: Lleva el control de uso y estado de cada tenant.
- **TokenLedgerModel**: Guarda el historial detallado de cada movimiento de tokens.

---

Estos modelos permiten implementar un sistema robusto de control de uso, límites y auditoría para cualquier plataforma multi-tenant que utilice recursos medidos por tokens.