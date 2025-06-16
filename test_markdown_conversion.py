#!/usr/bin/env python
"""
Script de prueba para verificar la conversión de JSON y CSV a Markdown
"""

import os
import sys

import django

# Configurar Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main.settings")
django.setup()

from knowledge.services.content_formatter_service import ContentFormatterService


def test_json_to_markdown():
    """Probar conversión de JSON a Markdown."""
    print("🧪 Probando conversión de JSON a Markdown...")

    # Datos de prueba como los que especificas
    test_data = [
        {"nombre": "Gustavo Ghioldi", "total": "$200"},
        {"nombre": "Paula D'angelo", "total": "$450"},
    ]

    # Convertir a Markdown usando el servicio
    result = ContentFormatterService.json_to_markdown(test_data, "Pedidos")

    print("📝 Resultado de conversión JSON:")
    print("=" * 50)
    print(result)
    print("=" * 50)

    return result


def test_csv_to_markdown():
    """Probar conversión de CSV a Markdown."""
    print("\n🧪 Probando conversión de CSV a Markdown...")

    # Datos CSV de prueba
    csv_data = """nombre,total
Gustavo Ghioldi,$200
Paula D'angelo,$450"""

    # Convertir a Markdown usando el servicio
    result = ContentFormatterService.csv_to_markdown(csv_data, "Pedidos CSV")

    print("📝 Resultado de conversión CSV:")
    print("=" * 50)
    print(result)
    print("=" * 50)

    return result


def test_json_with_existing_id():
    """Probar JSON que ya tiene campo ID."""
    print("\n🧪 Probando JSON con ID existente...")

    test_data = [
        {"id": 100, "nombre": "Juan Pérez", "total": "$300"},
        {"id": 101, "nombre": "Ana García", "total": "$150"},
    ]

    result = ContentFormatterService.json_to_markdown(test_data, "Pedidos con ID")

    print("📝 Resultado con ID existente:")
    print("=" * 50)
    print(result)
    print("=" * 50)

    return result


def test_csv_with_id_column():
    """Probar CSV que tiene columna ID."""
    print("\n🧪 Probando CSV con columna ID...")

    csv_data = """id,nombre,total
100,Juan Pérez,$300
101,Ana García,$150"""

    result = ContentFormatterService.csv_to_markdown(csv_data, "Pedidos CSV con ID")

    print("📝 Resultado CSV con ID:")
    print("=" * 50)
    print(result)
    print("=" * 50)

    return result


def print_emoji_examples():
    """Mostrar ejemplos de cómo usar emojis."""
    print("\n🎨 EJEMPLOS DE EMOJIS QUE PUEDES USAR:")
    print("=" * 60)

    # Números con emojis
    print("📊 Números:")
    for i in range(1, 11):
        emoji_numbers = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
        if i <= len(emoji_numbers):
            print(f"   {emoji_numbers[i-1]} Paso {i}")

    print("\n🛠️ Funcionalidades:")
    print("   ✅ Completado")
    print("   ❌ Error")
    print("   ⚠️ Advertencia")
    print("   🔄 En proceso")
    print("   📝 Documentación")
    print("   🧪 Pruebas")
    print("   🚀 Lanzamiento")
    print("   💡 Idea")
    print("   🎯 Objetivo")
    print("   📊 Estadísticas")
    print("   🔧 Configuración")
    print("   📋 Lista")
    print("   🌟 Destacado")
    print("   💾 Base de datos")
    print("   🔐 Seguridad")
    print("   🌐 Web/API")


if __name__ == "__main__":
    print("🚀 Iniciando pruebas de conversión a Markdown...\n")

    # Mostrar ejemplos de emojis
    print_emoji_examples()

    # Ejecutar todas las pruebas
    test_json_to_markdown()
    test_csv_to_markdown()
    test_json_with_existing_id()
    test_csv_with_id_column()

    print("\n✅ Todas las pruebas completadas!")
    print("\n💡 El formato generado debería coincidir con tus especificaciones:")
    print("   - IDs autogenerados incrementalmente si no existen")
    print("   - Formato de lista con viñetas para cada campo")
    print("   - Sección de datos originales al final")
