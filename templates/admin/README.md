# Templates Admin - Plantillas de Administración

## Descripción General
Este directorio contiene las plantillas HTML personalizadas para el panel de administración de Django. Estas plantillas extienden y personalizan la interfaz de administración para proporcionar una experiencia de gestión más rica y específica para el sistema Chat With Us.

## Estructura del Directorio

### Archivos Base
- **base_site.html**: Plantilla base personalizada del panel de administración

### Directorios por Módulo
- **analysis/**: Plantillas para administración de análisis
- **chats/**: Plantillas para gestión de chats
- **knowledge/**: Plantillas para administración de conocimiento
- **tenants/**: Plantillas para gestión de tenants

## Plantillas Base

### base_site.html
```html
<!-- admin/base_site.html -->
{% extends "admin/base.html" %}
{% load static %}

{% block title %}{{ title }} | Chat With Us Admin{% endblock %}

{% block branding %}
<h1 id="site-name">
    <a href="{% url 'admin:index' %}">
        <img src="{% static 'admin/img/logo.png' %}" alt="Chat With Us" height="32">
        Chat With Us Admin
    </a>
</h1>
{% endblock %}

{% block extrastyle %}
{{ block.super }}
<link rel="stylesheet" type="text/css" href="{% static 'admin/css/custom-admin.css' %}">
<link rel="stylesheet" type="text/css" href="{% static 'admin/css/dashboard.css' %}">
{% endblock %}

{% block extrahead %}
{{ block.super }}
<script src="{% static 'admin/js/jquery.min.js' %}"></script>
<script src="{% static 'admin/js/custom-admin.js' %}"></script>
{% endblock %}

{% block nav-sidebar %}
{{ block.super }}
<div class="module custom-sidebar">
    <h2>Herramientas Avanzadas</h2>
    <ul>
        <li><a href="{% url 'admin:analytics_dashboard' %}">Dashboard de Análisis</a></li>
        <li><a href="{% url 'admin:system_health' %}">Estado del Sistema</a></li>
        <li><a href="{% url 'admin:knowledge_manager' %}">Gestor de Conocimiento</a></li>
        <li><a href="{% url 'admin:chat_monitor' %}">Monitor de Chats</a></li>
    </ul>
</div>
{% endblock %}

{% block footer %}
<div id="footer">
    <div class="footer-content">
        <p>Chat With Us Admin Panel v2.0 |
           <a href="{% url 'admin:system_info' %}">Información del Sistema</a> |
           <a href="{% url 'admin:help' %}">Ayuda</a>
        </p>
    </div>
</div>
{% endblock %}
```

## Módulo Analysis

### Dashboard de Análisis
```html
<!-- admin/analysis/dashboard.html -->
{% extends "admin/base_site.html" %}
{% load static %}

{% block title %}Dashboard de Análisis{% endblock %}

{% block extrastyle %}
{{ block.super }}
<link rel="stylesheet" type="text/css" href="{% static 'admin/css/analysis-dashboard.css' %}">
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
{% endblock %}

{% block content %}
<div class="analysis-dashboard">
    <h1>Dashboard de Análisis</h1>

    <!-- Métricas Principales -->
    <div class="metrics-grid">
        <div class="metric-card">
            <div class="metric-icon">
                <i class="icon-message"></i>
            </div>
            <div class="metric-content">
                <h3>{{ total_messages|floatformat:0 }}</h3>
                <p>Mensajes Totales</p>
                <span class="metric-change positive">+{{ message_growth }}%</span>
            </div>
        </div>

        <div class="metric-card">
            <div class="metric-icon">
                <i class="icon-users"></i>
            </div>
            <div class="metric-content">
                <h3>{{ active_users|floatformat:0 }}</h3>
                <p>Usuarios Activos</p>
                <span class="metric-change positive">+{{ user_growth }}%</span>
            </div>
        </div>

        <div class="metric-card">
            <div class="metric-icon">
                <i class="icon-clock"></i>
            </div>
            <div class="metric-content">
                <h3>{{ avg_response_time|floatformat:1 }}s</h3>
                <p>Tiempo de Respuesta</p>
                <span class="metric-change negative">-{{ response_time_improvement }}%</span>
            </div>
        </div>

        <div class="metric-card">
            <div class="metric-icon">
                <i class="icon-smile"></i>
            </div>
            <div class="metric-content">
                <h3>{{ satisfaction_score|floatformat:1 }}/5</h3>
                <p>Satisfacción</p>
                <span class="metric-change positive">+{{ satisfaction_improvement }}%</span>
            </div>
        </div>
    </div>

    <!-- Gráficos -->
    <div class="charts-grid">
        <div class="chart-container">
            <div class="chart-header">
                <h3>Mensajes por Día</h3>
                <div class="chart-controls">
                    <select id="messages-period">
                        <option value="7">Últimos 7 días</option>
                        <option value="30">Últimos 30 días</option>
                        <option value="90">Últimos 90 días</option>
                    </select>
                </div>
            </div>
            <canvas id="messagesChart"></canvas>
        </div>

        <div class="chart-container">
            <div class="chart-header">
                <h3>Análisis de Sentimientos</h3>
            </div>
            <canvas id="sentimentChart"></canvas>
        </div>

        <div class="chart-container">
            <div class="chart-header">
                <h3>Agentes Más Activos</h3>
            </div>
            <canvas id="agentsChart"></canvas>
        </div>

        <div class="chart-container">
            <div class="chart-header">
                <h3>Temas Más Consultados</h3>
            </div>
            <canvas id="topicsChart"></canvas>
        </div>
    </div>

    <!-- Tabla de Detalles -->
    <div class="details-section">
        <h3>Análisis Detallado</h3>
        <div class="table-container">
            <table class="analysis-table">
                <thead>
                    <tr>
                        <th>Fecha</th>
                        <th>Mensajes</th>
                        <th>Usuarios Únicos</th>
                        <th>Tiempo Resp. Avg</th>
                        <th>Satisfacción</th>
                        <th>Acciones</th>
                    </tr>
                </thead>
                <tbody>
                    {% for row in analysis_data %}
                    <tr>
                        <td>{{ row.date|date:"d/m/Y" }}</td>
                        <td>{{ row.messages }}</td>
                        <td>{{ row.unique_users }}</td>
                        <td>{{ row.avg_response_time|floatformat:1 }}s</td>
                        <td>
                            <span class="satisfaction-badge {{ row.satisfaction_class }}">
                                {{ row.satisfaction|floatformat:1 }}
                            </span>
                        </td>
                        <td>
                            <a href="{% url 'admin:analysis_detail' row.date.isoformat %}"
                               class="btn-view">Ver Detalle</a>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>

<script>
// Configuración de gráficos
const messagesData = {{ messages_chart_data|safe }};
const sentimentData = {{ sentiment_chart_data|safe }};
const agentsData = {{ agents_chart_data|safe }};
const topicsData = {{ topics_chart_data|safe }};

// Inicializar gráficos
document.addEventListener('DOMContentLoaded', function() {
    initializeCharts();
});

function initializeCharts() {
    // Gráfico de mensajes por día
    new Chart(document.getElementById('messagesChart'), {
        type: 'line',
        data: {
            labels: messagesData.labels,
            datasets: [{
                label: 'Mensajes',
                data: messagesData.data,
                borderColor: '#007bff',
                backgroundColor: 'rgba(0, 123, 255, 0.1)',
                fill: true
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });

    // Gráfico de sentimientos
    new Chart(document.getElementById('sentimentChart'), {
        type: 'doughnut',
        data: {
            labels: ['Positivo', 'Neutral', 'Negativo'],
            datasets: [{
                data: sentimentData.data,
                backgroundColor: ['#28a745', '#ffc107', '#dc3545']
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });

    // Gráfico de agentes
    new Chart(document.getElementById('agentsChart'), {
        type: 'bar',
        data: {
            labels: agentsData.labels,
            datasets: [{
                label: 'Mensajes',
                data: agentsData.data,
                backgroundColor: '#17a2b8'
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });

    // Gráfico de temas
    new Chart(document.getElementById('topicsChart'), {
        type: 'horizontalBar',
        data: {
            labels: topicsData.labels,
            datasets: [{
                label: 'Consultas',
                data: topicsData.data,
                backgroundColor: '#6f42c1'
            }]
        },
        options: {
            responsive: true,
            scales: {
                x: {
                    beginAtZero: true
                }
            }
        }
    });
}
</script>
{% endblock %}
```

## Módulo Chats

### Monitor de Chats
```html
<!-- admin/chats/monitor.html -->
{% extends "admin/base_site.html" %}
{% load static %}

{% block title %}Monitor de Chats{% endblock %}

{% block extrastyle %}
{{ block.super }}
<link rel="stylesheet" type="text/css" href="{% static 'admin/css/chat-monitor.css' %}">
{% endblock %}

{% block content %}
<div class="chat-monitor">
    <h1>Monitor de Chats en Tiempo Real</h1>

    <!-- Estadísticas en Tiempo Real -->
    <div class="live-stats">
        <div class="stat-card">
            <h3 id="active-chats">{{ active_chats }}</h3>
            <p>Chats Activos</p>
        </div>
        <div class="stat-card">
            <h3 id="online-agents">{{ online_agents }}</h3>
            <p>Agentes Online</p>
        </div>
        <div class="stat-card">
            <h3 id="waiting-users">{{ waiting_users }}</h3>
            <p>Usuarios en Espera</p>
        </div>
        <div class="stat-card">
            <h3 id="avg-wait-time">{{ avg_wait_time }}s</h3>
            <p>Tiempo de Espera Promedio</p>
        </div>
    </div>

    <!-- Filtros -->
    <div class="monitor-filters">
        <div class="filter-group">
            <label>Estado:</label>
            <select id="status-filter">
                <option value="">Todos</option>
                <option value="active">Activos</option>
                <option value="waiting">En Espera</option>
                <option value="completed">Completados</option>
            </select>
        </div>

        <div class="filter-group">
            <label>Agente:</label>
            <select id="agent-filter">
                <option value="">Todos</option>
                {% for agent in agents %}
                <option value="{{ agent.id }}">{{ agent.name }}</option>
                {% endfor %}
            </select>
        </div>

        <div class="filter-group">
            <label>Tenant:</label>
            <select id="tenant-filter">
                <option value="">Todos</option>
                {% for tenant in tenants %}
                <option value="{{ tenant.id }}">{{ tenant.name }}</option>
                {% endfor %}
            </select>
        </div>
    </div>

    <!-- Lista de Chats -->
    <div class="chats-list">
        <div class="chats-header">
            <h3>Chats Activos</h3>
            <button class="btn-refresh" id="refresh-chats">
                <i class="icon-refresh"></i> Actualizar
            </button>
        </div>

        <div class="chats-table-container">
            <table class="chats-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Usuario</th>
                        <th>Agente</th>
                        <th>Estado</th>
                        <th>Inicio</th>
                        <th>Último Mensaje</th>
                        <th>Mensajes</th>
                        <th>Acciones</th>
                    </tr>
                </thead>
                <tbody id="chats-tbody">
                    {% for chat in chats %}
                    <tr class="chat-row" data-chat-id="{{ chat.id }}">
                        <td>{{ chat.id }}</td>
                        <td>
                            <div class="user-info">
                                <img src="{{ chat.user.avatar.url|default:'/static/images/default-avatar.png' }}"
                                     alt="{{ chat.user.name }}" class="user-avatar">
                                <span>{{ chat.user.name }}</span>
                            </div>
                        </td>
                        <td>
                            <div class="agent-info">
                                <img src="{{ chat.agent.avatar.url|default:'/static/images/agent-avatar.png' }}"
                                     alt="{{ chat.agent.name }}" class="agent-avatar">
                                <span>{{ chat.agent.name }}</span>
                                <span class="agent-status {{ chat.agent.status }}"></span>
                            </div>
                        </td>
                        <td>
                            <span class="status-badge {{ chat.status }}">
                                {{ chat.get_status_display }}
                            </span>
                        </td>
                        <td>{{ chat.created_at|date:"H:i d/m" }}</td>
                        <td>{{ chat.last_message_at|timesince }} ago</td>
                        <td>{{ chat.message_count }}</td>
                        <td>
                            <div class="action-buttons">
                                <button class="btn-view" onclick="viewChat({{ chat.id }})">
                                    <i class="icon-eye"></i>
                                </button>
                                <button class="btn-join" onclick="joinChat({{ chat.id }})">
                                    <i class="icon-join"></i>
                                </button>
                                <button class="btn-end" onclick="endChat({{ chat.id }})">
                                    <i class="icon-stop"></i>
                                </button>
                            </div>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>

    <!-- Panel de Alertas -->
    <div class="alerts-panel">
        <h3>Alertas del Sistema</h3>
        <div class="alerts-container" id="alerts-container">
            {% for alert in alerts %}
            <div class="alert alert-{{ alert.type }}">
                <i class="icon-{{ alert.type }}"></i>
                <div class="alert-content">
                    <strong>{{ alert.title }}</strong>
                    <p>{{ alert.message }}</p>
                    <small>{{ alert.timestamp|timesince }} ago</small>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
</div>

<!-- Modal para Ver Chat -->
<div class="modal" id="chat-modal">
    <div class="modal-content">
        <div class="modal-header">
            <h3>Detalles del Chat</h3>
            <button class="btn-close" onclick="closeModal('chat-modal')">
                <i class="icon-close"></i>
            </button>
        </div>
        <div class="modal-body" id="chat-modal-body">
            <!-- Contenido del chat se carga dinámicamente -->
        </div>
    </div>
</div>

<script>
// WebSocket para actualizaciones en tiempo real
const monitorSocket = new WebSocket(
    'ws://' + window.location.host + '/ws/admin/monitor/'
);

monitorSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    updateMonitorData(data);
};

function updateMonitorData(data) {
    // Actualizar estadísticas
    document.getElementById('active-chats').textContent = data.active_chats;
    document.getElementById('online-agents').textContent = data.online_agents;
    document.getElementById('waiting-users').textContent = data.waiting_users;
    document.getElementById('avg-wait-time').textContent = data.avg_wait_time + 's';

    // Actualizar tabla de chats
    updateChatsTable(data.chats);

    // Mostrar alertas
    showAlerts(data.alerts);
}

function updateChatsTable(chats) {
    const tbody = document.getElementById('chats-tbody');
    tbody.innerHTML = '';

    chats.forEach(chat => {
        const row = createChatRow(chat);
        tbody.appendChild(row);
    });
}

function createChatRow(chat) {
    const row = document.createElement('tr');
    row.className = 'chat-row';
    row.setAttribute('data-chat-id', chat.id);

    row.innerHTML = `
        <td>${chat.id}</td>
        <td>
            <div class="user-info">
                <img src="${chat.user.avatar}" alt="${chat.user.name}" class="user-avatar">
                <span>${chat.user.name}</span>
            </div>
        </td>
        <td>
            <div class="agent-info">
                <img src="${chat.agent.avatar}" alt="${chat.agent.name}" class="agent-avatar">
                <span>${chat.agent.name}</span>
                <span class="agent-status ${chat.agent.status}"></span>
            </div>
        </td>
        <td>
            <span class="status-badge ${chat.status}">
                ${chat.status_display}
            </span>
        </td>
        <td>${chat.created_at}</td>
        <td>${chat.last_message_at}</td>
        <td>${chat.message_count}</td>
        <td>
            <div class="action-buttons">
                <button class="btn-view" onclick="viewChat(${chat.id})">
                    <i class="icon-eye"></i>
                </button>
                <button class="btn-join" onclick="joinChat(${chat.id})">
                    <i class="icon-join"></i>
                </button>
                <button class="btn-end" onclick="endChat(${chat.id})">
                    <i class="icon-stop"></i>
                </button>
            </div>
        </td>
    `;

    return row;
}

function viewChat(chatId) {
    fetch(`/admin/chats/${chatId}/details/`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('chat-modal-body').innerHTML = data.html;
            document.getElementById('chat-modal').style.display = 'block';
        });
}

function joinChat(chatId) {
    if (confirm('¿Deseas unirte a este chat?')) {
        window.open(`/admin/chats/${chatId}/join/`, '_blank');
    }
}

function endChat(chatId) {
    if (confirm('¿Deseas finalizar este chat?')) {
        fetch(`/admin/chats/${chatId}/end/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Actualizar la tabla
                location.reload();
            } else {
                alert('Error al finalizar el chat');
            }
        });
    }
}

function showAlerts(alerts) {
    const container = document.getElementById('alerts-container');

    alerts.forEach(alert => {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${alert.type}`;
        alertDiv.innerHTML = `
            <i class="icon-${alert.type}"></i>
            <div class="alert-content">
                <strong>${alert.title}</strong>
                <p>${alert.message}</p>
                <small>${alert.timestamp}</small>
            </div>
        `;

        container.insertBefore(alertDiv, container.firstChild);

        // Remover después de 5 segundos
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    });
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

// Actualizar cada 30 segundos
setInterval(() => {
    location.reload();
}, 30000);
</script>
{% endblock %}
```

## Estilos CSS Personalizados

### custom-admin.css
```css
/* admin/css/custom-admin.css */

/* Branding personalizado */
#site-name a {
    color: #2c3e50;
    text-decoration: none;
    display: flex;
    align-items: center;
    gap: 10px;
}

#site-name img {
    border-radius: 4px;
}

/* Sidebar personalizada */
.custom-sidebar {
    background: #f8f9fa;
    border-radius: 8px;
    margin-top: 20px;
    padding: 15px;
}

.custom-sidebar h2 {
    color: #495057;
    font-size: 14px;
    text-transform: uppercase;
    margin-bottom: 10px;
}

.custom-sidebar ul {
    list-style: none;
    padding: 0;
}

.custom-sidebar li {
    margin-bottom: 5px;
}

.custom-sidebar a {
    color: #6c757d;
    text-decoration: none;
    padding: 5px 10px;
    border-radius: 4px;
    display: block;
    transition: all 0.2s;
}

.custom-sidebar a:hover {
    background: #e9ecef;
    color: #495057;
}

/* Footer personalizado */
#footer {
    background: #2c3e50;
    color: white;
    text-align: center;
    padding: 15px;
    margin-top: 30px;
}

#footer a {
    color: #3498db;
    text-decoration: none;
}

#footer a:hover {
    text-decoration: underline;
}

/* Métricas */
.metrics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
    margin-bottom: 30px;
}

.metric-card {
    background: white;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    display: flex;
    align-items: center;
    gap: 15px;
}

.metric-icon {
    width: 50px;
    height: 50px;
    border-radius: 50%;
    background: #3498db;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 24px;
}

.metric-content h3 {
    font-size: 28px;
    margin: 0;
    color: #2c3e50;
}

.metric-content p {
    margin: 5px 0;
    color: #6c757d;
}

.metric-change {
    font-size: 12px;
    padding: 2px 6px;
    border-radius: 4px;
}

.metric-change.positive {
    background: #d4edda;
    color: #155724;
}

.metric-change.negative {
    background: #f8d7da;
    color: #721c24;
}

/* Gráficos */
.charts-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
    gap: 20px;
    margin-bottom: 30px;
}

.chart-container {
    background: white;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.chart-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
}

.chart-header h3 {
    margin: 0;
    color: #2c3e50;
}

/* Tablas */
.table-container {
    background: white;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.analysis-table {
    width: 100%;
    border-collapse: collapse;
}

.analysis-table th,
.analysis-table td {
    padding: 12px;
    text-align: left;
    border-bottom: 1px solid #e9ecef;
}

.analysis-table th {
    background: #f8f9fa;
    font-weight: 600;
    color: #495057;
}

.analysis-table tr:hover {
    background: #f8f9fa;
}

/* Badges */
.satisfaction-badge {
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 600;
}

.satisfaction-badge.high {
    background: #d4edda;
    color: #155724;
}

.satisfaction-badge.medium {
    background: #fff3cd;
    color: #856404;
}

.satisfaction-badge.low {
    background: #f8d7da;
    color: #721c24;
}

/* Botones */
.btn-view {
    background: #17a2b8;
    color: white;
    border: none;
    padding: 6px 12px;
    border-radius: 4px;
    cursor: pointer;
    text-decoration: none;
    display: inline-block;
    font-size: 12px;
}

.btn-view:hover {
    background: #138496;
}

/* Responsive */
@media (max-width: 768px) {
    .metrics-grid {
        grid-template-columns: 1fr;
    }

    .charts-grid {
        grid-template-columns: 1fr;
    }

    .metric-card {
        flex-direction: column;
        text-align: center;
    }
}
```

## Funcionalidades Avanzadas

### 1. **Dashboard Interactivo**
- Gráficos en tiempo real con Chart.js
- Métricas actualizadas automáticamente
- Filtros interactivos

### 2. **Monitor de Chats**
- WebSocket para actualizaciones en tiempo real
- Capacidad de unirse a chats activos
- Alertas del sistema

### 3. **Gestión de Conocimiento**
- Interfaz visual para bases de conocimiento
- Métricas de uso y efectividad
- Herramientas de importación/exportación

### 4. **Herramientas de Análisis**
- Análisis de sentimientos
- Reportes detallados
- Exportación de datos

## Integración con Django Admin

### Configuración en admin.py
```python
# admin.py
from django.contrib import admin
from django.urls import path
from django.template.response import TemplateResponse

class CustomAdminSite(admin.AdminSite):
    site_header = 'Chat With Us Administration'
    site_title = 'Chat With Us Admin'
    index_title = 'Dashboard Principal'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('analytics/', self.admin_view(self.analytics_view), name='analytics_dashboard'),
            path('chat-monitor/', self.admin_view(self.chat_monitor_view), name='chat_monitor'),
            path('knowledge-manager/', self.admin_view(self.knowledge_manager_view), name='knowledge_manager'),
        ]
        return custom_urls + urls

    def analytics_view(self, request):
        # Lógica para dashboard de análisis
        context = {
            'total_messages': get_total_messages(),
            'active_users': get_active_users(),
            'satisfaction_score': get_satisfaction_score(),
            # ... más datos
        }
        return TemplateResponse(request, 'admin/analysis/dashboard.html', context)

    def chat_monitor_view(self, request):
        # Lógica para monitor de chats
        context = {
            'active_chats': get_active_chats(),
            'agents': get_online_agents(),
            'alerts': get_system_alerts(),
            # ... más datos
        }
        return TemplateResponse(request, 'admin/chats/monitor.html', context)

# Usar el sitio personalizado
admin_site = CustomAdminSite(name='customadmin')
```

Este sistema de templates de administración proporciona una interfaz rica y funcional para gestionar todos los aspectos del sistema Chat With Us desde el panel de administración de Django.
