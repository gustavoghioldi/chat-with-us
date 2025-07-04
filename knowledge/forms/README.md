# Formularios de Knowledge

## Descripción General
Este directorio contiene los formularios de Django para la gestión de conocimiento. Los formularios manejan la validación y procesamiento de datos de entrada para diferentes tipos de contenido de conocimiento.

## Estructura de Archivos

### `document_selection_form.py`
Formulario para seleccionar documentos existentes.

```python
from django import forms
from documents.models import Document
from django.contrib.auth.models import User

class DocumentSelectionForm(forms.Form):
    """
    Formulario para seleccionar documentos existentes.
    """

    documents = forms.ModelMultipleChoiceField(
        queryset=Document.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Documentos disponibles"
    )

    search_query = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Buscar documentos...',
            'class': 'form-control'
        }),
        label="Buscar"
    )

    document_type = forms.ChoiceField(
        choices=[
            ('', 'Todos los tipos'),
            ('pdf', 'PDF'),
            ('docx', 'Word'),
            ('txt', 'Texto'),
            ('csv', 'CSV'),
            ('json', 'JSON'),
            ('md', 'Markdown')
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Tipo de documento"
    )

    date_range = forms.ChoiceField(
        choices=[
            ('', 'Cualquier fecha'),
            ('today', 'Hoy'),
            ('week', 'Esta semana'),
            ('month', 'Este mes'),
            ('year', 'Este año')
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Rango de fechas"
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        tenant = kwargs.pop('tenant', None)
        super().__init__(*args, **kwargs)

        # Filtrar documentos por usuario y tenant
        queryset = Document.objects.filter(is_active=True)

        if tenant:
            queryset = queryset.filter(tenant=tenant)

        if user:
            # Mostrar documentos del usuario o públicos
            queryset = queryset.filter(
                models.Q(owner=user) | models.Q(is_public=True)
            )

        self.fields['documents'].queryset = queryset.order_by('-created_at')

    def clean_documents(self):
        """
        Valida la selección de documentos.
        """
        documents = self.cleaned_data.get('documents')

        if not documents:
            raise forms.ValidationError("Debe seleccionar al menos un documento")

        # Validar que no haya más de 50 documentos
        if len(documents) > 50:
            raise forms.ValidationError("No puede seleccionar más de 50 documentos")

        return documents

    def get_filtered_documents(self):
        """
        Obtiene documentos filtrados según los criterios.
        """
        queryset = self.fields['documents'].queryset

        # Aplicar filtro de búsqueda
        if self.cleaned_data.get('search_query'):
            query = self.cleaned_data['search_query']
            queryset = queryset.filter(
                models.Q(title__icontains=query) |
                models.Q(content__icontains=query) |
                models.Q(tags__name__icontains=query)
            ).distinct()

        # Aplicar filtro de tipo
        if self.cleaned_data.get('document_type'):
            queryset = queryset.filter(
                document_type=self.cleaned_data['document_type']
            )

        # Aplicar filtro de fecha
        if self.cleaned_data.get('date_range'):
            date_filter = self.get_date_filter(self.cleaned_data['date_range'])
            queryset = queryset.filter(created_at__gte=date_filter)

        return queryset

    def get_date_filter(self, date_range):
        """
        Obtiene el filtro de fecha según el rango seleccionado.
        """
        from django.utils import timezone
        from datetime import timedelta

        now = timezone.now()

        if date_range == 'today':
            return now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif date_range == 'week':
            return now - timedelta(days=7)
        elif date_range == 'month':
            return now - timedelta(days=30)
        elif date_range == 'year':
            return now - timedelta(days=365)

        return None
```

### `file_upload_form.py`
Formulario para carga de archivos.

```python
from django import forms
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
import os

class FileUploadForm(forms.Form):
    """
    Formulario para cargar archivos de conocimiento.
    """

    file = forms.FileField(
        label="Archivo",
        help_text="Seleccione un archivo para cargar (PDF, DOCX, TXT, CSV, JSON, MD)",
        validators=[
            FileExtensionValidator(
                allowed_extensions=['pdf', 'docx', 'txt', 'csv', 'json', 'md']
            )
        ],
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'accept': '.pdf,.docx,.txt,.csv,.json,.md'
        })
    )

    title = forms.CharField(
        max_length=200,
        required=False,
        help_text="Título para el documento (opcional, se usará el nombre del archivo si no se especifica)",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Título del documento'
        })
    )

    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 3,
            'class': 'form-control',
            'placeholder': 'Descripción opcional del documento'
        }),
        required=False,
        help_text="Descripción opcional del documento"
    )

    tags = forms.CharField(
        max_length=500,
        required=False,
        help_text="Etiquetas separadas por comas",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'etiqueta1, etiqueta2, etiqueta3'
        })
    )

    category = forms.ChoiceField(
        choices=[
            ('', 'Seleccionar categoría'),
            ('general', 'General'),
            ('technical', 'Técnico'),
            ('policy', 'Política'),
            ('procedure', 'Procedimiento'),
            ('faq', 'FAQ'),
            ('training', 'Entrenamiento'),
            ('reference', 'Referencia')
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    is_public = forms.BooleanField(
        required=False,
        initial=False,
        help_text="Marque para hacer el documento visible para todos los usuarios del tenant",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    generate_embeddings = forms.BooleanField(
        required=False,
        initial=True,
        help_text="Generar embeddings para búsqueda semántica",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    processing_config = forms.JSONField(
        required=False,
        help_text="Configuración de procesamiento en formato JSON",
        widget=forms.Textarea(attrs={
            'rows': 4,
            'class': 'form-control',
            'placeholder': '{"chunk_size": 1000, "overlap": 200}'
        })
    )

    def clean_file(self):
        """
        Valida el archivo cargado.
        """
        file = self.cleaned_data.get('file')

        if not file:
            return file

        # Validar tamaño del archivo (máximo 10MB)
        if file.size > 10 * 1024 * 1024:
            raise ValidationError("El archivo no puede ser mayor a 10MB")

        # Validar tipo de contenido
        allowed_content_types = {
            'pdf': 'application/pdf',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'txt': 'text/plain',
            'csv': 'text/csv',
            'json': 'application/json',
            'md': 'text/markdown'
        }

        file_extension = os.path.splitext(file.name)[1].lower().lstrip('.')

        if file_extension in allowed_content_types:
            expected_content_type = allowed_content_types[file_extension]
            if file.content_type != expected_content_type:
                # Permitir algunos tipos de contenido alternativos
                if file_extension == 'txt' and 'text/' in file.content_type:
                    pass  # Permitir diferentes tipos de texto
                elif file_extension == 'md' and 'text/' in file.content_type:
                    pass  # Permitir diferentes tipos de texto para markdown
                else:
                    raise ValidationError(f"Tipo de archivo incorrecto para {file_extension}")

        return file

    def clean_title(self):
        """
        Valida y limpia el título.
        """
        title = self.cleaned_data.get('title')

        if title:
            # Remover caracteres especiales
            import re
            title = re.sub(r'[^\w\s-]', '', title)
            title = title.strip()

            if len(title) < 3:
                raise ValidationError("El título debe tener al menos 3 caracteres")

        return title

    def clean_tags(self):
        """
        Valida y procesa las etiquetas.
        """
        tags = self.cleaned_data.get('tags')

        if tags:
            # Procesar etiquetas
            tag_list = [tag.strip().lower() for tag in tags.split(',')]
            tag_list = [tag for tag in tag_list if tag]  # Remover etiquetas vacías

            if len(tag_list) > 10:
                raise ValidationError("No puede tener más de 10 etiquetas")

            # Validar cada etiqueta
            for tag in tag_list:
                if len(tag) < 2:
                    raise ValidationError("Cada etiqueta debe tener al menos 2 caracteres")
                if len(tag) > 30:
                    raise ValidationError("Cada etiqueta no puede tener más de 30 caracteres")

            return tag_list

        return []

    def clean_processing_config(self):
        """
        Valida la configuración de procesamiento.
        """
        config = self.cleaned_data.get('processing_config')

        if config:
            # Validar que sea un diccionario válido
            if not isinstance(config, dict):
                raise ValidationError("La configuración debe ser un objeto JSON válido")

            # Validar configuraciones específicas
            if 'chunk_size' in config:
                if not isinstance(config['chunk_size'], int) or config['chunk_size'] <= 0:
                    raise ValidationError("chunk_size debe ser un número entero positivo")

            if 'overlap' in config:
                if not isinstance(config['overlap'], int) or config['overlap'] < 0:
                    raise ValidationError("overlap debe ser un número entero no negativo")

        return config

    def get_title_from_file(self):
        """
        Obtiene el título del archivo si no se especificó uno.
        """
        file = self.cleaned_data.get('file')
        title = self.cleaned_data.get('title')

        if not title and file:
            title = os.path.splitext(file.name)[0]

        return title
```

### `scrape_website_form.py`
Formulario para scraping de sitios web.

```python
from django import forms
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
import requests
from urllib.parse import urlparse, urljoin
import re

class ScrapeWebsiteForm(forms.Form):
    """
    Formulario para scraping de sitios web.
    """

    url = forms.URLField(
        label="URL del sitio web",
        help_text="URL completa del sitio web a scrappear",
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'https://ejemplo.com'
        })
    )

    max_depth = forms.IntegerField(
        min_value=1,
        max_value=5,
        initial=1,
        label="Profundidad máxima",
        help_text="Número máximo de niveles de enlaces a seguir",
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': 1,
            'max': 5
        })
    )

    max_pages = forms.IntegerField(
        min_value=1,
        max_value=100,
        initial=10,
        label="Páginas máximas",
        help_text="Número máximo de páginas a scrappear",
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': 1,
            'max': 100
        })
    )

    follow_links = forms.BooleanField(
        required=False,
        initial=True,
        label="Seguir enlaces",
        help_text="Seguir enlaces internos del sitio",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    css_selectors = forms.CharField(
        required=False,
        help_text="Selectores CSS para extraer contenido específico (uno por línea)",
        widget=forms.Textarea(attrs={
            'rows': 3,
            'class': 'form-control',
            'placeholder': 'article\n.content\n#main-content'
        })
    )

    exclude_patterns = forms.CharField(
        required=False,
        help_text="Patrones de URL a excluir (uno por línea)",
        widget=forms.Textarea(attrs={
            'rows': 3,
            'class': 'form-control',
            'placeholder': '/admin/\n/login/\n.pdf'
        })
    )

    include_patterns = forms.CharField(
        required=False,
        help_text="Patrones de URL a incluir (uno por línea, opcional)",
        widget=forms.Textarea(attrs={
            'rows': 3,
            'class': 'form-control',
            'placeholder': '/docs/\n/help/\n/faq/'
        })
    )

    wait_time = forms.FloatField(
        min_value=0.1,
        max_value=10.0,
        initial=1.0,
        label="Tiempo de espera (segundos)",
        help_text="Tiempo de espera entre requests",
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': 0.1,
            'min': 0.1,
            'max': 10.0
        })
    )

    user_agent = forms.CharField(
        max_length=500,
        required=False,
        initial="Mozilla/5.0 (compatible; KnowledgeBot/1.0)",
        label="User Agent",
        help_text="User Agent a usar para las requests",
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        })
    )

    respect_robots = forms.BooleanField(
        required=False,
        initial=True,
        label="Respetar robots.txt",
        help_text="Respetar las reglas del archivo robots.txt",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    def clean_url(self):
        """
        Valida la URL.
        """
        url = self.cleaned_data.get('url')

        if not url:
            return url

        # Validar formato de URL
        validator = URLValidator()
        try:
            validator(url)
        except ValidationError:
            raise ValidationError("URL inválida")

        # Verificar que la URL sea accesible
        try:
            response = requests.head(url, timeout=10)
            if response.status_code >= 400:
                raise ValidationError(f"URL no accesible (código {response.status_code})")
        except requests.RequestException as e:
            raise ValidationError(f"Error al acceder a la URL: {str(e)}")

        # Verificar que no sea un archivo binario
        content_type = response.headers.get('content-type', '')
        if content_type and not content_type.startswith('text/'):
            raise ValidationError("La URL debe apuntar a contenido HTML")

        return url

    def clean_css_selectors(self):
        """
        Valida los selectores CSS.
        """
        selectors = self.cleaned_data.get('css_selectors')

        if selectors:
            selector_list = [s.strip() for s in selectors.split('\n') if s.strip()]

            # Validar cada selector
            for selector in selector_list:
                if not self.is_valid_css_selector(selector):
                    raise ValidationError(f"Selector CSS inválido: {selector}")

            return selector_list

        return []

    def clean_exclude_patterns(self):
        """
        Valida los patrones de exclusión.
        """
        patterns = self.cleaned_data.get('exclude_patterns')

        if patterns:
            pattern_list = [p.strip() for p in patterns.split('\n') if p.strip()]

            # Validar cada patrón
            for pattern in pattern_list:
                try:
                    re.compile(pattern)
                except re.error:
                    raise ValidationError(f"Patrón regex inválido: {pattern}")

            return pattern_list

        return []

    def clean_include_patterns(self):
        """
        Valida los patrones de inclusión.
        """
        patterns = self.cleaned_data.get('include_patterns')

        if patterns:
            pattern_list = [p.strip() for p in patterns.split('\n') if p.strip()]

            # Validar cada patrón
            for pattern in pattern_list:
                try:
                    re.compile(pattern)
                except re.error:
                    raise ValidationError(f"Patrón regex inválido: {pattern}")

            return pattern_list

        return []

    def clean(self):
        """
        Validación global del formulario.
        """
        cleaned_data = super().clean()

        max_depth = cleaned_data.get('max_depth')
        max_pages = cleaned_data.get('max_pages')
        follow_links = cleaned_data.get('follow_links')

        # Si no se siguen enlaces, la profundidad debe ser 1
        if not follow_links and max_depth > 1:
            raise ValidationError("Si no se siguen enlaces, la profundidad máxima debe ser 1")

        # Validar combinación de parámetros
        if max_depth > 3 and max_pages > 50:
            raise ValidationError("Con profundidad alta, limite el número de páginas")

        return cleaned_data

    def is_valid_css_selector(self, selector):
        """
        Valida si un selector CSS es válido.
        """
        try:
            # Usar BeautifulSoup para validar el selector
            from bs4 import BeautifulSoup

            # Crear un HTML simple para probar
            html = "<div><p>test</p></div>"
            soup = BeautifulSoup(html, 'html.parser')

            # Intentar usar el selector
            soup.select(selector)
            return True
        except Exception:
            return False

    def get_scraping_config(self):
        """
        Obtiene la configuración de scraping.
        """
        return {
            'url': self.cleaned_data['url'],
            'max_depth': self.cleaned_data['max_depth'],
            'max_pages': self.cleaned_data['max_pages'],
            'follow_links': self.cleaned_data['follow_links'],
            'css_selectors': self.cleaned_data.get('css_selectors', []),
            'exclude_patterns': self.cleaned_data.get('exclude_patterns', []),
            'include_patterns': self.cleaned_data.get('include_patterns', []),
            'wait_time': self.cleaned_data['wait_time'],
            'user_agent': self.cleaned_data['user_agent'],
            'respect_robots': self.cleaned_data['respect_robots']
        }
```

## Formularios Base

### Formulario Base para Knowledge
```python
class BaseKnowledgeForm(forms.Form):
    """
    Formulario base para operaciones de conocimiento.
    """

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.tenant = kwargs.pop('tenant', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        """
        Validación común para todos los formularios de conocimiento.
        """
        cleaned_data = super().clean()

        # Validar permisos del usuario
        if self.user and not self.user.has_perm('knowledge.add_document'):
            raise ValidationError("No tiene permisos para agregar documentos")

        return cleaned_data
```

### Formulario de Configuración Avanzada
```python
class AdvancedProcessingForm(forms.Form):
    """
    Formulario para configuración avanzada de procesamiento.
    """

    chunk_size = forms.IntegerField(
        min_value=100,
        max_value=5000,
        initial=1000,
        label="Tamaño de chunk",
        help_text="Tamaño de cada fragmento de texto"
    )

    chunk_overlap = forms.IntegerField(
        min_value=0,
        max_value=500,
        initial=200,
        label="Solapamiento de chunks",
        help_text="Cantidad de texto que se solapa entre chunks"
    )

    embedding_model = forms.ChoiceField(
        choices=[
            ('openai', 'OpenAI'),
            ('sentence-transformers', 'Sentence Transformers'),
            ('huggingface', 'Hugging Face')
        ],
        initial='openai',
        label="Modelo de embeddings"
    )

    language = forms.ChoiceField(
        choices=[
            ('es', 'Español'),
            ('en', 'Inglés'),
            ('auto', 'Detectar automáticamente')
        ],
        initial='auto',
        label="Idioma del contenido"
    )
```

## Widgets Personalizados

### Widget de Carga de Archivos Drag & Drop
```python
class DragDropFileWidget(forms.ClearableFileInput):
    """
    Widget personalizado para carga de archivos con drag & drop.
    """

    template_name = 'knowledge/widgets/drag_drop_file.html'

    def __init__(self, attrs=None):
        default_attrs = {
            'class': 'drag-drop-file',
            'data-max-size': '10485760',  # 10MB
            'data-allowed-types': 'pdf,docx,txt,csv,json,md'
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)
```

### Widget de Selección de Documentos con Búsqueda
```python
class DocumentSearchWidget(forms.Widget):
    """
    Widget para selección de documentos con búsqueda.
    """

    template_name = 'knowledge/widgets/document_search.html'

    def format_value(self, value):
        if value is None:
            return ''
        return ','.join(str(v) for v in value)

    def value_from_datadict(self, data, files, name):
        value = data.get(name)
        if value:
            return [int(v) for v in value.split(',') if v.isdigit()]
        return []
```

## Validadores Personalizados

### Validador de Contenido de Archivo
```python
def validate_file_content(file):
    """
    Valida el contenido de un archivo.
    """
    if file.size == 0:
        raise ValidationError("El archivo está vacío")

    # Leer primeros bytes para verificar formato
    file.seek(0)
    header = file.read(1024)
    file.seek(0)

    # Verificar que no sea un archivo ejecutable
    if header.startswith(b'MZ') or header.startswith(b'\x7fELF'):
        raise ValidationError("No se permiten archivos ejecutables")
```

### Validador de URL de Sitio Web
```python
def validate_scrapeable_url(url):
    """
    Valida que una URL sea apropiada para scraping.
    """
    parsed = urlparse(url)

    # Verificar protocolo
    if parsed.scheme not in ['http', 'https']:
        raise ValidationError("Solo se permiten URLs HTTP/HTTPS")

    # Verificar que no sea localhost en producción
    if settings.ENVIRONMENT == 'production':
        if parsed.netloc in ['localhost', '127.0.0.1']:
            raise ValidationError("No se permite scraping de localhost en producción")
```

## Uso en Vistas

### Vista con Formulario de Carga
```python
def upload_document_view(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Procesar archivo
            file = form.cleaned_data['file']
            title = form.get_title_from_file()

            # Crear documento
            document = Document.objects.create(
                title=title,
                file=file,
                owner=request.user,
                tenant=request.tenant
            )

            return redirect('document_detail', pk=document.pk)
    else:
        form = FileUploadForm()

    return render(request, 'knowledge/upload.html', {'form': form})
```

### Vista con Formulario de Scraping
```python
def scrape_website_view(request):
    if request.method == 'POST':
        form = ScrapeWebsiteForm(request.POST)
        if form.is_valid():
            config = form.get_scraping_config()

            # Iniciar scraping asíncrono
            from knowledge.tasks import scrape_website_task
            task = scrape_website_task.delay(
                config,
                user_id=request.user.id,
                tenant_id=request.tenant.id
            )

            return redirect('scraping_status', task_id=task.id)
    else:
        form = ScrapeWebsiteForm()

    return render(request, 'knowledge/scrape.html', {'form': form})
```

## Testing

### Test de Formularios
```python
class KnowledgeFormsTestCase(TestCase):
    def test_file_upload_form_valid(self):
        # Crear archivo de prueba
        file_content = b"Test content"
        file = SimpleUploadedFile(
            "test.txt",
            file_content,
            content_type="text/plain"
        )

        form = FileUploadForm(data={
            'title': 'Test Document',
            'generate_embeddings': True
        }, files={'file': file})

        self.assertTrue(form.is_valid())

    def test_scrape_website_form_invalid_url(self):
        form = ScrapeWebsiteForm(data={
            'url': 'invalid-url',
            'max_depth': 1
        })

        self.assertFalse(form.is_valid())
        self.assertIn('url', form.errors)
```

## Mejores Prácticas

1. **Validación Robusta**: Implementar validaciones tanto en cliente como servidor
2. **Manejo de Errores**: Proporcionar mensajes de error claros y útiles
3. **Seguridad**: Validar todos los datos de entrada
4. **Usabilidad**: Usar widgets apropiados y ayuda contextual
5. **Performance**: Optimizar formularios para archivos grandes
6. **Accesibilidad**: Seguir estándares de accesibilidad web

## Extensibilidad

### Agregar Nuevos Tipos de Formularios
```python
class CustomKnowledgeForm(BaseKnowledgeForm):
    """
    Formulario personalizado para tipos específicos de conocimiento.
    """

    custom_field = forms.CharField(
        label="Campo personalizado",
        required=True
    )

    def clean_custom_field(self):
        # Validación específica
        pass
```

### Hooks para Validación Personalizada
```python
def custom_validation_hook(form, cleaned_data):
    """
    Hook para validación personalizada.
    """
    # Implementar validación específica del tenant
    pass
```
