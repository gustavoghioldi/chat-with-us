from main.models import AppModel, models
class ApiCallModel(AppModel):
    """Modelo para registrar llamadas a APIs externas"""

    name = models.CharField(max_length=255, unique=True)
    url = models.URLField()
    body = models.TextField(blank=True, null=True)
    method = models.CharField(
        max_length=10,
        choices=[
            ("GET", "GET"),
        ],
        default="GET",
    )
    username = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Nombre de usuario para autenticación básica, si es necesario",
    )
    password = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Contraseña para autenticación básica, si es necesario",
    )
    api_key = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Clave de API para autenticación, si es necesario",
    )
    headers = models.JSONField(
        blank=True,
        null=True,
        help_text="Encabezados adicionales para la llamada a la API en formato JSON",
    )
    verify_ssl = models.BooleanField(
        default=True,
        help_text="Verificar el certificado SSL de la API, por defecto True",
    )
    timeout = models.IntegerField(
        default=30,
        help_text="Tiempo de espera para la llamada a la API en segundos, por defecto 30",
    )
    intructions = models.TextField(
        blank=True,
        null=True,
        help_text="Instrucciones opcionales para la llamada a la API",
    )
    tenant = models.ForeignKey(
        "tenants.TenantModel",
        on_delete=models.CASCADE,
        related_name="api_calls",
        help_text="Inquilino al que pertenece la llamada a la API",
        null=True,
        blank=True,
        default=None,
    )

    def __str__(self):
        return self.name
