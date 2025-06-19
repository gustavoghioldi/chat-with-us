#!/usr/bin/env python3
"""
Test simple para ToolkitService
"""

import os
import sys

# Agregar el directorio del proyecto al path
sys.path.append("/Users/gustavo.ghioldi/barba/chat-with-us")

# Configurar Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main.settings.development")

import django

django.setup()

from tools.services.toolkit_service import ToolkitService


def test_toolkit_service():
    print("🧪 Probando ToolkitService...")

    # Test 1: Sin parámetros (todas las herramientas)
    print("\n1️⃣ Test: Obtener todas las herramientas")
    all_tools = ToolkitService.get_toolkits()
    print(f"   Todas las herramientas: {list(all_tools.keys())}")
    print(f"   Total: {len(all_tools)} herramientas")

    # Test 2: Con lista específica
    print("\n2️⃣ Test: Obtener herramientas específicas")
    specific_tools = ToolkitService.get_toolkits(["obtener_datos_de_factura"])
    print(f"   Herramientas solicitadas: ['obtener_datos_de_factura']")
    print(f"   Herramientas obtenidas: {list(specific_tools.keys())}")
    print(f"   Total: {len(specific_tools)} herramientas")

    # Test 3: Con herramienta inexistente
    print("\n3️⃣ Test: Solicitar herramienta inexistente")
    nonexistent_tools = ToolkitService.get_toolkits(["herramienta_inexistente"])
    print(f"   Herramientas solicitadas: ['herramienta_inexistente']")
    print(f"   Herramientas obtenidas: {list(nonexistent_tools.keys())}")
    print(f"   Total: {len(nonexistent_tools)} herramientas")

    # Test 4: Mix de existentes e inexistentes
    print("\n4️⃣ Test: Mix de herramientas existentes e inexistentes")
    mixed_tools = ToolkitService.get_toolkits(
        ["obtener_datos_de_factura", "inexistente", "otro"]
    )
    print(
        f"   Herramientas solicitadas: ['obtener_datos_de_factura', 'inexistente', 'otro']"
    )
    print(f"   Herramientas obtenidas: {list(mixed_tools.keys())}")
    print(f"   Total: {len(mixed_tools)} herramientas")

    # Test 5: Lista vacía
    print("\n5️⃣ Test: Lista vacía")
    empty_tools = ToolkitService.get_toolkits([])
    print(f"   Herramientas solicitadas: []")
    print(f"   Herramientas obtenidas: {list(empty_tools.keys())}")
    print(f"   Total: {len(empty_tools)} herramientas")

    print("\n✅ Todos los tests completados!")


if __name__ == "__main__":
    test_toolkit_service()
