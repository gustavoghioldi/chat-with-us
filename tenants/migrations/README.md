# Tenants - Migrations

## Descripción

Este directorio contiene las migraciones de base de datos para el módulo de tenants, que gestiona los cambios en el esquema de la base de datos para funcionalidades de multi-tenancy, gestión de clientes y perfiles de usuario.

## Estructura de Migraciones

```
migrations/
├── __init__.py
├── 0001_initial.py                              # Migración inicial
├── 0002_tenantmodel_ai_token_tenantmodel_cwu_token.py  # Tokens de AI y CWU
├── 0003_userprofile.py                          # Perfiles de usuario
└── 0004_alter_tenantmodel_model.py             # Modificación del modelo
```

## Evolución del Modelo

### 0001_initial.py
- **Propósito**: Migración inicial del módulo de tenants
- **Cambios**: Creación de la estructura base para multi-tenancy
- **Modelos**: TenantModel base
- **Campos iniciales**:
  - Información básica del tenant
  - Configuración inicial
  - Metadatos de tenant
  - Timestamps

### 0002_tenantmodel_ai_token_tenantmodel_cwu_token.py
- **Propósito**: Implementación de tokens de autenticación
- **Cambios**: Adición de campos de tokens
- **Funcionalidades**:
  - `ai_token`: Token para servicios de IA
  - `cwu_token`: Token para Chat With Us
- **Beneficios**: Autenticación segura y específica por tenant

### 0003_userprofile.py
- **Propósito**: Gestión de perfiles de usuario
- **Cambios**: Creación del modelo `UserProfile`
- **Funcionalidades**:
  - Extensión del modelo User de Django
  - Relación con tenants
  - Configuraciones específicas de usuario
  - Metadatos adicionales

### 0004_alter_tenantmodel_model.py
- **Propósito**: Modificación del campo modelo
- **Cambios**: Ajuste del campo `model` en TenantModel
- **Mejoras**:
  - Validación mejorada
  - Opciones de modelo extendidas
  - Configuración más flexible

## Arquitectura de Modelos

### TenantModel (Estado Final)
```python
class TenantModel(models.Model):
    MODEL_CHOICES = [
        ('gpt-3.5-turbo', 'GPT-3.5 Turbo'),
        ('gpt-4', 'GPT-4'),
        ('gpt-4-turbo', 'GPT-4 Turbo'),
        ('claude-3-haiku', 'Claude 3 Haiku'),
        ('claude-3-sonnet', 'Claude 3 Sonnet'),
        ('claude-3-opus', 'Claude 3 Opus'),
    ]

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    model = models.CharField(max_length=100, choices=MODEL_CHOICES)

    # Tokens de autenticación
    ai_token = models.CharField(max_length=255, blank=True)
    cwu_token = models.CharField(max_length=255, blank=True)

    # Configuración
    configuration = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)

    # Límites y cuotas
    max_agents = models.IntegerField(default=10)
    max_documents = models.IntegerField(default=1000)
    max_storage_mb = models.IntegerField(default=1000)

    # Auditoría
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Tenant"
        verbose_name_plural = "Tenants"
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['is_active']),
        ]
```

### UserProfile
```python
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tenant = models.ForeignKey(TenantModel, on_delete=models.CASCADE)

    # Información personal
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True)
    bio = models.TextField(blank=True)

    # Configuración
    language = models.CharField(max_length=10, default='es')
    timezone = models.CharField(max_length=50, default='UTC')
    notifications_enabled = models.BooleanField(default=True)

    # Permisos
    is_tenant_admin = models.BooleanField(default=False)
    permissions = models.JSONField(default=dict)

    # Auditoría
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuario"
        unique_together = ['user', 'tenant']
```

## Mejores Prácticas

### Gestión de Migraciones
```python
# Aplicar migraciones
python manage.py migrate tenants

# Verificar estado de migraciones
python manage.py showmigrations tenants

# Crear nueva migración
python manage.py makemigrations tenants
```

### Gestión de Tokens
```python
# Generar tokens para tenants
python manage.py generate_tenant_tokens

# Rotar tokens existentes
python manage.py rotate_tenant_tokens --tenant-id=1
```

## Gestión de Datos

### Migración de Tokens
```python
# migration_script.py
from django.db import migrations
import secrets

def generate_tenant_tokens(apps, schema_editor):
    """Generar tokens para tenants existentes"""
    TenantModel = apps.get_model('tenants', 'TenantModel')

    for tenant in TenantModel.objects.all():
        if not tenant.ai_token:
            tenant.ai_token = f"ai_{secrets.token_urlsafe(32)}"
        if not tenant.cwu_token:
            tenant.cwu_token = f"cwu_{secrets.token_urlsafe(32)}"
        tenant.save()

def create_user_profiles(apps, schema_editor):
    """Crear perfiles para usuarios existentes"""
    User = apps.get_model('auth', 'User')
    UserProfile = apps.get_model('tenants', 'UserProfile')
    TenantModel = apps.get_model('tenants', 'TenantModel')

    # Crear tenant por defecto si no existe
    default_tenant, created = TenantModel.objects.get_or_create(
        name="default",
        defaults={
            'description': "Tenant por defecto",
            'model': 'gpt-3.5-turbo'
        }
    )

    # Crear perfiles para usuarios sin perfil
    for user in User.objects.all():
        if not hasattr(user, 'userprofile'):
            UserProfile.objects.create(
                user=user,
                tenant=default_tenant,
                language='es',
                timezone='America/Santiago'
            )

class Migration(migrations.Migration):
    dependencies = [
        ('tenants', '0002_tenantmodel_ai_token_tenantmodel_cwu_token'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.RunPython(generate_tenant_tokens),
        migrations.RunPython(create_user_profiles),
    ]
```

### Validación de Datos
```python
def validate_tenant_data(apps, schema_editor):
    """Validar integridad de datos de tenants"""
    TenantModel = apps.get_model('tenants', 'TenantModel')
    UserProfile = apps.get_model('tenants', 'UserProfile')

    # Verificar que todos los tenants tienen tokens
    tenants_without_tokens = TenantModel.objects.filter(
        models.Q(ai_token='') | models.Q(cwu_token='')
    )
    if tenants_without_tokens.exists():
        raise ValueError(f"Tenants sin tokens: {tenants_without_tokens.count()}")

    # Verificar que todos los usuarios tienen perfil
    from django.contrib.auth.models import User
    users_without_profile = User.objects.filter(userprofile__isnull=True)
    if users_without_profile.exists():
        raise ValueError(f"Usuarios sin perfil: {users_without_profile.count()}")
```

## Testing de Migraciones

### Pruebas de Migración
```python
# tests/test_migrations.py
from django.test import TestCase
from django.db import connection
from django.core.management import call_command
from django.contrib.auth.models import User

class TenantMigrationTestCase(TestCase):
    def test_tenant_tokens_creation(self):
        """Test creación de tokens de tenant"""
        from tenants.models import TenantModel

        # Crear tenant
        tenant = TenantModel.objects.create(
            name="Test Tenant",
            description="Test tenant",
            model="gpt-3.5-turbo"
        )

        # Verificar que se pueden asignar tokens
        tenant.ai_token = "test_ai_token"
        tenant.cwu_token = "test_cwu_token"
        tenant.save()

        # Verificar que se guardaron correctamente
        tenant.refresh_from_db()
        self.assertEqual(tenant.ai_token, "test_ai_token")
        self.assertEqual(tenant.cwu_token, "test_cwu_token")

    def test_user_profile_creation(self):
        """Test creación de perfiles de usuario"""
        from tenants.models import TenantModel, UserProfile

        # Crear tenant y usuario
        tenant = TenantModel.objects.create(
            name="Test Tenant",
            model="gpt-4"
        )

        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )

        # Crear perfil
        profile = UserProfile.objects.create(
            user=user,
            tenant=tenant,
            language="es",
            timezone="America/Santiago",
            is_tenant_admin=True
        )

        # Verificar relaciones
        self.assertEqual(profile.user, user)
        self.assertEqual(profile.tenant, tenant)
        self.assertTrue(profile.is_tenant_admin)

    def test_tenant_model_evolution(self):
        """Test evolución del modelo de tenant"""
        from tenants.models import TenantModel

        # Verificar campos requeridos
        required_fields = ['name', 'model', 'ai_token', 'cwu_token']

        for field in required_fields:
            self.assertTrue(hasattr(TenantModel, field))

        # Verificar opciones de modelo
        model_choices = [choice[0] for choice in TenantModel.MODEL_CHOICES]
        self.assertIn('gpt-3.5-turbo', model_choices)
        self.assertIn('gpt-4', model_choices)
```

### Validación de Integridad
```python
def test_data_integrity_after_migration(self):
    """Verificar integridad de datos después de migración"""
    from tenants.models import TenantModel, UserProfile
    from django.contrib.auth.models import User

    # Crear tenant completo
    tenant = TenantModel.objects.create(
        name="Complete Tenant",
        description="Complete test tenant",
        model="gpt-4-turbo",
        ai_token="ai_test_token_123",
        cwu_token="cwu_test_token_456",
        configuration={'max_tokens': 4000, 'temperature': 0.7},
        max_agents=20,
        max_documents=2000,
        max_storage_mb=5000
    )

    # Crear usuario con perfil
    user = User.objects.create_user(
        username="completeuser",
        email="complete@example.com",
        password="testpass123"
    )

    profile = UserProfile.objects.create(
        user=user,
        tenant=tenant,
        phone="+56912345678",
        bio="Test user bio",
        language="es",
        timezone="America/Santiago",
        notifications_enabled=True,
        is_tenant_admin=True,
        permissions={'can_create_agents': True, 'can_manage_documents': True}
    )

    # Verificar integridad completa
    self.assertEqual(tenant.name, "Complete Tenant")
    self.assertEqual(tenant.model, "gpt-4-turbo")
    self.assertEqual(tenant.max_agents, 20)
    self.assertEqual(profile.tenant, tenant)
    self.assertTrue(profile.is_tenant_admin)
    self.assertEqual(profile.permissions['can_create_agents'], True)
```

## Configuración de Tenants

### Settings para Tenants
```python
# settings/base.py
TENANT_SETTINGS = {
    'DEFAULT_MODEL': 'gpt-3.5-turbo',
    'MAX_AGENTS_PER_TENANT': 50,
    'MAX_DOCUMENTS_PER_TENANT': 10000,
    'MAX_STORAGE_MB_PER_TENANT': 10000,
    'TOKEN_EXPIRY_DAYS': 365,
    'ENABLE_TENANT_ISOLATION': True,
    'ALLOW_TENANT_REGISTRATION': False,
    'REQUIRE_TENANT_APPROVAL': True,
}
```

### Configuración de Seguridad
```python
# Configuración de tokens
TOKEN_SETTINGS = {
    'AI_TOKEN_PREFIX': 'ai_',
    'CWU_TOKEN_PREFIX': 'cwu_',
    'TOKEN_LENGTH': 32,
    'ENCRYPT_TOKENS': True,
    'ROTATE_TOKENS_DAYS': 90,
}
```

## Comandos de Gestión

### Comandos de Migración
```python
# management/commands/migrate_tenant_data.py
from django.core.management.base import BaseCommand
from tenants.services import TenantMigrationService

class Command(BaseCommand):
    help = 'Migrar datos de tenants'

    def add_arguments(self, parser):
        parser.add_argument(
            '--tenant-id',
            type=int,
            help='ID del tenant específico a migrar'
        )
        parser.add_argument(
            '--generate-tokens',
            action='store_true',
            help='Generar tokens para tenants sin tokens'
        )
        parser.add_argument(
            '--create-profiles',
            action='store_true',
            help='Crear perfiles para usuarios sin perfil'
        )

    def handle(self, *args, **options):
        service = TenantMigrationService()

        if options['generate_tokens']:
            generated = service.generate_missing_tokens()
            self.stdout.write(
                self.style.SUCCESS(f'Tokens generados: {generated}')
            )

        if options['create_profiles']:
            created = service.create_missing_profiles()
            self.stdout.write(
                self.style.SUCCESS(f'Perfiles creados: {created}')
            )

        if options['tenant_id']:
            result = service.migrate_tenant_data(options['tenant_id'])
        else:
            result = service.migrate_all_tenants()

        self.stdout.write(
            self.style.SUCCESS(f'Migrados {result["migrated"]} tenants')
        )
```

### Gestión de Tokens
```python
# management/commands/manage_tenant_tokens.py
class Command(BaseCommand):
    help = 'Gestionar tokens de tenants'

    def add_arguments(self, parser):
        parser.add_argument(
            '--rotate',
            action='store_true',
            help='Rotar tokens existentes'
        )
        parser.add_argument(
            '--tenant-id',
            type=int,
            help='ID del tenant específico'
        )
        parser.add_argument(
            '--token-type',
            choices=['ai', 'cwu', 'both'],
            default='both',
            help='Tipo de token a gestionar'
        )

    def handle(self, *args, **options):
        from tenants.services import TokenManagementService

        service = TokenManagementService()

        if options['rotate']:
            if options['tenant_id']:
                result = service.rotate_tenant_tokens(
                    options['tenant_id'],
                    options['token_type']
                )
            else:
                result = service.rotate_all_tokens(options['token_type'])

            self.stdout.write(
                self.style.SUCCESS(f'Tokens rotados: {result["rotated"]}')
            )
        else:
            # Mostrar información de tokens
            info = service.get_token_info(options['tenant_id'])
            self.stdout.write(f'Información de tokens: {info}')
```

## Monitoreo y Métricas

### Métricas de Tenants
```python
# Comando para generar métricas
python manage.py tenant_metrics --period=monthly

# Análisis de uso por tenant
python manage.py analyze_tenant_usage --days=30

# Estadísticas de perfiles
python manage.py profile_statistics
```

### Auditoría de Seguridad
```python
# Auditoría de tokens
python manage.py audit_tenant_tokens

# Verificar permisos
python manage.py audit_tenant_permissions

# Análisis de acceso
python manage.py analyze_tenant_access --days=7
```

## Seguridad y Privacidad

### Protección de Datos
```python
# Encriptación de tokens
python manage.py encrypt_tenant_tokens

# Auditoría de acceso
python manage.py audit_tenant_access --tenant-id=1

# Limpieza de datos sensibles
python manage.py cleanup_sensitive_data --tenant-id=1
```

### Cumplimiento
```python
# Logs de auditoría
LOGGING = {
    'loggers': {
        'tenants.security': {
            'level': 'INFO',
            'handlers': ['security_file'],
            'propagate': False,
        },
        'tenants.access': {
            'level': 'INFO',
            'handlers': ['audit_file'],
            'propagate': False,
        },
    },
}
```

## Troubleshooting

### Problemas Comunes
1. **Tokens duplicados**: Verificar unicidad de tokens
2. **Perfiles huérfanos**: Limpiar perfiles sin usuario
3. **Tenants inactivos**: Gestionar tenants obsoletos
4. **Límites excedidos**: Monitorear cuotas de uso

### Comandos de Diagnóstico
```bash
# Verificar integridad de tenants
python manage.py check tenants

# Validar tokens
python manage.py validate_tenant_tokens

# Análisis de perfiles
python manage.py analyze_user_profiles
```

## Integración con Otros Módulos

### Agents
- Agentes asociados a tenants
- Límites de agentes por tenant
- Configuración específica por tenant

### Documents
- Documentos aislados por tenant
- Cuotas de almacenamiento
- Permisos de acceso

### Chats
- Historial de chats por tenant
- Análisis de conversaciones
- Métricas de satisfacción

## Roadmap

### Próximas Funcionalidades
- Facturación automática
- Métricas avanzadas
- Integración con SSO
- API de gestión de tenants

### Mejoras Planificadas
- Optimización de consultas
- Dashboard de administración
- Alertas automáticas
- Backup automático

## Extensibilidad

### Nuevas Configuraciones
```python
# Ejemplo de configuración extendida
class TenantConfigurationModel(models.Model):
    tenant = models.ForeignKey(TenantModel, on_delete=models.CASCADE)
    config_type = models.CharField(max_length=50)
    config_data = models.JSONField()

    class Meta:
        verbose_name = "Configuración de Tenant"
        verbose_name_plural = "Configuraciones de Tenant"
```

### Plugins de Tenant
- Sistema de plugins específicos por tenant
- Configuraciones personalizadas
- Extensiones de funcionalidad
