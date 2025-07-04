# Vistas de API

## Descripción General
Este directorio contiene las vistas de la API REST del sistema. Las vistas manejan las peticiones HTTP y coordinan entre los serializadores, servicios y modelos para proporcionar respuestas JSON.

## Estructura de Archivos

### `agents_view.py`
Vistas para la gestión de agentes de IA.

```python
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from agents.models import AgentModel
from api.serializers.agent_serializer import AgentSerializer
from api.permissions_classes.is_tenant_authenticated import IsTenantAuthenticated

class AgentViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de agentes.

    Endpoints:
    - GET /api/agents/ - Lista todos los agentes
    - POST /api/agents/ - Crea un nuevo agente
    - GET /api/agents/{id}/ - Obtiene un agente específico
    - PUT /api/agents/{id}/ - Actualiza un agente
    - DELETE /api/agents/{id}/ - Elimina un agente
    """

    serializer_class = AgentSerializer
    permission_classes = [IsTenantAuthenticated]

    def get_queryset(self):
        """Filtra agentes por tenant."""
        tenant_id = self.request.META.get('HTTP_X_TENANT_ID')
        return AgentModel.objects.filter(tenant_id=tenant_id)

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activa un agente específico."""
        agent = self.get_object()
        agent.is_active = True
        agent.save()
        return Response({'status': 'Agent activated'})

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Desactiva un agente específico."""
        agent = self.get_object()
        agent.is_active = False
        agent.save()
        return Response({'status': 'Agent deactivated'})

    @action(detail=True, methods=['get'])
    def performance(self, request, pk=None):
        """Obtiene métricas de rendimiento del agente."""
        agent = self.get_object()
        # Calcular métricas
        metrics = {
            'total_conversations': agent.conversations.count(),
            'average_response_time': agent.get_average_response_time(),
            'success_rate': agent.get_success_rate(),
        }
        return Response(metrics)
```

### `chat_view.py`
Vistas para la gestión de chats y conversaciones.

```python
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from chats.models import Chat, Message
from api.serializers.chat_serializer import ChatSerializer, MessageSerializer
from agents.services.agent_service import AgentService

class ChatViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de chats.
    """

    serializer_class = ChatSerializer
    permission_classes = [IsTenantAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Chat.objects.filter(user=user)

    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        """Envía un mensaje en el chat."""
        chat = self.get_object()
        message_content = request.data.get('message')

        if not message_content:
            return Response(
                {'error': 'Message content is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Crear mensaje del usuario
        user_message = Message.objects.create(
            chat=chat,
            content=message_content,
            sender='user'
        )

        # Generar respuesta del agente
        agent_service = AgentService()
        response = agent_service.generate_response(
            agent_id=chat.agent.id,
            message=message_content,
            context={'chat_id': chat.id}
        )

        # Crear mensaje del agente
        agent_message = Message.objects.create(
            chat=chat,
            content=response,
            sender='agent'
        )

        return Response({
            'user_message': MessageSerializer(user_message).data,
            'agent_message': MessageSerializer(agent_message).data
        })

    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """Obtiene el historial de mensajes del chat."""
        chat = self.get_object()
        messages = chat.messages.order_by('created_at')
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)
```

### `knowledge_crud_view.py`
Vistas para la gestión de conocimiento.

```python
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from knowledge.models import Document
from knowledge.services.document_service_factory import DocumentServiceFactory
from api.serializers.knowledge_csv_serializer import KnowledgeCSVSerializer
from api.serializers.knowledge_json_serializer import KnowledgeJSONSerializer

class KnowledgeViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de conocimiento.
    """

    permission_classes = [IsTenantAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        tenant_id = self.request.META.get('HTTP_X_TENANT_ID')
        return Document.objects.filter(tenant_id=tenant_id)

    @action(detail=False, methods=['post'])
    def upload_csv(self, request):
        """Carga conocimiento desde archivo CSV."""
        serializer = KnowledgeCSVSerializer(data=request.data)
        if serializer.is_valid():
            csv_file = serializer.validated_data['csv_file']
            delimiter = serializer.validated_data.get('delimiter', ',')

            # Procesar archivo CSV
            document_service = DocumentServiceFactory.create_service('csv')
            result = document_service.process_file(csv_file, delimiter)

            if result['success']:
                return Response({
                    'message': 'CSV uploaded successfully',
                    'documents_created': result['documents_created']
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'error': result['error']
                }, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def upload_json(self, request):
        """Carga conocimiento desde archivo JSON."""
        serializer = KnowledgeJSONSerializer(data=request.data)
        if serializer.is_valid():
            json_file = serializer.validated_data['json_file']

            # Procesar archivo JSON
            document_service = DocumentServiceFactory.create_service('json')
            result = document_service.process_file(json_file)

            if result['success']:
                return Response({
                    'message': 'JSON uploaded successfully',
                    'documents_created': result['documents_created']
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'error': result['error']
                }, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def search(self, request):
        """Busca en la base de conocimiento."""
        query = request.query_params.get('q', '')
        if not query:
            return Response({
                'error': 'Query parameter "q" is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Realizar búsqueda
        results = self.perform_search(query)

        return Response({
            'query': query,
            'results': results,
            'total': len(results)
        })

    def perform_search(self, query):
        """Realiza búsqueda en documentos."""
        # Implementar lógica de búsqueda
        documents = self.get_queryset().filter(
            content__icontains=query
        )[:10]

        return [{
            'id': doc.id,
            'title': doc.title,
            'content_snippet': doc.content[:200] + '...',
            'relevance_score': self.calculate_relevance(doc, query)
        } for doc in documents]

    def calculate_relevance(self, document, query):
        """Calcula puntuación de relevancia."""
        # Implementar cálculo de relevancia
        return 0.8  # Placeholder
```

### `s3_upload_view.py`
Vistas para carga de archivos a S3.

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from api.serializers.s3_upload_serializer import S3UploadSerializer
from api.services.s3_upload_service import S3UploadService

class S3UploadView(APIView):
    """
    Vista para carga de archivos a S3.
    """

    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsTenantAuthenticated]

    def post(self, request):
        """
        Sube un archivo a S3.

        Body:
        - file: Archivo a subir
        - bucket_name: Nombre del bucket (opcional)
        - folder: Carpeta destino (opcional)
        """
        serializer = S3UploadSerializer(data=request.data)
        if serializer.is_valid():
            file_obj = serializer.validated_data['file']
            bucket_name = serializer.validated_data.get('bucket_name')
            folder = serializer.validated_data.get('folder', '')

            # Generar key único
            file_key = self.generate_file_key(file_obj, folder)

            # Subir archivo
            s3_service = S3UploadService()
            result = s3_service.upload_file(file_obj, file_key, bucket_name)

            if result['success']:
                return Response({
                    'message': 'File uploaded successfully',
                    'url': result['url'],
                    'key': result['key']
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'error': result['error']
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def generate_file_key(self, file_obj, folder):
        """Genera una key única para el archivo."""
        import uuid
        import os

        unique_id = str(uuid.uuid4())
        file_extension = os.path.splitext(file_obj.name)[1]

        if folder:
            return f"{folder}/{unique_id}{file_extension}"
        else:
            return f"{unique_id}{file_extension}"
```

### `analysis_view.py`
Vistas para análisis y métricas.

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Avg
from analysis.models import SentimentChatModel, SentimentAgentsModel
from chats.models import Chat
from agents.models import AgentModel

class AnalysisView(APIView):
    """
    Vista para análisis y métricas del sistema.
    """

    permission_classes = [IsTenantAuthenticated]

    def get(self, request):
        """
        Obtiene análisis general del sistema.
        """
        tenant_id = request.META.get('HTTP_X_TENANT_ID')

        # Métricas de chats
        chat_metrics = self.get_chat_metrics(tenant_id)

        # Métricas de agentes
        agent_metrics = self.get_agent_metrics(tenant_id)

        # Análisis de sentimientos
        sentiment_analysis = self.get_sentiment_analysis(tenant_id)

        return Response({
            'chat_metrics': chat_metrics,
            'agent_metrics': agent_metrics,
            'sentiment_analysis': sentiment_analysis
        })

    def get_chat_metrics(self, tenant_id):
        """Obtiene métricas de chats."""
        chats = Chat.objects.filter(tenant_id=tenant_id)

        return {
            'total_chats': chats.count(),
            'active_chats': chats.filter(is_active=True).count(),
            'average_messages_per_chat': chats.aggregate(
                avg_messages=Avg('messages__count')
            )['avg_messages'] or 0,
            'chats_by_agent': list(chats.values('agent__name').annotate(
                count=Count('id')
            ))
        }

    def get_agent_metrics(self, tenant_id):
        """Obtiene métricas de agentes."""
        agents = AgentModel.objects.filter(tenant_id=tenant_id)

        return {
            'total_agents': agents.count(),
            'active_agents': agents.filter(is_active=True).count(),
            'agents_by_provider': list(agents.values('model_provider').annotate(
                count=Count('id')
            ))
        }

    def get_sentiment_analysis(self, tenant_id):
        """Obtiene análisis de sentimientos."""
        chat_sentiments = SentimentChatModel.objects.filter(
            chat__tenant_id=tenant_id
        )

        sentiment_distribution = chat_sentiments.values('sentiment').annotate(
            count=Count('id')
        )

        return {
            'total_analyzed': chat_sentiments.count(),
            'sentiment_distribution': list(sentiment_distribution),
            'average_sentiment_score': chat_sentiments.aggregate(
                avg_score=Avg('sentiment_score')
            )['avg_score'] or 0
        }
```

## Patrones de Vistas

### 1. ViewSet Personalizado
```python
class CustomViewSet(viewsets.ModelViewSet):
    """
    ViewSet con funcionalidad personalizada.
    """

    def get_serializer_class(self):
        """Selecciona serializador según la acción."""
        if self.action == 'create':
            return CreateSerializer
        elif self.action == 'list':
            return ListSerializer
        return self.serializer_class

    def get_permissions(self):
        """Permisos dinámicos según la acción."""
        if self.action == 'create':
            return [IsAuthenticated()]
        elif self.action == 'destroy':
            return [IsAdminUser()]
        return super().get_permissions()
```

### 2. Vista con Paginación
```python
from rest_framework.pagination import PageNumberPagination

class CustomPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class PaginatedViewSet(viewsets.ModelViewSet):
    pagination_class = CustomPagination

    def list(self, request):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
```

### 3. Vista con Filtros
```python
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

class FilteredViewSet(viewsets.ModelViewSet):
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'status', 'created_at']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
```

## Manejo de Errores

### Excepciones Personalizadas
```python
from rest_framework.views import exception_handler
from rest_framework import status

def custom_exception_handler(exc, context):
    """
    Manejo personalizado de excepciones.
    """
    response = exception_handler(exc, context)

    if response is not None:
        custom_response_data = {
            'error': {
                'status_code': response.status_code,
                'message': response.data.get('detail', 'An error occurred'),
                'timestamp': timezone.now().isoformat()
            }
        }
        response.data = custom_response_data

    return response
```

### Validación de Entrada
```python
class ValidatedView(APIView):
    def post(self, request):
        required_fields = ['name', 'email']

        # Validar campos requeridos
        missing_fields = [field for field in required_fields if field not in request.data]
        if missing_fields:
            return Response({
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Procesar datos
        return Response({'success': True})
```

## Middleware y Decoradores

### Decorador de Rate Limiting
```python
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_ratelimit.decorators import ratelimit

@method_decorator(ratelimit(key='ip', rate='100/h', method='POST'), name='post')
class RateLimitedView(APIView):
    def post(self, request):
        # Lógica de la vista
        pass
```

### Logging de Requests
```python
import logging

logger = logging.getLogger(__name__)

class LoggedView(APIView):
    def dispatch(self, request, *args, **kwargs):
        logger.info(f"{request.method} {request.path} - User: {request.user}")
        return super().dispatch(request, *args, **kwargs)
```

## Testing

### Test de Vistas
```python
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User

class AgentViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        self.client.force_authenticate(user=self.user)

    def test_list_agents(self):
        response = self.client.get('/api/agents/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_agent(self):
        data = {
            'name': 'Test Agent',
            'description': 'Test Description',
            'model_provider': 'openai'
        }
        response = self.client.post('/api/agents/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
```

## Documentación de API

### Swagger/OpenAPI
```python
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class DocumentedViewSet(viewsets.ModelViewSet):
    @swagger_auto_schema(
        operation_description="Lista todos los agentes",
        responses={200: AgentSerializer(many=True)}
    )
    def list(self, request):
        return super().list(request)

    @swagger_auto_schema(
        operation_description="Crea un nuevo agente",
        request_body=AgentSerializer,
        responses={201: AgentSerializer}
    )
    def create(self, request):
        return super().create(request)
```

## Mejores Prácticas

1. **Validación de Entrada**: Siempre validar datos de entrada
2. **Manejo de Errores**: Proporcionar mensajes de error claros
3. **Logging**: Registrar operaciones importantes
4. **Paginación**: Implementar paginación para listas grandes
5. **Filtros**: Permitir filtrado y búsqueda
6. **Permisos**: Aplicar permisos apropiados
7. **Versionado**: Versionar la API para mantener compatibilidad

## Monitoreo y Métricas

### Métricas de Performance
```python
import time
from functools import wraps

def monitor_performance(func):
    @wraps(func)
    def wrapper(self, request, *args, **kwargs):
        start_time = time.time()
        response = func(self, request, *args, **kwargs)
        duration = time.time() - start_time

        # Registrar métricas
        logger.info(f"{func.__name__} took {duration:.2f}s")

        return response
    return wrapper
```

### Health Check
```python
class HealthCheckView(APIView):
    """
    Vista para verificar el estado del sistema.
    """

    def get(self, request):
        # Verificar conexión a base de datos
        try:
            from django.db import connection
            connection.cursor().execute("SELECT 1")
            db_status = "OK"
        except Exception as e:
            db_status = f"ERROR: {str(e)}"

        # Verificar otros servicios
        return Response({
            'status': 'OK',
            'database': db_status,
            'timestamp': timezone.now().isoformat()
        })
```
