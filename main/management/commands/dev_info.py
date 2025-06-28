"""
Comando para mostrar información útil de desarrollo sin debug toolbar.
"""

import os
import sys

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Muestra información útil para desarrollo"

    def add_arguments(self, parser):
        parser.add_argument(
            "--sql",
            action="store_true",
            help="Muestra las últimas consultas SQL",
        )
        parser.add_argument(
            "--config",
            action="store_true",
            help="Muestra configuraciones importantes",
        )
        parser.add_argument(
            "--env",
            action="store_true",
            help="Muestra variables de entorno relevantes",
        )

    def handle(self, *args, **options):
        self.stdout.write("🚀 Información de Desarrollo")
        self.stdout.write("=" * 50)

        if options["sql"]:
            self.show_sql_queries()

        if options["config"]:
            self.show_important_settings()

        if options["env"]:
            self.show_environment_vars()

        # Si no se especifica nada, mostrar todo
        if not any([options["sql"], options["config"], options["env"]]):
            self.show_important_settings()
            self.show_environment_vars()
            self.show_quick_stats()

        self.stdout.write(self.style.SUCCESS("\n✨ Información mostrada"))

    def show_sql_queries(self):
        """Muestra las últimas consultas SQL"""
        self.stdout.write("\n📊 Últimas Consultas SQL:")

        if not settings.DEBUG:
            self.stdout.write(
                self.style.WARNING("⚠️ DEBUG debe estar en True para ver consultas SQL")
            )
            return

        queries = connection.queries[-10:]  # Últimas 10 consultas

        for i, query in enumerate(queries, 1):
            time = query.get("time", "N/A")
            sql = (
                query.get("sql", "N/A")[:100] + "..."
                if len(query.get("sql", "")) > 100
                else query.get("sql", "N/A")
            )
            self.stdout.write(f"  {i}. [{time}s] {sql}")

    def show_important_settings(self):
        """Muestra configuraciones importantes"""
        self.stdout.write("\n⚙️ Configuraciones Importantes:")

        config_items = [
            ("DEBUG", settings.DEBUG),
            ("ENVIRONMENT", os.environ.get("DJANGO_ENV", "development")),
            ("DATABASE", settings.DATABASES["default"]["NAME"]),
            ("DB_HOST", settings.DATABASES["default"]["HOST"]),
            ("ALLOWED_HOSTS", settings.ALLOWED_HOSTS),
            ("SECRET_KEY", settings.SECRET_KEY[:20] + "..."),
            (
                "CORS_ALLOW_ALL_ORIGINS",
                getattr(settings, "CORS_ALLOW_ALL_ORIGINS", False),
            ),
        ]

        for key, value in config_items:
            status = "✅" if value else "❌"
            self.stdout.write(f"  {status} {key}: {value}")

    def show_environment_vars(self):
        """Muestra variables de entorno relevantes"""
        self.stdout.write("\n🌍 Variables de Entorno:")

        env_vars = [
            "DJANGO_ENV",
            "DB_NAME",
            "DB_USER",
            "DB_HOST",
            "DB_PORT",
            "CELERY_BROKER_URL",
            "CELERY_RESULT_BACKEND",
        ]

        for var in env_vars:
            value = os.environ.get(var, "No configurada")
            status = "✅" if value != "No configurada" else "⚠️"
            # Ocultar contraseñas
            if "PASSWORD" in var or "SECRET" in var:
                value = "***" if value != "No configurada" else value
            self.stdout.write(f"  {status} {var}: {value}")

    def show_quick_stats(self):
        """Muestra estadísticas rápidas"""
        self.stdout.write("\n📈 Estadísticas Rápidas:")

        try:
            # Importar modelos principales
            from agents.models import AgentModel
            from documents.models import DocumentModel
            from tenants.models import TenantModel

            stats = [
                ("Agentes", AgentModel.objects.count()),
                ("Tenants", TenantModel.objects.count()),
                ("Documentos", DocumentModel.objects.count()),
            ]

            for name, count in stats:
                self.stdout.write(f"  📊 {name}: {count}")

        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f"⚠️ No se pudieron obtener estadísticas: {e}")
            )
