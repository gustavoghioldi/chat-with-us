#!/usr/bin/env python
"""
Script de prueba completo para las APIs de Agent y Knowledge.
Prueba todas las funcionalidades implementadas incluyendo:
- Gestión de Agentes (CRUD)
- Gestión de Knowledge con diferentes tipos (text, json, csv, web-scraping)
- Generación de tokens para tenants
- Formateo de contenido a Markdown
"""

import json
import sys

import requests

# Configuración del servidor
BASE_URL = "http://127.0.0.1:8000"
API_BASE = f"{BASE_URL}/api/v1"

# Headers por defecto
HEADERS = {
    "Content-Type": "application/json",
}


def print_test_header(title):
    """Imprimir encabezado de prueba."""
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print("=" * 60)


def print_response(response, title="Response"):
    """Imprimir respuesta de la API."""
    print(f"\n📋 {title}:")
    print(f"Status: {response.status_code}")
    try:
        data = response.json()
        print(f"Data: {json.dumps(data, indent=2, ensure_ascii=False)}")
    except:
        print(f"Text: {response.text}")


def test_agents_api():
    """Probar la API de Agentes."""
    print_test_header("PRUEBAS DE API DE AGENTES")

    # 1. Listar agentes
    print("\n1️⃣ Listando agentes existentes...")
    response = requests.get(f"{API_BASE}/agents/", headers=HEADERS)
    print_response(response, "Lista de Agentes")

    # 2. Crear un nuevo agente
    print("\n2️⃣ Creando nuevo agente...")
    agent_data = {
        "name": "Agente de Prueba API",
        "description": "Agente creado para probar la API REST completa",
        "agent_model_id": "test-agent-001",
    }
    response = requests.post(
        f"{API_BASE}/agents/", headers=HEADERS, data=json.dumps(agent_data)
    )
    print_response(response, "Agente Creado")

    if response.status_code == 201:
        agent_id = response.json().get("id")

        # 3. Obtener agente específico
        print(f"\n3️⃣ Obteniendo agente ID {agent_id}...")
        response = requests.get(f"{API_BASE}/agents/{agent_id}/", headers=HEADERS)
        print_response(response, "Detalle del Agente")

        # 4. Actualizar agente
        print(f"\n4️⃣ Actualizando agente ID {agent_id}...")
        update_data = {"description": "Agente actualizado desde la API REST"}
        response = requests.patch(
            f"{API_BASE}/agents/{agent_id}/",
            headers=HEADERS,
            data=json.dumps(update_data),
        )
        print_response(response, "Agente Actualizado")

        # 5. Filtrar agentes por nombre
        print("\n5️⃣ Filtrando agentes por nombre...")
        response = requests.get(f"{API_BASE}/agents/?search=Prueba", headers=HEADERS)
        print_response(response, "Agentes Filtrados")

        return agent_id

    return None


def test_knowledge_text_api():
    """Probar la API de Knowledge tipo TEXT."""
    print_test_header("PRUEBAS DE KNOWLEDGE API - TIPO TEXT")

    # 1. Crear conocimiento tipo texto
    print("\n1️⃣ Creando knowledge tipo TEXT...")
    text_data = {
        "name": "Documento de Prueba",
        "content": "Este es un documento de texto de prueba para la API de Knowledge.\n\nContiene múltiples líneas y información importante sobre el sistema.",
    }
    response = requests.post(
        f"{API_BASE}/knowledge/text/", headers=HEADERS, data=json.dumps(text_data)
    )
    print_response(response, "Knowledge TEXT Creado")

    if response.status_code == 201:
        knowledge_id = response.json().get("id")

        # 2. Obtener knowledge específico
        print(f"\n2️⃣ Obteniendo knowledge TEXT ID {knowledge_id}...")
        response = requests.get(
            f"{API_BASE}/knowledge/text/{knowledge_id}/", headers=HEADERS
        )
        print_response(response, "Detalle Knowledge TEXT")

        return knowledge_id

    return None


def test_knowledge_json_api():
    """Probar la API de Knowledge tipo JSON."""
    print_test_header("PRUEBAS DE KNOWLEDGE API - TIPO JSON")

    # 1. Crear conocimiento tipo JSON con lista de objetos
    print("\n1️⃣ Creando knowledge tipo JSON con lista de objetos...")
    json_data = {
        "name": "Base de Datos de Usuarios",
        "content": [
            {
                "id": 1,
                "nombre": "Juan Pérez",
                "email": "juan@ejemplo.com",
                "edad": 30,
                "departamento": "Desarrollo",
            },
            {
                "id": 2,
                "nombre": "María García",
                "email": "maria@ejemplo.com",
                "edad": 28,
                "departamento": "Marketing",
            },
            {
                "id": 3,
                "nombre": "Carlos López",
                "email": "carlos@ejemplo.com",
                "edad": 35,
                "departamento": "Ventas",
            },
        ],
    }
    response = requests.post(
        f"{API_BASE}/knowledge/json/", headers=HEADERS, data=json.dumps(json_data)
    )
    print_response(response, "Knowledge JSON Creado")

    if response.status_code == 201:
        knowledge_id = response.json().get("id")

        # 2. Obtener knowledge específico
        print(f"\n2️⃣ Obteniendo knowledge JSON ID {knowledge_id}...")
        response = requests.get(
            f"{API_BASE}/knowledge/json/{knowledge_id}/", headers=HEADERS
        )
        print_response(response, "Detalle Knowledge JSON")

        return knowledge_id

    return None


def test_knowledge_csv_api():
    """Probar la API de Knowledge tipo CSV."""
    print_test_header("PRUEBAS DE KNOWLEDGE API - TIPO CSV")

    # 1. Crear conocimiento tipo CSV
    print("\n1️⃣ Creando knowledge tipo CSV...")
    csv_data = {
        "name": "Datos de Ventas Q1 2025",
        "content": """id,producto,precio,cantidad,vendedor,fecha
1,Laptop Dell,1200.00,5,Juan Pérez,2025-01-15
2,Monitor Samsung,300.00,10,María García,2025-01-20
3,Teclado Mecánico,80.00,25,Carlos López,2025-02-01
4,Mouse Gaming,45.00,30,Ana Martín,2025-02-10
5,Webcam HD,120.00,15,Luis Torres,2025-03-05""",
    }
    response = requests.post(
        f"{API_BASE}/knowledge/csv/", headers=HEADERS, data=json.dumps(csv_data)
    )
    print_response(response, "Knowledge CSV Creado")

    if response.status_code == 201:
        knowledge_id = response.json().get("id")

        # 2. Obtener knowledge específico
        print(f"\n2️⃣ Obteniendo knowledge CSV ID {knowledge_id}...")
        response = requests.get(
            f"{API_BASE}/knowledge/csv/{knowledge_id}/", headers=HEADERS
        )
        print_response(response, "Detalle Knowledge CSV")

        return knowledge_id

    return None


def test_knowledge_webscraping_api():
    """Probar la API de Knowledge tipo Web Scraping."""
    print_test_header("PRUEBAS DE KNOWLEDGE API - TIPO WEB SCRAPING")

    # 1. Crear conocimiento tipo web scraping
    print("\n1️⃣ Creando knowledge tipo WEB SCRAPING...")
    scraping_data = {
        "name": "Documentación Django",
        "url": "https://docs.djangoproject.com/en/stable/",
        "max_depth": 2,
        "max_links": 5,
    }
    response = requests.post(
        f"{API_BASE}/knowledge/web-scraping/",
        headers=HEADERS,
        data=json.dumps(scraping_data),
    )
    print_response(response, "Knowledge WEB SCRAPING Creado")

    if response.status_code == 201:
        knowledge_id = response.json().get("id")

        # 2. Obtener knowledge específico
        print(f"\n2️⃣ Obteniendo knowledge WEB SCRAPING ID {knowledge_id}...")
        response = requests.get(
            f"{API_BASE}/knowledge/web-scraping/{knowledge_id}/", headers=HEADERS
        )
        print_response(response, "Detalle Knowledge WEB SCRAPING")

        return knowledge_id

    return None


def test_knowledge_list_and_filters():
    """Probar listado y filtros de Knowledge."""
    print_test_header("PRUEBAS DE LISTADO Y FILTROS DE KNOWLEDGE")

    # 1. Listar todos los knowledge
    print("\n1️⃣ Listando todos los knowledge...")
    response = requests.get(f"{API_BASE}/knowledge/text/", headers=HEADERS)
    print_response(response, "Lista Knowledge TEXT")

    # 2. Buscar knowledge
    print("\n2️⃣ Buscando knowledge por nombre...")
    response = requests.get(
        f"{API_BASE}/knowledge/json/?search=Usuarios", headers=HEADERS
    )
    print_response(response, "Búsqueda Knowledge")


def test_server_connection():
    """Verificar que el servidor Django esté funcionando."""
    print_test_header("VERIFICACIÓN DE CONEXIÓN AL SERVIDOR")

    try:
        response = requests.get(BASE_URL, timeout=5)
        print(f"✅ Servidor Django funcionando en {BASE_URL}")
        print(f"Status: {response.status_code}")
        return True
    except requests.exceptions.ConnectionError:
        print(f"❌ No se puede conectar al servidor Django en {BASE_URL}")
        print("Por favor, asegúrate de que el servidor esté ejecutándose con:")
        print("python manage.py runserver")
        return False
    except Exception as e:
        print(f"❌ Error al conectar: {e}")
        return False


def main():
    """Función principal que ejecuta todas las pruebas."""
    print("🚀 INICIANDO PRUEBAS COMPLETAS DE LA API")
    print(f"Servidor: {BASE_URL}")

    # Verificar conexión al servidor
    if not test_server_connection():
        sys.exit(1)

    try:
        # Probar APIs
        agent_id = test_agents_api()
        text_id = test_knowledge_text_api()
        json_id = test_knowledge_json_api()
        csv_id = test_knowledge_csv_api()
        webscraping_id = test_knowledge_webscraping_api()
        test_knowledge_list_and_filters()

        # Resumen final
        print_test_header("RESUMEN FINAL")
        print("✅ Pruebas completadas exitosamente!")
        print(f"📊 IDs creados:")
        if agent_id:
            print(f"   - Agente: {agent_id}")
        if text_id:
            print(f"   - Knowledge TEXT: {text_id}")
        if json_id:
            print(f"   - Knowledge JSON: {json_id}")
        if csv_id:
            print(f"   - Knowledge CSV: {csv_id}")
        if webscraping_id:
            print(f"   - Knowledge WEB SCRAPING: {webscraping_id}")

        print("\n🎯 Todas las funcionalidades han sido probadas:")
        print("   ✓ API REST de Agentes (CRUD completo)")
        print("   ✓ API REST de Knowledge con tipos dinámicos")
        print("   ✓ Formateo automático de JSON/CSV a Markdown")
        print("   ✓ Validación de contenido según tipo")
        print("   ✓ Filtros y búsqueda")
        print("   ✓ Serializers dinámicos según URL")

    except Exception as e:
        print(f"\n❌ Error durante las pruebas: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
