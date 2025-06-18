from django import forms


class FileUploadForm(forms.Form):
    """Formulario para subir archivos CSV o JSON."""

    CONTENT_TYPE_CHOICES = [
        ("json", "📄 Archivo JSON"),
        ("csv", "📊 Archivo CSV"),
    ]

    name = forms.CharField(
        max_length=255,
        label="📝 Nombre del documento",
        help_text="Nombre que se asignará al documento en la base de datos",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Ej: Base de datos de clientes",
            }
        ),
    )

    content_type = forms.ChoiceField(
        choices=CONTENT_TYPE_CHOICES,
        label="🗂️ Tipo de contenido",
        help_text="Selecciona el tipo de archivo que vas a subir",
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    file = forms.FileField(
        label="📂 Archivo",
        help_text="Selecciona un archivo .json o .csv",
        widget=forms.FileInput(attrs={"class": "form-control", "accept": ".json,.csv"}),
    )

    description = forms.CharField(
        required=False,
        label="📋 Descripción (opcional)",
        help_text="Descripción adicional del contenido",
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Descripción del documento...",
            }
        ),
    )
