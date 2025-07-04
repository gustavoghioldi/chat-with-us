# Módulo de Crews (Equipos)

## Descripción General
Este módulo implementa un sistema avanzado de gestión de equipos ("crews") que permite agrupar agentes de IA y usuarios humanos para colaborar en tareas específicas. Los equipos proporcionan un framework para la colaboración multi-agente, el intercambio de recursos y la gestión de flujos de trabajo complejos.

## Arquitectura del Módulo

### Estructura de Archivos
- **models.py**: Define el modelo `CrewModel` y entidades relacionadas con gestión de equipos
- **admin.py**: Configuración avanzada para administrar equipos en el panel de administración
- **views.py**: Vistas para gestión y visualización de equipos desde la interfaz web
- **tests.py**: Suite completa de pruebas unitarias y de integración

### Carpeta `migrations/`
Contiene las migraciones de la base de datos para todos los modelos relacionados con equipos.

## Modelos de Datos

### CrewModel
```python
class CrewModel(models.Model):
    """
    Modelo principal para representar un equipo de trabajo.

    Attributes:
        name: Nombre del equipo
        description: Descripción del equipo y sus objetivos
        tenant: Tenant al que pertenece el equipo
        created_by: Usuario que creó el equipo
        is_active: Estado del equipo
        team_lead: Líder del equipo (opcional)
        max_members: Límite máximo de miembros
        crew_type: Tipo de equipo (support, sales, research, etc.)
        priority_level: Nivel de prioridad del equipo
        performance_metrics: Métricas de rendimiento en JSON
    """

    CREW_TYPES = [
        ('support', 'Soporte Técnico'),
        ('sales', 'Ventas'),
        ('research', 'Investigación'),
        ('development', 'Desarrollo'),
        ('marketing', 'Marketing'),
        ('operations', 'Operaciones'),
        ('custom', 'Personalizado'),
    ]

    PRIORITY_LEVELS = [
        ('low', 'Baja'),
        ('medium', 'Media'),
        ('high', 'Alta'),
        ('critical', 'Crítica'),
    ]

    name = models.CharField(max_length=200, verbose_name="Nombre del Equipo")
    description = models.TextField(blank=True, verbose_name="Descripción")
    tenant = models.ForeignKey(
        'tenants.TenantModel',
        on_delete=models.CASCADE,
        verbose_name="Tenant"
    )
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='created_crews',
        verbose_name="Creado por"
    )
    team_lead = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='led_crews',
        verbose_name="Líder del Equipo"
    )
    crew_type = models.CharField(
        max_length=20,
        choices=CREW_TYPES,
        default='custom',
        verbose_name="Tipo de Equipo"
    )
    priority_level = models.CharField(
        max_length=10,
        choices=PRIORITY_LEVELS,
        default='medium',
        verbose_name="Nivel de Prioridad"
    )
    max_members = models.PositiveIntegerField(
        default=50,
        verbose_name="Máximo de Miembros"
    )
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    performance_metrics = models.JSONField(
        default=dict,
        verbose_name="Métricas de Rendimiento"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Equipo"
        verbose_name_plural = "Equipos"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', 'is_active']),
            models.Index(fields=['crew_type']),
            models.Index(fields=['priority_level']),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_crew_type_display()})"

    @property
    def member_count(self):
        """Retorna el número total de miembros del equipo."""
        return self.members.filter(is_active=True).count()

    @property
    def agent_count(self):
        """Retorna el número de agentes en el equipo."""
        return self.members.filter(
            is_active=True,
            member_type='agent'
        ).count()

    @property
    def human_count(self):
        """Retorna el número de usuarios humanos en el equipo."""
        return self.members.filter(
            is_active=True,
            member_type='human'
        ).count()

    def can_add_member(self):
        """Verifica si se puede agregar un nuevo miembro."""
        return self.member_count < self.max_members

    def get_performance_summary(self):
        """Retorna un resumen de las métricas de rendimiento."""
        metrics = self.performance_metrics
        return {
            'total_tasks': metrics.get('total_tasks', 0),
            'completed_tasks': metrics.get('completed_tasks', 0),
            'success_rate': metrics.get('success_rate', 0.0),
            'avg_response_time': metrics.get('avg_response_time', 0.0),
            'customer_satisfaction': metrics.get('customer_satisfaction', 0.0),
        }
```

### CrewMember
```python
class CrewMember(models.Model):
    """
    Modelo para representar la membresía en un equipo.

    Attributes:
        crew: Equipo al que pertenece
        user: Usuario miembro (opcional)
        agent: Agente miembro (opcional)
        role: Rol del miembro en el equipo
        permissions: Permisos del miembro
        joined_at: Fecha de ingreso al equipo
        is_active: Estado de la membresía
    """

    MEMBER_ROLES = [
        ('leader', 'Líder'),
        ('senior', 'Senior'),
        ('junior', 'Junior'),
        ('specialist', 'Especialista'),
        ('observer', 'Observador'),
    ]

    MEMBER_TYPES = [
        ('human', 'Usuario Humano'),
        ('agent', 'Agente IA'),
    ]

    crew = models.ForeignKey(
        CrewModel,
        on_delete=models.CASCADE,
        related_name='members',
        verbose_name="Equipo"
    )
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Usuario"
    )
    agent = models.ForeignKey(
        'agents.AgentModel',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Agente"
    )
    member_type = models.CharField(
        max_length=10,
        choices=MEMBER_TYPES,
        verbose_name="Tipo de Miembro"
    )
    role = models.CharField(
        max_length=20,
        choices=MEMBER_ROLES,
        default='junior',
        verbose_name="Rol"
    )
    permissions = models.JSONField(
        default=dict,
        verbose_name="Permisos"
    )
    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        verbose_name = "Miembro del Equipo"
        verbose_name_plural = "Miembros del Equipo"
        unique_together = [
            ['crew', 'user'],
            ['crew', 'agent'],
        ]
        indexes = [
            models.Index(fields=['crew', 'is_active']),
            models.Index(fields=['member_type']),
        ]

    def clean(self):
        """Validación personalizada del modelo."""
        if not self.user and not self.agent:
            raise ValidationError("Debe especificar un usuario o un agente")

        if self.user and self.agent:
            raise ValidationError("No puede especificar tanto usuario como agente")

        if self.user:
            self.member_type = 'human'
        elif self.agent:
            self.member_type = 'agent'

    def __str__(self):
        member_name = self.user.username if self.user else self.agent.name
        return f"{member_name} - {self.crew.name} ({self.get_role_display()})"

    @property
    def member_name(self):
        """Retorna el nombre del miembro."""
        return self.user.get_full_name() if self.user else self.agent.name

    @property
    def member_avatar(self):
        """Retorna el avatar del miembro."""
        if self.user and hasattr(self.user, 'profile'):
            return self.user.profile.avatar
        elif self.agent:
            return self.agent.avatar
        return None
```

### CrewTask
```python
class CrewTask(models.Model):
    """
    Modelo para representar tareas asignadas a equipos.

    Attributes:
        crew: Equipo asignado
        title: Título de la tarea
        description: Descripción detallada
        assigned_to: Miembro específico asignado
        priority: Prioridad de la tarea
        status: Estado actual
        due_date: Fecha límite
        completion_rate: Porcentaje de completitud
    """

    TASK_PRIORITIES = [
        ('low', 'Baja'),
        ('medium', 'Media'),
        ('high', 'Alta'),
        ('urgent', 'Urgente'),
    ]

    TASK_STATUS = [
        ('pending', 'Pendiente'),
        ('in_progress', 'En Progreso'),
        ('review', 'En Revisión'),
        ('completed', 'Completada'),
        ('cancelled', 'Cancelada'),
    ]

    crew = models.ForeignKey(
        CrewModel,
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name="Equipo"
    )
    title = models.CharField(max_length=200, verbose_name="Título")
    description = models.TextField(verbose_name="Descripción")
    assigned_to = models.ForeignKey(
        CrewMember,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Asignado a"
    )
    priority = models.CharField(
        max_length=10,
        choices=TASK_PRIORITIES,
        default='medium',
        verbose_name="Prioridad"
    )
    status = models.CharField(
        max_length=20,
        choices=TASK_STATUS,
        default='pending',
        verbose_name="Estado"
    )
    due_date = models.DateTimeField(null=True, blank=True, verbose_name="Fecha Límite")
    completion_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        verbose_name="Porcentaje de Completitud"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Tarea del Equipo"
        verbose_name_plural = "Tareas del Equipo"
        ordering = ['-priority', '-created_at']
        indexes = [
            models.Index(fields=['crew', 'status']),
            models.Index(fields=['priority']),
            models.Index(fields=['due_date']),
        ]

    def __str__(self):
        return f"{self.title} - {self.crew.name}"

    @property
    def is_overdue(self):
        """Verifica si la tarea está vencida."""
        if self.due_date and self.status not in ['completed', 'cancelled']:
            return timezone.now() > self.due_date
        return False

    def get_progress_percentage(self):
        """Retorna el porcentaje de progreso como entero."""
        return int(self.completion_rate)
```

## Funcionalidades Principales

### 1. Gestión de Equipos

#### CrewManager
```python
class CrewManager:
    """
    Servicio para gestionar equipos y sus operaciones.
    """

    def __init__(self, tenant):
        self.tenant = tenant

    def create_crew(self, name, description, crew_type, created_by, **kwargs):
        """
        Crea un nuevo equipo con configuración inicial.

        Args:
            name: Nombre del equipo
            description: Descripción
            crew_type: Tipo de equipo
            created_by: Usuario creador
            **kwargs: Argumentos adicionales

        Returns:
            CrewModel: Equipo creado
        """
        crew = CrewModel.objects.create(
            name=name,
            description=description,
            crew_type=crew_type,
            created_by=created_by,
            tenant=self.tenant,
            **kwargs
        )

        # Agregar creador como líder por defecto
        self.add_member(crew, user=created_by, role='leader')

        # Configurar permisos por defecto
        self.setup_default_permissions(crew)

        return crew

    def add_member(self, crew, user=None, agent=None, role='junior'):
        """
        Agrega un miembro al equipo.

        Args:
            crew: Equipo al que agregar
            user: Usuario a agregar (opcional)
            agent: Agente a agregar (opcional)
            role: Rol del miembro

        Returns:
            CrewMember: Miembro agregado
        """
        if not crew.can_add_member():
            raise ValueError("El equipo ha alcanzado el límite máximo de miembros")

        member = CrewMember.objects.create(
            crew=crew,
            user=user,
            agent=agent,
            role=role
        )

        # Actualizar métricas del equipo
        self.update_team_metrics(crew)

        return member

    def assign_task(self, crew, title, description, assigned_to=None, priority='medium', due_date=None):
        """
        Asigna una nueva tarea al equipo.

        Args:
            crew: Equipo al que asignar
            title: Título de la tarea
            description: Descripción
            assigned_to: Miembro específico (opcional)
            priority: Prioridad de la tarea
            due_date: Fecha límite (opcional)

        Returns:
            CrewTask: Tarea creada
        """
        task = CrewTask.objects.create(
            crew=crew,
            title=title,
            description=description,
            assigned_to=assigned_to,
            priority=priority,
            due_date=due_date
        )

        # Notificar a los miembros del equipo
        self.notify_team_members(crew, f"Nueva tarea asignada: {title}")

        return task

    def get_team_performance(self, crew, period_days=30):
        """
        Calcula las métricas de rendimiento del equipo.

        Args:
            crew: Equipo a analizar
            period_days: Período de análisis en días

        Returns:
            dict: Métricas de rendimiento
        """
        start_date = timezone.now() - timedelta(days=period_days)

        tasks = crew.tasks.filter(created_at__gte=start_date)
        completed_tasks = tasks.filter(status='completed')

        metrics = {
            'total_tasks': tasks.count(),
            'completed_tasks': completed_tasks.count(),
            'success_rate': (completed_tasks.count() / tasks.count() * 100) if tasks.count() > 0 else 0,
            'avg_completion_time': self.calculate_avg_completion_time(completed_tasks),
            'overdue_tasks': tasks.filter(due_date__lt=timezone.now()).count(),
            'member_productivity': self.calculate_member_productivity(crew, start_date),
        }

        # Actualizar métricas en el modelo
        crew.performance_metrics.update(metrics)
        crew.save()

        return metrics

    def setup_default_permissions(self, crew):
        """
        Configura permisos por defecto para el equipo.

        Args:
            crew: Equipo para configurar permisos
        """
        default_permissions = {
            'can_view_tasks': True,
            'can_create_tasks': False,
            'can_assign_tasks': False,
            'can_manage_members': False,
            'can_view_analytics': True,
            'can_access_knowledge_base': True,
        }

        # Aplicar permisos por defecto a todos los miembros
        for member in crew.members.all():
            member.permissions.update(default_permissions)

            # Permisos especiales para líderes
            if member.role == 'leader':
                member.permissions.update({
                    'can_create_tasks': True,
                    'can_assign_tasks': True,
                    'can_manage_members': True,
                })

            member.save()
```

### 2. Colaboración Multi-Agente

#### CrewCollaborationEngine
```python
class CrewCollaborationEngine:
    """
    Motor de colaboración para equipos multi-agente.
    """

    def __init__(self, crew):
        self.crew = crew
        self.agents = crew.members.filter(member_type='agent', is_active=True)
        self.humans = crew.members.filter(member_type='human', is_active=True)

    def coordinate_task_execution(self, task):
        """
        Coordina la ejecución de una tarea entre múltiples agentes.

        Args:
            task: Tarea a ejecutar

        Returns:
            dict: Resultado de la coordinación
        """
        # Analizar la tarea y determinar agentes requeridos
        required_skills = self.analyze_task_requirements(task)
        suitable_agents = self.find_suitable_agents(required_skills)

        if not suitable_agents:
            return {
                'success': False,
                'message': 'No se encontraron agentes adecuados para la tarea'
            }

        # Distribuir subtareas entre agentes
        subtasks = self.decompose_task(task)
        assignments = self.assign_subtasks(subtasks, suitable_agents)

        # Ejecutar subtareas en paralelo
        results = self.execute_parallel_subtasks(assignments)

        # Consolidar resultados
        final_result = self.consolidate_results(results)

        return {
            'success': True,
            'result': final_result,
            'agents_used': [agent.agent.name for agent in suitable_agents],
            'execution_time': self.calculate_execution_time(assignments)
        }

    def analyze_task_requirements(self, task):
        """
        Analiza los requisitos de habilidades para una tarea.

        Args:
            task: Tarea a analizar

        Returns:
            list: Lista de habilidades requeridas
        """
        # Implementar análisis de NLP para extraer requisitos
        description = task.description.lower()

        skill_keywords = {
            'technical_support': ['soporte', 'técnico', 'problema', 'error'],
            'sales': ['venta', 'producto', 'precio', 'compra'],
            'research': ['investigación', 'análisis', 'estudio'],
            'customer_service': ['cliente', 'servicio', 'atención'],
            'content_creation': ['contenido', 'redacción', 'texto'],
        }

        required_skills = []
        for skill, keywords in skill_keywords.items():
            if any(keyword in description for keyword in keywords):
                required_skills.append(skill)

        return required_skills

    def find_suitable_agents(self, required_skills):
        """
        Encuentra agentes adecuados para las habilidades requeridas.

        Args:
            required_skills: Lista de habilidades requeridas

        Returns:
            QuerySet: Agentes adecuados
        """
        suitable_agents = []

        for agent_member in self.agents:
            agent = agent_member.agent
            agent_skills = agent.capabilities.get('skills', [])

            # Verificar si el agente tiene las habilidades requeridas
            if any(skill in agent_skills for skill in required_skills):
                suitable_agents.append(agent_member)

        # Ordenar por experiencia y disponibilidad
        return sorted(suitable_agents, key=lambda x: (
            x.agent.experience_level,
            -x.agent.current_load
        ))

    def coordinate_knowledge_sharing(self, topic):
        """
        Coordina el intercambio de conocimientos entre miembros del equipo.

        Args:
            topic: Tema para el intercambio de conocimientos

        Returns:
            dict: Resultado del intercambio
        """
        knowledge_sources = []

        # Recopilar conocimientos de agentes
        for agent_member in self.agents:
            agent_knowledge = agent_member.agent.query_knowledge(topic)
            if agent_knowledge:
                knowledge_sources.append({
                    'source': agent_member.agent.name,
                    'type': 'agent',
                    'knowledge': agent_knowledge
                })

        # Consolidar conocimientos
        consolidated_knowledge = self.consolidate_knowledge(knowledge_sources)

        # Compartir con todos los miembros del equipo
        self.share_knowledge_with_team(consolidated_knowledge, topic)

        return {
            'topic': topic,
            'sources': len(knowledge_sources),
            'consolidated_knowledge': consolidated_knowledge
        }
```

### 3. Análisis de Rendimiento

#### CrewAnalytics
```python
class CrewAnalytics:
    """
    Servicio de análisis y métricas para equipos.
    """

    def __init__(self, crew):
        self.crew = crew

    def generate_performance_report(self, start_date, end_date):
        """
        Genera un reporte completo de rendimiento del equipo.

        Args:
            start_date: Fecha de inicio
            end_date: Fecha de fin

        Returns:
            dict: Reporte de rendimiento
        """
        tasks = self.crew.tasks.filter(
            created_at__range=[start_date, end_date]
        )

        report = {
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat(),
                'days': (end_date - start_date).days
            },
            'team_info': {
                'name': self.crew.name,
                'type': self.crew.crew_type,
                'total_members': self.crew.member_count,
                'active_members': self.crew.members.filter(is_active=True).count()
            },
            'task_metrics': self.calculate_task_metrics(tasks),
            'member_performance': self.calculate_member_performance(start_date, end_date),
            'collaboration_metrics': self.calculate_collaboration_metrics(start_date, end_date),
            'efficiency_score': self.calculate_efficiency_score(tasks),
            'recommendations': self.generate_recommendations(tasks)
        }

        return report

    def calculate_task_metrics(self, tasks):
        """
        Calcula métricas relacionadas con tareas.

        Args:
            tasks: QuerySet de tareas

        Returns:
            dict: Métricas de tareas
        """
        total_tasks = tasks.count()
        completed_tasks = tasks.filter(status='completed').count()
        overdue_tasks = tasks.filter(
            due_date__lt=timezone.now(),
            status__in=['pending', 'in_progress']
        ).count()

        return {
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'in_progress_tasks': tasks.filter(status='in_progress').count(),
            'pending_tasks': tasks.filter(status='pending').count(),
            'overdue_tasks': overdue_tasks,
            'completion_rate': (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
            'overdue_rate': (overdue_tasks / total_tasks * 100) if total_tasks > 0 else 0,
            'avg_completion_time': self.calculate_avg_completion_time(
                tasks.filter(status='completed')
            ),
            'task_distribution': self.calculate_task_distribution(tasks)
        }

    def calculate_member_performance(self, start_date, end_date):
        """
        Calcula el rendimiento individual de cada miembro.

        Args:
            start_date: Fecha de inicio
            end_date: Fecha de fin

        Returns:
            list: Performance de cada miembro
        """
        performance_data = []

        for member in self.crew.members.filter(is_active=True):
            member_tasks = self.crew.tasks.filter(
                assigned_to=member,
                created_at__range=[start_date, end_date]
            )

            performance = {
                'member_name': member.member_name,
                'member_type': member.member_type,
                'role': member.role,
                'tasks_assigned': member_tasks.count(),
                'tasks_completed': member_tasks.filter(status='completed').count(),
                'tasks_overdue': member_tasks.filter(
                    due_date__lt=timezone.now(),
                    status__in=['pending', 'in_progress']
                ).count(),
                'avg_completion_time': self.calculate_avg_completion_time(
                    member_tasks.filter(status='completed')
                ),
                'efficiency_score': self.calculate_member_efficiency(member, member_tasks)
            }

            performance_data.append(performance)

        return performance_data

    def generate_recommendations(self, tasks):
        """
        Genera recomendaciones basadas en el análisis de rendimiento.

        Args:
            tasks: QuerySet de tareas

        Returns:
            list: Lista de recomendaciones
        """
        recommendations = []

        # Análisis de tareas vencidas
        overdue_rate = tasks.filter(
            due_date__lt=timezone.now(),
            status__in=['pending', 'in_progress']
        ).count() / tasks.count() * 100 if tasks.count() > 0 else 0

        if overdue_rate > 20:
            recommendations.append({
                'type': 'warning',
                'title': 'Alto porcentaje de tareas vencidas',
                'description': f'El {overdue_rate:.1f}% de las tareas están vencidas. Considere revisar la carga de trabajo y los plazos.',
                'priority': 'high'
            })

        # Análisis de distribución de carga
        member_workload = self.analyze_workload_distribution()
        if member_workload['imbalance_score'] > 0.7:
            recommendations.append({
                'type': 'optimization',
                'title': 'Desequilibrio en la carga de trabajo',
                'description': 'La distribución de tareas entre miembros no es equilibrada. Considere redistribuir las tareas.',
                'priority': 'medium'
            })

        # Análisis de colaboración
        collaboration_score = self.calculate_collaboration_score()
        if collaboration_score < 0.5:
            recommendations.append({
                'type': 'improvement',
                'title': 'Baja colaboración entre miembros',
                'description': 'El equipo podría beneficiarse de más tareas colaborativas y intercambio de conocimientos.',
                'priority': 'medium'
            })

        return recommendations
```

## Vistas y API

### CrewListView
```python
class CrewListView(LoginRequiredMixin, ListView):
    """
    Vista para listar equipos del usuario.
    """
    model = CrewModel
    template_name = 'crews/crew_list.html'
    context_object_name = 'crews'
    paginate_by = 20

    def get_queryset(self):
        """Filtra equipos por tenant y permisos del usuario."""
        return CrewModel.objects.filter(
            tenant=self.request.tenant,
            is_active=True
        ).filter(
            Q(members__user=self.request.user) |
            Q(created_by=self.request.user)
        ).distinct().select_related('tenant', 'created_by')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['can_create_crew'] = self.request.user.has_perm('crews.add_crewmodel')
        return context
```

### CrewDetailView
```python
class CrewDetailView(LoginRequiredMixin, DetailView):
    """
    Vista detallada de un equipo.
    """
    model = CrewModel
    template_name = 'crews/crew_detail.html'
    context_object_name = 'crew'

    def get_object(self):
        """Obtiene el equipo con validación de permisos."""
        obj = super().get_object()

        # Verificar acceso
        if not self.has_crew_access(obj):
            raise PermissionDenied("No tienes permisos para ver este equipo")

        return obj

    def has_crew_access(self, crew):
        """Verifica si el usuario tiene acceso al equipo."""
        return (
            crew.tenant == self.request.tenant and
            (crew.members.filter(user=self.request.user).exists() or
             crew.created_by == self.request.user or
             self.request.user.is_superuser)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'members': self.object.members.filter(is_active=True),
            'recent_tasks': self.object.tasks.all()[:5],
            'performance_metrics': self.object.get_performance_summary(),
            'can_manage': self.can_manage_crew(),
        })
        return context

    def can_manage_crew(self):
        """Verifica si el usuario puede gestionar el equipo."""
        if self.request.user.is_superuser:
            return True

        member = self.object.members.filter(user=self.request.user).first()
        if member:
            return member.role in ['leader', 'senior'] or \
                   member.permissions.get('can_manage_members', False)

        return self.object.created_by == self.request.user
```

## Testing

### Ejemplo de Tests
```python
class CrewModelTestCase(TestCase):

    def setUp(self):
        self.tenant = TenantFactory()
        self.user = UserFactory()
        self.crew = CrewFactory(tenant=self.tenant, created_by=self.user)

    def test_crew_creation(self):
        """Test de creación de equipo."""
        self.assertEqual(self.crew.name, 'Test Crew')
        self.assertEqual(self.crew.tenant, self.tenant)
        self.assertEqual(self.crew.created_by, self.user)
        self.assertTrue(self.crew.is_active)

    def test_member_addition(self):
        """Test de agregar miembro al equipo."""
        agent = AgentFactory()
        member = CrewMember.objects.create(
            crew=self.crew,
            agent=agent,
            role='junior'
        )

        self.assertEqual(member.crew, self.crew)
        self.assertEqual(member.agent, agent)
        self.assertEqual(member.member_type, 'agent')

    def test_crew_capacity_limit(self):
        """Test del límite de capacidad del equipo."""
        self.crew.max_members = 2
        self.crew.save()

        # Agregar miembros hasta el límite
        for i in range(2):
            user = UserFactory()
            CrewMember.objects.create(crew=self.crew, user=user)

        # Verificar que no se pueden agregar más miembros
        self.assertFalse(self.crew.can_add_member())

    def test_task_assignment(self):
        """Test de asignación de tareas."""
        task = CrewTask.objects.create(
            crew=self.crew,
            title='Test Task',
            description='Test Description',
            priority='high'
        )

        self.assertEqual(task.crew, self.crew)
        self.assertEqual(task.priority, 'high')
        self.assertEqual(task.status, 'pending')

    def test_performance_metrics(self):
        """Test de métricas de rendimiento."""
        # Crear tareas completadas
        for i in range(3):
            CrewTask.objects.create(
                crew=self.crew,
                title=f'Task {i}',
                description='Test',
                status='completed'
            )

        # Crear tareas pendientes
        for i in range(2):
            CrewTask.objects.create(
                crew=self.crew,
                title=f'Pending Task {i}',
                description='Test',
                status='pending'
            )

        metrics = self.crew.get_performance_summary()
        self.assertEqual(metrics['total_tasks'], 5)
        self.assertEqual(metrics['completed_tasks'], 3)
```

## Integración con otros Módulos

### Con Agents
```python
# Asignar agentes a equipos automáticamente
@receiver(post_save, sender=AgentModel)
def auto_assign_agent_to_crew(sender, instance, created, **kwargs):
    if created:
        # Buscar equipos que necesiten agentes con las habilidades del agente
        suitable_crews = CrewModel.objects.filter(
            tenant=instance.tenant,
            crew_type=instance.specialization,
            is_active=True
        )

        for crew in suitable_crews:
            if crew.can_add_member():
                CrewMember.objects.create(
                    crew=crew,
                    agent=instance,
                    role='junior'
                )
```

### Con Knowledge
```python
# Compartir conocimientos entre miembros del equipo
class CrewKnowledgeSharing:
    def __init__(self, crew):
        self.crew = crew

    def share_knowledge(self, topic, source_member):
        """Comparte conocimiento con todos los miembros del equipo."""
        knowledge_entry = KnowledgeEntry.objects.create(
            crew=self.crew,
            topic=topic,
            source=source_member,
            shared_at=timezone.now()
        )

        # Notificar a todos los miembros
        for member in self.crew.members.filter(is_active=True):
            if member != source_member:
                self.notify_knowledge_sharing(member, knowledge_entry)
```

## Configuración y Deployment

### Settings
```python
# settings.py
CREWS_CONFIG = {
    'MAX_MEMBERS_PER_CREW': 100,
    'AUTO_ASSIGN_AGENTS': True,
    'ENABLE_COLLABORATION_ENGINE': True,
    'PERFORMANCE_ANALYSIS_ENABLED': True,
    'KNOWLEDGE_SHARING_ENABLED': True,
    'NOTIFICATION_SETTINGS': {
        'NEW_MEMBER_NOTIFICATION': True,
        'TASK_ASSIGNMENT_NOTIFICATION': True,
        'PERFORMANCE_REPORTS': True,
    }
}
```

### Celery Tasks
```python
# tasks.py
@shared_task
def update_crew_performance_metrics():
    """Actualiza métricas de rendimiento de todos los equipos."""
    for crew in CrewModel.objects.filter(is_active=True):
        manager = CrewManager(crew.tenant)
        manager.get_team_performance(crew)

@shared_task
def send_crew_performance_reports():
    """Envía reportes de rendimiento a líderes de equipos."""
    for crew in CrewModel.objects.filter(is_active=True):
        analytics = CrewAnalytics(crew)
        report = analytics.generate_performance_report(
            start_date=timezone.now() - timedelta(days=7),
            end_date=timezone.now()
        )

        # Enviar reporte a líderes
        leaders = crew.members.filter(role='leader', is_active=True)
        for leader in leaders:
            send_performance_report_email(leader, report)
```

## Mejores Prácticas

### 1. Organización de Equipos
- Definir roles claros y responsabilidades
- Establecer límites de capacidad apropiados
- Configurar permisos granulares

### 2. Gestión de Tareas
- Usar prioridades para organizar el trabajo
- Establecer fechas límite realistas
- Monitorear el progreso regularmente

### 3. Colaboración
- Fomentar el intercambio de conocimientos
- Implementar revisiones por pares
- Usar métricas para identificar oportunidades de mejora

### 4. Monitoreo y Análisis
- Revisar métricas de rendimiento regularmente
- Implementar alertas para problemas críticos
- Usar datos para optimizar procesos

Este módulo proporciona una base sólida para la gestión de equipos colaborativos con características avanzadas de análisis, coordinación multi-agente y optimización del rendimiento.
