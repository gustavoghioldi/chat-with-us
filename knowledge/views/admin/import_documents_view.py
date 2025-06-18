from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from knowledge.forms import DocumentSelectionForm
from knowledge.models import KnowledgeModel
from knowledge.services.document_knowledge_base_service import (
    DocumentKnowledgeBaseService,
)


def import_documents_view(request):
    """Vista para importar un documento existente."""
    if request.method == "POST":
        form = DocumentSelectionForm(request.POST, user=request.user)
        if form.is_valid():
            try:
                selected_document = form.cleaned_data["document"]
                name_prefix = form.cleaned_data.get("name_prefix", "")
                default_description = form.cleaned_data.get(
                    "default_description",
                    "Documento importado desde el sistema de archivos",
                )

                # Crear nombre para el KnowledgeModel
                knowledge_name = (
                    f"{name_prefix}{selected_document.title}"
                    if name_prefix
                    else selected_document.title
                )

                # Usar descripción del documento si existe, o la predeterminada
                description = selected_document.description or default_description

                # Crear modelo de conocimiento para el documento seleccionado
                knowledge = KnowledgeModel.objects.create(
                    name=knowledge_name,
                    path=selected_document.file.path,
                    description=description,
                    category="document",
                    tenant=selected_document.tenant,
                )

                messages.success(
                    request,
                    f"✅ El documento '{selected_document.title}' ha sido importado exitosamente a la base de conocimiento.",
                )

                return HttpResponseRedirect(
                    reverse("admin:knowledge_knowledgemodel_changelist")
                )

            except Exception as e:
                messages.error(request, f"❌ Error al importar documentos: {str(e)}")
                return render(
                    request, "admin/knowledge/import_documents.html", {"form": form}
                )
    else:
        form = DocumentSelectionForm(user=request.user)

    return render(
        request,
        "admin/knowledge/import_documents.html",
        {
            "form": form,
            "title": "📄 Importar Documentos Existentes",
            "subtitle": "Selecciona documentos para agregarlos a la base de conocimiento",
        },
    )
