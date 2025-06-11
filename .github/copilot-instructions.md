# Copilot Instructions - Django Python

## Contexto del Proyecto
Este es un proyecto Django en Python. Sigue estas directrices para proporcionar asistencia de código consistente y de alta calidad.

## Principios de Desarrollo

### Estructura y Arquitectura
- Sigue el patrón MVT (Model-View-Template) de Django
- Mantén una separación clara de responsabilidades
- Usa Django apps para modularizar funcionalidades
- Implementa el principio DRY (Don't Repeat Yourself)
- Aplica principios SOLID cuando sea apropiado

### Convenciones de Código
- Sigue PEP 8 para el estilo de código Python
- Usa nombres descriptivos en inglés para variables, funciones y clases
- Aplica snake_case para funciones y variables
- Usa PascalCase para nombres de clases
- Mantén líneas de máximo 79-88 caracteres

## Patrones Django Específicos

### Modelos
```python
# Siempre incluir __str__ method
class MyModel(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "My Models"
        ordering = ['-created_at']

    def __str__(self):
        return self.name
```

### Vistas
- Preferir Class-Based Views (CBV) sobre Function-Based Views cuando sea apropiado
- Usar Django REST Framework para APIs
- Implementar validación robusta
- Manejar excepciones apropiadamente

```python
# Ejemplo CBV
class MyModelListView(ListView):
    model = MyModel
    template_name = 'myapp/list.html'
    context_object_name = 'objects'
    paginate_by = 20
```

### URLs
- Usar nombres descriptivos para URLs
- Agrupar URLs relacionadas en namespaces
- Usar path() en lugar de url() (Django 2.0+)

```python
# urls.py
from django.urls import path, include

app_name = 'myapp'
urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('api/', include('myapp.api.urls')),
]
```

## Mejores Prácticas

### Seguridad
- Siempre validar datos de entrada
- Usar Django forms para validación
- Implementar CSRF protection
- Usar Django's built-in authentication
- Sanitizar datos antes de mostrar en templates

### Performance
- Usar select_related() y prefetch_related() para optimizar queries
- Implementar caching cuando sea apropiado
- Usar database indexes en campos consultados frecuentemente
- Optimizar queries N+1

```python
# Optimización de queries
articles = Article.objects.select_related('author').prefetch_related('tags')
```

### Testing
- Escribir tests unitarios para modelos, vistas y forms
- Usar TestCase de Django
- Implementar tests de integración
- Mantener cobertura de tests alta

```python
class MyModelTestCase(TestCase):
    def setUp(self):
        self.model = MyModel.objects.create(name="Test")

    def test_str_representation(self):
        self.assertEqual(str(self.model), "Test")
```

## Estructura de Archivos Recomendada

```
myproject/
├── manage.py
├── myproject/
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   └── myapp/
│       ├── __init__.py
│       ├── models.py
│       ├── views.py
│       ├── urls.py
│       ├── admin.py
│       ├── forms.py
│       ├── serializers.py (si usa DRF)
│       ├── tests/
│       └── migrations/
├── templates/
├── static/
├── media/
└── requirements/
    ├── base.txt
    ├── development.txt
    └── production.txt
```

## Configuración y Settings

### Settings Modulares
- Separar settings por ambiente (development, staging, production)
- Usar variables de entorno para configuración sensible
- Nunca hardcodear credenciales

```python
# settings/base.py
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY')
DEBUG = False

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    # ... otras apps
    'apps.myapp',
]
```

## Django REST Framework (si aplica)

### Serializers
```python
class MyModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyModel
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
```

### ViewSets
```python
class MyModelViewSet(viewsets.ModelViewSet):
    queryset = MyModel.objects.all()
    serializer_class = MyModelSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['name']
```

## Base de Datos

### Migraciones
- Crear migraciones descriptivas
- Revisar migraciones antes de aplicar
- Usar data migrations para cambios de datos
- Hacer backup antes de migraciones en producción

### Queries Complejas
- Usar Django ORM cuando sea posible
- Recurrir a raw SQL solo cuando sea necesario
- Documentar queries complejas

## Logging y Debugging

```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

## Comandos de Management

### Crear comandos personalizados
```python
# management/commands/my_command.py
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Descripción del comando'

    def add_arguments(self, parser):
        parser.add_argument('--option', type=str, help='Opción del comando')

    def handle(self, *args, **options):
        self.stdout.write('Comando ejecutado exitosamente')
```

## Internacionalización (i18n)

- Usar Django's translation framework
- Marcar strings para traducción con gettext
- Configurar LOCALE_PATHS correctamente

```python
from django.utils.translation import gettext_lazy as _

verbose_name = _('My Model')
```

## Deployment

### Checklist Pre-Deployment
- [ ] DEBUG = False en producción
- [ ] SECRET_KEY segura y única
- [ ] ALLOWED_HOSTS configurado
- [ ] Base de datos de producción configurada
- [ ] Archivos estáticos configurados (STATIC_ROOT, MEDIA_ROOT)
- [ ] Variables de entorno configuradas
- [ ] SSL/HTTPS habilitado
- [ ] Logs configurados

## Herramientas Recomendadas

### Desarrollo
- `django-debug-toolbar` para debugging
- `django-extensions` para comandos adicionales
- `factory-boy` para testing
- `black` para formateo de código
- `flake8` para linting

### Producción
- `gunicorn` como WSGI server
- `redis` para caching
- `celery` para tareas asíncronas
- `sentry` para error tracking

## Notas Adicionales

1. **Comentarios**: Escribe comentarios explicativos para lógica compleja
2. **Documentación**: Mantén docstrings actualizados
3. **Versionado**: Usa semantic versioning
4. **Code Review**: Siempre revisar código antes de merge
5. **Backup**: Implementar estrategia de backup regular

## Ejemplos de Código Común

### Form con Validación Custom
```python
class MyForm(forms.ModelForm):
    class Meta:
        model = MyModel
        fields = ['name', 'email']

    def clean_email(self):
        email = self.cleaned_data['email']
        if MyModel.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists")
        return email
```

### Middleware Custom
```python
class MyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Código antes de la vista
        response = self.get_response(request)
        # Código después de la vista
        return response
```
