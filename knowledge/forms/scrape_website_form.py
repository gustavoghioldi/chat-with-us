"""
Formulario para scrapear contenido de un sitio web.
"""

from django import forms
from django.utils.text import slugify

from knowledge.models import KnowledgeModel
from knowledge.services.web_scraper_service import WebScraperService


class ScrapeWebsiteForm(forms.Form):
    """Formulario para scrapear contenido de un sitio web."""

    url = forms.URLField(
        label="URL del sitio web",
        required=True,
        help_text="Ingresa la URL completa del sitio web que deseas scrapear (incluyendo http:// o https://)",
        widget=forms.URLInput(
            attrs={
                "class": "form-control",
                "placeholder": "https://ejemplo.com",
            }
        ),
    )

    name = forms.CharField(
        label="Nombre",
        required=True,
        help_text="Nombre para el modelo de conocimiento",
        max_length=255,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Nombre del modelo de conocimiento",
            }
        ),
    )

    description = forms.CharField(
        label="Descripción",
        required=False,
        help_text="Descripción opcional para el modelo de conocimiento",
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "placeholder": "Descripción del contenido",
                "rows": 3,
            }
        ),
    )

    tenant = forms.ChoiceField(
        label="Tenant",
        required=False,
        help_text="Selecciona el tenant al que pertenece este conocimiento (opcional)",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Obtener todos los tenants disponibles para el campo de selección
        from tenants.models import TenantModel

        tenant_choices = [(None, "---------")] + [
            (tenant.id, tenant.name) for tenant in TenantModel.objects.all()
        ]
        self.fields["tenant"].choices = tenant_choices

    def clean_name(self):
        """Validar que el nombre no exista ya en la base de datos."""
        name = self.cleaned_data["name"]
        if KnowledgeModel.objects.filter(name=name).exists():
            raise forms.ValidationError(
                f"Ya existe un modelo de conocimiento con el nombre '{name}'."
            )
        return name

    def save(self):
        """Scrapear el contenido de la URL y crear un modelo de conocimiento."""
        url = self.cleaned_data["url"]
        name = self.cleaned_data["name"]
        description = self.cleaned_data.get("description", "")
        tenant_id = self.cleaned_data.get("tenant")

        tenant = None
        if tenant_id:
            from tenants.models import TenantModel

            tenant = TenantModel.objects.get(pk=tenant_id)

        # Usar el servicio de scraping para obtener el contenido
        scraped_content = WebScraperService.scrape_website(url)

        # Crear el modelo de conocimiento
        knowledge = KnowledgeModel.objects.create(
            name=name,
            description=description,
            url=url,
            text=scraped_content,
            category="website",  # Categoría específica para sitios web
            tenant=tenant,
            recreate=False,  # No es necesario recrear, ya tiene el contenido
        )

        return knowledge
