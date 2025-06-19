# Módulo de Tenants

## Descripción General
Este módulo implementa un sistema multitenancy que permite gestionar múltiples organizaciones o espacios de trabajo aislados dentro de la misma aplicación. Cada tenant representa un entorno aislado con sus propios usuarios, datos y configuraciones.

## Estructura del Módulo

- **models.py**: Define el modelo `TenantModel` y otras entidades relacionadas con la gestión de tenants.
- **admin.py**: Configuración para administrar tenants desde el panel de administración de Django.
- **views.py**: Vistas para operaciones relacionadas con tenants en la interfaz web.
- **services.py**: Implementa servicios para la gestión de tenants, incluyendo creación, actualización y configuración.
- **signals.py**: Define señales para manejar eventos relacionados con tenants, como su creación o eliminación.
- **helpers.py**: Funciones auxiliares utilizadas en la lógica de tenancy.
- **tests.py**: Pruebas unitarias y de integración para el sistema de tenants.

### Carpeta `migrations/`
Contiene las migraciones de la base de datos para los modelos relacionados con tenants.

## Funcionalidades Principales

1. **Aislamiento de datos**: Cada tenant tiene sus propios datos aislados de otros tenants.
2. **Gestión de usuarios**: Los usuarios están asociados a uno o más tenants, con diferentes roles y permisos.
3. **Configuración personalizada**: Cada tenant puede tener configuraciones específicas.
4. **Auditoría**: Seguimiento de acciones realizadas en cada tenant.

## Relaciones con otros Módulos
Prácticamente todos los módulos del sistema se relacionan con Tenants:
- **agents**: Los agentes pertenecen a tenants específicos.
- **chats**: Las conversaciones están asociadas a un tenant.
- **documents**: Los documentos pertenecen a un tenant.
- **knowledge**: Las bases de conocimiento están segmentadas por tenant.

## Filtrado por Tenant
El sistema implementa un filtrado automático por tenant en:
- Consultas a la base de datos
- APIs REST
- Interfaces de administración
- Formularios y vistas

Esto garantiza que los usuarios solo puedan acceder a los datos de los tenants a los que pertenecen, implementando un sólido nivel de seguridad y aislamiento.
