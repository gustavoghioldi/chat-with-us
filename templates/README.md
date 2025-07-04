# Templates - Plantillas HTML

## Descripción General
Este directorio contiene las plantillas HTML utilizadas por Django para renderizar las vistas del sistema. Las plantillas están organizadas por módulos y funcionalidades para facilitar el mantenimiento y la reutilización.

## Estructura del Directorio

### `/admin/`
Plantillas personalizadas para el panel de administración de Django:
- **base_site.html**: Plantilla base personalizada del admin
- **change_list.html**: Plantilla para listas de objetos
- **change_form.html**: Plantilla para formularios de edición
- **login.html**: Plantilla personalizada de login del admin

### `/UI/`
Plantillas para la interfaz de usuario principal:
- **base.html**: Plantilla base de la aplicación
- **index.html**: Página principal
- **dashboard.html**: Dashboard principal
- **components/**: Componentes reutilizables

#### Estructura Base
```html
<!-- base.html -->
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Chat With Us{% endblock %}</title>

    <!-- CSS -->
    {% load static %}
    <link rel="stylesheet" href="{% static 'css/main.css' %}">
    <link rel="stylesheet" href="{% static 'css/components.css' %}">

    {% block extra_css %}{% endblock %}
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar">
        <div class="navbar-brand">
            <h1>Chat With Us</h1>
        </div>
        <div class="navbar-nav">
            {% if user.is_authenticated %}
                <a href="{% url 'dashboard' %}">Dashboard</a>
                <a href="{% url 'agents:list' %}">Agentes</a>
                <a href="{% url 'chats:list' %}">Chats</a>
                <a href="{% url 'logout' %}">Cerrar Sesión</a>
            {% else %}
                <a href="{% url 'login' %}">Iniciar Sesión</a>
            {% endif %}
        </div>
    </nav>

    <!-- Main Content -->
    <main class="main-content">
        {% block content %}{% endblock %}
    </main>

    <!-- Footer -->
    <footer class="footer">
        <p>&copy; 2024 Chat With Us. Todos los derechos reservados.</p>
    </footer>

    <!-- JavaScript -->
    <script src="{% static 'js/main.js' %}"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>
```

## Plantillas por Módulo

### Plantillas de Agentes
```html
<!-- agents/agent_list.html -->
{% extends 'UI/base.html' %}
{% load static %}

{% block title %}Agentes - Chat With Us{% endblock %}

{% block content %}
<div class="container">
    <div class="page-header">
        <h2>Gestión de Agentes</h2>
        <a href="{% url 'agents:create' %}" class="btn btn-primary">
            <i class="fas fa-plus"></i> Crear Agente
        </a>
    </div>

    <div class="agents-grid">
        {% for agent in agents %}
            <div class="agent-card">
                <div class="agent-card__header">
                    <div class="agent-card__avatar">
                        <i class="fas fa-robot"></i>
                    </div>
                    <div class="agent-card__info">
                        <h3 class="agent-card__title">{{ agent.name }}</h3>
                        <p class="agent-card__description">{{ agent.description|truncatewords:20 }}</p>
                    </div>
                </div>

                <div class="agent-card__stats">
                    <div class="stat">
                        <span class="stat__label">Chats</span>
                        <span class="stat__value">{{ agent.chat_count }}</span>
                    </div>
                    <div class="stat">
                        <span class="stat__label">Conocimientos</span>
                        <span class="stat__value">{{ agent.knowledge_count }}</span>
                    </div>
                </div>

                <div class="agent-card__actions">
                    <a href="{% url 'agents:detail' agent.id %}" class="btn btn-sm btn-outline-primary">
                        Ver Detalles
                    </a>
                    <a href="{% url 'agents:edit' agent.id %}" class="btn btn-sm btn-outline-secondary">
                        Editar
                    </a>
                    <a href="{% url 'chats:create' %}?agent={{ agent.id }}" class="btn btn-sm btn-success">
                        Iniciar Chat
                    </a>
                </div>
            </div>
        {% empty %}
            <div class="empty-state">
                <i class="fas fa-robot fa-3x"></i>
                <h3>No hay agentes disponibles</h3>
                <p>Crea tu primer agente para comenzar a chatear</p>
                <a href="{% url 'agents:create' %}" class="btn btn-primary">
                    Crear Primer Agente
                </a>
            </div>
        {% endfor %}
    </div>
</div>
{% endblock %}
```

### Plantillas de Chat
```html
<!-- chats/chat_room.html -->
{% extends 'UI/base.html' %}
{% load static %}

{% block title %}Chat con {{ agent.name }} - Chat With Us{% endblock %}

{% block extra_css %}
    <link rel="stylesheet" href="{% static 'css/chat.css' %}">
{% endblock %}

{% block content %}
<div class="chat-container">
    <div class="chat-header">
        <div class="chat-header__agent">
            <div class="agent-avatar">
                <i class="fas fa-robot"></i>
            </div>
            <div class="agent-info">
                <h3>{{ agent.name }}</h3>
                <p class="agent-status">
                    <span class="status-indicator status-indicator--online"></span>
                    En línea
                </p>
            </div>
        </div>

        <div class="chat-header__actions">
            <button class="btn btn-sm btn-outline-secondary" id="export-chat">
                <i class="fas fa-download"></i> Exportar
            </button>
            <button class="btn btn-sm btn-outline-danger" id="clear-chat">
                <i class="fas fa-trash"></i> Limpiar
            </button>
        </div>
    </div>

    <div class="chat-messages" id="chat-messages">
        {% for message in messages %}
            <div class="chat-message chat-message--{{ message.sender_type }}">
                <div class="chat-message__content">
                    <div class="message-text">{{ message.content|linebreaks }}</div>
                    <div class="message-timestamp">
                        {{ message.created_at|date:"H:i" }}
                    </div>
                </div>
            </div>
        {% endfor %}
    </div>

    <div class="chat-input">
        <form id="message-form" class="message-form">
            {% csrf_token %}
            <div class="input-group">
                <input
                    type="text"
                    id="message-input"
                    class="form-control"
                    placeholder="Escribe tu mensaje..."
                    maxlength="1000"
                    autocomplete="off"
                >
                <button type="submit" class="btn btn-primary">
                    <i class="fas fa-paper-plane"></i>
                </button>
            </div>
        </form>
    </div>
</div>
{% endblock %}

{% block extra_js %}
    <script src="{% static 'js/chat.js' %}"></script>
    <script>
        const chatManager = new ChatManager({{ chat.id }});
        chatManager.initialize();
    </script>
{% endblock %}
```

### Plantillas de Dashboard
```html
<!-- dashboard.html -->
{% extends 'UI/base.html' %}
{% load static %}

{% block title %}Dashboard - Chat With Us{% endblock %}

{% block extra_css %}
    <link rel="stylesheet" href="{% static 'css/dashboard.css' %}">
{% endblock %}

{% block content %}
<div class="dashboard">
    <div class="dashboard-header">
        <h2>Dashboard</h2>
        <div class="dashboard-header__actions">
            <select class="form-select" id="time-range">
                <option value="7">Últimos 7 días</option>
                <option value="30">Últimos 30 días</option>
                <option value="90">Últimos 90 días</option>
            </select>
        </div>
    </div>

    <div class="dashboard-stats">
        <div class="stat-card">
            <div class="stat-card__icon">
                <i class="fas fa-comments"></i>
            </div>
            <div class="stat-card__content">
                <h3>{{ stats.total_chats }}</h3>
                <p>Chats Totales</p>
                <span class="stat-card__change stat-card__change--positive">
                    +{{ stats.chats_growth }}%
                </span>
            </div>
        </div>

        <div class="stat-card">
            <div class="stat-card__icon">
                <i class="fas fa-robot"></i>
            </div>
            <div class="stat-card__content">
                <h3>{{ stats.active_agents }}</h3>
                <p>Agentes Activos</p>
                <span class="stat-card__change stat-card__change--positive">
                    +{{ stats.agents_growth }}%
                </span>
            </div>
        </div>

        <div class="stat-card">
            <div class="stat-card__icon">
                <i class="fas fa-smile"></i>
            </div>
            <div class="stat-card__content">
                <h3>{{ stats.avg_satisfaction }}%</h3>
                <p>Satisfacción Promedio</p>
                <span class="stat-card__change stat-card__change--neutral">
                    {{ stats.satisfaction_change }}%
                </span>
            </div>
        </div>

        <div class="stat-card">
            <div class="stat-card__icon">
                <i class="fas fa-clock"></i>
            </div>
            <div class="stat-card__content">
                <h3>{{ stats.avg_response_time }}s</h3>
                <p>Tiempo de Respuesta</p>
                <span class="stat-card__change stat-card__change--negative">
                    {{ stats.response_time_change }}%
                </span>
            </div>
        </div>
    </div>

    <div class="dashboard-charts">
        <div class="chart-container">
            <h3>Actividad de Chats</h3>
            <canvas id="chats-chart"></canvas>
        </div>

        <div class="chart-container">
            <h3>Análisis de Sentimientos</h3>
            <canvas id="sentiment-chart"></canvas>
        </div>
    </div>

    <div class="dashboard-tables">
        <div class="table-container">
            <h3>Agentes Más Activos</h3>
            <table class="table">
                <thead>
                    <tr>
                        <th>Agente</th>
                        <th>Chats</th>
                        <th>Satisfacción</th>
                        <th>Tiempo Resp.</th>
                    </tr>
                </thead>
                <tbody>
                    {% for agent in top_agents %}
                        <tr>
                            <td>
                                <div class="agent-info">
                                    <i class="fas fa-robot"></i>
                                    {{ agent.name }}
                                </div>
                            </td>
                            <td>{{ agent.chat_count }}</td>
                            <td>
                                <span class="badge badge-{% if agent.satisfaction > 80 %}success{% elif agent.satisfaction > 60 %}warning{% else %}danger{% endif %}">
                                    {{ agent.satisfaction }}%
                                </span>
                            </td>
                            <td>{{ agent.avg_response_time }}s</td>
                        </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

        <div class="table-container">
            <h3>Chats Recientes</h3>
            <table class="table">
                <thead>
                    <tr>
                        <th>Usuario</th>
                        <th>Agente</th>
                        <th>Fecha</th>
                        <th>Sentimiento</th>
                        <th>Acciones</th>
                    </tr>
                </thead>
                <tbody>
                    {% for chat in recent_chats %}
                        <tr>
                            <td>{{ chat.user.username }}</td>
                            <td>{{ chat.agent.name }}</td>
                            <td>{{ chat.created_at|date:"d/m/Y H:i" }}</td>
                            <td>
                                <span class="sentiment-badge sentiment-badge--{{ chat.sentiment }}">
                                    {{ chat.get_sentiment_display }}
                                </span>
                            </td>
                            <td>
                                <a href="{% url 'chats:detail' chat.id %}" class="btn btn-sm btn-outline-primary">
                                    Ver
                                </a>
                            </td>
                        </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
    <script src="{% static 'js/charts.js' %}"></script>
    <script>
        // Inicializar gráficos
        initializeCharts({
            chatsData: {{ charts_data.chats|safe }},
            sentimentData: {{ charts_data.sentiment|safe }}
        });
    </script>
{% endblock %}
```

## Componentes Reutilizables

### Formularios
```html
<!-- components/forms/form_field.html -->
<div class="form-group">
    <label for="{{ field.id_for_label }}" class="form-label">
        {{ field.label }}
        {% if field.field.required %}
            <span class="required">*</span>
        {% endif %}
    </label>

    {{ field }}

    {% if field.help_text %}
        <small class="form-text text-muted">{{ field.help_text }}</small>
    {% endif %}

    {% if field.errors %}
        <div class="invalid-feedback">
            {% for error in field.errors %}
                <div>{{ error }}</div>
            {% endfor %}
        </div>
    {% endif %}
</div>
```

### Paginación
```html
<!-- components/pagination.html -->
{% if is_paginated %}
    <nav aria-label="Page navigation">
        <ul class="pagination">
            {% if page_obj.has_previous %}
                <li class="page-item">
                    <a class="page-link" href="?page=1">Primera</a>
                </li>
                <li class="page-item">
                    <a class="page-link" href="?page={{ page_obj.previous_page_number }}">Anterior</a>
                </li>
            {% endif %}

            {% for num in page_obj.paginator.page_range %}
                {% if page_obj.number == num %}
                    <li class="page-item active">
                        <span class="page-link">{{ num }}</span>
                    </li>
                {% elif num > page_obj.number|add:'-3' and num < page_obj.number|add:'3' %}
                    <li class="page-item">
                        <a class="page-link" href="?page={{ num }}">{{ num }}</a>
                    </li>
                {% endif %}
            {% endfor %}

            {% if page_obj.has_next %}
                <li class="page-item">
                    <a class="page-link" href="?page={{ page_obj.next_page_number }}">Siguiente</a>
                </li>
                <li class="page-item">
                    <a class="page-link" href="?page={{ page_obj.paginator.num_pages }}">Última</a>
                </li>
            {% endif %}
        </ul>
    </nav>
{% endif %}
```

### Modales
```html
<!-- components/modal.html -->
<div class="modal fade" id="{{ modal_id }}" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">{{ modal_title }}</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Cerrar"></button>
            </div>
            <div class="modal-body">
                {{ modal_content }}
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                    Cancelar
                </button>
                <button type="button" class="btn btn-primary" id="{{ modal_id }}-confirm">
                    {{ confirm_text|default:"Confirmar" }}
                </button>
            </div>
        </div>
    </div>
</div>
```

## Filtros y Tags Personalizados

### Template Tags
```python
# templatetags/chat_tags.py
from django import template
from django.utils.safestring import mark_safe
import markdown

register = template.Library()

@register.filter
def markdown_to_html(text):
    """Convierte markdown a HTML"""
    html = markdown.markdown(text, extensions=['codehilite', 'fenced_code'])
    return mark_safe(html)

@register.filter
def sentiment_icon(sentiment):
    """Devuelve el icono apropiado para el sentimiento"""
    icons = {
        'positive': 'fas fa-smile',
        'negative': 'fas fa-frown',
        'neutral': 'fas fa-meh'
    }
    return icons.get(sentiment, 'fas fa-question')

@register.inclusion_tag('components/agent_card.html')
def agent_card(agent):
    """Renderiza una tarjeta de agente"""
    return {'agent': agent}
```

### Uso en Templates
```html
{% load chat_tags %}

<!-- Usar filtro markdown -->
<div class="message-content">
    {{ message.content|markdown_to_html }}
</div>

<!-- Usar filtro de sentimiento -->
<i class="{{ chat.sentiment|sentiment_icon }}"></i>

<!-- Usar inclusion tag -->
{% agent_card agent %}
```

## Internacionalización

### Plantillas Multiidioma
```html
{% load i18n %}

<h2>{% trans "Gestión de Agentes" %}</h2>

<p>{% blocktrans count counter=agents|length %}
    Tienes {{ counter }} agente.
{% plural %}
    Tienes {{ counter }} agentes.
{% endblocktrans %}</p>

<button class="btn btn-primary">
    {% trans "Crear Nuevo Agente" %}
</button>
```

### Configuración de Idiomas
```python
# settings.py
LANGUAGES = [
    ('es', 'Español'),
    ('en', 'English'),
    ('pt', 'Português'),
]

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]
```

## Optimización y Performance

### Caching de Templates
```python
# settings.py
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'OPTIONS': {
            'loaders': [
                ('django.template.loaders.cached.Loader', [
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
                ]),
            ],
        },
    },
]
```

### Lazy Loading
```html
<!-- Lazy loading de imágenes -->
<img src="{% static 'img/placeholder.jpg' %}"
     data-src="{% static 'img/actual-image.jpg' %}"
     class="lazy-load"
     alt="Descripción">

<!-- Lazy loading de scripts -->
<script>
    // Cargar script solo cuando sea necesario
    if (document.querySelector('.chart-container')) {
        import('{% static "js/charts.js" %}').then(module => {
            module.initializeCharts();
        });
    }
</script>
```

## Seguridad

### Protección CSRF
```html
<!-- En formularios -->
<form method="post">
    {% csrf_token %}
    <!-- campos del formulario -->
</form>

<!-- En JavaScript -->
<script>
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    fetch('/api/endpoint/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    });
</script>
```

### Escape de Contenido
```html
<!-- Contenido escapado por defecto -->
<p>{{ user_input }}</p>

<!-- Contenido sin escapar (usar con precaución) -->
<p>{{ trusted_content|safe }}</p>

<!-- Escapar manualmente -->
<p>{{ potentially_dangerous_content|escape }}</p>
```

## Mejores Prácticas

### Organización de Templates
1. **Herencia**: Usar herencia de templates para reutilizar código
2. **Inclusión**: Usar includes para componentes reutilizables
3. **Bloques**: Definir bloques apropiados para extensibilidad
4. **Nomenclatura**: Usar nomenclatura consistente y descriptiva

### Performance
1. **Minimizar queries**: Usar select_related y prefetch_related
2. **Caching**: Implementar caching de templates y fragmentos
3. **Lazy loading**: Cargar contenido bajo demanda
4. **Optimización de imágenes**: Usar formatos optimizados y responsive

### Mantenibilidad
1. **Componentes**: Crear componentes reutilizables
2. **Documentación**: Documentar templates complejos
3. **Testing**: Probar templates con datos diversos
4. **Versionado**: Mantener versionado de cambios importantes
