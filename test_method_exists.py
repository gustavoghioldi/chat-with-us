#!/usr/bin/env python
"""
Script para verificar que el método is_document_type_auto_detected existe
"""
import os

import django

# Configurar Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main.settings")
django.setup()

from documents.models import DocumentModel


def test_method_exists():
    """Verifica que el método existe"""

    # Crear una instancia ficticia para probar
    doc = DocumentModel()

    # Verificar que el método existe
    if hasattr(doc, "is_document_type_auto_detected"):
        print("✅ Método is_document_type_auto_detected existe")

        # Probar que funciona con valores None
        result = doc.is_document_type_auto_detected()
        print(f"✅ Método retorna: {result} (debería ser False para instancia vacía)")

    else:
        print("❌ Método is_document_type_auto_detected NO existe")

    # Verificar mapeo de extensiones
    if hasattr(DocumentModel, "EXTENSION_MAPPING"):
        print("✅ EXTENSION_MAPPING existe")
        print(f"📋 Extensiones: {DocumentModel.EXTENSION_MAPPING}")
    else:
        print("❌ EXTENSION_MAPPING NO existe")

    print("🎉 Verificación completada")


if __name__ == "__main__":
    test_method_exists()
