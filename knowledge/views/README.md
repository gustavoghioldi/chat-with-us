# Knowledge Views - Vistas del Módulo de Conocimiento

## Descripción General
Este módulo contiene las vistas que manejan la presentación y gestión de las bases de conocimiento del sistema. Incluye vistas tanto para el panel de administración como para la interfaz de usuario final.

## Estructura del Módulo

### `/admin/`
Vistas personalizadas para el panel de administración de Django relacionadas con el módulo de conocimiento:
- Gestión avanzada de bases de conocimiento
- Visualización de métricas de uso
- Herramientas de importación/exportación
- Configuración de procesamiento de documentos

### Vistas Principales

#### AdminKnowledgeBaseView
```python
class AdminKnowledgeBaseView(LoginRequiredMixin, TemplateView):
    """
    Vista principal para la gestión de bases de conocimiento en el admin.
    """
    template_name = 'admin/knowledge/knowledge_base.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'knowledge_bases': self.get_knowledge_bases(),
            'stats': self.get_statistics(),
            'recent_updates': self.get_recent_updates(),
        })
        return context

    def get_knowledge_bases(self):
        """Obtiene las bases de conocimiento del tenant actual."""
        return KnowledgeBase.objects.filter(
            tenant=self.request.tenant
        ).prefetch_related('documents', 'categories')

    def get_statistics(self):
        """Calcula estadísticas de uso de la base de conocimiento."""
        return {
            'total_documents': Document.objects.filter(
                tenant=self.request.tenant
            ).count(),
            'total_queries': KnowledgeQuery.objects.filter(
                tenant=self.request.tenant
            ).count(),
            'processing_status': self.get_processing_status(),
        }
```

#### KnowledgeBaseListView
```python
class KnowledgeBaseListView(LoginRequiredMixin, ListView):
    """
    Vista para listar bases de conocimiento disponibles.
    """
    model = KnowledgeBase
    template_name = 'knowledge/list.html'
    context_object_name = 'knowledge_bases'
    paginate_by = 20

    def get_queryset(self):
        """Filtra bases de conocimiento por tenant y permisos."""
        queryset = super().get_queryset().filter(
            tenant=self.request.tenant
        )

        # Filtrar por permisos de usuario
        if not self.request.user.is_superuser:
            queryset = queryset.filter(
                Q(is_public=True) |
                Q(created_by=self.request.user) |
                Q(permissions__user=self.request.user)
            )

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['can_create'] = self.request.user.has_perm(
            'knowledge.add_knowledgebase'
        )
        return context
```

#### KnowledgeBaseDetailView
```python
class KnowledgeBaseDetailView(LoginRequiredMixin, DetailView):
    """
    Vista detallada de una base de conocimiento específica.
    """
    model = KnowledgeBase
    template_name = 'knowledge/detail.html'
    context_object_name = 'knowledge_base'

    def get_object(self):
        """Obtiene la base de conocimiento con validación de permisos."""
        obj = super().get_object()

        # Verificar acceso
        if not self.has_access(obj):
            raise PermissionDenied("No tienes permisos para acceder a esta base de conocimiento")

        return obj

    def has_access(self, obj):
        """Verifica si el usuario tiene acceso a la base de conocimiento."""
        if self.request.user.is_superuser:
            return True

        return (
            obj.tenant == self.request.tenant and
            (obj.is_public or
             obj.created_by == self.request.user or
             obj.permissions.filter(user=self.request.user).exists())
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'documents': self.get_documents(),
            'categories': self.get_categories(),
            'recent_queries': self.get_recent_queries(),
            'can_edit': self.can_edit_knowledge_base(),
        })
        return context

    def get_documents(self):
        """Obtiene documentos de la base de conocimiento."""
        return self.object.documents.filter(
            is_active=True
        ).order_by('-created_at')[:10]

    def get_categories(self):
        """Obtiene categorías de la base de conocimiento."""
        return self.object.categories.all()

    def get_recent_queries(self):
        """Obtiene consultas recientes a la base de conocimiento."""
        return KnowledgeQuery.objects.filter(
            knowledge_base=self.object,
            created_at__gte=timezone.now() - timedelta(days=7)
        ).order_by('-created_at')[:5]
```

#### KnowledgeSearchView
```python
class KnowledgeSearchView(LoginRequiredMixin, FormView):
    """
    Vista para buscar en las bases de conocimiento.
    """
    form_class = KnowledgeSearchForm
    template_name = 'knowledge/search.html'

    def form_valid(self, form):
        """Procesa la búsqueda y retorna resultados."""
        query = form.cleaned_data['query']
        knowledge_bases = form.cleaned_data['knowledge_bases']

        # Realizar búsqueda
        search_service = KnowledgeSearchService(
            tenant=self.request.tenant,
            user=self.request.user
        )

        results = search_service.search(
            query=query,
            knowledge_bases=knowledge_bases,
            limit=form.cleaned_data.get('limit', 20)
        )

        # Registrar la consulta
        self.log_search_query(query, knowledge_bases, results)

        context = self.get_context_data(form=form)
        context.update({
            'results': results,
            'query': query,
            'total_results': len(results),
        })

        return self.render_to_response(context)

    def log_search_query(self, query, knowledge_bases, results):
        """Registra la consulta de búsqueda para análisis."""
        for kb in knowledge_bases:
            KnowledgeQuery.objects.create(
                knowledge_base=kb,
                user=self.request.user,
                query=query,
                results_count=len(results),
                tenant=self.request.tenant
            )
```

## Mixins y Utilidades

### KnowledgePermissionMixin
```python
class KnowledgePermissionMixin:
    """
    Mixin para verificar permisos de acceso a bases de conocimiento.
    """

    def dispatch(self, request, *args, **kwargs):
        """Verifica permisos antes de procesar la vista."""
        if not self.has_knowledge_permission():
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    def has_knowledge_permission(self):
        """Verifica si el usuario tiene permisos para acceder al conocimiento."""
        return (
            self.request.user.is_authenticated and
            self.request.user.has_perm('knowledge.view_knowledgebase')
        )

    def get_accessible_knowledge_bases(self):
        """Obtiene las bases de conocimiento accesibles para el usuario."""
        if self.request.user.is_superuser:
            return KnowledgeBase.objects.filter(
                tenant=self.request.tenant
            )

        return KnowledgeBase.objects.filter(
            tenant=self.request.tenant
        ).filter(
            Q(is_public=True) |
            Q(created_by=self.request.user) |
            Q(permissions__user=self.request.user)
        ).distinct()
```

### KnowledgeContextMixin
```python
class KnowledgeContextMixin:
    """
    Mixin para agregar contexto común de conocimiento.
    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'available_knowledge_bases': self.get_available_knowledge_bases(),
            'knowledge_stats': self.get_knowledge_stats(),
        })
        return context

    def get_available_knowledge_bases(self):
        """Obtiene bases de conocimiento disponibles para el usuario."""
        return KnowledgeBase.objects.filter(
            tenant=self.request.tenant,
            is_active=True
        ).filter(
            Q(is_public=True) |
            Q(created_by=self.request.user)
        ).distinct()

    def get_knowledge_stats(self):
        """Obtiene estadísticas básicas de conocimiento."""
        return {
            'total_documents': Document.objects.filter(
                tenant=self.request.tenant,
                is_active=True
            ).count(),
            'total_knowledge_bases': KnowledgeBase.objects.filter(
                tenant=self.request.tenant,
                is_active=True
            ).count(),
        }
```

## Vistas AJAX

### KnowledgeAjaxSearchView
```python
class KnowledgeAjaxSearchView(LoginRequiredMixin, View):
    """
    Vista AJAX para búsqueda en tiempo real.
    """

    def get(self, request, *args, **kwargs):
        """Procesa búsqueda AJAX."""
        query = request.GET.get('q', '').strip()
        knowledge_base_id = request.GET.get('kb_id')

        if not query or len(query) < 3:
            return JsonResponse({
                'results': [],
                'message': 'La consulta debe tener al menos 3 caracteres'
            })

        # Realizar búsqueda
        search_service = KnowledgeSearchService(
            tenant=request.tenant,
            user=request.user
        )

        results = search_service.search(
            query=query,
            knowledge_base_id=knowledge_base_id,
            limit=10
        )

        return JsonResponse({
            'results': [
                {
                    'id': r.id,
                    'title': r.title,
                    'content': r.content[:200] + '...' if len(r.content) > 200 else r.content,
                    'score': r.score,
                    'source': r.source,
                }
                for r in results
            ],
            'total': len(results)
        })
```

## Validaciones y Seguridad

### Validaciones de Entrada
```python
def validate_knowledge_query(query):
    """Valida una consulta de conocimiento."""
    if not query or len(query.strip()) < 3:
        raise ValidationError("La consulta debe tener al menos 3 caracteres")

    if len(query) > 500:
        raise ValidationError("La consulta no puede exceder 500 caracteres")

    # Validar caracteres especiales
    if re.search(r'[<>\"\'&]', query):
        raise ValidationError("La consulta contiene caracteres no permitidos")

    return query.strip()
```

### Seguridad de Acceso
```python
class SecureKnowledgeView(LoginRequiredMixin, View):
    """
    Vista base con validaciones de seguridad para conocimiento.
    """

    def dispatch(self, request, *args, **kwargs):
        """Validaciones de seguridad antes de procesar."""
        # Verificar tenant
        if not hasattr(request, 'tenant'):
            return HttpResponseForbidden("Tenant no válido")

        # Verificar rate limiting
        if not self.check_rate_limit():
            return HttpResponseTooManyRequests("Demasiadas solicitudes")

        return super().dispatch(request, *args, **kwargs)

    def check_rate_limit(self):
        """Verifica límites de velocidad."""
        cache_key = f"knowledge_rate_limit_{self.request.user.id}"
        requests = cache.get(cache_key, 0)

        if requests >= 100:  # 100 requests per hour
            return False

        cache.set(cache_key, requests + 1, 3600)  # 1 hour
        return True
```

## Testing

### Ejemplo de Tests
```python
class KnowledgeViewsTestCase(TestCase):

    def setUp(self):
        self.tenant = TenantFactory()
        self.user = UserFactory()
        self.knowledge_base = KnowledgeBaseFactory(tenant=self.tenant)
        self.client.force_login(self.user)

    def test_knowledge_base_list_view(self):
        """Test de vista de lista de bases de conocimiento."""
        response = self.client.get(reverse('knowledge:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.knowledge_base.name)

    def test_knowledge_search_view(self):
        """Test de vista de búsqueda."""
        response = self.client.post(reverse('knowledge:search'), {
            'query': 'test query',
            'knowledge_bases': [self.knowledge_base.id]
        })
        self.assertEqual(response.status_code, 200)

    def test_permission_denied(self):
        """Test de acceso denegado."""
        private_kb = KnowledgeBaseFactory(
            tenant=self.tenant,
            is_public=False
        )

        response = self.client.get(
            reverse('knowledge:detail', args=[private_kb.id])
        )
        self.assertEqual(response.status_code, 403)
```

## Mejores Prácticas

### 1. Caching
```python
class CachedKnowledgeView(View):
    """Vista con caché para mejorar rendimiento."""

    def get_cached_results(self, cache_key):
        """Obtiene resultados del caché."""
        return cache.get(cache_key)

    def cache_results(self, cache_key, results, timeout=300):
        """Guarda resultados en caché."""
        cache.set(cache_key, results, timeout)
```

### 2. Logging
```python
import logging

logger = logging.getLogger(__name__)

class LoggedKnowledgeView(View):
    """Vista con logging detallado."""

    def log_knowledge_access(self, knowledge_base, action):
        """Registra acceso a base de conocimiento."""
        logger.info(
            f"User {self.request.user.id} performed {action} "
            f"on knowledge base {knowledge_base.id}"
        )
```

### 3. Monitoreo
```python
from django.utils import timezone
from knowledge.models import KnowledgeAccessLog

class MonitoredKnowledgeView(View):
    """Vista con monitoreo de acceso."""

    def log_access(self, knowledge_base):
        """Registra acceso para análisis."""
        KnowledgeAccessLog.objects.create(
            knowledge_base=knowledge_base,
            user=self.request.user,
            timestamp=timezone.now(),
            ip_address=self.get_client_ip(),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )
```

## Configuración

### URLs
```python
# knowledge/urls.py
from django.urls import path
from . import views

app_name = 'knowledge'

urlpatterns = [
    path('', views.KnowledgeBaseListView.as_view(), name='list'),
    path('<int:pk>/', views.KnowledgeBaseDetailView.as_view(), name='detail'),
    path('search/', views.KnowledgeSearchView.as_view(), name='search'),
    path('ajax/search/', views.KnowledgeAjaxSearchView.as_view(), name='ajax_search'),
]
```

### Templates
- `knowledge/list.html`: Lista de bases de conocimiento
- `knowledge/detail.html`: Detalle de base de conocimiento
- `knowledge/search.html`: Búsqueda de conocimiento
- `admin/knowledge/`: Templates para administración

## Extensibilidad

### Hooks para Extensiones
```python
class ExtensibleKnowledgeView(View):
    """Vista base extensible para conocimiento."""

    def get_extension_context(self):
        """Hook para agregar contexto desde extensiones."""
        return {}

    def process_search_results(self, results):
        """Hook para procesar resultados de búsqueda."""
        return results
```

### Decoradores Personalizados
```python
def require_knowledge_permission(permission):
    """Decorador para requerir permisos específicos."""
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.has_perm(permission):
                return HttpResponseForbidden()
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
```

Este módulo proporciona una interfaz completa para la gestión y búsqueda de conocimiento, con énfasis en la seguridad, rendimiento y extensibilidad.
