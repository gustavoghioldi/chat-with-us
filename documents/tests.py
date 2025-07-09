import os
import tempfile

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from tenants.models import TenantModel

from .models import DocumentModel
from .services import DocumentService


class DocumentModelTestCase(TestCase):
    """Tests para el modelo DocumentModel"""

    def setUp(self):
        """Configurar datos de prueba"""
        self.tenant = TenantModel.objects.create(
            name="Test Tenant", description="Tenant para pruebas"
        )

        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        # Crear un archivo de prueba
        self.test_file = SimpleUploadedFile(
            "test_document.txt",
            b"Este es un documento de prueba",
            content_type="text/plain",
        )

    def test_document_creation(self):
        """Test de creación de documento"""
        document = DocumentModel.objects.create(
            title="Documento de Prueba",
            description="Descripción del documento",
            file=self.test_file,
            document_type="txt",
            tenant=self.tenant,
            uploaded_by=self.user,
        )

        self.assertEqual(document.title, "Documento de Prueba")
        self.assertEqual(document.tenant, self.tenant)
        self.assertEqual(document.uploaded_by, self.user)
        self.assertEqual(document.document_type, "txt")
        self.assertTrue(document.is_active)
        self.assertFalse(document.is_processed)

    def test_document_str_representation(self):
        """Test del método __str__"""
        document = DocumentModel.objects.create(
            title="Documento de Prueba",
            file=self.test_file,
            tenant=self.tenant,
            uploaded_by=self.user,
        )

        expected_str = f"Documento de Prueba - {self.tenant.name}"
        self.assertEqual(str(document), expected_str)

    def test_file_size_display(self):
        """Test del método get_file_size_display"""
        document = DocumentModel.objects.create(
            title="Documento de Prueba",
            file=self.test_file,
            tenant=self.tenant,
            uploaded_by=self.user,
        )

        # El archivo debería tener un tamaño en bytes
        size_display = document.get_file_size_display()
        self.assertIn("bytes", size_display)

    def test_file_extension_property(self):
        """Test de la propiedad file_extension"""
        document = DocumentModel.objects.create(
            title="Documento de Prueba",
            file=self.test_file,
            tenant=self.tenant,
            uploaded_by=self.user,
        )

        self.assertEqual(document.file_extension, ".txt")


class DocumentServiceTestCase(TestCase):
    """Tests para DocumentService"""

    def setUp(self):
        """Configurar datos de prueba"""
        self.tenant = TenantModel.objects.create(
            name="Test Tenant", description="Tenant para pruebas"
        )

        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        self.test_file = SimpleUploadedFile(
            "test_document.txt",
            b"Este es un documento de prueba",
            content_type="text/plain",
        )

    def test_create_document_service(self):
        """Test del servicio de creación de documentos"""
        document = DocumentService.create_document(
            title="Documento desde Servicio",
            file=self.test_file,
            tenant=self.tenant,
            uploaded_by=self.user,
            description="Creado mediante servicio",
        )

        self.assertEqual(document.title, "Documento desde Servicio")
        self.assertEqual(document.description, "Creado mediante servicio")
        self.assertEqual(document.document_type, "txt")
        self.assertTrue(DocumentModel.objects.filter(id=document.id).exists())

    def test_get_documents_by_tenant(self):
        """Test de obtención de documentos por tenant"""
        # Crear algunos documentos
        doc1 = DocumentService.create_document(
            title="Documento 1",
            file=self.test_file,
            tenant=self.tenant,
            uploaded_by=self.user,
        )

        # Crear otro tenant y documento
        other_tenant = TenantModel.objects.create(name="Other Tenant")
        doc2 = DocumentService.create_document(
            title="Documento 2",
            file=SimpleUploadedFile(
                "test2.txt", b"contenido", content_type="text/plain"
            ),
            tenant=other_tenant,
            uploaded_by=self.user,
        )

        # Obtener documentos del primer tenant
        tenant_docs = DocumentService.get_documents_by_tenant(self.tenant)

        self.assertEqual(tenant_docs.count(), 1)
        self.assertEqual(tenant_docs.first().id, doc1.id)

    def test_validate_file_service(self):
        """Test de validación de archivos"""
        # Archivo válido
        valid_file = SimpleUploadedFile(
            "valid.txt", b"contenido valido", content_type="text/plain"
        )

        validation = DocumentService.validate_file(valid_file)
        self.assertTrue(validation["is_valid"])
        self.assertEqual(len(validation["errors"]), 0)

        # Archivo demasiado grande (simulado)
        large_file = SimpleUploadedFile(
            "large.txt", b"x" * (51 * 1024 * 1024), content_type="text/plain"  # 51MB
        )

        validation = DocumentService.validate_file(large_file)
        self.assertFalse(validation["is_valid"])
        self.assertGreater(len(validation["errors"]), 0)

    def test_mark_as_processed(self):
        """Test de marcar documento como procesado"""
        document = DocumentService.create_document(
            title="Documento para Procesar",
            file=self.test_file,
            tenant=self.tenant,
            uploaded_by=self.user,
        )

        self.assertFalse(document.is_processed)
        self.assertIsNone(document.processed_at)

        processed_doc = DocumentService.mark_as_processed(document)

        self.assertTrue(processed_doc.is_processed)
        self.assertIsNotNone(processed_doc.processed_at)

    def test_get_document_stats(self):
        """Test de estadísticas de documentos"""
        # Crear algunos documentos
        doc1 = DocumentService.create_document(
            title="Documento 1",
            file=self.test_file,
            tenant=self.tenant,
            uploaded_by=self.user,
        )

        doc2 = DocumentService.create_document(
            title="Documento 2",
            file=SimpleUploadedFile(
                "test2.pdf", b"pdf content", content_type="application/pdf"
            ),
            tenant=self.tenant,
            uploaded_by=self.user,
        )

        # Marcar uno como procesado
        DocumentService.mark_as_processed(doc1)

        stats = DocumentService.get_document_stats(self.tenant)

        self.assertEqual(stats["total_documents"], 2)
        self.assertEqual(stats["active_documents"], 2)
        self.assertEqual(stats["processed_documents"], 1)
        self.assertEqual(stats["unprocessed_documents"], 1)
        self.assertIn("txt", stats["documents_by_type"])
        self.assertIn("pdf", stats["documents_by_type"])

    def test_unique_filename_generation(self):
        """Test de generación de nombres únicos"""
        import time

        from .services import DocumentService

        # Generar varios nombres para el mismo archivo
        original_name = "test_document.pdf"

        name1 = DocumentService.generate_unique_filename(original_name)
        time.sleep(0.001)  # Pequeño delay para asegurar timestamps diferentes
        name2 = DocumentService.generate_unique_filename(original_name)
        time.sleep(0.001)  # Pequeño delay para asegurar timestamps diferentes
        name3 = DocumentService.generate_unique_filename(original_name)

        # Los nombres deben ser diferentes
        self.assertNotEqual(name1, name2)
        self.assertNotEqual(name2, name3)
        self.assertNotEqual(name1, name3)

        # Todos deben terminar con .pdf
        self.assertTrue(name1.endswith(".pdf"))
        self.assertTrue(name2.endswith(".pdf"))
        self.assertTrue(name3.endswith(".pdf"))

        # Todos deben contener "test_document"
        self.assertIn("test_document", name1)
        self.assertIn("test_document", name2)
        self.assertIn("test_document", name3)

    def test_upload_path_with_timestamp(self):
        """Test de la función upload_path con timestamp"""
        import time

        from .models import user_document_upload_path

        document = DocumentModel(
            title="Test Document", tenant=self.tenant, uploaded_by=self.user
        )

        # Generar rutas para el mismo nombre de archivo
        path1 = user_document_upload_path(document, "test_file.pdf")
        time.sleep(0.001)  # Pequeño delay para asegurar timestamps diferentes
        path2 = user_document_upload_path(document, "test_file.pdf")

        # Las rutas deben ser diferentes (por el timestamp y UUID)
        self.assertNotEqual(path1, path2)

        # Ambas deben empezar con documents/tenant_name (con espacios reemplazados por _)
        # El tenant name "Test Tenant" se convierte en "Test_Tenant"
        clean_tenant_name = self.tenant.name.replace(" ", "_")
        expected_prefix = f"documents/{clean_tenant_name}/"
        self.assertTrue(
            path1.startswith(expected_prefix),
            f"Path '{path1}' should start with '{expected_prefix}'",
        )
        self.assertTrue(
            path2.startswith(expected_prefix),
            f"Path '{path2}' should start with '{expected_prefix}'",
        )

        # Ambas deben terminar con .pdf
        self.assertTrue(path1.endswith(".pdf"))
        self.assertTrue(path2.endswith(".pdf"))
