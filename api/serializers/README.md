# Serializadores de API

## Descripción General
Este directorio contiene los serializadores para la API REST del sistema. Los serializadores manejan la conversión entre objetos Python y formatos de datos JSON, así como la validación de datos de entrada y salida.

## Estructura de Archivos

### `agent_serializer.py`
Serializadores para el modelo Agent y operaciones relacionadas.

```python
from rest_framework import serializers
from agents.models import AgentModel

class AgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentModel
        fields = ['id', 'name', 'description', 'model_provider', 'temperature']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_temperature(self, value):
        if not 0 <= value <= 1:
            raise serializers.ValidationError("Temperature must be between 0 and 1")
        return value
```

### `chat_serializer.py`
Serializadores para modelos de chat y mensajes.

```python
class ChatSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Chat
        fields = ['id', 'title', 'agent', 'user', 'messages', 'created_at']
        read_only_fields = ['id', 'created_at']

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'content', 'sender', 'timestamp', 'message_type']
```

### `knowledge_csv_serializer.py`
Serializador para carga de conocimiento desde archivos CSV.

```python
class KnowledgeCSVSerializer(serializers.Serializer):
    csv_file = serializers.FileField()
    delimiter = serializers.CharField(default=',', max_length=1)
    has_header = serializers.BooleanField(default=True)

    def validate_csv_file(self, value):
        if not value.name.endswith('.csv'):
            raise serializers.ValidationError("File must be a CSV file")
        return value
```

### `knowledge_json_serializer.py`
Serializador para carga de conocimiento desde archivos JSON.

```python
class KnowledgeJSONSerializer(serializers.Serializer):
    json_file = serializers.FileField()

    def validate_json_file(self, value):
        if not value.name.endswith('.json'):
            raise serializers.ValidationError("File must be a JSON file")

        # Validar que es JSON válido
        try:
            import json
            content = value.read()
            json.loads(content)
            value.seek(0)  # Reset file pointer
        except json.JSONDecodeError:
            raise serializers.ValidationError("Invalid JSON file")

        return value
```

### `knowledge_text_serializer.py`
Serializador para carga de conocimiento desde texto plano.

```python
class KnowledgeTextSerializer(serializers.Serializer):
    text_content = serializers.CharField()
    title = serializers.CharField(max_length=200)
    tags = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False
    )

    def validate_text_content(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Text content must be at least 10 characters")
        return value
```

### `knowledge_web_scraping_serializer.py`
Serializador para web scraping de conocimiento.

```python
class KnowledgeWebScrapingSerializer(serializers.Serializer):
    url = serializers.URLField()
    max_depth = serializers.IntegerField(default=1, min_value=1, max_value=5)
    follow_links = serializers.BooleanField(default=False)
    selectors = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=False
    )

    def validate_url(self, value):
        # Validar que la URL es accesible
        import requests
        try:
            response = requests.head(value, timeout=5)
            if response.status_code >= 400:
                raise serializers.ValidationError("URL is not accessible")
        except requests.RequestException:
            raise serializers.ValidationError("Unable to access URL")
        return value
```

### `s3_upload_serializer.py`
Serializador para carga de archivos a S3.

```python
class S3UploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    bucket_name = serializers.CharField(max_length=100, required=False)
    folder = serializers.CharField(max_length=200, required=False)

    def validate_file(self, value):
        # Validar tamaño del archivo (max 10MB)
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("File size cannot exceed 10MB")

        # Validar tipos de archivo permitidos
        allowed_types = ['.pdf', '.txt', '.docx', '.json', '.csv']
        file_extension = value.name.lower().split('.')[-1]
        if f'.{file_extension}' not in allowed_types:
            raise serializers.ValidationError(f"File type not allowed. Allowed types: {', '.join(allowed_types)}")

        return value
```

## Patrones de Serializadores

### 1. Serializador con Validación Personalizada
```python
class CustomSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyModel
        fields = '__all__'

    def validate_field_name(self, value):
        # Validación específica para un campo
        if some_condition:
            raise serializers.ValidationError("Error message")
        return value

    def validate(self, attrs):
        # Validación que involucra múltiples campos
        if attrs['field1'] and not attrs['field2']:
            raise serializers.ValidationError("Field2 is required when Field1 is provided")
        return attrs
```

### 2. Serializador con Campos Calculados
```python
class SerializerWithCalculatedFields(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'full_name']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
```

### 3. Serializador Anidado
```python
class NestedSerializer(serializers.ModelSerializer):
    related_objects = RelatedSerializer(many=True, read_only=True)

    class Meta:
        model = MainModel
        fields = ['id', 'name', 'related_objects']
```

## Validaciones Comunes

### Validación de Archivos
```python
def validate_file_upload(self, value):
    # Validar extensión
    allowed_extensions = ['.pdf', '.doc', '.docx', '.txt']
    file_extension = os.path.splitext(value.name)[1].lower()
    if file_extension not in allowed_extensions:
        raise serializers.ValidationError(f"File type not allowed: {file_extension}")

    # Validar tamaño
    max_size = 5 * 1024 * 1024  # 5MB
    if value.size > max_size:
        raise serializers.ValidationError("File size exceeds 5MB limit")

    return value
```

### Validación de URLs
```python
def validate_url_accessibility(self, value):
    import requests
    try:
        response = requests.head(value, timeout=10)
        if response.status_code >= 400:
            raise serializers.ValidationError("URL is not accessible")
    except requests.RequestException as e:
        raise serializers.ValidationError(f"Unable to access URL: {str(e)}")
    return value
```

### Validación de Datos JSON
```python
def validate_json_data(self, value):
    import json
    try:
        json.loads(value)
    except json.JSONDecodeError:
        raise serializers.ValidationError("Invalid JSON format")
    return value
```

## Uso en Vistas

### ViewSet con Serializadores
```python
class MyViewSet(viewsets.ModelViewSet):
    queryset = MyModel.objects.all()
    serializer_class = MySerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return MyCreateSerializer
        elif self.action == 'list':
            return MyListSerializer
        return MySerializer
```

### Validación Manual
```python
def my_api_view(request):
    serializer = MySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)
```

## Campos Personalizados

### Campo de Archivo con Validación
```python
class ValidatedFileField(serializers.FileField):
    def __init__(self, **kwargs):
        self.max_size = kwargs.pop('max_size', None)
        self.allowed_extensions = kwargs.pop('allowed_extensions', None)
        super().__init__(**kwargs)

    def validate(self, value):
        if self.max_size and value.size > self.max_size:
            raise serializers.ValidationError(f"File size exceeds {self.max_size} bytes")

        if self.allowed_extensions:
            extension = value.name.split('.')[-1].lower()
            if extension not in self.allowed_extensions:
                raise serializers.ValidationError(f"File type not allowed: {extension}")

        return value
```

### Campo de Lista con Validación
```python
class ValidatedListField(serializers.ListField):
    def __init__(self, **kwargs):
        self.max_length = kwargs.pop('max_length', None)
        self.unique_items = kwargs.pop('unique_items', False)
        super().__init__(**kwargs)

    def validate(self, value):
        if self.max_length and len(value) > self.max_length:
            raise serializers.ValidationError(f"List cannot contain more than {self.max_length} items")

        if self.unique_items and len(value) != len(set(value)):
            raise serializers.ValidationError("List items must be unique")

        return value
```

## Optimización de Rendimiento

### Serialización Eficiente
```python
class OptimizedSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyModel
        fields = ['id', 'name', 'description']
        # Evitar campos pesados por defecto
```

### Serializador con Prefetch
```python
class EfficientSerializer(serializers.ModelSerializer):
    related_data = serializers.SerializerMethodField()

    class Meta:
        model = MyModel
        fields = ['id', 'name', 'related_data']

    def get_related_data(self, obj):
        # Usar prefetch_related en la vista
        return [item.name for item in obj.related_items.all()]
```

## Testing

### Test de Serializadores
```python
class SerializerTestCase(TestCase):
    def test_valid_serializer(self):
        data = {
            'name': 'Test Name',
            'description': 'Test Description'
        }
        serializer = MySerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_invalid_serializer(self):
        data = {
            'name': '',  # Campo requerido vacío
            'description': 'Test Description'
        }
        serializer = MySerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)
```

## Mejores Prácticas

1. **Validación Explícita**: Siempre validar datos de entrada
2. **Campos Read-Only**: Marcar campos que no deben ser modificados
3. **Mensajes de Error Claros**: Proporcionar mensajes de error descriptivos
4. **Reutilización**: Crear serializadores base para funcionalidad común
5. **Documentación**: Documentar validaciones y campos especiales

## Manejo de Errores

### Errores de Validación
```python
try:
    serializer = MySerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
except serializers.ValidationError as e:
    return Response({'errors': e.detail}, status=400)
```

### Errores Personalizados
```python
class CustomValidationError(serializers.ValidationError):
    def __init__(self, message, code=None):
        super().__init__(message)
        self.code = code
```

## Integración con Modelos

### Creación de Objetos
```python
class CreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyModel
        fields = '__all__'

    def create(self, validated_data):
        # Lógica personalizada de creación
        instance = MyModel.objects.create(**validated_data)
        # Procesar después de la creación
        return instance
```

### Actualización de Objetos
```python
class UpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyModel
        fields = '__all__'

    def update(self, instance, validated_data):
        # Lógica personalizada de actualización
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
```
