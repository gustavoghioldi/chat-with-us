# Templates UI - Interfaz de Usuario

## Descripción General
Este directorio contiene las plantillas HTML para la interfaz de usuario principal del sistema Chat With Us. Incluye componentes modernos, responsive y accesibles para proporcionar una experiencia de usuario óptima.

## Estructura del Directorio

### `/chat-ui/`
Plantillas específicas para la interfaz de chat interactivo:
- Componentes de chat en tiempo real
- Interfaces de conversación con agentes
- Elementos de UI para mensajes y respuestas
- Componentes de carga y estados

## Componentes Principales

### 1. Chat Interface Components

#### Base Chat Template
```html
<!-- chat-ui/base_chat.html -->
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Chat{% endblock %} - Chat With Us</title>

    <!-- CSS -->
    {% load static %}
    <link rel="stylesheet" href="{% static 'css/chat.css' %}">
    <link rel="stylesheet" href="{% static 'css/components/chat-bubble.css' %}">
    <link rel="stylesheet" href="{% static 'css/components/typing-indicator.css' %}">

    <!-- WebSocket y JavaScript -->
    <script src="{% static 'js/websocket-client.js' %}"></script>
    <script src="{% static 'js/chat-handler.js' %}"></script>

    {% block extra_css %}{% endblock %}
</head>
<body class="chat-interface">
    <div class="chat-container">
        <!-- Header del Chat -->
        <div class="chat-header">
            <div class="agent-info">
                <div class="agent-avatar">
                    <img src="{% static 'images/agent-avatar.png' %}" alt="Agent">
                </div>
                <div class="agent-details">
                    <h3>{{ agent.name }}</h3>
                    <span class="agent-status">{{ agent.status }}</span>
                </div>
            </div>
            <div class="chat-actions">
                <button class="btn-minimize" title="Minimizar">
                    <i class="icon-minimize"></i>
                </button>
                <button class="btn-close" title="Cerrar">
                    <i class="icon-close"></i>
                </button>
            </div>
        </div>

        <!-- Área de Mensajes -->
        <div class="chat-messages" id="chat-messages">
            {% block messages %}
                {% for message in messages %}
                    {% include 'UI/chat-ui/components/message.html' with message=message %}
                {% endfor %}
            {% endblock %}
        </div>

        <!-- Indicador de Escritura -->
        <div class="typing-indicator" id="typing-indicator" style="display: none;">
            <div class="typing-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
            <span class="typing-text">El agente está escribiendo...</span>
        </div>

        <!-- Input de Mensaje -->
        <div class="chat-input-container">
            <form class="chat-input-form" id="chat-form">
                {% csrf_token %}
                <div class="input-group">
                    <textarea
                        class="chat-input"
                        id="message-input"
                        placeholder="Escribe tu mensaje aquí..."
                        rows="1"
                        maxlength="2000"
                    ></textarea>
                    <button type="submit" class="btn-send" id="send-button">
                        <i class="icon-send"></i>
                    </button>
                </div>
                <div class="input-actions">
                    <button type="button" class="btn-attach" title="Adjuntar archivo">
                        <i class="icon-attach"></i>
                    </button>
                    <button type="button" class="btn-emoji" title="Emojis">
                        <i class="icon-emoji"></i>
                    </button>
                    <span class="char-count">0/2000</span>
                </div>
            </form>
        </div>
    </div>

    {% block extra_js %}{% endblock %}
</body>
</html>
```

#### Message Component
```html
<!-- chat-ui/components/message.html -->
<div class="message {% if message.is_from_user %}message-user{% else %}message-agent{% endif %}"
     data-message-id="{{ message.id }}">

    <div class="message-avatar">
        {% if message.is_from_user %}
            <img src="{{ message.user.avatar.url|default:'/static/images/user-avatar.png' }}"
                 alt="{{ message.user.name }}">
        {% else %}
            <img src="{{ message.agent.avatar.url|default:'/static/images/agent-avatar.png' }}"
                 alt="{{ message.agent.name }}">
        {% endif %}
    </div>

    <div class="message-content">
        <div class="message-header">
            <span class="message-author">
                {% if message.is_from_user %}
                    {{ message.user.name }}
                {% else %}
                    {{ message.agent.name }}
                {% endif %}
            </span>
            <span class="message-timestamp">
                {{ message.created_at|date:"H:i" }}
            </span>
        </div>

        <div class="message-body">
            {% if message.message_type == 'text' %}
                <p class="message-text">{{ message.content|linebreaks }}</p>
            {% elif message.message_type == 'image' %}
                <div class="message-image">
                    <img src="{{ message.attachment.url }}" alt="Imagen">
                </div>
            {% elif message.message_type == 'file' %}
                <div class="message-file">
                    <i class="icon-file"></i>
                    <a href="{{ message.attachment.url }}" download>
                        {{ message.attachment.name }}
                    </a>
                </div>
            {% elif message.message_type == 'quick_reply' %}
                <div class="message-quick-replies">
                    {% for reply in message.quick_replies %}
                        <button class="quick-reply-btn" data-reply="{{ reply.value }}">
                            {{ reply.text }}
                        </button>
                    {% endfor %}
                </div>
            {% endif %}
        </div>

        {% if message.reactions %}
            <div class="message-reactions">
                {% for reaction in message.reactions %}
                    <span class="reaction" data-reaction="{{ reaction.type }}">
                        {{ reaction.emoji }} {{ reaction.count }}
                    </span>
                {% endfor %}
            </div>
        {% endif %}
    </div>

    <div class="message-actions">
        <button class="btn-react" title="Reaccionar">
            <i class="icon-react"></i>
        </button>
        <button class="btn-copy" title="Copiar">
            <i class="icon-copy"></i>
        </button>
        {% if message.is_from_user %}
            <button class="btn-edit" title="Editar">
                <i class="icon-edit"></i>
            </button>
        {% endif %}
    </div>
</div>
```

#### Chat List Template
```html
<!-- chat-ui/chat_list.html -->
{% extends 'UI/chat-ui/base_chat.html' %}

{% block title %}Mis Chats{% endblock %}

{% block extra_css %}
    <link rel="stylesheet" href="{% static 'css/chat-list.css' %}">
{% endblock %}

{% block content %}
<div class="chat-list-container">
    <div class="chat-list-header">
        <h2>Mis Conversaciones</h2>
        <button class="btn-new-chat" id="new-chat-btn">
            <i class="icon-plus"></i>
            Nuevo Chat
        </button>
    </div>

    <div class="chat-search">
        <div class="search-box">
            <input type="text"
                   class="search-input"
                   placeholder="Buscar conversaciones..."
                   id="chat-search">
            <i class="icon-search"></i>
        </div>
    </div>

    <div class="chat-filters">
        <button class="filter-btn active" data-filter="all">
            Todas
        </button>
        <button class="filter-btn" data-filter="active">
            Activas
        </button>
        <button class="filter-btn" data-filter="archived">
            Archivadas
        </button>
    </div>

    <div class="chat-list" id="chat-list">
        {% for chat in chats %}
            <div class="chat-item {% if chat.unread_count > 0 %}unread{% endif %}"
                 data-chat-id="{{ chat.id }}">

                <div class="chat-avatar">
                    <img src="{{ chat.agent.avatar.url|default:'/static/images/agent-avatar.png' }}"
                         alt="{{ chat.agent.name }}">
                    {% if chat.agent.is_online %}
                        <span class="online-indicator"></span>
                    {% endif %}
                </div>

                <div class="chat-info">
                    <div class="chat-header">
                        <h4 class="chat-title">{{ chat.title|default:chat.agent.name }}</h4>
                        <span class="chat-time">
                            {{ chat.last_message.created_at|timesince }}
                        </span>
                    </div>

                    <div class="chat-preview">
                        <p class="last-message">
                            {% if chat.last_message.is_from_user %}
                                <span class="message-sender">Tú:</span>
                            {% endif %}
                            {{ chat.last_message.content|truncatechars:50 }}
                        </p>

                        {% if chat.unread_count > 0 %}
                            <span class="unread-badge">{{ chat.unread_count }}</span>
                        {% endif %}
                    </div>
                </div>

                <div class="chat-actions">
                    <button class="btn-archive" title="Archivar">
                        <i class="icon-archive"></i>
                    </button>
                    <button class="btn-delete" title="Eliminar">
                        <i class="icon-delete"></i>
                    </button>
                </div>
            </div>
        {% empty %}
            <div class="empty-state">
                <i class="icon-chat-empty"></i>
                <h3>No tienes conversaciones</h3>
                <p>Inicia una nueva conversación con uno de nuestros agentes</p>
                <button class="btn-primary" id="start-chat-btn">
                    Iniciar Chat
                </button>
            </div>
        {% endfor %}
    </div>
</div>

<!-- Modal para Nuevo Chat -->
<div class="modal" id="new-chat-modal">
    <div class="modal-content">
        <div class="modal-header">
            <h3>Nuevo Chat</h3>
            <button class="btn-close" data-close-modal>
                <i class="icon-close"></i>
            </button>
        </div>

        <div class="modal-body">
            <div class="agent-selection">
                <h4>Selecciona un agente:</h4>
                <div class="agent-grid">
                    {% for agent in available_agents %}
                        <div class="agent-card" data-agent-id="{{ agent.id }}">
                            <div class="agent-avatar">
                                <img src="{{ agent.avatar.url|default:'/static/images/agent-avatar.png' }}"
                                     alt="{{ agent.name }}">
                                {% if agent.is_online %}
                                    <span class="online-indicator"></span>
                                {% endif %}
                            </div>
                            <div class="agent-info">
                                <h5>{{ agent.name }}</h5>
                                <p>{{ agent.description|truncatechars:80 }}</p>
                                <div class="agent-stats">
                                    <span class="rating">
                                        <i class="icon-star"></i>
                                        {{ agent.rating|floatformat:1 }}
                                    </span>
                                    <span class="response-time">
                                        ~{{ agent.avg_response_time }}s
                                    </span>
                                </div>
                            </div>
                        </div>
                    {% endfor %}
                </div>
            </div>
        </div>

        <div class="modal-footer">
            <button class="btn-secondary" data-close-modal>
                Cancelar
            </button>
            <button class="btn-primary" id="create-chat-btn" disabled>
                Crear Chat
            </button>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
    <script src="{% static 'js/chat-list.js' %}"></script>
{% endblock %}
```

## Estilos CSS

### Chat Styles
```css
/* chat.css */
.chat-interface {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    margin: 0;
    padding: 0;
    height: 100vh;
    overflow: hidden;
}

.chat-container {
    display: flex;
    flex-direction: column;
    height: 100vh;
    max-width: 800px;
    margin: 0 auto;
    background: white;
    border-radius: 12px;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
    overflow: hidden;
}

.chat-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 20px;
    background: #f8f9fa;
    border-bottom: 1px solid #e9ecef;
}

.agent-info {
    display: flex;
    align-items: center;
    gap: 12px;
}

.agent-avatar img {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    object-fit: cover;
}

.agent-details h3 {
    margin: 0;
    font-size: 16px;
    font-weight: 600;
    color: #2c3e50;
}

.agent-status {
    font-size: 12px;
    color: #27ae60;
    display: flex;
    align-items: center;
    gap: 4px;
}

.agent-status::before {
    content: '';
    width: 8px;
    height: 8px;
    background: #27ae60;
    border-radius: 50%;
}

.chat-messages {
    flex: 1;
    overflow-y: auto;
    padding: 20px;
    background: #ffffff;
    scroll-behavior: smooth;
}

.message {
    display: flex;
    gap: 12px;
    margin-bottom: 16px;
    opacity: 0;
    animation: fadeInUp 0.3s ease forwards;
}

.message-user {
    flex-direction: row-reverse;
}

.message-user .message-content {
    background: #007bff;
    color: white;
    margin-left: auto;
}

.message-agent .message-content {
    background: #f8f9fa;
    color: #2c3e50;
}

.message-content {
    max-width: 70%;
    padding: 12px 16px;
    border-radius: 18px;
    position: relative;
}

.message-text {
    margin: 0;
    line-height: 1.4;
    word-wrap: break-word;
}

.typing-indicator {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 12px 20px;
    background: #f8f9fa;
    border-top: 1px solid #e9ecef;
}

.typing-dots {
    display: flex;
    gap: 4px;
}

.typing-dots span {
    width: 8px;
    height: 8px;
    background: #6c757d;
    border-radius: 50%;
    animation: typing 1.4s infinite;
}

.typing-dots span:nth-child(2) {
    animation-delay: 0.2s;
}

.typing-dots span:nth-child(3) {
    animation-delay: 0.4s;
}

.chat-input-container {
    padding: 20px;
    background: #f8f9fa;
    border-top: 1px solid #e9ecef;
}

.input-group {
    display: flex;
    gap: 12px;
    align-items: flex-end;
}

.chat-input {
    flex: 1;
    padding: 12px 16px;
    border: 2px solid #e9ecef;
    border-radius: 24px;
    resize: none;
    outline: none;
    font-family: inherit;
    font-size: 14px;
    line-height: 1.4;
    transition: border-color 0.2s ease;
}

.chat-input:focus {
    border-color: #007bff;
}

.btn-send {
    width: 44px;
    height: 44px;
    border: none;
    border-radius: 50%;
    background: #007bff;
    color: white;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: background 0.2s ease;
}

.btn-send:hover {
    background: #0056b3;
}

.btn-send:disabled {
    background: #6c757d;
    cursor: not-allowed;
}

@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes typing {
    0%, 60%, 100% {
        transform: translateY(0);
    }
    30% {
        transform: translateY(-10px);
    }
}

/* Responsive Design */
@media (max-width: 768px) {
    .chat-container {
        height: 100vh;
        border-radius: 0;
    }

    .message-content {
        max-width: 85%;
    }

    .chat-header {
        padding: 12px 16px;
    }

    .chat-messages {
        padding: 16px;
    }

    .chat-input-container {
        padding: 16px;
    }
}
```

## JavaScript Functionality

### Chat Handler
```javascript
// chat-handler.js
class ChatHandler {
    constructor() {
        this.chatContainer = document.getElementById('chat-messages');
        this.messageInput = document.getElementById('message-input');
        this.sendButton = document.getElementById('send-button');
        this.chatForm = document.getElementById('chat-form');
        this.typingIndicator = document.getElementById('typing-indicator');

        this.initializeEventListeners();
        this.initializeWebSocket();
    }

    initializeEventListeners() {
        this.chatForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.sendMessage();
        });

        this.messageInput.addEventListener('input', () => {
            this.handleInputChange();
        });

        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
    }

    initializeWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/chat/${this.chatId}/`;

        this.socket = new WebSocket(wsUrl);

        this.socket.onopen = () => {
            console.log('WebSocket connection established');
        };

        this.socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleIncomingMessage(data);
        };

        this.socket.onclose = () => {
            console.log('WebSocket connection closed');
            this.reconnectWebSocket();
        };

        this.socket.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
    }

    sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message) return;

        // Mostrar mensaje del usuario inmediatamente
        this.displayMessage({
            content: message,
            is_from_user: true,
            timestamp: new Date().toISOString()
        });

        // Enviar mensaje por WebSocket
        this.socket.send(JSON.stringify({
            type: 'chat_message',
            message: message
        }));

        // Limpiar input
        this.messageInput.value = '';
        this.updateSendButton();

        // Mostrar indicador de escritura
        this.showTypingIndicator();
    }

    handleIncomingMessage(data) {
        switch (data.type) {
            case 'chat_message':
                this.hideTypingIndicator();
                this.displayMessage(data.message);
                break;
            case 'typing_start':
                this.showTypingIndicator();
                break;
            case 'typing_stop':
                this.hideTypingIndicator();
                break;
            case 'error':
                this.showError(data.message);
                break;
        }
    }

    displayMessage(message) {
        const messageElement = this.createMessageElement(message);
        this.chatContainer.appendChild(messageElement);
        this.scrollToBottom();
    }

    createMessageElement(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${message.is_from_user ? 'message-user' : 'message-agent'}`;

        messageDiv.innerHTML = `
            <div class="message-avatar">
                <img src="${message.avatar || '/static/images/default-avatar.png'}"
                     alt="${message.author}">
            </div>
            <div class="message-content">
                <div class="message-header">
                    <span class="message-author">${message.author}</span>
                    <span class="message-timestamp">${this.formatTimestamp(message.timestamp)}</span>
                </div>
                <div class="message-body">
                    <p class="message-text">${this.escapeHtml(message.content)}</p>
                </div>
            </div>
        `;

        return messageDiv;
    }

    showTypingIndicator() {
        this.typingIndicator.style.display = 'flex';
        this.scrollToBottom();
    }

    hideTypingIndicator() {
        this.typingIndicator.style.display = 'none';
    }

    scrollToBottom() {
        this.chatContainer.scrollTop = this.chatContainer.scrollHeight;
    }

    formatTimestamp(timestamp) {
        const date = new Date(timestamp);
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    handleInputChange() {
        this.updateSendButton();
        this.updateCharCount();
        this.autoResize();
    }

    updateSendButton() {
        const hasContent = this.messageInput.value.trim().length > 0;
        this.sendButton.disabled = !hasContent;
    }

    updateCharCount() {
        const charCount = this.messageInput.value.length;
        const charCountElement = document.querySelector('.char-count');
        if (charCountElement) {
            charCountElement.textContent = `${charCount}/2000`;
        }
    }

    autoResize() {
        this.messageInput.style.height = 'auto';
        this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 120) + 'px';
    }

    reconnectWebSocket() {
        setTimeout(() => {
            this.initializeWebSocket();
        }, 3000);
    }

    showError(message) {
        // Mostrar mensaje de error
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = message;
        this.chatContainer.appendChild(errorDiv);
        this.scrollToBottom();
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    new ChatHandler();
});
```

## Características Avanzadas

### 1. **Responsive Design**
- Adaptable a diferentes tamaños de pantalla
- Optimizado para dispositivos móviles
- Interfaz fluida y accesible

### 2. **Real-time Communication**
- WebSocket para mensajes en tiempo real
- Indicadores de escritura
- Estado de conexión

### 3. **Accessibility**
- Navegación por teclado
- Lectores de pantalla compatibles
- Contraste adecuado

### 4. **Performance**
- Lazy loading de mensajes
- Optimización de imágenes
- Caching de componentes

### 5. **User Experience**
- Animaciones suaves
- Feedback visual
- Estados de carga

## Integración con Backend

### WebSocket Views
```python
# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.chat_group_name = f'chat_{self.chat_id}'

        await self.channel_layer.group_add(
            self.chat_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.chat_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']

        # Procesar mensaje con agente
        response = await self.process_message_with_agent(message)

        # Enviar respuesta al grupo
        await self.channel_layer.group_send(
            self.chat_group_name,
            {
                'type': 'chat_message',
                'message': response
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message']
        }))
```

## Testing

### Frontend Tests
```javascript
// chat-handler.test.js
describe('ChatHandler', () => {
    let chatHandler;

    beforeEach(() => {
        document.body.innerHTML = `
            <div id="chat-messages"></div>
            <input id="message-input" />
            <button id="send-button"></button>
            <form id="chat-form"></form>
        `;

        chatHandler = new ChatHandler();
    });

    test('should send message on form submit', () => {
        const messageInput = document.getElementById('message-input');
        messageInput.value = 'Test message';

        const sendSpy = jest.spyOn(chatHandler, 'sendMessage');

        document.getElementById('chat-form').dispatchEvent(new Event('submit'));

        expect(sendSpy).toHaveBeenCalled();
    });

    test('should display incoming message', () => {
        const message = {
            content: 'Hello world',
            is_from_user: false,
            timestamp: new Date().toISOString()
        };

        chatHandler.displayMessage(message);

        const messageElements = document.querySelectorAll('.message');
        expect(messageElements.length).toBe(1);
        expect(messageElements[0].textContent).toContain('Hello world');
    });
});
```

Este módulo de templates UI proporciona una interfaz de chat moderna, responsive y funcional con características avanzadas para una experiencia de usuario óptima.
