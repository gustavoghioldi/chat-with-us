# Módulo de Análisis

## Descripción General
Este módulo se encarga del análisis de datos generados por el sistema, principalmente el análisis de sentimientos en las conversaciones de chat y las interacciones con agentes. Proporciona insights y métricas sobre el funcionamiento del sistema.

## Estructura del Módulo

- **services.py**: Implementa servicios para el análisis de datos, como el análisis de sentimientos de los mensajes.
- **tasks.py**: Define tareas asíncronas para procesar análisis que pueden ser ejecutados en segundo plano utilizando Celery.
- **views.py**: Vistas para visualizar resultados de análisis y dashboards.
- **admin.py**: Configuración para la visualización de datos de análisis en el panel de administración.

### Carpeta `migrations/`
Contiene las migraciones de la base de datos para los modelos de análisis, registrando cambios estructurales en los modelos.

### Carpeta `models/`
- **sentiment_chat_model.py**: Modelo para almacenar análisis de sentimientos de conversaciones en chats.
- **sentiment_agents_model.py**: Modelo para almacenar análisis de sentimientos de interacciones con agentes.

### Carpeta `signals/`
- **new_chat_text_receiver.py**: Receptor de señales que se activa cuando hay nuevos mensajes de chat para analizar.

### Carpeta `tests/`
Pruebas unitarias y de integración para el módulo de análisis.

## Relaciones con otros Módulos
- **chats**: Analiza las conversaciones generadas en el módulo de chats.
- **agents**: Analiza las interacciones y respuestas generadas por los agentes.

## Flujo de Trabajo
1. Un nuevo mensaje se envía en una conversación.
2. La señal `new_chat_text_receiver` detecta el mensaje.
3. Se ejecuta un análisis de sentimientos sobre el mensaje.
4. Los resultados del análisis se almacenan en la base de datos.
5. Los datos de análisis pueden ser consultados a través de dashboards o el panel de administración.
