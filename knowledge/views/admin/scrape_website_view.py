"""
Vista para scrapear contenido de un sitio web desde el admin.
"""

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from knowledge.forms.scrape_website_form import ScrapeWebsiteForm


@staff_member_required
def scrape_website_view(request):
    """
    Vista para scrapear contenido de un sitio web.
    Permite a los administradores ingresar una URL para extraer su contenido
    y crear un modelo de conocimiento a partir de ella.
    """
    if request.method == "POST":
        form = ScrapeWebsiteForm(request.POST)
        if form.is_valid():
            try:
                form.save()  # Este método debe manejar el scraping y la creación del modelo
                messages.success(
                    request,
                    f"✅ Se ha scrapeado correctamente la URL: {form.cleaned_data['url']}",
                )
                return HttpResponseRedirect(
                    reverse("admin:knowledge_knowledgemodel_changelist")
                )
            except Exception as e:
                messages.error(request, f"❌ Error al scrapear el sitio web: {str(e)}")
    else:
        form = ScrapeWebsiteForm()

    context = {
        "form": form,
        "title": "Scrapear contenido web",
        "is_popup": False,
        "opts": {
            "app_label": "knowledge",
            "app_config": {"verbose_name": "Conocimiento"},
        },
    }
    return render(request, "admin/knowledge/scrape_website_form.html", context)
