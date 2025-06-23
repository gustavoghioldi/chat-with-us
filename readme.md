# Chat With Us - AI-Powered Chat Platform

A Django-based platform for creating and managing AI-powered chat agents with customizable knowledge bases and multi-tenant support.

## Features

- 🤖 AI Agent Management
- 💬 Real-time Chat Interface
- 📚 Knowledge Base Integration
- 🎯 Sentiment Analysis
- 👥 Multi-tenant Support
- 📊 Chat Analytics
- 📝 Automated Changelog

## Tech Stack

- Python 3.12.3
- Django 5.2
- PostgreSQL with pgvector
- Ollama AI
- Redis
- Celery
- Docker

## Prerequisites

- Docker
- Ollama
- Git
- DBeaver (or any other DB management tool)
- Python 3.12.3
- WSL2 (for Windows users)

## Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd chat-with-us
   ```

2. **Start PostgreSQL Containers**
   ```bash
   # AI Database with vector support
   docker run -d \
     -e POSTGRES_DB=ai \
     -e POSTGRES_USER=ai \
     -e POSTGRES_PASSWORD=ai \
     -e PGDATA=/var/lib/postgresql/data/pgdata \
     -v pgvolume:/var/lib/postgresql/data \
     -p 5532:5432 \
     --name pgvector \
     agnohq/pgvector:16

   # Application Database
   docker run -d \
     -e POSTGRES_PASSWORD=barba \
     -v appvolume:/var/lib/postgresql/data \
     -p 5632:5432 \
     --name pgapp \
     postgres:latest
   ```
2. **If having any problem with psycopg:**
   ```bash
   sudo apt-get update
   sudo apt-get install libpq-dev
   ```

3. **Create Database**
   - Open DBeaver
   - Create a new database named `barbadb`

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
7. **Run redis**
   ```bash
   docker run -p 6379:6379 redis
   ```

8. **Run the Development Server**
   ```bash
   python manage.py runserver
   ```

9. **Run Celery**
     ```
     celery -A main worker --loglevel=info
     ```
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

## License

[Add your license information here]
