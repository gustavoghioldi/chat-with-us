"""
Servicio para scrapear contenido de sitios web.
"""

import requests
from bs4 import BeautifulSoup


class WebScraperService:
    """Servicio para extraer contenido de sitios web."""

    @staticmethod
    def scrape_website(url):
        """
        Scrapea el contenido de una URL y lo devuelve formateado.

        Args:
            url (str): La URL del sitio a scrapear

        Returns:
            str: El contenido extraído en formato markdown
        """
        try:
            # Realizar la solicitud HTTP
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()  # Lanzar excepción si hay error HTTP

            # Parsear el HTML
            soup = BeautifulSoup(response.text, "html.parser")

            # Extraer el título
            title = soup.title.string if soup.title else "Título no encontrado"

            # Comenzar el contenido markdown con el título
            markdown_content = f"# {title}\n\n"

            # Extraer la URL canónica si está disponible
            canonical = soup.find("link", rel="canonical")
            if canonical and canonical.get("href"):
                markdown_content += f"URL Canónica: {canonical.get('href')}\n\n"
            else:
                markdown_content += f"URL: {url}\n\n"

            # Extraer la descripción meta si está disponible
            meta_desc = soup.find("meta", attrs={"name": "description"})
            if meta_desc and meta_desc.get("content"):
                markdown_content += f"## Descripción\n\n{meta_desc.get('content')}\n\n"

            # Extraer el contenido principal
            markdown_content += "## Contenido principal\n\n"

            # Intentar encontrar el contenido principal (diferentes estrategias)
            main_content = (
                soup.find("main")
                or soup.find("article")
                or soup.find("div", class_="content")
            )

            if main_content:
                # Procesar el contenido principal
                for element in main_content.find_all(
                    ["h1", "h2", "h3", "h4", "h5", "h6", "p"]
                ):
                    if element.name.startswith("h"):
                        level = int(element.name[1])
                        markdown_content += (
                            f"{'#' * (level + 1)} {element.get_text().strip()}\n\n"
                        )
                    else:
                        text = element.get_text().strip()
                        if text:
                            markdown_content += f"{text}\n\n"
            else:
                # Si no se encuentra un contenido principal claro, extraer párrafos y encabezados
                for element in soup.find_all(["h1", "h2", "h3", "h4", "p"]):
                    if element.name.startswith("h"):
                        level = int(element.name[1])
                        markdown_content += (
                            f"{'#' * (level + 1)} {element.get_text().strip()}\n\n"
                        )
                    else:
                        text = element.get_text().strip()
                        if text and len(text) > 20:  # Evitar párrafos muy cortos
                            markdown_content += f"{text}\n\n"

            # Extraer enlaces relevantes
            links = []
            for a in soup.find_all("a", href=True):
                href = a.get("href")
                text = a.get_text().strip()
                if (
                    text
                    and href
                    and not href.startswith("#")
                    and not href.startswith("javascript:")
                ):
                    # Convertir enlaces relativos a absolutos
                    if not href.startswith(("http://", "https://")):
                        from urllib.parse import urljoin

                        href = urljoin(url, href)
                    links.append(f"- [{text}]({href})")

            if links:
                markdown_content += "## Enlaces relevantes\n\n"
                markdown_content += "\n".join(links)
                markdown_content += "\n\n"

            # Agregar información de origen
            markdown_content += f"---\n\nFuente: [{url}]({url})\n"
            markdown_content += (
                f"Fecha de extracción: {WebScraperService._get_current_date()}\n"
            )

            return markdown_content

        except Exception as e:
            raise Exception(f"Error al scrapear la URL {url}: {str(e)}")

    @staticmethod
    def _get_current_date():
        """Obtener la fecha actual formateada."""
        from datetime import datetime

        return datetime.now().strftime("%d/%m/%Y %H:%M:%S")
