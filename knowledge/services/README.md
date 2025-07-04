# Servicios de Knowledge

## Descripción General
Este directorio contiene los servicios para la gestión de conocimiento del sistema. Los servicios manejan el procesamiento, indexación, búsqueda y gestión de diferentes tipos de documentos y fuentes de conocimiento.

## Estructura de Archivos

### `content_formatter_service.py`
Servicio para formatear y limpiar contenido de documentos.

```python
import re
import html
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class ContentFormatterService:
    """
    Servicio para formatear y limpiar contenido de documentos.
    """

    def __init__(self):
        self.html_tag_pattern = re.compile(r'<[^>]+>')
        self.whitespace_pattern = re.compile(r'\s+')
        self.url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')

    def format_content(self, content: str, content_type: str = 'text') -> str:
        """
        Formatea contenido según su tipo.

        Args:
            content: Contenido a formatear
            content_type: Tipo de contenido (html, markdown, text)

        Returns:
            Contenido formateado
        """
        try:
            if content_type == 'html':
                return self.format_html_content(content)
            elif content_type == 'markdown':
                return self.format_markdown_content(content)
            else:
                return self.format_text_content(content)

        except Exception as e:
            logger.error(f"Error formatting content: {e}")
            return content

    def format_html_content(self, content: str) -> str:
        """
        Formatea contenido HTML.
        """
        # Decodificar entidades HTML
        content = html.unescape(content)

        # Remover scripts y estilos
        content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
        content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL | re.IGNORECASE)

        # Convertir elementos de lista en texto plano
        content = re.sub(r'<li[^>]*>', '• ', content, flags=re.IGNORECASE)
        content = re.sub(r'</li>', '\n', content, flags=re.IGNORECASE)

        # Convertir párrafos en saltos de línea
        content = re.sub(r'<p[^>]*>', '', content, flags=re.IGNORECASE)
        content = re.sub(r'</p>', '\n\n', content, flags=re.IGNORECASE)

        # Convertir encabezados
        for i in range(1, 7):
            content = re.sub(f'<h{i}[^>]*>', f'\n{"#" * i} ', content, flags=re.IGNORECASE)
            content = re.sub(f'</h{i}>', '\n\n', content, flags=re.IGNORECASE)

        # Remover todas las etiquetas HTML restantes
        content = self.html_tag_pattern.sub('', content)

        # Limpiar espacios en blanco
        return self.clean_whitespace(content)

    def format_markdown_content(self, content: str) -> str:
        """
        Formatea contenido Markdown.
        """
        # Normalizar saltos de línea
        content = content.replace('\r\n', '\n').replace('\r', '\n')

        # Limpiar enlaces excesivos
        content = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', content)

        # Limpiar imágenes
        content = re.sub(r'!\[([^\]]*)\]\([^)]+\)', r'[Imagen: \1]', content)

        # Limpiar código inline excesivo
        content = re.sub(r'`([^`]+)`', r'\1', content)

        return self.clean_whitespace(content)

    def format_text_content(self, content: str) -> str:
        """
        Formatea contenido de texto plano.
        """
        # Normalizar saltos de línea
        content = content.replace('\r\n', '\n').replace('\r', '\n')

        return self.clean_whitespace(content)

    def clean_whitespace(self, content: str) -> str:
        """
        Limpia espacios en blanco excesivos.
        """
        # Remover espacios múltiples
        content = self.whitespace_pattern.sub(' ', content)

        # Remover líneas vacías múltiples
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)

        # Remover espacios al inicio y final
        content = content.strip()

        return content

    def extract_metadata(self, content: str, content_type: str = 'text') -> Dict[str, Any]:
        """
        Extrae metadatos del contenido.
        """
        metadata = {
            'word_count': len(content.split()),
            'char_count': len(content),
            'paragraph_count': content.count('\n\n') + 1,
            'urls': self.extract_urls(content),
            'language': self.detect_language(content)
        }

        if content_type == 'html':
            metadata.update(self.extract_html_metadata(content))
        elif content_type == 'markdown':
            metadata.update(self.extract_markdown_metadata(content))

        return metadata

    def extract_urls(self, content: str) -> list:
        """
        Extrae URLs del contenido.
        """
        return self.url_pattern.findall(content)

    def detect_language(self, content: str) -> str:
        """
        Detecta el idioma del contenido.
        """
        try:
            from langdetect import detect
            return detect(content)
        except:
            return 'unknown'

    def extract_html_metadata(self, content: str) -> Dict[str, Any]:
        """
        Extrae metadatos específicos de HTML.
        """
        metadata = {}

        # Extraer título
        title_match = re.search(r'<title[^>]*>([^<]+)</title>', content, re.IGNORECASE)
        if title_match:
            metadata['title'] = title_match.group(1).strip()

        # Extraer meta descripción
        desc_match = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']+)["\']', content, re.IGNORECASE)
        if desc_match:
            metadata['description'] = desc_match.group(1).strip()

        # Contar encabezados
        for i in range(1, 7):
            headings = re.findall(f'<h{i}[^>]*>([^<]+)</h{i}>', content, re.IGNORECASE)
            if headings:
                metadata[f'h{i}_count'] = len(headings)
                metadata[f'h{i}_texts'] = headings

        return metadata

    def extract_markdown_metadata(self, content: str) -> Dict[str, Any]:
        """
        Extrae metadatos específicos de Markdown.
        """
        metadata = {}

        # Contar encabezados
        for i in range(1, 7):
            pattern = f'^{"#" * i} (.+)$'
            headings = re.findall(pattern, content, re.MULTILINE)
            if headings:
                metadata[f'h{i}_count'] = len(headings)
                metadata[f'h{i}_texts'] = headings

        # Contar elementos de código
        code_blocks = re.findall(r'```[\s\S]*?```', content)
        metadata['code_blocks'] = len(code_blocks)

        # Contar enlaces
        links = re.findall(r'\[([^\]]+)\]\([^)]+\)', content)
        metadata['links'] = len(links)

        return metadata

    def chunk_content(self, content: str, chunk_size: int = 1000, overlap: int = 200) -> list:
        """
        Divide el contenido en chunks.

        Args:
            content: Contenido a dividir
            chunk_size: Tamaño de cada chunk en caracteres
            overlap: Solapamiento entre chunks

        Returns:
            Lista de chunks
        """
        if len(content) <= chunk_size:
            return [content]

        chunks = []
        start = 0

        while start < len(content):
            end = start + chunk_size

            # Si no es el último chunk, buscar un punto de corte natural
            if end < len(content):
                # Buscar el final de una oración
                sentence_end = content.rfind('.', start, end)
                if sentence_end > start + chunk_size // 2:
                    end = sentence_end + 1
                else:
                    # Buscar el final de una palabra
                    word_end = content.rfind(' ', start, end)
                    if word_end > start + chunk_size // 2:
                        end = word_end

            chunk = content[start:end].strip()
            if chunk:
                chunks.append(chunk)

            # Calcular el próximo inicio con solapamiento
            start = max(start + 1, end - overlap)

            # Evitar chunks muy pequeños al final
            if len(content) - start < chunk_size // 4:
                remaining = content[start:].strip()
                if remaining and remaining not in chunks:
                    chunks.append(remaining)
                break

        return chunks

    def summarize_content(self, content: str, max_length: int = 500) -> str:
        """
        Genera un resumen del contenido.
        """
        if len(content) <= max_length:
            return content

        # Dividir en oraciones
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if s.strip()]

        # Seleccionar las primeras oraciones que quepan en max_length
        summary = ""
        for sentence in sentences:
            if len(summary + sentence + ". ") <= max_length:
                summary += sentence + ". "
            else:
                break

        return summary.strip()

    def clean_for_search(self, content: str) -> str:
        """
        Limpia contenido para indexación de búsqueda.
        """
        # Convertir a minúsculas
        content = content.lower()

        # Remover caracteres especiales
        content = re.sub(r'[^\w\s]', ' ', content)

        # Remover números solos
        content = re.sub(r'\b\d+\b', '', content)

        # Limpiar espacios
        content = self.whitespace_pattern.sub(' ', content)

        return content.strip()

    def validate_content(self, content: str, min_length: int = 10) -> Dict[str, Any]:
        """
        Valida el contenido.
        """
        validation_result = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }

        # Validar longitud mínima
        if len(content.strip()) < min_length:
            validation_result['is_valid'] = False
            validation_result['errors'].append(f"Content too short (minimum {min_length} characters)")

        # Verificar si el contenido es principalmente código
        code_ratio = len(re.findall(r'[{}();]', content)) / len(content)
        if code_ratio > 0.3:
            validation_result['warnings'].append("Content appears to be mostly code")

        # Verificar si hay mucho contenido repetitivo
        words = content.split()
        unique_words = set(words)
        if len(words) > 100 and len(unique_words) / len(words) < 0.3:
            validation_result['warnings'].append("Content appears to be repetitive")

        return validation_result
```

### `document_service_factory.py`
Factory para crear servicios de procesamiento de documentos.

```python
from typing import Dict, Type, Optional
import logging

logger = logging.getLogger(__name__)

class DocumentServiceFactory:
    """
    Factory para crear servicios de procesamiento de documentos.
    """

    _services: Dict[str, Type] = {}

    @classmethod
    def register_service(cls, document_type: str, service_class: Type):
        """
        Registra un servicio para un tipo de documento.
        """
        cls._services[document_type.lower()] = service_class
        logger.info(f"Registered service {service_class.__name__} for type {document_type}")

    @classmethod
    def create_service(cls, document_type: str, **kwargs):
        """
        Crea un servicio para el tipo de documento especificado.
        """
        document_type = document_type.lower()

        if document_type not in cls._services:
            raise ValueError(f"No service registered for document type: {document_type}")

        service_class = cls._services[document_type]
        return service_class(**kwargs)

    @classmethod
    def get_supported_types(cls) -> list:
        """
        Obtiene los tipos de documento soportados.
        """
        return list(cls._services.keys())

    @classmethod
    def is_supported(cls, document_type: str) -> bool:
        """
        Verifica si un tipo de documento es soportado.
        """
        return document_type.lower() in cls._services

# Importar y registrar servicios
from .pdf_document_service import PDFDocumentService
from .docx_document_service import DocxDocumentService
from .plain_document_service import PlainDocumentService
from .csv_document_service import CSVDocumentService
from .json_document_service import JSONDocumentService
from .markdown_document_service import MarkdownDocumentService

# Registrar servicios
DocumentServiceFactory.register_service('pdf', PDFDocumentService)
DocumentServiceFactory.register_service('docx', DocxDocumentService)
DocumentServiceFactory.register_service('doc', DocxDocumentService)
DocumentServiceFactory.register_service('txt', PlainDocumentService)
DocumentServiceFactory.register_service('csv', CSVDocumentService)
DocumentServiceFactory.register_service('json', JSONDocumentService)
DocumentServiceFactory.register_service('md', MarkdownDocumentService)
DocumentServiceFactory.register_service('markdown', MarkdownDocumentService)
```

### `web_scraper_service.py`
Servicio para scraping de sitios web.

```python
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser
import time
import re
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class WebScraperService:
    """
    Servicio para scraping de sitios web.
    """

    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.config.get('user_agent', 'Mozilla/5.0 (compatible; KnowledgeBot/1.0)')
        })
        self.visited_urls = set()
        self.scraped_pages = []

    def scrape_website(self, url: str, max_depth: int = 1, max_pages: int = 10) -> List[Dict]:
        """
        Scrappea un sitio web.

        Args:
            url: URL inicial
            max_depth: Profundidad máxima de enlaces
            max_pages: Número máximo de páginas

        Returns:
            Lista de páginas scrapeadas
        """
        try:
            logger.info(f"Starting website scraping: {url}")

            # Verificar robots.txt si está habilitado
            if self.config.get('respect_robots', True):
                if not self.can_fetch(url):
                    logger.warning(f"Robots.txt disallows scraping: {url}")
                    return []

            # Inicializar variables
            self.visited_urls = set()
            self.scraped_pages = []

            # Comenzar scraping
            self._scrape_recursive(url, 0, max_depth, max_pages)

            logger.info(f"Scraping completed. Pages scraped: {len(self.scraped_pages)}")
            return self.scraped_pages

        except Exception as e:
            logger.error(f"Error scraping website: {e}")
            return []

    def _scrape_recursive(self, url: str, current_depth: int, max_depth: int, max_pages: int):
        """
        Scrappea recursivamente una URL.
        """
        if (len(self.scraped_pages) >= max_pages or
            current_depth > max_depth or
            url in self.visited_urls):
            return

        self.visited_urls.add(url)

        try:
            # Hacer request
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            # Verificar tipo de contenido
            content_type = response.headers.get('content-type', '')
            if not content_type.startswith('text/html'):
                logger.warning(f"Skipping non-HTML content: {url}")
                return

            # Parsear contenido
            soup = BeautifulSoup(response.content, 'html.parser')
            page_data = self._extract_page_data(soup, url)

            if page_data['content'].strip():
                self.scraped_pages.append(page_data)
                logger.info(f"Scraped page: {url}")

            # Esperar antes del siguiente request
            wait_time = self.config.get('wait_time', 1.0)
            time.sleep(wait_time)

            # Buscar enlaces para scraping recursivo
            if current_depth < max_depth and self.config.get('follow_links', True):
                links = self._extract_links(soup, url)

                for link_url in links:
                    if len(self.scraped_pages) >= max_pages:
                        break

                    if self._should_follow_link(link_url):
                        self._scrape_recursive(link_url, current_depth + 1, max_depth, max_pages)

        except Exception as e:
            logger.error(f"Error scraping URL {url}: {e}")

    def _extract_page_data(self, soup: BeautifulSoup, url: str) -> Dict:
        """
        Extrae datos de una página.
        """
        # Extraer título
        title = ""
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text().strip()

        # Extraer meta descripción
        description = ""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            description = meta_desc.get('content', '').strip()

        # Extraer contenido usando selectores CSS si están configurados
        content = ""
        css_selectors = self.config.get('css_selectors', [])

        if css_selectors:
            for selector in css_selectors:
                elements = soup.select(selector)
                for element in elements:
                    content += element.get_text() + "\n"
        else:
            # Extraer contenido principal por defecto
            content = self._extract_main_content(soup)

        # Limpiar contenido
        content = self._clean_content(content)

        # Extraer metadatos adicionales
        metadata = {
            'url': url,
            'title': title,
            'description': description,
            'word_count': len(content.split()),
            'scraped_at': time.time()
        }

        return {
            'url': url,
            'title': title,
            'content': content,
            'metadata': metadata
        }

    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """
        Extrae el contenido principal de la página.
        """
        # Remover elementos no deseados
        for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            tag.decompose()

        # Buscar contenedores de contenido principal
        content_selectors = [
            'main', 'article', '[role="main"]',
            '.content', '.main-content', '#content',
            '.post-content', '.entry-content'
        ]

        for selector in content_selectors:
            elements = soup.select(selector)
            if elements:
                return '\n'.join(element.get_text() for element in elements)

        # Si no se encuentra contenido específico, usar el body
        body = soup.find('body')
        if body:
            return body.get_text()

        return soup.get_text()

    def _clean_content(self, content: str) -> str:
        """
        Limpia el contenido extraído.
        """
        # Normalizar espacios en blanco
        content = re.sub(r'\s+', ' ', content)

        # Remover líneas muy cortas (posiblemente navegación)
        lines = content.split('\n')
        cleaned_lines = []

        for line in lines:
            line = line.strip()
            if len(line) > 20:  # Solo mantener líneas con contenido sustancial
                cleaned_lines.append(line)

        return '\n'.join(cleaned_lines)

    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """
        Extrae enlaces de la página.
        """
        links = []
        base_domain = urlparse(base_url).netloc

        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(base_url, href)

            # Solo seguir enlaces del mismo dominio
            if urlparse(full_url).netloc == base_domain:
                links.append(full_url)

        return list(set(links))  # Remover duplicados

    def _should_follow_link(self, url: str) -> bool:
        """
        Determina si se debe seguir un enlace.
        """
        # Verificar patrones de exclusión
        exclude_patterns = self.config.get('exclude_patterns', [])
        for pattern in exclude_patterns:
            if re.search(pattern, url):
                return False

        # Verificar patrones de inclusión
        include_patterns = self.config.get('include_patterns', [])
        if include_patterns:
            for pattern in include_patterns:
                if re.search(pattern, url):
                    break
            else:
                return False

        # Excluir tipos de archivo no deseados
        excluded_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.zip', '.exe']
        parsed_url = urlparse(url)
        path = parsed_url.path.lower()

        for ext in excluded_extensions:
            if path.endswith(ext):
                return False

        return True

    def can_fetch(self, url: str) -> bool:
        """
        Verifica si se puede hacer scraping según robots.txt.
        """
        try:
            parsed_url = urlparse(url)
            robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"

            rp = RobotFileParser()
            rp.set_url(robots_url)
            rp.read()

            user_agent = self.config.get('user_agent', '*')
            return rp.can_fetch(user_agent, url)

        except Exception as e:
            logger.warning(f"Error checking robots.txt: {e}")
            return True  # Permitir si no se puede verificar
```

### `document_knowledge_base_service.py`
Servicio para gestión de la base de conocimiento.

```python
from typing import List, Dict, Any, Optional
from django.db.models import Q
from documents.models import Document
from knowledge.models import KnowledgeBase
import logging

logger = logging.getLogger(__name__)

class DocumentKnowledgeBaseService:
    """
    Servicio para gestión de la base de conocimiento de documentos.
    """

    def __init__(self, tenant=None):
        self.tenant = tenant

    def create_knowledge_base(self, name: str, description: str = "",
                            documents: List[Document] = None) -> KnowledgeBase:
        """
        Crea una nueva base de conocimiento.
        """
        try:
            kb = KnowledgeBase.objects.create(
                name=name,
                description=description,
                tenant=self.tenant
            )

            if documents:
                kb.documents.set(documents)

            logger.info(f"Created knowledge base: {name}")
            return kb

        except Exception as e:
            logger.error(f"Error creating knowledge base: {e}")
            raise

    def add_documents_to_kb(self, kb_id: int, document_ids: List[int]) -> bool:
        """
        Agrega documentos a una base de conocimiento.
        """
        try:
            kb = KnowledgeBase.objects.get(id=kb_id, tenant=self.tenant)
            documents = Document.objects.filter(
                id__in=document_ids,
                tenant=self.tenant,
                is_active=True
            )

            kb.documents.add(*documents)

            # Actualizar índices
            self.update_knowledge_base_index(kb)

            logger.info(f"Added {len(documents)} documents to knowledge base {kb.name}")
            return True

        except Exception as e:
            logger.error(f"Error adding documents to knowledge base: {e}")
            return False

    def search_knowledge_base(self, kb_id: int, query: str,
                            limit: int = 10) -> List[Dict[str, Any]]:
        """
        Busca en una base de conocimiento.
        """
        try:
            kb = KnowledgeBase.objects.get(id=kb_id, tenant=self.tenant)

            # Búsqueda en documentos de la KB
            documents = kb.documents.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(tags__name__icontains=query),
                is_active=True
            ).distinct()[:limit]

            results = []
            for doc in documents:
                # Calcular puntuación de relevancia
                relevance = self.calculate_relevance(doc, query)

                # Extraer snippet
                snippet = self.extract_snippet(doc.content, query)

                results.append({
                    'document_id': doc.id,
                    'title': doc.title,
                    'snippet': snippet,
                    'relevance': relevance,
                    'document_type': doc.document_type,
                    'created_at': doc.created_at.isoformat()
                })

            # Ordenar por relevancia
            results.sort(key=lambda x: x['relevance'], reverse=True)

            return results

        except Exception as e:
            logger.error(f"Error searching knowledge base: {e}")
            return []

    def calculate_relevance(self, document: Document, query: str) -> float:
        """
        Calcula la relevancia de un documento para una consulta.
        """
        score = 0.0
        query_lower = query.lower()

        # Puntuación por título
        if query_lower in document.title.lower():
            score += 1.0

        # Puntuación por contenido
        content_lower = document.content.lower()
        query_words = query_lower.split()

        for word in query_words:
            count = content_lower.count(word)
            score += count * 0.1

        # Puntuación por tags
        for tag in document.tags.all():
            if query_lower in tag.name.lower():
                score += 0.5

        # Normalizar score
        max_score = len(query_words) * 2
        return min(score / max_score, 1.0) if max_score > 0 else 0.0

    def extract_snippet(self, content: str, query: str,
                       snippet_length: int = 200) -> str:
        """
        Extrae un snippet relevante del contenido.
        """
        query_lower = query.lower()
        content_lower = content.lower()

        # Buscar la primera ocurrencia de la consulta
        index = content_lower.find(query_lower)

        if index == -1:
            # Si no se encuentra, buscar palabras individuales
            words = query_lower.split()
            for word in words:
                index = content_lower.find(word)
                if index != -1:
                    break

        if index == -1:
            # Si no se encuentra nada, devolver el inicio
            return content[:snippet_length] + "..."

        # Calcular inicio y fin del snippet
        start = max(0, index - snippet_length // 2)
        end = min(len(content), start + snippet_length)

        snippet = content[start:end]

        # Agregar "..." si es necesario
        if start > 0:
            snippet = "..." + snippet
        if end < len(content):
            snippet = snippet + "..."

        return snippet

    def get_knowledge_base_stats(self, kb_id: int) -> Dict[str, Any]:
        """
        Obtiene estadísticas de una base de conocimiento.
        """
        try:
            kb = KnowledgeBase.objects.get(id=kb_id, tenant=self.tenant)

            documents = kb.documents.filter(is_active=True)

            stats = {
                'total_documents': documents.count(),
                'total_words': sum(len(doc.content.split()) for doc in documents),
                'document_types': {},
                'recent_additions': 0,
                'avg_document_size': 0
            }

            # Estadísticas por tipo
            for doc in documents:
                doc_type = doc.document_type
                if doc_type not in stats['document_types']:
                    stats['document_types'][doc_type] = 0
                stats['document_types'][doc_type] += 1

            # Documentos recientes (últimos 7 días)
            from django.utils import timezone
            from datetime import timedelta

            recent_date = timezone.now() - timedelta(days=7)
            stats['recent_additions'] = documents.filter(
                created_at__gte=recent_date
            ).count()

            # Tamaño promedio
            if documents.exists():
                total_size = sum(len(doc.content) for doc in documents)
                stats['avg_document_size'] = total_size / documents.count()

            return stats

        except Exception as e:
            logger.error(f"Error getting knowledge base stats: {e}")
            return {}

    def update_knowledge_base_index(self, kb: KnowledgeBase):
        """
        Actualiza los índices de la base de conocimiento.
        """
        try:
            # Aquí se implementaría la lógica de reindexación
            # Por ejemplo, actualizar índices de búsqueda, embeddings, etc.

            kb.last_indexed = timezone.now()
            kb.save(update_fields=['last_indexed'])

            logger.info(f"Updated knowledge base index: {kb.name}")

        except Exception as e:
            logger.error(f"Error updating knowledge base index: {e}")

    def export_knowledge_base(self, kb_id: int, format: str = 'json') -> Dict[str, Any]:
        """
        Exporta una base de conocimiento.
        """
        try:
            kb = KnowledgeBase.objects.get(id=kb_id, tenant=self.tenant)
            documents = kb.documents.filter(is_active=True)

            export_data = {
                'knowledge_base': {
                    'name': kb.name,
                    'description': kb.description,
                    'created_at': kb.created_at.isoformat()
                },
                'documents': []
            }

            for doc in documents:
                doc_data = {
                    'title': doc.title,
                    'content': doc.content,
                    'document_type': doc.document_type,
                    'tags': [tag.name for tag in doc.tags.all()],
                    'metadata': doc.metadata,
                    'created_at': doc.created_at.isoformat()
                }
                export_data['documents'].append(doc_data)

            return export_data

        except Exception as e:
            logger.error(f"Error exporting knowledge base: {e}")
            return {}
```

## Servicios Base

### Servicio Base para Documentos
```python
from abc import ABC, abstractmethod

class BaseDocumentService(ABC):
    """
    Clase base para servicios de procesamiento de documentos.
    """

    def __init__(self):
        self.content_formatter = ContentFormatterService()

    @abstractmethod
    def extract_content(self, file_path: str) -> str:
        """
        Extrae contenido de un archivo.
        """
        pass

    @abstractmethod
    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Extrae metadatos de un archivo.
        """
        pass

    def process_document(self, file_path: str) -> Dict[str, Any]:
        """
        Procesa un documento completo.
        """
        try:
            content = self.extract_content(file_path)
            metadata = self.extract_metadata(file_path)

            # Formatear contenido
            formatted_content = self.content_formatter.format_content(
                content,
                self.get_content_type()
            )

            # Validar contenido
            validation = self.content_formatter.validate_content(formatted_content)

            return {
                'content': formatted_content,
                'metadata': metadata,
                'validation': validation,
                'success': True
            }

        except Exception as e:
            logger.error(f"Error processing document: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    @abstractmethod
    def get_content_type(self) -> str:
        """
        Obtiene el tipo de contenido que maneja este servicio.
        """
        pass
```

## Integración con Tareas Asíncronas

### Tareas de Celery
```python
from celery import shared_task

@shared_task
def process_document_async(document_id):
    """
    Procesa un documento de forma asíncrona.
    """
    try:
        document = Document.objects.get(id=document_id)

        # Obtener servicio apropiado
        service = DocumentServiceFactory.create_service(document.document_type)

        # Procesar documento
        result = service.process_document(document.file_path)

        if result['success']:
            # Actualizar documento con contenido procesado
            document.content = result['content']
            document.metadata = result['metadata']
            document.processing_status = 'completed'
            document.save()
        else:
            document.processing_status = 'failed'
            document.processing_error = result['error']
            document.save()

    except Exception as e:
        logger.error(f"Error in async document processing: {e}")
```

## Testing

### Test de Servicios
```python
class KnowledgeServicesTestCase(TestCase):
    def test_content_formatter(self):
        formatter = ContentFormatterService()

        html_content = "<p>Test <b>content</b></p>"
        formatted = formatter.format_html_content(html_content)

        self.assertEqual(formatted, "Test content")

    def test_document_service_factory(self):
        service = DocumentServiceFactory.create_service('pdf')
        self.assertIsInstance(service, PDFDocumentService)

        with self.assertRaises(ValueError):
            DocumentServiceFactory.create_service('unsupported')
```

## Mejores Prácticas

1. **Separación de Responsabilidades**: Cada servicio tiene una función específica
2. **Factory Pattern**: Usar factory para crear servicios dinámicamente
3. **Manejo de Errores**: Capturar y registrar errores apropiadamente
4. **Async Processing**: Procesar documentos grandes de forma asíncrona
5. **Caching**: Cachear resultados cuando sea apropiado
6. **Logging**: Registrar operaciones importantes para debugging

## Configuración

### Variables de Entorno
```bash
# Procesamiento de documentos
MAX_DOCUMENT_SIZE=10485760  # 10MB
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# Web scraping
DEFAULT_USER_AGENT="Mozilla/5.0 (compatible; KnowledgeBot/1.0)"
DEFAULT_WAIT_TIME=1.0
RESPECT_ROBOTS_TXT=true
```

## Monitoreo

### Métricas de Servicios
```python
def monitor_service_performance(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            # Registrar éxito
            return result
        except Exception as e:
            # Registrar error
            raise
        finally:
            duration = time.time() - start_time
            # Registrar duración
    return wrapper
```
