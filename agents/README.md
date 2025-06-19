# Módulo de Agentes

## Descripción General
Este módulo gestiona los agentes de inteligencia artificial que pueden interactuar con los usuarios a través del sistema de chat. Los agentes son entidades que pueden recibir consultas, procesarlas y proporcionar respuestas utilizando modelos de lenguaje y bases de conocimiento.

## Estructura del Módulo

- **models.py**: Define el modelo `AgentModel` que representa un agente en el sistema, incluyendo sus configuraciones, parámetros y relaciones con otros modelos.
- **admin.py**: Configuración para la visualización y administración de agentes en el panel de administración de Django.
- **views.py**: Vistas para interactuar con los agentes desde la interfaz web.
- **signals.py**: Señales para manejar eventos relacionados con los agentes, como su creación o modificación.
- **tests.py**: Pruebas unitarias y de integración para asegurar el correcto funcionamiento del módulo.

### Carpeta `migrations/`
Contiene las migraciones de la base de datos para el modelo de agentes, registrando los cambios estructurales del modelo a lo largo del tiempo.

### Carpeta `services/`
- **agent_service.py**: Implementa la lógica principal para el funcionamiento de los agentes, incluyendo la interacción con modelos de lenguaje y bases de conocimiento.
- **agent_storage_service.py**: Gestiona el almacenamiento y recuperación de datos relacionados con los agentes.

## Relaciones con otros Módulos
- **knowledge**: Los agentes utilizan bases de conocimiento para responder consultas con información específica.
- **chats**: Los agentes participan en conversaciones a través del módulo de chats.
- **tenants**: Los agentes pertenecen a un tenant específico.

## Flujo de Trabajo
1. Un usuario hace una consulta a través del sistema de chat.
2. El mensaje se envía al agente asignado a la conversación.
3. El agente procesa la consulta utilizando modelos de lenguaje y bases de conocimiento.
4. El agente genera una respuesta que se envía de vuelta al usuario a través del chat.
