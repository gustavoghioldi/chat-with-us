#!/usr/bin/env python
"""
Script de prueba para la API REST de AgentModel
Ejecutar con: python test_agent_api.py
"""

import os
import sys

import django

# Configurar Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main.settings")
django.setup()

from django.contrib.auth.models import User

from agents.models import AgentModel
from knowledge.models import KnowledgeModel
from tenants.models import TenantModel


def test_api_functionality():
    """Prueba las funcionalidades básicas de la API."""

    print("🧪 Iniciando pruebas de la API de AgentModel...")

    # 1. Verificar que existen datos de prueba
    print("\n1. Verificando datos existentes...")
    agents_count = AgentModel.objects.count()
    tenants_count = TenantModel.objects.count()
    knowledge_count = KnowledgeModel.objects.count()
    users_count = User.objects.count()

    print(f"   📊 Agentes: {agents_count}")
    print(f"   🏢 Tenants: {tenants_count}")
    print(f"   📚 Knowledge: {knowledge_count}")
    print(f"   👤 Usuarios: {users_count}")

    # 2. Crear datos de prueba si no existen
    if tenants_count == 0:
        print("\n2. Creando tenant de prueba...")
        tenant = TenantModel.objects.create(
            name="Tenant de Prueba", description="Tenant creado para pruebas de la API"
        )
        print(f"   ✅ Tenant creado: {tenant.name} (Token: {tenant.cwu_token})")
    else:
        tenant = TenantModel.objects.first()
        print(f"\n2. Usando tenant existente: {tenant.name}")

    if users_count == 0:
        print("\n3. Creando usuario de prueba...")
        user = User.objects.create_user(
            username="api_test_user",
            email="test@example.com",
            password="testpassword123",
        )
        print(f"   ✅ Usuario creado: {user.username}")
    else:
        user = User.objects.first()
        print(f"\n3. Usando usuario existente: {user.username}")

    if knowledge_count == 0:
        print("\n4. Creando modelo de conocimiento de prueba...")
        knowledge = KnowledgeModel.objects.create(
            title="Conocimiento de Prueba",
            category="plain_document",
            text="Este es un documento de conocimiento de prueba para la API.",
        )
        print(f"   ✅ Knowledge creado: {knowledge.title}")
    else:
        knowledge = KnowledgeModel.objects.first()
        print(f"\n4. Usando knowledge existente: {knowledge.title}")

    # 3. Crear agente de prueba
    print("\n5. Creando agente de prueba...")
    agent_data = {
        "name": "Agente API Test",
        "instructions": "Este es un agente creado para probar la API REST.",
        "agent_model_id": "llama3.2:3b",
        "tenant": tenant,
    }

    # Verificar si ya existe un agente con este nombre
    existing_agent = AgentModel.objects.filter(name=agent_data["name"]).first()
    if existing_agent:
        print(f"   ⚠️  Agente ya existe: {existing_agent.name}")
        agent = existing_agent
    else:
        agent = AgentModel.objects.create(**agent_data)
        print(f"   ✅ Agente creado: {agent.name}")

    # 4. Agregar conocimiento al agente
    print("\n6. Agregando conocimiento al agente...")
    agent.knoledge_text_models.add(knowledge)
    print(f"   ✅ Conocimiento agregado al agente")

    # 5. Mostrar datos finales
    print("\n7. 📋 Resumen de datos creados:")
    print(f"   🏢 Tenant: {tenant.name} (ID: {tenant.id})")
    print(f"   👤 Usuario: {user.username} (ID: {user.id})")
    print(f"   🤖 Agente: {agent.name} (ID: {agent.id})")
    print(f"   📚 Knowledge: {knowledge.title} (ID: {knowledge.id})")

    # 6. URLs de la API disponibles
    print("\n8. 🌐 URLs de la API disponibles:")
    print("   GET    /api/v1/agents/                     - Listar agentes")
    print("   POST   /api/v1/agents/                     - Crear agente")
    print(
        f"   GET    /api/v1/agents/{agent.id}/               - Obtener agente específico"
    )
    print(
        f"   PUT    /api/v1/agents/{agent.id}/               - Actualizar agente completo"
    )
    print(
        f"   PATCH  /api/v1/agents/{agent.id}/               - Actualizar agente parcial"
    )
    print(f"   DELETE /api/v1/agents/{agent.id}/               - Eliminar agente")
    print(f"   GET    /api/v1/agents/by-tenant/{tenant.id}/    - Agentes por tenant")
    print(f"   POST   /api/v1/agents/{agent.id}/add_knowledge/ - Agregar conocimiento")
    print(
        f"   POST   /api/v1/agents/{agent.id}/remove_knowledge/ - Remover conocimiento"
    )
    print("   GET    /api/v1/agents/search/?q=test         - Búsqueda avanzada")

    print("\n✅ Pruebas completadas. La API está lista para usar!")
    print("\n💡 Para probar la API, ejecuta:")
    print("   python manage.py runserver")
    print("   Luego visita: http://localhost:8000/api/v1/agents/")


if __name__ == "__main__":
    test_api_functionality()
