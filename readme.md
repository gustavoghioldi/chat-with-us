# Chat With Us - AI-Powered Chat Platform

A Django-based platform for creating and managing AI-powered chat agents with customizable knowledge bases and multi-tenant support.

## Features

- 🤖 AI Agent Management
- 💬 Real-time Chat Interface
- 📚 Knowledge Base Integration
- 🎯 Sentiment Analysis
- 👥 Multi-tenant Support
- 📊 Chat Analytics

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
     -p 5432:5432 \
     --name pgapp \
     postgres:latest
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

7. **Run the Development Server**
   ```bash
   python manage.py runserver
   ```

The application will be available at `http://localhost:8000`

## Documentation

For detailed documentation about the platform's architecture, APIs, and usage, please refer to [DOCUMENTATION.md](DOCUMENTATION.md)

## License

[Add your license information here]
