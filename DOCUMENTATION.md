# Chat With Us - Technical Documentation

## Overview

Chat With Us is an advanced AI-powered chat platform built with Django that enables organizations to create and manage intelligent chat agents. The platform supports multiple tenants, each with their own set of agents, knowledge bases, and chat analytics.

## System Architecture

### Core Components

1. **Tenant Management (`tenants` app)**
   - Handles multi-tenant support
   - Manages tenant-specific configurations
   - Controls access to AI models (Ollama, Bedrock)

2. **Agent System (`agents` app)**
   - Creates and manages AI agents
   - Configures agent behaviors and instructions
   - Links agents with knowledge bases
   - Handles agent-tenant relationships

3. **Knowledge Base (`knowledge` app)**
   - Manages various types of knowledge sources
   - Supports plain documents and websites
   - Processes and stores information for agent consumption

4. **Chat System (`chats` app)**
   - Handles chat sessions and message history
   - Manages real-time communication
   - Stores chat content and metadata

5. **Analytics System (`analysis` app)**
   - Performs sentiment analysis on chat messages
   - Tracks chat metrics and statistics
   - Generates insights from conversations

6. **API Layer (`api` app)**
   - Provides RESTful endpoints for chat interactions
   - Handles chat session management
   - Processes incoming messages and responses

### Database Structure

1. **Tenant Model**
   - Name
   - Description
   - AI Model Configuration (Ollama/Bedrock)

2. **Agent Model**
   - Name
   - Instructions
   - Knowledge Base References
   - Tenant Reference
   - Model Configuration

3. **Knowledge Model**
   - Name
   - Category (plain_document/website)
   - Content (URL or text)
   - Description

4. **Chat Model**
   - Session ID (UUID)
   - Agent Reference
   - Creation/Update Timestamps

5. **Content Chat Model**
   - Chat Reference
   - Request Content
   - Response Content

6. **Sentiment Analysis Model**
   - Chat Content Reference
   - Sentiment (Positive/Negative/Neutral)
   - Analysis Cause

## Key Features

### 1. AI Agent Management
- Create and configure AI agents
- Customize agent instructions
- Assign knowledge bases to agents
- Configure AI model parameters

### 2. Knowledge Base Integration
- Import documents and websites
- Process and store information
- Link knowledge to specific agents
- Update and manage knowledge sources

### 3. Multi-tenant Support
- Isolated tenant environments
- Tenant-specific configurations
- Separate agent management
- Independent knowledge bases

### 4. Chat Analytics
- Real-time sentiment analysis
- Chat metrics tracking
- Performance analytics
- User interaction insights

### 5. API Integration
- RESTful API endpoints
- Secure communication
- Session management
- Real-time message processing

## Technical Implementation

### Authentication & Security
- Django's built-in authentication system
- CSRF protection
- Tenant isolation
- Secure API endpoints

### Data Processing
- Celery for asynchronous tasks
- Redis for caching and message queuing
- PostgreSQL with pgvector for vector storage
- Ollama AI for language processing

### Real-time Features
- Asynchronous message processing
- Real-time sentiment analysis
- Live chat session management
- Immediate agent responses

## API Documentation

### Chat Endpoint
`POST /api/v1/chat`

Request Body:
```json
{
    "agent": "agent_id",
    "message": "user_message",
    "session_id": "optional_session_id"
}
```

Response:
```json
{
    "agent": "agent_id",
    "message": "user_message",
    "session_id": "session_id",
    "response": "agent_response"
}
```

## Development Guidelines

1. **Code Style**
   - Follow PEP 8 guidelines
   - Use meaningful variable names
   - Include docstrings and comments
   - Maintain consistent formatting

2. **Testing**
   - Write unit tests for models and views
   - Include integration tests
   - Test API endpoints
   - Validate multi-tenant functionality

3. **Security**
   - Validate all inputs
   - Sanitize outputs
   - Implement proper authentication
   - Maintain tenant isolation

4. **Performance**
   - Use database indexes
   - Implement caching
   - Optimize queries
   - Monitor resource usage

## Deployment

The application is containerized using Docker and can be deployed using Docker Compose or Kubernetes. Key components:

- Django application server
- PostgreSQL databases (App DB and Vector DB)
- Redis server
- Celery workers
- Ollama AI service

## Maintenance

1. **Database Backups**
   - Regular automated backups
   - Backup verification
   - Recovery procedures

2. **Monitoring**
   - System health checks
   - Performance metrics
   - Error logging
   - Usage statistics

3. **Updates**
   - Security patches
   - Dependency updates
   - Feature additions
   - Bug fixes

## Troubleshooting

Common issues and their solutions:

1. **Database Connectivity**
   - Check PostgreSQL service status
   - Verify connection settings
   - Validate credentials

2. **AI Model Issues**
   - Verify Ollama service status
   - Check model availability
   - Validate API keys

3. **Performance Problems**
   - Monitor database queries
   - Check cache hit rates
   - Analyze server resources
   - Review log files
