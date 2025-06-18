#!/usr/bin/env python
"""
Script de prueba para verificar la funcionalidad de nombres únicos en documentos.
"""
import os
import sys

import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main.settings.development")
django.setup()

from documents.models import user_document_upload_path
from documents.services import DocumentService


def test_unique_filename_generation():
    """Probar generación de nombres únicos"""
    print("=== Test de generación de nombres únicos ===")

    # Probar con el mismo nombre varias veces
    original_name = "documento_prueba.pdf"
    names = []

    for i in range(5):
        unique_name = DocumentService.generate_unique_filename(original_name)
        names.append(unique_name)
        print(f"Iteración {i+1}: {unique_name}")

    # Verificar que todos sean únicos
    unique_names = set(names)
    print(f"\nNombres generados: {len(names)}")
    print(f"Nombres únicos: {len(unique_names)}")
    print(f"¿Todos únicos?: {'✅ SÍ' if len(names) == len(unique_names) else '❌ NO'}")


def test_different_file_types():
    """Probar con diferentes tipos de archivos"""
    print("\n=== Test con diferentes tipos de archivo ===")

    test_files = [
        "reporte.pdf",
        "datos.csv",
        "presentacion.docx",
        "archivo con espacios.txt",
        "MAYUSCULAS.PDF",
        "archivo-con-guiones.json",
        "archivo_con_underscores.xlsx",
    ]

    for original in test_files:
        unique = DocumentService.generate_unique_filename(original)
        print(f"{original:25} -> {unique}")


def test_upload_path():
    """Probar la función de upload path"""
    print("\n=== Test de rutas de upload ===")

    # Simular un documento (sin crear realmente)
    class MockTenant:
        name = "Mi Empresa Test"

    class MockDocument:
        tenant = MockTenant()

    mock_doc = MockDocument()

    # Probar con diferentes nombres
    test_files = ["documento.pdf", "archivo con espacios.docx", "MAYÚSCULAS.txt"]

    for filename in test_files:
        path = user_document_upload_path(mock_doc, filename)
        print(f"{filename:20} -> {path}")


if __name__ == "__main__":
    try:
        test_unique_filename_generation()
        test_different_file_types()
        test_upload_path()
        print("\n✅ Todas las pruebas completadas exitosamente!")

    except Exception as e:
        print(f"\n❌ Error durante las pruebas: {e}")
        import traceback

        traceback.print_exc()
