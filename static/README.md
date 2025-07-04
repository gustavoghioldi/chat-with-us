# Static Files - Archivos Estáticos

## Descripción General
Este directorio contiene todos los archivos estáticos del proyecto, incluyendo CSS, JavaScript, imágenes, fuentes y otros recursos que se sirven directamente al navegador.

## Estructura del Directorio

### `/admin/`
Archivos estáticos del panel de administración de Django:
- **CSS**: Estilos personalizados para el admin
- **JavaScript**: Scripts personalizados para el admin
- **Imágenes**: Iconos y recursos gráficos del admin
- **Fuentes**: Fuentes tipográficas específicas

### `/css/`
Hojas de estilo CSS del proyecto:

#### Archivos Principales
- **main.css**: Estilos principales de la aplicación
- **components.css**: Estilos de componentes reutilizables
- **layout.css**: Estilos de diseño y layout
- **themes.css**: Temas y variables de color
- **responsive.css**: Estilos responsivos para dispositivos móviles

#### Organización CSS
```css
/* main.css - Estructura principal */
:root {
  --primary-color: #007bff;
  --secondary-color: #6c757d;
  --success-color: #28a745;
  --danger-color: #dc3545;
  --warning-color: #ffc107;
  --info-color: #17a2b8;
}

/* Estilos base */
body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  line-height: 1.6;
  color: #333;
}

/* Componentes */
.chat-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.agent-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  padding: 20px;
  margin-bottom: 20px;
}
```

### `/js/`
Archivos JavaScript del proyecto:

#### Archivos Principales
- **main.js**: Funcionalidad principal
- **chat.js**: Funcionalidad del sistema de chat
- **agents.js**: Gestión de agentes
- **utils.js**: Utilidades y funciones auxiliares
- **api.js**: Comunicación con APIs

#### Estructura JavaScript
```javascript
// main.js - Funcionalidad principal
document.addEventListener('DOMContentLoaded', function() {
    // Inicialización de la aplicación
    initializeApp();

    // Configuración global
    window.AppConfig = {
        apiUrl: '/api/v1/',
        csrfToken: document.querySelector('[name=csrfmiddlewaretoken]').value
    };
});

// chat.js - Sistema de chat
class ChatManager {
    constructor(chatId) {
        this.chatId = chatId;
        this.websocket = null;
        this.initializeWebSocket();
    }

    initializeWebSocket() {
        const wsUrl = `ws://localhost:8000/ws/chat/${this.chatId}/`;
        this.websocket = new WebSocket(wsUrl);

        this.websocket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleMessage(data);
        };
    }

    sendMessage(message) {
        this.websocket.send(JSON.stringify({
            'message': message,
            'type': 'chat_message'
        }));
    }
}
```

### Librerías Externas
- **Bootstrap**: Framework CSS para diseño responsivo
- **jQuery**: Librería JavaScript para manipulación DOM
- **Chart.js**: Librería para gráficos y visualizaciones
- **FontAwesome**: Iconos vectoriales

## Gestión de Archivos Estáticos

### Configuración en Django
```python
# settings.py
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]
```

### Comando de Recolección
```bash
# Recolectar archivos estáticos para producción
python manage.py collectstatic

# Recolectar sin confirmación
python manage.py collectstatic --noinput

# Limpiar archivos estáticos antiguos
python manage.py collectstatic --clear
```

## Optimización

### Minificación CSS/JS
```python
# settings.py para producción
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

# Configuración de compresión
COMPRESS_ENABLED = True
COMPRESS_CSS_FILTERS = [
    'compressor.filters.css_default.CssAbsoluteFilter',
    'compressor.filters.cssmin.CSSMinFilter',
]
COMPRESS_JS_FILTERS = [
    'compressor.filters.jsmin.JSMinFilter',
]
```

### Versionado de Archivos
- Hash automático de archivos para cache busting
- Versionado basado en contenido
- Invalidación automática de caché

## Estructura de Estilos

### Metodología BEM (Block Element Modifier)
```css
/* Bloque */
.chat-window {
    background: white;
    border: 1px solid #ddd;
}

/* Elemento */
.chat-window__header {
    background: #f8f9fa;
    padding: 15px;
    border-bottom: 1px solid #ddd;
}

/* Modificador */
.chat-window--minimized {
    height: 50px;
    overflow: hidden;
}
```

### Variables CSS
```css
:root {
    /* Colores */
    --color-primary: #007bff;
    --color-secondary: #6c757d;
    --color-success: #28a745;
    --color-danger: #dc3545;

    /* Espaciado */
    --spacing-xs: 0.25rem;
    --spacing-sm: 0.5rem;
    --spacing-md: 1rem;
    --spacing-lg: 1.5rem;
    --spacing-xl: 3rem;

    /* Tipografía */
    --font-size-sm: 0.875rem;
    --font-size-base: 1rem;
    --font-size-lg: 1.125rem;
    --font-size-xl: 1.25rem;

    /* Breakpoints */
    --breakpoint-sm: 576px;
    --breakpoint-md: 768px;
    --breakpoint-lg: 992px;
    --breakpoint-xl: 1200px;
}
```

## Responsive Design

### Media Queries
```css
/* Mobile First */
.container {
    width: 100%;
    padding: 0 15px;
}

/* Tablet */
@media (min-width: 768px) {
    .container {
        max-width: 720px;
        margin: 0 auto;
    }
}

/* Desktop */
@media (min-width: 1024px) {
    .container {
        max-width: 1140px;
    }
}
```

### Grid System
```css
.grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 20px;
}

.grid-item {
    background: white;
    border-radius: 8px;
    padding: 20px;
}
```

## Componentes UI

### Componentes de Chat
```css
.chat-message {
    display: flex;
    margin-bottom: 15px;
    padding: 10px;
    border-radius: 8px;
}

.chat-message--user {
    background: #e3f2fd;
    margin-left: auto;
    max-width: 70%;
}

.chat-message--agent {
    background: #f5f5f5;
    margin-right: auto;
    max-width: 70%;
}

.chat-message__content {
    flex: 1;
}

.chat-message__timestamp {
    font-size: 0.8em;
    color: #666;
    margin-top: 5px;
}
```

### Componentes de Agentes
```css
.agent-card {
    background: white;
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    padding: 24px;
    margin-bottom: 20px;
    transition: transform 0.2s ease;
}

.agent-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 15px rgba(0, 0, 0, 0.15);
}

.agent-card__header {
    display: flex;
    align-items: center;
    margin-bottom: 16px;
}

.agent-card__avatar {
    width: 48px;
    height: 48px;
    border-radius: 50%;
    margin-right: 16px;
}

.agent-card__title {
    font-size: 1.25rem;
    font-weight: 600;
    color: #333;
}

.agent-card__description {
    color: #666;
    line-height: 1.5;
}
```

## JavaScript Modules

### Estructura Modular
```javascript
// modules/chat.js
export class ChatModule {
    constructor(options) {
        this.options = options;
        this.initialize();
    }

    initialize() {
        this.setupEventListeners();
        this.connectWebSocket();
    }

    setupEventListeners() {
        document.addEventListener('click', (e) => {
            if (e.target.matches('.send-message-btn')) {
                this.sendMessage();
            }
        });
    }
}

// modules/agents.js
export class AgentsModule {
    constructor() {
        this.agents = [];
        this.loadAgents();
    }

    async loadAgents() {
        try {
            const response = await fetch('/api/v1/agents/');
            this.agents = await response.json();
            this.renderAgents();
        } catch (error) {
            console.error('Error loading agents:', error);
        }
    }
}
```

### Gestión de Estados
```javascript
// State management
class AppState {
    constructor() {
        this.state = {
            currentUser: null,
            activeChat: null,
            agents: [],
            theme: 'light'
        };
        this.subscribers = [];
    }

    subscribe(callback) {
        this.subscribers.push(callback);
    }

    setState(newState) {
        this.state = { ...this.state, ...newState };
        this.subscribers.forEach(callback => callback(this.state));
    }
}
```

## Performance

### Optimizaciones CSS
- Uso de flexbox y grid para layouts
- Minimización de reflow y repaint
- Uso eficiente de selectores
- Carga condicional de estilos

### Optimizaciones JavaScript
- Lazy loading de módulos
- Debouncing de eventos
- Uso de Web Workers para tareas pesadas
- Caching de resultados

## Mantenimiento

### Linting y Formateo
```json
// .eslintrc.js
module.exports = {
    extends: ['eslint:recommended'],
    rules: {
        'no-unused-vars': 'warn',
        'no-console': 'warn',
        'indent': ['error', 2],
        'quotes': ['error', 'single']
    }
};

// .stylelintrc.js
module.exports = {
    extends: ['stylelint-config-standard'],
    rules: {
        'indentation': 2,
        'string-quotes': 'single'
    }
};
```

### Documentación de Estilos
- Guía de estilo visual
- Componentes documentados
- Ejemplos de uso
- Patrones de diseño
