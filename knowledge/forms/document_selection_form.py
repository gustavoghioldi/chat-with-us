from django import forms

from documents.models import DocumentModel


class DocumentSelectionForm(forms.Form):
    """Formulario para seleccionar un documento de DocumentModel."""

    document = forms.ModelChoiceField(
        queryset=DocumentModel.objects.filter(is_active=True),
        widget=forms.Select(attrs={"class": "form-control"}),
        label="📄 Seleccionar Documento",
        help_text="Selecciona un documento para agregar al Knowledge Base",
        required=True,
    )

    name_prefix = forms.CharField(
        max_length=200,
        label="📝 Prefijo para nombres",
        help_text="Prefijo que se añadirá al nombre de cada documento seleccionado",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Ej: Doc importado - ",
                "value": "Doc importado - ",
            }
        ),
        required=False,
    )

    default_description = forms.CharField(
        required=False,
        label="📋 Descripción por defecto",
        help_text="Descripción que se asignará a los documentos si no tienen una propia",
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Documento importado desde el sistema de archivos...",
            }
        ),
        initial="Documento importado desde el sistema de archivos",
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # Filtrar documentos por tenant del usuario si está disponible
        if user and hasattr(user, "profile") and user.profile.tenant:
            self.fields["document"].queryset = DocumentModel.objects.filter(
                is_active=True, tenant=user.profile.tenant
            ).order_by("-created_at")
        else:
            # Si no hay tenant, mostrar todos los documentos activos
            self.fields["document"].queryset = DocumentModel.objects.filter(
                is_active=True
            ).order_by("-created_at")
