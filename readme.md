# Chat With Us - AI-Powered Chat Platform

A comprehensive Django-based platform for creating and managing AI-powered chat agents with customizable knowledge bases, multi-tenant support, and advanced analytics capabilities.

## 🚀 Features

- 🤖 **AI Agent Management**: Create and configure intelligent agents with customizable instructions
- 💬 **Real-time Chat Interface**: Interactive chat system with sentiment analysis
- 📚 **Knowledge Base Integration**: Support for multiple document types (PDF, DOCX, CSV, JSON, Markdown)
- 🎯 **Sentiment Analysis**: Advanced chat sentiment detection and analysis
- 👥 **Multi-tenant Support**: Isolated environments for different organizations
- 📊 **Chat Analytics**: Comprehensive analytics and reporting
- 🔧 **Tool Integration**: Extensible tool system for agent capabilities
- 📝 **Document Management**: Advanced document processing and storage
- 🔄 **Automated Workflows**: Celery-based background task processing
- 🔐 **Security**: Built-in authentication and authorization
- 📈 **Scalability**: Designed for enterprise-level deployment

## 🏗️ Tech Stack

- **Backend**: Python 3.12.3, Django 5.2
- **Database**: PostgreSQL with pgvector (AI embeddings)
- **AI/ML**: Ollama AI, OpenAI API, Anthropic API
- **Cache/Queue**: Redis, Celery
- **Deployment**: Docker, Docker Compose
- **Documentation**: Automated changelog generation

## 📋 Prerequisites

- Docker and Docker Compose
- Python 3.12.3
- Git
- DBeaver (or preferred PostgreSQL client)
- Ollama (for local AI models)
- WSL2 (for Windows users)

## Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd chat-with-us
   ```

2. **Start project containers**
   ```bash
   docker compose up -d
   ```
   this will set up pgvector, postgres, grafana and redis
3. **If having any problem with psycopg:**
   ```bash
   sudo apt-get update
   sudo apt-get install libpq-dev
   ```
   
4. **Set up Python Environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

5. **Environment Configuration**
   ```bash
   # Request and copy the .env file to the project root
   ```

6. **Initialize Database**
   ```bash
   python manage.py migrate
   ```

7. **Run the Development Server**
   ```bash
   python manage.py runserver
   ```

8. **Run Celery**
     ```bash
     celery -A main worker --loglevel=info
     ```
    
9. **Import grafana configuration**
    </br>Grafana is available at `http://localhost:3000`.
    </br>Admin credentials are ``` USER: admin PASSWORD: admin```.
    </br>You can change them on your first login.

----
The application will be available at `http://localhost:8000`

## Development Workflow

### Pre-commit Hooks

This project uses pre-commit hooks to maintain code quality and documentation. The following hooks are configured:

1. **Code Quality**
   - Black for code formatting
   - isort for import sorting
   - flake8 for code linting

2. **Automated Changelog**
   - Every commit automatically updates `CHANGELOG.md`
   - Changes are categorized and dated
   - Modified files are tracked

3. **Other Checks**
   - Trailing whitespace removal
   - End of file fixing
   - YAML validation
   - Large file checks

### Using the Changelog

The `CHANGELOG.md` file is automatically updated with every commit. The changes are organized in the following format:

```markdown
### YYYY-MM-DD HH:MM:SS
- Commit message
  Changed files:
  - file1.py
  - file2.py
```

This helps track changes and maintain a clear project history.

## Documentation

For detailed documentation about the platform's architecture, APIs, and usage, please refer to [DOCUMENTATION.md](DOCUMENTATION.md)

## 🏢 Project Structure

```
chat-with-us/
├── agents/          # AI Agent management and configuration
├── analysis/        # Chat analytics and sentiment analysis
├── api/             # REST API endpoints and serializers
├── chats/           # Chat functionality and message handling
├── crews/           # Agent crew management
├── documents/       # Document processing and storage
├── examples/        # Sample data and test files
├── knowledge/       # Knowledge base management
├── logs/            # Application logs
├── main/            # Django project settings and configuration
├── media/           # User-uploaded media files
├── static/          # Static assets (CSS, JS, images)
├── templates/       # HTML templates
├── tenants/         # Multi-tenant support
├── tools/           # Extensible tool system for agents
├── manage.py        # Django management script
└── requirements.txt # Python dependencies
```

## � Documentación Completa

Cada módulo y directorio del proyecto cuenta con documentación detallada:

### Módulos Principales
- **[agents/](agents/README.md)**: Sistema de agentes de IA
- **[analysis/](analysis/README.md)**: Análisis y métricas de chat
- **[api/](api/README.md)**: API RESTful del sistema
- **[chats/](chats/README.md)**: Sistema de mensajería
- **[crews/](crews/README.md)**: Gestión de equipos de agentes
- **[documents/](documents/README.md)**: Procesamiento de documentos
- **[knowledge/](knowledge/README.md)**: Base de conocimiento
- **[tenants/](tenants/README.md)**: Sistema multi-tenant
- **[tools/](tools/README.md)**: Herramientas para agentes

### Infraestructura
- **[main/](main/README.md)**: Configuración principal de Django
- **[static/](static/README.md)**: Archivos estáticos (CSS, JS)
- **[templates/](templates/README.md)**: Plantillas HTML
- **[media/](media/README.md)**: Archivos multimedia
- **[logs/](logs/README.md)**: Sistema de logging

### Subdirectorios Especializados
- **[main/settings/](main/settings/README.md)**: Configuraciones por ambiente
- **[main/management/](main/management/README.md)**: Comandos de gestión
- **[tools/kit/](tools/kit/README.md)**: Kit de herramientas
- **[tools/models/](tools/models/README.md)**: Modelos de herramientas
- **[tools/services/](tools/services/README.md)**: Servicios de herramientas
- **[tools/dtos/](tools/dtos/README.md)**: Objetos de transferencia de datos
- **[analysis/models/](analysis/models/README.md)**: Modelos de análisis
- **[analysis/services/](analysis/services/README.md)**: Servicios de análisis
- **[analysis/serializers/](analysis/serializers/README.md)**: Serializadores de análisis
- **[analysis/views/](analysis/views/README.md)**: Vistas de análisis
- **[analysis/signals/](analysis/signals/README.md)**: Señales de análisis
- **[analysis/tests/](analysis/tests/README.md)**: Tests de análisis
- **[agents/services/](agents/services/README.md)**: Servicios de agentes
- **[api/permissions_classes/](api/permissions_classes/README.md)**: Clases de permisos
- **[api/serializers/](api/serializers/README.md)**: Serializadores de API
- **[api/services/](api/services/README.md)**: Servicios de API
- **[api/views/](api/views/README.md)**: Vistas de API
- **[chats/signals/](chats/signals/README.md)**: Señales de chat
- **[documents/management/commands/](documents/management/commands/README.md)**: Comandos de documentos
- **[documents/signals/](documents/signals/README.md)**: Señales de documentos
- **[knowledge/forms/](knowledge/forms/README.md)**: Formularios de conocimiento
- **[knowledge/services/](knowledge/services/README.md)**: Servicios de conocimiento
- **[knowledge/views/](knowledge/views/README.md)**: Vistas de conocimiento
- **[knowledge/signals/](knowledge/signals/README.md)**: Señales de conocimiento
- **[templates/UI/](templates/UI/README.md)**: Interfaz de usuario
- **[templates/admin/](templates/admin/README.md)**: Templates de administración

### Migraciones de Base de Datos
- **[agents/migrations/](agents/migrations/README.md)**: Migraciones de agentes
- **[analysis/migrations/](analysis/migrations/README.md)**: Migraciones de análisis
- **[chats/migrations/](chats/migrations/README.md)**: Migraciones de chat
- **[documents/migrations/](documents/migrations/README.md)**: Migraciones de documentos
- **[knowledge/migrations/](knowledge/migrations/README.md)**: Migraciones de conocimiento
- **[tenants/migrations/](tenants/migrations/README.md)**: Migraciones de tenants
- **[tools/migrations/](tools/migrations/README.md)**: Migraciones de herramientas

### Tests y Configuraciones
- **[agents/tests/](agents/tests/README.md)**: Tests de agentes
- **[agents/services/configurators/](agents/services/configurators/README.md)**: Configuradores de agentes

Para información detallada sobre arquitectura y APIs, consulte la documentación específica de cada módulo.

## 📊 Key Features

### AI Agent Management
- Create custom AI agents with specific instructions
- Configure agent parameters (temperature, max tokens, etc.)
- Link agents to knowledge bases and tools
- Support for multiple AI models (OpenAI, Anthropic, Ollama)

### Knowledge Base Integration
- Support for multiple document formats (PDF, DOCX, CSV, JSON, Markdown)
- Automatic text extraction and processing
- Vector-based similarity search
- Real-time knowledge base updates

### Multi-tenant Architecture
- Complete data isolation between tenants
- Tenant-specific configurations
- User management per tenant
- Scalable multi-organization support

### Advanced Analytics
- Real-time sentiment analysis
- Chat performance metrics
- User engagement tracking
- Custom reporting dashboards

## License

[Add your license information here]

## 🤝 Contributing

Please read our contributing guidelines before submitting pull requests.

## 📞 Support

For support and questions, please contact the development team.
