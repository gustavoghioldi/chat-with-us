import csv
import io
import json

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from knowledge.forms import FileUploadForm
from knowledge.models import KnowledgeModel
from knowledge.services.content_formatter_service import ContentFormatterService


def upload_file_view(request):
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
                        messages.error(request, f"❌ Error al procesar JSON: {str(e)}")
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
                        messages.error(request, f"❌ Error al procesar CSV: {str(e)}")
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
