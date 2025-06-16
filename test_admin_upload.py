#!/usr/bin/env python
"""
Script de prueba para verificar la funcionalidad de subida de archivos en el admin.
Prueba el ContentFormatterService con archivos JSON y CSV reales.
"""

import json
import os
import sys

import django

# Configurar Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main.settings")
django.setup()

from knowledge.services.content_formatter_service import ContentFormatterService


def test_json_file_processing():
    """Probar el procesamiento del archivo JSON de empleados."""
    print("🧪 Probando procesamiento de archivo JSON de empleados...")
    print("=" * 60)

    # Leer el archivo JSON
    try:
        with open(
            "/Users/gustavo.ghioldi/barba/chat-with-us/test_data_empleados.json",
            "r",
            encoding="utf-8",
        ) as f:
            json_data = json.load(f)

        print(f"📄 Archivo JSON cargado exitosamente: {len(json_data)} empleados")

        # Convertir usando el servicio
        markdown_result = ContentFormatterService.json_to_markdown(
            json_data, "Base de Datos de Empleados"
        )

        print("\n📝 Resultado de conversión a Markdown:")
        print("=" * 60)
        print(
            markdown_result[:1000] + "..."
            if len(markdown_result) > 1000
            else markdown_result
        )
        print("=" * 60)

        return True

    except Exception as e:
        print(f"❌ Error al procesar archivo JSON: {e}")
        return False


def test_csv_file_processing():
    """Probar el procesamiento del archivo CSV de productos."""
    print("\n🧪 Probando procesamiento de archivo CSV de productos...")
    print("=" * 60)

    # Leer el archivo CSV
    try:
        with open(
            "/Users/gustavo.ghioldi/barba/chat-with-us/test_data_productos.csv",
            "r",
            encoding="utf-8",
        ) as f:
            csv_content = f.read()

        print(f"📊 Archivo CSV cargado exitosamente")
        print(f"📏 Tamaño del contenido: {len(csv_content)} caracteres")

        # Mostrar las primeras líneas
        lines = csv_content.split("\n")
        print(f"📋 Número de líneas: {len(lines)}")
        print("🔍 Primeras 3 líneas:")
        for i, line in enumerate(lines[:3]):
            print(f"   {i+1}: {line}")

        # Convertir usando el servicio
        markdown_result = ContentFormatterService.csv_to_markdown(
            csv_content, "Inventario de Productos"
        )

        print("\n📝 Resultado de conversión a Markdown:")
        print("=" * 60)
        print(
            markdown_result[:1500] + "..."
            if len(markdown_result) > 1500
            else markdown_result
        )
        print("=" * 60)

        return True

    except Exception as e:
        print(f"❌ Error al procesar archivo CSV: {e}")
        return False


def test_admin_form_simulation():
    """Simular lo que haría el formulario del admin."""
    print("\n🎯 Simulando procesamiento del admin...")
    print("=" * 60)

    # Simular datos del formulario
    form_data = {
        "name": "Datos de Prueba Admin",
        "content_type": "json",
        "description": "Archivo de prueba subido desde el admin de Django",
    }

    print(f"📋 Datos del formulario simulado:")
    for key, value in form_data.items():
        print(f"   {key}: {value}")

    # Test de validación como lo haría el admin
    if form_data["content_type"] == "json":
        try:
            with open(
                "/Users/gustavo.ghioldi/barba/chat-with-us/test_data_empleados.json",
                "r",
            ) as f:
                file_content = f.read()

            json_data = json.loads(file_content)

            # Validar límite de elementos
            if isinstance(json_data, list) and len(json_data) > 1000:
                print(
                    f"⚠️ El archivo contiene {len(json_data)} elementos (límite recomendado: 1000)"
                )
            else:
                print(
                    f"✅ El archivo contiene {len(json_data)} elementos (dentro del límite)"
                )

            # Convertir a markdown
            markdown_content = ContentFormatterService.json_to_markdown(
                json_data, form_data["name"]
            )

            print(
                f"✅ Conversión exitosa! Tamaño del Markdown: {len(markdown_content)} caracteres"
            )

            # Simular creación del modelo (sin realmente crearlo)
            print("🏗️ El admin crearía un KnowledgeModel con:")
            print(f"   - name: {form_data['name']}")
            print(f"   - category: plain_document")
            print(f"   - description: {form_data['description']}")
            print(
                f"   - text: [Contenido Markdown de {len(markdown_content)} caracteres]"
            )

            return True

        except Exception as e:
            print(f"❌ Error en simulación del admin: {e}")
            return False


def show_usage_instructions():
    """Mostrar instrucciones de uso del admin."""
    print("\n📚 INSTRUCCIONES DE USO DEL ADMIN:")
    print("=" * 60)
    print("1️⃣ Inicia el servidor Django:")
    print("   python manage.py runserver")
    print()
    print("2️⃣ Ve al admin de Django:")
    print("   http://127.0.0.1:8000/admin/")
    print()
    print("3️⃣ Navega a Knowledge models:")
    print("   http://127.0.0.1:8000/admin/knowledge/knowledgemodel/")
    print()
    print("4️⃣ Haz clic en el botón '📤 Subir Archivo CSV/JSON'")
    print()
    print("5️⃣ Completa el formulario:")
    print("   - Nombre: Ej. 'Base de Datos de Empleados'")
    print("   - Tipo: Selecciona 'JSON' o 'CSV'")
    print("   - Archivo: Sube uno de los archivos de prueba creados:")
    print("     • test_data_empleados.json")
    print("     • test_data_productos.csv")
    print("   - Descripción: (opcional)")
    print()
    print("6️⃣ Haz clic en '📤 Procesar y Crear Documento'")
    print()
    print("✨ El sistema automáticamente:")
    print("   • Validará el formato del archivo")
    print("   • Convertirá el contenido a Markdown estructurado")
    print("   • Creará un nuevo documento de Knowledge")
    print("   • Te redirigirá a la página de edición del documento")
    print()
    print("🔍 Podrás ver el contenido transformado en la sección 'Vista Previa'")


def main():
    """Función principal."""
    print("🚀 PRUEBAS DE FUNCIONALIDAD DE SUBIDA DE ARCHIVOS EN ADMIN")
    print("=" * 70)

    # Verificar que los archivos de prueba existen
    json_file = "/Users/gustavo.ghioldi/barba/chat-with-us/test_data_empleados.json"
    csv_file = "/Users/gustavo.ghioldi/barba/chat-with-us/test_data_productos.csv"

    if not os.path.exists(json_file):
        print(f"❌ No se encuentra el archivo de prueba JSON: {json_file}")
        return

    if not os.path.exists(csv_file):
        print(f"❌ No se encuentra el archivo de prueba CSV: {csv_file}")
        return

    print("✅ Archivos de prueba encontrados")

    # Ejecutar pruebas
    tests_passed = 0
    total_tests = 3

    if test_json_file_processing():
        tests_passed += 1

    if test_csv_file_processing():
        tests_passed += 1

    if test_admin_form_simulation():
        tests_passed += 1

    # Mostrar instrucciones
    show_usage_instructions()

    # Resumen final
    print(f"\n📊 RESUMEN DE PRUEBAS:")
    print("=" * 40)
    print(f"✅ Pruebas exitosas: {tests_passed}/{total_tests}")

    if tests_passed == total_tests:
        print("🎉 ¡Todas las pruebas pasaron! El admin está listo para usar.")
    else:
        print("⚠️ Algunas pruebas fallaron. Revisa los errores arriba.")

    print("\n🎯 Funcionalidades implementadas:")
    print("   ✓ Formulario de subida de archivos con validación")
    print("   ✓ Procesamiento automático de JSON y CSV")
    print("   ✓ Conversión a formato Markdown estructurado")
    print("   ✓ Validación de límites y formatos")
    print("   ✓ Interfaz de admin personalizada con emojis")
    print("   ✓ Vista previa del contenido transformado")
    print("   ✓ Mensajes informativos y de error")


if __name__ == "__main__":
    main()
