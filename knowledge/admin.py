import csv
import io
import json

from django import forms
from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import path, reverse
from django.utils.html import format_html

from knowledge.models import KnowledgeModel
from knowledge.services.content_formatter_service import ContentFormatterService


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


@admin.register(KnowledgeModel)
class KnowledgeAdmin(admin.ModelAdmin):
    change_form_template = "admin/knowledge/change_form.html"
    list_display = ("name", "category", "tenant", "file_upload_actions", "created_at")
    search_fields = ("name", "url", "description", "text")
    list_filter = ("category", "tenant", "created_at")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at", "formatted_text_preview")

    fieldsets = (
        (
            "📝 Información Básica",
            {"fields": ("name", "description", "category", "tenant")},
        ),
        (
            "🌐 Contenido Web",
            {
                "fields": ("url",),
                "classes": ("collapse",),
                "description": "Para contenido web o scraping",
            },
        ),
        (
            "📄 Contenido de Texto",
            {
                "fields": ("text", "formatted_text_preview"),
                "classes": ("collapse",),
                "description": "Contenido transformado a Markdown",
            },
        ),
        (
            "🕒 Metadatos",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                    "recreate",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    def get_urls(self):
        """Agregar URLs personalizadas para la carga de archivos."""
        urls = super().get_urls()
        custom_urls = [
            path(
                "upload-file/",
                self.admin_site.admin_view(self.upload_file_view),
                name="knowledge_upload_file",
            ),
        ]
        return custom_urls + urls

    def file_upload_actions(self, obj):
        """Mostrar botones de acción para subir archivos."""
        return format_html(
            '<a class="button" href="{}">📤 Subir Archivo</a>',
            reverse("admin:knowledge_upload_file"),
        )

    file_upload_actions.short_description = "🔧 Acciones"
    file_upload_actions.allow_tags = True

    def formatted_text_preview(self, obj):
        """Vista previa del texto formateado."""
        if obj.text:
            preview = obj.text[:500] + "..." if len(obj.text) > 500 else obj.text
            return format_html(
                '<pre style="white-space: pre-wrap; max-height: 300px; overflow-y: auto;">{}</pre>',
                preview,
            )
        return "Sin contenido"

    formatted_text_preview.short_description = "🔍 Vista Previa del Contenido"

    def upload_file_view(self, request):
        """Vista para subir archivos CSV o JSON."""
        if request.method == "POST":
            form = FileUploadForm(request.POST, request.FILES)
            if form.is_valid():
                try:
                    # Obtener datos del formulario
                    name = form.cleaned_data["name"]
                    content_type = form.cleaned_data["content_type"]
                    uploaded_file = form.cleaned_data["file"]
                    description = form.cleaned_data.get("description", "")

                    # Leer el contenido del archivo
                    file_content = uploaded_file.read().decode("utf-8")

                    # Procesar según el tipo de contenido
                    markdown_content = ""

                    if content_type == "json":
                        # Validar y procesar JSON
                        try:
                            json_data = json.loads(file_content)
                            markdown_content = ContentFormatterService.json_to_markdown(
                                json_data, name
                            )
                            category = "plain_document"

                            # Validar si es una lista con más de 1000 elementos
                            if isinstance(json_data, list) and len(json_data) > 1000:
                                messages.warning(
                                    request,
                                    f"⚠️ El archivo JSON contiene {len(json_data)} elementos. "
                                    f"Se recomienda usar archivos con menos de 1000 elementos para mejor rendimiento.",
                                )

                        except json.JSONDecodeError as e:
                            messages.error(
                                request, f"❌ Error al procesar JSON: {str(e)}"
                            )
                            return render(
                                request,
                                "admin/knowledge/upload_file.html",
                                {"form": form},
                            )

                    elif content_type == "csv":
                        # Validar y procesar CSV
                        try:
                            # Validar formato CSV
                            csv_file = io.StringIO(file_content)
                            reader = csv.reader(csv_file)
                            rows = list(reader)

                            if len(rows) < 2:
                                messages.error(
                                    request,
                                    "❌ El archivo CSV debe tener al menos una fila de encabezados y una fila de datos.",
                                )
                                return render(
                                    request,
                                    "admin/knowledge/upload_file.html",
                                    {"form": form},
                                )

                            # Validar límite de filas
                            if len(rows) > 1001:  # 1 header + 1000 data rows
                                messages.warning(
                                    request,
                                    f"⚠️ El archivo CSV contiene {len(rows)-1} filas de datos. "
                                    f"Se recomienda usar archivos con menos de 1000 filas para mejor rendimiento.",
                                )

                            markdown_content = ContentFormatterService.csv_to_markdown(
                                file_content, name
                            )
                            category = "plain_document"

                        except Exception as e:
                            messages.error(
                                request, f"❌ Error al procesar CSV: {str(e)}"
                            )
                            return render(
                                request,
                                "admin/knowledge/upload_file.html",
                                {"form": form},
                            )

                    # Crear el modelo de conocimiento
                    knowledge = KnowledgeModel.objects.create(
                        name=name,
                        text=markdown_content,
                        description=description
                        or f"Documento {content_type.upper()} importado desde archivo: {uploaded_file.name}",
                        category=category,
                        tenant=(
                            request.user.profile.tenant
                            if hasattr(request.user, "profile")
                            and request.user.profile.tenant
                            else None
                        ),
                    )

                    messages.success(
                        request,
                        f"✅ Archivo {content_type.upper()} procesado exitosamente! "
                        f"Se creó el documento '{name}' con ID {knowledge.id}. "
                        f"El contenido fue convertido a formato Markdown.",
                    )

                    # Redirigir al detalle del objeto creado
                    return HttpResponseRedirect(
                        reverse(
                            "admin:knowledge_knowledgemodel_change", args=[knowledge.id]
                        )
                    )

                except Exception as e:
                    messages.error(
                        request, f"❌ Error inesperado al procesar el archivo: {str(e)}"
                    )
                    return render(
                        request, "admin/knowledge/upload_file.html", {"form": form}
                    )
        else:
            form = FileUploadForm()

        return render(
            request,
            "admin/knowledge/upload_file.html",
            {
                "form": form,
                "title": "📤 Subir Archivo CSV o JSON",
                "subtitle": "Los archivos serán convertidos automáticamente a formato Markdown",
            },
        )

    def changelist_view(self, request, extra_context=None):
        """Personalizar la vista de lista para agregar botón de subida."""
        extra_context = extra_context or {}
        extra_context["upload_url"] = reverse("admin:knowledge_upload_file")
        return super().changelist_view(request, extra_context)
