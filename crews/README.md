# Módulo de Crews (Equipos)

## Descripción General
Este módulo gestiona los equipos o "crews" dentro del sistema, permitiendo agrupar agentes de IA y usuarios para colaborar en tareas específicas. Los equipos pueden compartir recursos, conocimientos y conversaciones.

## Estructura del Módulo

- **models.py**: Define el modelo `CrewModel` que representa un equipo y sus relaciones con agentes, usuarios y otros recursos.
- **admin.py**: Configuración para administrar equipos en el panel de administración de Django.
- **views.py**: Vistas para la gestión y visualización de equipos desde la interfaz web.
- **tests.py**: Pruebas unitarias y de integración para el módulo de equipos.

### Carpeta `migrations/`
Contiene las migraciones de la base de datos para el modelo de equipos.

## Funcionalidades Principales

1. **Gestión de Equipos**: Crear, actualizar y eliminar equipos.
2. **Asignación de Miembros**: Asignar usuarios y agentes a equipos.
3. **Recursos Compartidos**: Compartir documentos, bases de conocimiento y conversaciones entre miembros del equipo.
4. **Colaboración**: Permitir que múltiples miembros contribuyan a las mismas tareas y conversaciones.

## Relaciones con otros Módulos
- **agents**: Los equipos pueden incluir múltiples agentes con diferentes especializaciones.
- **users**: Los usuarios pueden ser miembros de uno o más equipos.
- **tenants**: Los equipos pertenecen a un tenant específico.
- **knowledge**: Los equipos pueden compartir bases de conocimiento específicas.
- **chats**: Los equipos pueden participar en conversaciones grupales.

## Escenarios de Uso
1. Un equipo de soporte técnico con varios agentes especializados en diferentes áreas.
2. Un equipo de ventas donde agentes y representantes humanos colaboran para atender clientes.
3. Un equipo de investigación que comparte bases de conocimiento y documentos especializados.
