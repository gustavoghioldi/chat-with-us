# Clases de Permisos de API

## Descripción General
Este directorio contiene las clases de permisos personalizadas para la API REST del sistema. Estas clases controlan el acceso a los endpoints de la API basándose en diferentes criterios de autenticación y autorización.

## Estructura de Archivos

### `is_tenant_authenticated.py`
Clase de permisos para verificar que el usuario esté autenticado dentro del contexto de un tenant específico.

```python
from rest_framework.permissions import BasePermission
from tenants.models import Tenant

class IsTenantAuthenticated(BasePermission):
    """
    Permiso que verifica que el usuario esté autenticado
    y pertenezca al tenant especificado.
    """

    def has_permission(self, request, view):
        # Verificar autenticación básica
        if not request.user.is_authenticated:
            return False

        # Verificar tenant en headers o parámetros
        tenant_id = request.META.get('HTTP_X_TENANT_ID')
        if not tenant_id:
            return False

        # Verificar que el usuario pertenezca al tenant
        return self.user_belongs_to_tenant(request.user, tenant_id)

    def user_belongs_to_tenant(self, user, tenant_id):
        try:
            tenant = Tenant.objects.get(id=tenant_id)
            return user in tenant.users.all()
        except Tenant.DoesNotExist:
            return False
```

## Uso en Vistas

### Aplicar Permisos a ViewSets
```python
from rest_framework.viewsets import ModelViewSet
from .permissions_classes.is_tenant_authenticated import IsTenantAuthenticated

class MyAPIViewSet(ModelViewSet):
    permission_classes = [IsTenantAuthenticated]
    queryset = MyModel.objects.all()
    serializer_class = MyModelSerializer
```

### Aplicar Permisos a Vistas Basadas en Función
```python
from rest_framework.decorators import api_view, permission_classes
from .permissions_classes.is_tenant_authenticated import IsTenantAuthenticated

@api_view(['GET', 'POST'])
@permission_classes([IsTenantAuthenticated])
def my_api_view(request):
    # Lógica de la vista
    return Response(data)
```

## Implementación de Permisos Personalizados

### Estructura Base
```python
from rest_framework.permissions import BasePermission

class CustomPermission(BasePermission):
    """
    Permiso personalizado.
    """

    def has_permission(self, request, view):
        """
        Verificar permisos a nivel de vista.
        """
        # Implementar lógica de permisos
        return True

    def has_object_permission(self, request, view, obj):
        """
        Verificar permisos a nivel de objeto.
        """
        # Implementar lógica de permisos para objetos específicos
        return True
```

### Ejemplo: Permiso por Rol
```python
class IsAdminOrReadOnly(BasePermission):
    """
    Permiso que permite acceso completo a administradores
    y solo lectura a otros usuarios autenticados.
    """

    def has_permission(self, request, view):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return request.user.is_authenticated
        return request.user.is_authenticated and request.user.is_staff
```

## Validación de Headers

### Verificar Headers de Tenant
```python
def get_tenant_from_request(request):
    """
    Extrae el tenant ID de los headers de la request.
    """
    tenant_id = request.META.get('HTTP_X_TENANT_ID')
    if not tenant_id:
        tenant_id = request.data.get('tenant_id')
    return tenant_id
```

### Validar API Key
```python
class APIKeyAuthenticated(BasePermission):
    """
    Permiso basado en API Key.
    """

    def has_permission(self, request, view):
        api_key = request.META.get('HTTP_X_API_KEY')
        if not api_key:
            return False

        # Verificar API key en base de datos
        return self.is_valid_api_key(api_key)

    def is_valid_api_key(self, api_key):
        from tenants.models import APIKey
        try:
            key = APIKey.objects.get(key=api_key, is_active=True)
            return True
        except APIKey.DoesNotExist:
            return False
```

## Casos de Uso Comunes

### 1. Acceso Multi-Tenant
```python
# Vista que requiere autenticación de tenant
class TenantSpecificViewSet(ModelViewSet):
    permission_classes = [IsTenantAuthenticated]

    def get_queryset(self):
        tenant_id = self.request.META.get('HTTP_X_TENANT_ID')
        return MyModel.objects.filter(tenant_id=tenant_id)
```

### 2. Permisos Combinados
```python
from rest_framework.permissions import IsAuthenticated

class MyViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, IsTenantAuthenticated]
    # Ambos permisos deben cumplirse
```

### 3. Permisos Condicionales
```python
class ConditionalPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'DELETE':
            return request.user.is_superuser
        return request.user.is_authenticated
```

## Headers Requeridos

### Para Autenticación de Tenant
```http
X-Tenant-ID: 123
Authorization: Bearer <token>
```

### Para API Key
```http
X-API-Key: your-api-key-here
```

## Manejo de Errores

### Respuestas de Error Personalizadas
```python
class CustomPermission(BasePermission):
    message = "No tienes permisos para acceder a este recurso."

    def has_permission(self, request, view):
        if not self.check_permission(request):
            return False
        return True
```

### Códigos de Error
- `401 Unauthorized`: Usuario no autenticado
- `403 Forbidden`: Usuario autenticado pero sin permisos
- `400 Bad Request`: Headers requeridos faltantes

## Testing

### Test de Permisos
```python
from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User

class PermissionTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )

    def test_tenant_authentication_required(self):
        # Test sin autenticación
        response = self.client.get('/api/data/')
        self.assertEqual(response.status_code, 401)

        # Test con autenticación pero sin tenant
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/data/')
        self.assertEqual(response.status_code, 403)

        # Test con autenticación y tenant
        response = self.client.get(
            '/api/data/',
            HTTP_X_TENANT_ID='123'
        )
        self.assertEqual(response.status_code, 200)
```

## Mejores Prácticas

1. **Principio de Menor Privilegio**: Otorgar solo los permisos mínimos necesarios
2. **Validación Temprana**: Verificar permisos antes de procesar la lógica de negocio
3. **Logging**: Registrar intentos de acceso no autorizados
4. **Caching**: Cachear resultados de verificación de permisos cuando sea apropiado
5. **Documentación**: Documentar claramente qué permisos requiere cada endpoint

## Seguridad

### Consideraciones de Seguridad
- Validar todos los headers de entrada
- No exponer información sensible en mensajes de error
- Implementar rate limiting
- Usar HTTPS en producción
- Validar tokens de forma segura

### Ejemplo de Validación Segura
```python
class SecurePermission(BasePermission):
    def has_permission(self, request, view):
        try:
            # Validación segura
            return self.validate_securely(request)
        except Exception as e:
            # Log el error pero no lo expongas
            logger.error(f"Permission validation error: {e}")
            return False
```

## Extensibilidad

Para agregar nuevos permisos:

1. Crear nueva clase heredando de `BasePermission`
2. Implementar `has_permission()` y opcionalmente `has_object_permission()`
3. Documentar el nuevo permiso
4. Agregar tests correspondientes
5. Actualizar documentación de API

```python
class NewPermissionClass(BasePermission):
    """
    Descripción del nuevo permiso.
    """

    def has_permission(self, request, view):
        # Implementar lógica específica
        return True
```
