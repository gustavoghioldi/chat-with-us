# Módulo de Tenants - Sistema Multitenancy

## Descripción General
Este módulo implementa un sistema multitenancy robusto y escalable que permite gestionar múltiples organizaciones o espacios de trabajo completamente aislados dentro de la misma aplicación. Cada tenant representa un entorno independiente con sus propios datos, usuarios, configuraciones y recursos, garantizando total privacidad y segregación de datos.

## Arquitectura del Sistema

### Estructura de Archivos
- **models.py**: Define `TenantModel` y entidades relacionadas con la gestión multitenancy
- **admin.py**: Configuración avanzada para administrar tenants desde el panel de administración
- **views.py**: Vistas especializadas para operaciones de tenants en la interfaz web
- **services.py**: Servicios empresariales para gestión completa de tenants
- **signals.py**: Señales para manejar eventos del ciclo de vida de tenants
- **helpers.py**: Funciones auxiliares y utilidades para operaciones de tenancy
- **tests.py**: Suite completa de pruebas unitarias, integración y rendimiento

### Carpeta `migrations/`
Migraciones de base de datos para todos los modelos relacionados con el sistema multitenancy.

## Modelos de Datos

### TenantModel
```python
class TenantModel(models.Model):
    """
    Modelo principal para representar un tenant en el sistema multitenancy.

    Attributes:
        name: Nombre del tenant/organización
        slug: Identificador único en URL
        domain: Dominio personalizado (opcional)
        subdomain: Subdominio asignado
        subscription_tier: Nivel de suscripción
        max_users: Límite máximo de usuarios
        max_agents: Límite máximo de agentes
        max_storage: Límite de almacenamiento en MB
        settings: Configuraciones específicas del tenant
        is_active: Estado del tenant
        trial_end_date: Fecha de fin del período de prueba
        billing_info: Información de facturación
    """

    SUBSCRIPTION_TIERS = [
        ('free', 'Gratuito'),
        ('basic', 'Básico'),
        ('professional', 'Profesional'),
        ('enterprise', 'Empresarial'),
        ('custom', 'Personalizado'),
    ]

    STATUS_CHOICES = [
        ('active', 'Activo'),
        ('inactive', 'Inactivo'),
        ('suspended', 'Suspendido'),
        ('trial', 'Período de Prueba'),
        ('expired', 'Expirado'),
    ]

    # Información básica
    name = models.CharField(max_length=200, verbose_name="Nombre del Tenant")
    slug = models.SlugField(
        unique=True,
        max_length=100,
        verbose_name="Identificador Único"
    )
    description = models.TextField(blank=True, verbose_name="Descripción")

    # Configuración de dominio
    domain = models.CharField(
        max_length=253,
        unique=True,
        null=True,
        blank=True,
        verbose_name="Dominio Personalizado"
    )
    subdomain = models.CharField(
        max_length=63,
        unique=True,
        null=True,
        blank=True,
        verbose_name="Subdominio"
    )

    # Suscripción y límites
    subscription_tier = models.CharField(
        max_length=20,
        choices=SUBSCRIPTION_TIERS,
        default='free',
        verbose_name="Nivel de Suscripción"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='trial',
        verbose_name="Estado"
    )

    # Límites de recursos
    max_users = models.PositiveIntegerField(
        default=5,
        verbose_name="Máximo de Usuarios"
    )
    max_agents = models.PositiveIntegerField(
        default=3,
        verbose_name="Máximo de Agentes"
    )
    max_storage = models.PositiveIntegerField(
        default=1024,  # MB
        verbose_name="Máximo de Almacenamiento (MB)"
    )
    max_monthly_messages = models.PositiveIntegerField(
        default=1000,
        verbose_name="Máximo de Mensajes Mensuales"
    )

    # Configuraciones específicas
    settings = models.JSONField(
        default=dict,
        verbose_name="Configuraciones del Tenant"
    )

    # Fechas importantes
    trial_end_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fin del Período de Prueba"
    )
    subscription_start_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Inicio de Suscripción"
    )
    subscription_end_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fin de Suscripción"
    )

    # Información de facturación
    billing_info = models.JSONField(
        default=dict,
        verbose_name="Información de Facturación"
    )

    # Metadatos
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Creado por"
    )

    # Contacto
    contact_email = models.EmailField(verbose_name="Email de Contacto")
    contact_phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Teléfono de Contacto"
    )

    class Meta:
        verbose_name = "Tenant"
        verbose_name_plural = "Tenants"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['domain']),
            models.Index(fields=['subdomain']),
            models.Index(fields=['subscription_tier']),
            models.Index(fields=['status']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.slug})"

    def clean(self):
        """Validación personalizada del modelo."""
        if not self.domain and not self.subdomain:
            raise ValidationError("Debe especificar un dominio o subdominio")

        if self.domain and not self.is_valid_domain(self.domain):
            raise ValidationError("Formato de dominio no válido")

        if self.subdomain and not self.is_valid_subdomain(self.subdomain):
            raise ValidationError("Formato de subdominio no válido")

    def save(self, *args, **kwargs):
        """Guardar con validaciones adicionales."""
        if not self.slug:
            self.slug = slugify(self.name)

        # Generar subdominio si no existe
        if not self.subdomain and not self.domain:
            self.subdomain = self.generate_unique_subdomain()

        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def current_user_count(self):
        """Retorna el número actual de usuarios."""
        return self.users.filter(is_active=True).count()

    @property
    def current_agent_count(self):
        """Retorna el número actual de agentes."""
        return self.agents.filter(is_active=True).count()

    @property
    def current_storage_usage(self):
        """Retorna el uso actual de almacenamiento en MB."""
        from documents.models import Document
        total_size = Document.objects.filter(
            tenant=self
        ).aggregate(
            total=models.Sum('file_size')
        )['total'] or 0
        return total_size / (1024 * 1024)  # Convert to MB

    @property
    def current_monthly_messages(self):
        """Retorna el número de mensajes del mes actual."""
        from django.utils import timezone
        from chats.models import Message

        now = timezone.now()
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        return Message.objects.filter(
            chat__tenant=self,
            created_at__gte=start_of_month
        ).count()

    def can_add_user(self):
        """Verifica si se puede agregar un nuevo usuario."""
        return self.current_user_count < self.max_users

    def can_add_agent(self):
        """Verifica si se puede agregar un nuevo agente."""
        return self.current_agent_count < self.max_agents

    def can_upload_file(self, file_size_mb):
        """Verifica si se puede subir un archivo."""
        return (self.current_storage_usage + file_size_mb) <= self.max_storage

    def can_send_message(self):
        """Verifica si se puede enviar un mensaje."""
        return self.current_monthly_messages < self.max_monthly_messages

    def get_usage_summary(self):
        """Retorna un resumen del uso actual de recursos."""
        return {
            'users': {
                'current': self.current_user_count,
                'max': self.max_users,
                'percentage': (self.current_user_count / self.max_users * 100) if self.max_users > 0 else 0
            },
            'agents': {
                'current': self.current_agent_count,
                'max': self.max_agents,
                'percentage': (self.current_agent_count / self.max_agents * 100) if self.max_agents > 0 else 0
            },
            'storage': {
                'current': self.current_storage_usage,
                'max': self.max_storage,
                'percentage': (self.current_storage_usage / self.max_storage * 100) if self.max_storage > 0 else 0
            },
            'monthly_messages': {
                'current': self.current_monthly_messages,
                'max': self.max_monthly_messages,
                'percentage': (self.current_monthly_messages / self.max_monthly_messages * 100) if self.max_monthly_messages > 0 else 0
            }
        }

    def is_trial_expired(self):
        """Verifica si el período de prueba ha expirado."""
        if self.trial_end_date:
            return timezone.now() > self.trial_end_date
        return False

    def is_subscription_active(self):
        """Verifica si la suscripción está activa."""
        if not self.subscription_end_date:
            return True
        return timezone.now() <= self.subscription_end_date

    def get_full_domain(self):
        """Retorna el dominio completo del tenant."""
        if self.domain:
            return self.domain
        elif self.subdomain:
            from django.conf import settings
            base_domain = getattr(settings, 'BASE_DOMAIN', 'example.com')
            return f"{self.subdomain}.{base_domain}"
        return None

    @staticmethod
    def is_valid_domain(domain):
        """Valida el formato de un dominio."""
        import re
        pattern = r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$'
        return re.match(pattern, domain) is not None

    @staticmethod
    def is_valid_subdomain(subdomain):
        """Valida el formato de un subdominio."""
        import re
        pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$'
        return re.match(pattern, subdomain) is not None

    def generate_unique_subdomain(self):
        """Genera un subdominio único basado en el nombre."""
        base_subdomain = slugify(self.name)
        subdomain = base_subdomain
        counter = 1

        while TenantModel.objects.filter(subdomain=subdomain).exists():
            subdomain = f"{base_subdomain}-{counter}"
            counter += 1

        return subdomain
```

### TenantUser
```python
class TenantUser(models.Model):
    """
    Modelo para gestionar la relación entre usuarios y tenants.

    Attributes:
        tenant: Tenant al que pertenece el usuario
        user: Usuario del sistema
        role: Rol del usuario en el tenant
        permissions: Permisos específicos
        is_active: Estado de la membresía
        joined_at: Fecha de ingreso al tenant
    """

    USER_ROLES = [
        ('owner', 'Propietario'),
        ('admin', 'Administrador'),
        ('manager', 'Gerente'),
        ('user', 'Usuario'),
        ('viewer', 'Visualizador'),
    ]

    tenant = models.ForeignKey(
        TenantModel,
        on_delete=models.CASCADE,
        related_name='tenant_users',
        verbose_name="Tenant"
    )
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='tenant_memberships',
        verbose_name="Usuario"
    )
    role = models.CharField(
        max_length=20,
        choices=USER_ROLES,
        default='user',
        verbose_name="Rol"
    )
    permissions = models.JSONField(
        default=dict,
        verbose_name="Permisos Específicos"
    )
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    joined_at = models.DateTimeField(auto_now_add=True)
    invited_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sent_invitations',
        verbose_name="Invitado por"
    )

    class Meta:
        verbose_name = "Usuario del Tenant"
        verbose_name_plural = "Usuarios del Tenant"
        unique_together = [['tenant', 'user']]
        indexes = [
            models.Index(fields=['tenant', 'is_active']),
            models.Index(fields=['role']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.tenant.name} ({self.role})"

    def has_permission(self, permission):
        """Verifica si el usuario tiene un permiso específico."""
        # Permisos de rol
        role_permissions = self.get_role_permissions()
        if permission in role_permissions:
            return True

        # Permisos específicos
        return self.permissions.get(permission, False)

    def get_role_permissions(self):
        """Retorna los permisos por defecto del rol."""
        role_permissions = {
            'owner': [
                'manage_tenant', 'manage_users', 'manage_agents',
                'manage_billing', 'view_analytics', 'manage_settings'
            ],
            'admin': [
                'manage_users', 'manage_agents', 'view_analytics',
                'manage_settings'
            ],
            'manager': [
                'manage_agents', 'view_analytics', 'manage_basic_settings'
            ],
            'user': [
                'use_agents', 'view_chats', 'upload_documents'
            ],
            'viewer': [
                'view_chats', 'view_analytics'
            ]
        }

        return role_permissions.get(self.role, [])
```

### TenantSettings
```python
class TenantSettings(models.Model):
    """
    Modelo para configuraciones avanzadas del tenant.

    Attributes:
        tenant: Tenant asociado
        category: Categoría de configuración
        key: Clave de configuración
        value: Valor de configuración
        data_type: Tipo de dato del valor
        is_public: Si la configuración es pública
        description: Descripción de la configuración
    """

    DATA_TYPES = [
        ('string', 'Texto'),
        ('integer', 'Entero'),
        ('float', 'Decimal'),
        ('boolean', 'Booleano'),
        ('json', 'JSON'),
        ('date', 'Fecha'),
        ('datetime', 'Fecha y Hora'),
    ]

    CATEGORIES = [
        ('general', 'General'),
        ('security', 'Seguridad'),
        ('notifications', 'Notificaciones'),
        ('integrations', 'Integraciones'),
        ('branding', 'Marca'),
        ('limits', 'Límites'),
        ('features', 'Características'),
    ]

    tenant = models.ForeignKey(
        TenantModel,
        on_delete=models.CASCADE,
        related_name='settings',
        verbose_name="Tenant"
    )
    category = models.CharField(
        max_length=20,
        choices=CATEGORIES,
        verbose_name="Categoría"
    )
    key = models.CharField(max_length=100, verbose_name="Clave")
    value = models.TextField(verbose_name="Valor")
    data_type = models.CharField(
        max_length=20,
        choices=DATA_TYPES,
        default='string',
        verbose_name="Tipo de Dato"
    )
    is_public = models.BooleanField(
        default=False,
        verbose_name="Es Público"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Descripción"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Configuración del Tenant"
        verbose_name_plural = "Configuraciones del Tenant"
        unique_together = [['tenant', 'category', 'key']]
        indexes = [
            models.Index(fields=['tenant', 'category']),
            models.Index(fields=['category', 'key']),
        ]

    def __str__(self):
        return f"{self.tenant.name} - {self.category}.{self.key}"

    def get_typed_value(self):
        """Retorna el valor convertido al tipo de dato correspondiente."""
        if self.data_type == 'integer':
            return int(self.value)
        elif self.data_type == 'float':
            return float(self.value)
        elif self.data_type == 'boolean':
            return self.value.lower() in ['true', '1', 'yes']
        elif self.data_type == 'json':
            import json
            return json.loads(self.value)
        elif self.data_type == 'date':
            from datetime import datetime
            return datetime.strptime(self.value, '%Y-%m-%d').date()
        elif self.data_type == 'datetime':
            from datetime import datetime
            return datetime.fromisoformat(self.value)
        else:
            return self.value
```

## Servicios de Tenant

### TenantManager
```python
class TenantManager:
    """
    Servicio principal para gestionar operaciones de tenants.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def create_tenant(self, name, contact_email, subscription_tier='free', created_by=None, **kwargs):
        """
        Crea un nuevo tenant con toda la configuración inicial.

        Args:
            name: Nombre del tenant
            contact_email: Email de contacto
            subscription_tier: Nivel de suscripción
            created_by: Usuario creador
            **kwargs: Parámetros adicionales

        Returns:
            TenantModel: Tenant creado
        """
        try:
            # Crear el tenant
            tenant = TenantModel.objects.create(
                name=name,
                contact_email=contact_email,
                subscription_tier=subscription_tier,
                created_by=created_by,
                **kwargs
            )

            # Configurar límites según el tier
            self.setup_subscription_limits(tenant)

            # Crear configuraciones por defecto
            self.create_default_settings(tenant)

            # Crear usuario propietario si se especifica
            if created_by:
                self.add_user_to_tenant(tenant, created_by, role='owner')

            # Configurar recursos iniciales
            self.setup_initial_resources(tenant)

            self.logger.info(f"Tenant created successfully: {tenant.slug}")
            return tenant

        except Exception as e:
            self.logger.error(f"Error creating tenant: {str(e)}")
            raise

    def setup_subscription_limits(self, tenant):
        """
        Configura los límites según el nivel de suscripción.

        Args:
            tenant: Tenant a configurar
        """
        limits = {
            'free': {
                'max_users': 5,
                'max_agents': 3,
                'max_storage': 1024,  # 1GB
                'max_monthly_messages': 1000,
            },
            'basic': {
                'max_users': 25,
                'max_agents': 10,
                'max_storage': 10240,  # 10GB
                'max_monthly_messages': 10000,
            },
            'professional': {
                'max_users': 100,
                'max_agents': 50,
                'max_storage': 51200,  # 50GB
                'max_monthly_messages': 100000,
            },
            'enterprise': {
                'max_users': 1000,
                'max_agents': 200,
                'max_storage': 512000,  # 500GB
                'max_monthly_messages': 1000000,
            }
        }

        tier_limits = limits.get(tenant.subscription_tier, limits['free'])

        for key, value in tier_limits.items():
            setattr(tenant, key, value)

        tenant.save()

    def create_default_settings(self, tenant):
        """
        Crea configuraciones por defecto para el tenant.

        Args:
            tenant: Tenant para el cual crear configuraciones
        """
        default_settings = [
            # General
            ('general', 'timezone', 'UTC', 'string'),
            ('general', 'language', 'es', 'string'),
            ('general', 'date_format', 'YYYY-MM-DD', 'string'),

            # Seguridad
            ('security', 'require_2fa', 'false', 'boolean'),
            ('security', 'session_timeout', '3600', 'integer'),
            ('security', 'password_policy', 'medium', 'string'),

            # Notificaciones
            ('notifications', 'email_notifications', 'true', 'boolean'),
            ('notifications', 'sms_notifications', 'false', 'boolean'),
            ('notifications', 'push_notifications', 'true', 'boolean'),

            # Características
            ('features', 'enable_chat_history', 'true', 'boolean'),
            ('features', 'enable_file_upload', 'true', 'boolean'),
            ('features', 'enable_analytics', 'true', 'boolean'),

            # Branding
            ('branding', 'primary_color', '#007bff', 'string'),
            ('branding', 'secondary_color', '#6c757d', 'string'),
            ('branding', 'logo_url', '', 'string'),
        ]

        for category, key, value, data_type in default_settings:
            TenantSettings.objects.create(
                tenant=tenant,
                category=category,
                key=key,
                value=value,
                data_type=data_type
            )

    def add_user_to_tenant(self, tenant, user, role='user', invited_by=None):
        """
        Agrega un usuario a un tenant.

        Args:
            tenant: Tenant al que agregar el usuario
            user: Usuario a agregar
            role: Rol del usuario
            invited_by: Usuario que envió la invitación

        Returns:
            TenantUser: Relación creada
        """
        if not tenant.can_add_user():
            raise ValueError(f"Tenant {tenant.name} ha alcanzado el límite de usuarios")

        tenant_user, created = TenantUser.objects.get_or_create(
            tenant=tenant,
            user=user,
            defaults={
                'role': role,
                'invited_by': invited_by
            }
        )

        if not created:
            # Usuario ya existe, actualizar rol si es necesario
            tenant_user.role = role
            tenant_user.is_active = True
            tenant_user.save()

        return tenant_user

    def upgrade_subscription(self, tenant, new_tier, billing_info=None):
        """
        Actualiza la suscripción de un tenant.

        Args:
            tenant: Tenant a actualizar
            new_tier: Nuevo nivel de suscripción
            billing_info: Información de facturación

        Returns:
            bool: True si la actualización fue exitosa
        """
        try:
            old_tier = tenant.subscription_tier
            tenant.subscription_tier = new_tier

            # Actualizar límites
            self.setup_subscription_limits(tenant)

            # Actualizar información de facturación
            if billing_info:
                tenant.billing_info.update(billing_info)

            # Establecer fechas de suscripción
            if new_tier != 'free':
                tenant.subscription_start_date = timezone.now()
                # Calcular fecha de fin según el plan
                tenant.subscription_end_date = self.calculate_subscription_end_date(new_tier)

            tenant.status = 'active'
            tenant.save()

            self.logger.info(f"Subscription upgraded for tenant {tenant.slug}: {old_tier} -> {new_tier}")
            return True

        except Exception as e:
            self.logger.error(f"Error upgrading subscription for tenant {tenant.slug}: {str(e)}")
            return False

    def suspend_tenant(self, tenant, reason=""):
        """
        Suspende un tenant.

        Args:
            tenant: Tenant a suspender
            reason: Razón de la suspensión
        """
        tenant.status = 'suspended'
        tenant.is_active = False

        # Registrar razón en configuraciones
        TenantSettings.objects.update_or_create(
            tenant=tenant,
            category='admin',
            key='suspension_reason',
            defaults={
                'value': reason,
                'data_type': 'string'
            }
        )

        tenant.save()
        self.logger.warning(f"Tenant suspended: {tenant.slug} - Reason: {reason}")

    def reactivate_tenant(self, tenant):
        """
        Reactiva un tenant suspendido.

        Args:
            tenant: Tenant a reactivar
        """
        tenant.status = 'active'
        tenant.is_active = True
        tenant.save()

        # Eliminar razón de suspensión
        TenantSettings.objects.filter(
            tenant=tenant,
            category='admin',
            key='suspension_reason'
        ).delete()

        self.logger.info(f"Tenant reactivated: {tenant.slug}")

    def get_tenant_analytics(self, tenant, period_days=30):
        """
        Obtiene analíticas del tenant.

        Args:
            tenant: Tenant a analizar
            period_days: Período de análisis en días

        Returns:
            dict: Analíticas del tenant
        """
        from django.utils import timezone
        from django.db.models import Count, Sum
        from datetime import timedelta

        start_date = timezone.now() - timedelta(days=period_days)

        analytics = {
            'period': {
                'start': start_date.isoformat(),
                'end': timezone.now().isoformat(),
                'days': period_days
            },
            'usage': tenant.get_usage_summary(),
            'activity': {
                'total_messages': tenant.chats.filter(
                    created_at__gte=start_date
                ).aggregate(
                    total=Count('messages')
                )['total'] or 0,
                'active_users': tenant.users.filter(
                    last_login__gte=start_date
                ).count(),
                'new_users': tenant.tenant_users.filter(
                    joined_at__gte=start_date
                ).count(),
            },
            'performance': {
                'avg_response_time': self.calculate_avg_response_time(tenant, start_date),
                'satisfaction_score': self.calculate_satisfaction_score(tenant, start_date),
                'resolution_rate': self.calculate_resolution_rate(tenant, start_date),
            }
        }

        return analytics
```

## Middleware de Tenant

### TenantMiddleware
```python
class TenantMiddleware:
    """
    Middleware para identificar y establecer el tenant actual.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """
        Procesa la request para identificar el tenant.

        Args:
            request: Request de Django

        Returns:
            Response: Respuesta procesada
        """
        # Identificar tenant por dominio/subdominio
        tenant = self.get_tenant_from_request(request)

        if tenant:
            # Verificar estado del tenant
            if not self.is_tenant_accessible(tenant):
                return self.handle_inaccessible_tenant(tenant, request)

            # Establecer tenant en el request
            request.tenant = tenant

            # Configurar base de datos específica si es necesario
            self.setup_tenant_database(tenant)

        else:
            # Manejar caso sin tenant
            return self.handle_no_tenant(request)

        response = self.get_response(request)
        return response

    def get_tenant_from_request(self, request):
        """
        Identifica el tenant desde la request.

        Args:
            request: Request de Django

        Returns:
            TenantModel: Tenant identificado o None
        """
        host = request.get_host().lower()

        # Intentar por dominio personalizado
        try:
            return TenantModel.objects.get(domain=host, is_active=True)
        except TenantModel.DoesNotExist:
            pass

        # Intentar por subdominio
        subdomain = self.extract_subdomain(host)
        if subdomain:
            try:
                return TenantModel.objects.get(subdomain=subdomain, is_active=True)
            except TenantModel.DoesNotExist:
                pass

        return None

    def extract_subdomain(self, host):
        """
        Extrae el subdominio del host.

        Args:
            host: Host de la request

        Returns:
            str: Subdominio extraído o None
        """
        from django.conf import settings

        base_domain = getattr(settings, 'BASE_DOMAIN', 'example.com')

        if host.endswith(f'.{base_domain}'):
            subdomain = host.replace(f'.{base_domain}', '')
            # Verificar que no sea www u otro subdominio reservado
            reserved_subdomains = ['www', 'api', 'admin', 'app']
            if subdomain not in reserved_subdomains:
                return subdomain

        return None

    def is_tenant_accessible(self, tenant):
        """
        Verifica si el tenant es accesible.

        Args:
            tenant: Tenant a verificar

        Returns:
            bool: True si es accesible
        """
        if not tenant.is_active:
            return False

        if tenant.status == 'suspended':
            return False

        if tenant.status == 'trial' and tenant.is_trial_expired():
            return False

        if not tenant.is_subscription_active():
            return False

        return True

    def handle_inaccessible_tenant(self, tenant, request):
        """
        Maneja el caso de tenant no accesible.

        Args:
            tenant: Tenant no accesible
            request: Request de Django

        Returns:
            Response: Respuesta de error
        """
        from django.shortcuts import render
        from django.http import HttpResponse

        if tenant.status == 'suspended':
            return render(request, 'tenants/suspended.html', {
                'tenant': tenant,
                'message': 'Esta cuenta ha sido suspendida.'
            }, status=403)

        if tenant.is_trial_expired():
            return render(request, 'tenants/trial_expired.html', {
                'tenant': tenant,
                'message': 'El período de prueba ha expirado.'
            }, status=402)

        if not tenant.is_subscription_active():
            return render(request, 'tenants/subscription_expired.html', {
                'tenant': tenant,
                'message': 'La suscripción ha expirado.'
            }, status=402)

        return HttpResponse('Tenant no disponible', status=503)

    def handle_no_tenant(self, request):
        """
        Maneja el caso de no encontrar tenant.

        Args:
            request: Request de Django

        Returns:
            Response: Respuesta de error o redirección
        """
        from django.shortcuts import render

        # Verificar si es una ruta de administración
        if request.path.startswith('/admin/'):
            # Permitir acceso a admin sin tenant
            request.tenant = None
            return None

        # Mostrar página de tenant no encontrado
        return render(request, 'tenants/not_found.html', {
            'host': request.get_host(),
            'message': 'No se encontró una organización asociada a este dominio.'
        }, status=404)
```

## Helpers y Utilidades

### TenantHelpers
```python
def get_current_tenant():
    """
    Obtiene el tenant actual desde el contexto de request.

    Returns:
        TenantModel: Tenant actual o None
    """
    from django.contrib.admin.models import LogEntry

    # Intentar obtener desde middleware local storage
    import threading
    local = threading.local()
    return getattr(local, 'current_tenant', None)

def set_current_tenant(tenant):
    """
    Establece el tenant actual en el contexto local.

    Args:
        tenant: Tenant a establecer
    """
    import threading
    local = threading.local()
    local.current_tenant = tenant

def tenant_required(view_func):
    """
    Decorador que requiere un tenant válido.

    Args:
        view_func: Vista a decorar

    Returns:
        function: Vista decorada
    """
    def wrapper(request, *args, **kwargs):
        if not hasattr(request, 'tenant') or not request.tenant:
            from django.http import HttpResponseForbidden
            return HttpResponseForbidden('Tenant requerido')
        return view_func(request, *args, **kwargs)
    return wrapper

def get_tenant_setting(tenant, category, key, default=None):
    """
    Obtiene una configuración específica del tenant.

    Args:
        tenant: Tenant del cual obtener la configuración
        category: Categoría de la configuración
        key: Clave de la configuración
        default: Valor por defecto

    Returns:
        Valor de la configuración
    """
    try:
        setting = TenantSettings.objects.get(
            tenant=tenant,
            category=category,
            key=key
        )
        return setting.get_typed_value()
    except TenantSettings.DoesNotExist:
        return default

def set_tenant_setting(tenant, category, key, value, data_type='string'):
    """
    Establece una configuración del tenant.

    Args:
        tenant: Tenant para el cual establecer la configuración
        category: Categoría de la configuración
        key: Clave de la configuración
        value: Valor a establecer
        data_type: Tipo de dato del valor
    """
    setting, created = TenantSettings.objects.update_or_create(
        tenant=tenant,
        category=category,
        key=key,
        defaults={
            'value': str(value),
            'data_type': data_type
        }
    )
    return setting
```

## Testing

### Ejemplos de Tests Completos
```python
class TenantModelTestCase(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.tenant_data = {
            'name': 'Test Tenant',
            'contact_email': 'test@example.com',
            'subscription_tier': 'basic',
            'created_by': self.user
        }

    def test_tenant_creation(self):
        """Test de creación básica de tenant."""
        tenant = TenantModel.objects.create(**self.tenant_data)

        self.assertEqual(tenant.name, 'Test Tenant')
        self.assertEqual(tenant.slug, 'test-tenant')
        self.assertTrue(tenant.is_active)
        self.assertIsNotNone(tenant.subdomain)

    def test_tenant_usage_limits(self):
        """Test de límites de uso del tenant."""
        tenant = TenantModel.objects.create(**self.tenant_data)

        # Verificar límites iniciales
        self.assertTrue(tenant.can_add_user())
        self.assertTrue(tenant.can_add_agent())
        self.assertTrue(tenant.can_upload_file(100))  # 100MB
        self.assertTrue(tenant.can_send_message())

    def test_tenant_subscription_upgrade(self):
        """Test de actualización de suscripción."""
        tenant = TenantModel.objects.create(**self.tenant_data)
        manager = TenantManager()

        # Actualizar a profesional
        success = manager.upgrade_subscription(tenant, 'professional')

        self.assertTrue(success)
        tenant.refresh_from_db()
        self.assertEqual(tenant.subscription_tier, 'professional')
        self.assertEqual(tenant.max_users, 100)

    def test_tenant_user_management(self):
        """Test de gestión de usuarios del tenant."""
        tenant = TenantModel.objects.create(**self.tenant_data)
        manager = TenantManager()

        # Agregar usuario
        new_user = UserFactory()
        tenant_user = manager.add_user_to_tenant(tenant, new_user, role='admin')

        self.assertEqual(tenant_user.tenant, tenant)
        self.assertEqual(tenant_user.user, new_user)
        self.assertEqual(tenant_user.role, 'admin')
        self.assertTrue(tenant_user.has_permission('manage_users'))

    def test_tenant_settings(self):
        """Test de configuraciones del tenant."""
        tenant = TenantModel.objects.create(**self.tenant_data)

        # Crear configuración
        setting = TenantSettings.objects.create(
            tenant=tenant,
            category='general',
            key='timezone',
            value='America/New_York',
            data_type='string'
        )

        # Verificar valor tipado
        self.assertEqual(setting.get_typed_value(), 'America/New_York')

        # Probar configuración booleana
        bool_setting = TenantSettings.objects.create(
            tenant=tenant,
            category='features',
            key='enable_chat',
            value='true',
            data_type='boolean'
        )

        self.assertTrue(bool_setting.get_typed_value())

class TenantMiddlewareTestCase(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = TenantMiddleware(lambda r: HttpResponse())
        self.tenant = TenantFactory(subdomain='test')

    def test_tenant_identification_by_subdomain(self):
        """Test de identificación de tenant por subdominio."""
        request = self.factory.get('/', HTTP_HOST='test.example.com')

        # Mock del método extract_subdomain
        with patch.object(self.middleware, 'extract_subdomain', return_value='test'):
            response = self.middleware(request)

        self.assertEqual(request.tenant, self.tenant)

    def test_suspended_tenant_handling(self):
        """Test de manejo de tenant suspendido."""
        self.tenant.status = 'suspended'
        self.tenant.save()

        request = self.factory.get('/', HTTP_HOST='test.example.com')

        with patch.object(self.middleware, 'get_tenant_from_request', return_value=self.tenant):
            response = self.middleware(request)

        self.assertEqual(response.status_code, 403)

    def test_no_tenant_handling(self):
        """Test de manejo cuando no se encuentra tenant."""
        request = self.factory.get('/', HTTP_HOST='unknown.example.com')

        with patch.object(self.middleware, 'get_tenant_from_request', return_value=None):
            response = self.middleware(request)

        self.assertEqual(response.status_code, 404)
```

## Configuración y Deployment

### Settings de Tenancy
```python
# settings.py
TENANT_CONFIG = {
    'BASE_DOMAIN': 'chatwithus.com',
    'ENABLE_SUBDOMAIN_ROUTING': True,
    'ENABLE_CUSTOM_DOMAINS': True,
    'DEFAULT_SUBSCRIPTION_TIER': 'free',
    'TRIAL_PERIOD_DAYS': 14,
    'SUSPENDED_TENANT_TEMPLATE': 'tenants/suspended.html',
    'EXPIRED_TENANT_TEMPLATE': 'tenants/expired.html',
}

# Middleware
MIDDLEWARE = [
    'tenants.middleware.TenantMiddleware',
    # ... otros middlewares
]

# Cache per tenant
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'KEY_PREFIX': 'tenant_',
        }
    }
}
```

### Comandos de Management
```python
# management/commands/create_tenant.py
from django.core.management.base import BaseCommand
from tenants.services import TenantManager

class Command(BaseCommand):
    help = 'Crea un nuevo tenant'

    def add_arguments(self, parser):
        parser.add_argument('name', type=str, help='Nombre del tenant')
        parser.add_argument('email', type=str, help='Email de contacto')
        parser.add_argument('--tier', type=str, default='free', help='Nivel de suscripción')
        parser.add_argument('--subdomain', type=str, help='Subdominio personalizado')

    def handle(self, *args, **options):
        manager = TenantManager()

        tenant = manager.create_tenant(
            name=options['name'],
            contact_email=options['email'],
            subscription_tier=options['tier'],
            subdomain=options.get('subdomain')
        )

        self.stdout.write(
            self.style.SUCCESS(f'Tenant creado exitosamente: {tenant.slug}')
        )
```

## Mejores Prácticas

### 1. Seguridad
- Aislamiento completo de datos entre tenants
- Validación estricta de dominios y subdominios
- Autenticación y autorización por tenant

### 2. Rendimiento
- Indexación optimizada para consultas multi-tenant
- Cache por tenant para mejorar rendimiento
- Lazy loading de configuraciones

### 3. Escalabilidad
- Diseño preparado para sharding de base de datos
- Balanceador de carga tenant-aware
- Monitoreo de recursos por tenant

### 4. Mantenimiento
- Logging detallado de operaciones de tenant
- Métricas de uso y rendimiento
- Herramientas de administración automatizadas

Este sistema de multitenancy proporciona una base sólida y escalable para gestionar múltiples organizaciones con aislamiento completo de datos, configuraciones flexibles y herramientas avanzadas de administración.
