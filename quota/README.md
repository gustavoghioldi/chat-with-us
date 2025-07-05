# Módulo de Quotas

## Descripción General
La app `quota` administra y controla el uso de recursos por tenant, principalmente el consumo de tokens en interacciones con modelos de IA. Permite definir límites (quotas) mensuales o diarios registrar el uso real y aplicar políticas de restricción para cada tenant.
Los tokens se resetean el primer dia de cada mes

## Funcionalidades Principales

- Definición de límites de tokens por tenant.
- Registro y actualización automática del consumo de tokens.
- Validación de quotas antes de procesar requests.
- Soporte para diferentes periodos de cuota (mensual, diario, etc.).
- Señales y servicios para extender el control a otros recursos (requests, almacenamiento, etc.).
- Task encargada del reset de cada mes

## Estructura del Módulo

- **models.py**: Modelos para almacenar límites y consumo de tokens por tenant.
- **services.py**: Lógica de negocio para validación y actualización de quotas.
- **middleware.py**: Middleware para validar el uso antes de procesar requests (opcional).
- **admin.py**: Configuración para la gestión de quotas en el panel de administración.
- **tests/**: Pruebas unitarias y de integración para la lógica de quotas.
- **migrations/**: Migraciones de base de datos para los modelos de quotas.

## Ejemplo de Uso

1. Se define un límite de tokens mensual para cada tenant.
2. Cada vez que un tenant realiza una request a la IA, se registra el consumo real de tokens usando las métricas del modelo.
3. Si el tenant supera su cuota, se rechazan nuevas requests hasta el próximo periodo.

## Integración

- Se recomienda integrar la validación de quotas en los servicios que gestionan requests a modelos de IA.
- Puede usarse como middleware o mediante decoradores en vistas y endpoints.

## Buenas Prácticas

- Usar los valores reales de tokens reportados por la API de IA para registrar el consumo.
- Configurar los límites de cuota según el plan de cada tenant.
- Implementar alertas o notificaciones cuando un tenant esté cerca de su límite.

## Relación con Otros Módulos

- **tenants**: Relaciona cada cuota con un tenant específico.
- **agents**: Controla el uso de tokens en las interacciones de agentes con modelos de IA.
- **billing** (opcional): Puede integrarse para facturación basada en consumo.

## Testing

- Incluye pruebas para la lógica de validación, actualización y reinicio de quotas.
- Pruebas de integración con los servicios de IA y el flujo de requests.

---

> Para más detalles sobre la configuración y extensión del módulo, consulta la documentación interna y los docstrings en el código fuente.