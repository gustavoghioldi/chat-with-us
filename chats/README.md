# Módulo de Chats

## Descripción General
Este módulo gestiona el sistema de conversaciones entre usuarios y agentes de inteligencia artificial. Almacena, procesa y presenta los mensajes intercambiados, proporcionando una interfaz para la comunicación bidireccional.

## Estructura del Módulo

- **models.py**: Define los modelos principales como `ChatModel` (conversación) y `ChatTextModel` (mensaje individual).
- **services.py**: Implementa la lógica de negocio para gestionar conversaciones, enviar mensajes y procesar respuestas de agentes.
- **tasks.py**: Define tareas asíncronas relacionadas con el procesamiento de mensajes utilizando Celery.
- **views.py**: Vistas para la interfaz web del sistema de chat.
- **admin.py**: Configuración para administrar conversaciones y mensajes en el panel de administración.
- **tests.py**: Pruebas unitarias y de integración para el módulo de chat.

### Carpeta `migrations/`
Contiene las migraciones de la base de datos para los modelos de chat.

### Carpeta `signals/`
Define señales para responder a eventos relacionados con los chats, como la creación de nuevos mensajes.

## Funcionalidades Principales

1. **Gestión de Conversaciones**: Crear, actualizar y eliminar conversaciones.
2. **Mensajería**: Envío y recepción de mensajes de texto.
3. **Integración con Agentes**: Enrutamiento de mensajes a agentes de IA para procesar y generar respuestas.
4. **Historial de Conversaciones**: Almacenamiento y recuperación del historial completo de conversaciones.
5. **Notificaciones**: Alertas sobre nuevos mensajes o actualizaciones en conversaciones.

## Relaciones con otros Módulos
- **agents**: Los chats interactúan con agentes para procesar consultas y generar respuestas.
- **tenants**: Las conversaciones pertenecen a tenants específicos.
- **analysis**: Los mensajes de chat pueden ser analizados para extraer insights.

## Flujo de Trabajo
1. Un usuario inicia una conversación o selecciona una existente.
2. El usuario envía un mensaje que se almacena en la base de datos.
3. El mensaje se envía al agente asignado a la conversación.
4. El agente procesa el mensaje y genera una respuesta.
5. La respuesta se almacena en la base de datos y se envía al usuario.
6. El historial de la conversación se actualiza con los nuevos mensajes.
