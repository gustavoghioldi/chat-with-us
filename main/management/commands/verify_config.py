"""
Django management command to verify project configurations.
"""

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Verifica configuraciones del proyecto"

    def add_arguments(self, parser):
        parser.add_argument(
            "--check-apps",
            action="store_true",
            help="Verifica las aplicaciones instaladas",
        )
        parser.add_argument(
            "--check-configurators",
            action="store_true",
            help="Verifica los configuradores de agentes",
        )

    def handle(self, *args, **options):
        self.stdout.write("🔧 Verificando configuración del proyecto...")

        if options["check_apps"]:
            self.check_installed_apps()
        elif options["check_configurators"]:
            self.check_configurators()
        else:
            # Verificación general si no se especifica nada
            self.check_installed_apps()
            self.check_configurators()

        self.stdout.write(self.style.SUCCESS("✅ Verificación completada"))

    def check_installed_apps(self):
        """Verifica las aplicaciones instaladas"""
        self.stdout.write("\n📱 Verificando aplicaciones instaladas...")

        custom_apps = [
            "agents",
            "api",
            "chats",
            "crews",
            "documents",
            "knowledge",
            "tenants",
            "tools",
            "analysis",
        ]

        for app in custom_apps:
            if app in settings.INSTALLED_APPS:
                self.stdout.write(f"✅ {app}")
            else:
                self.stdout.write(
                    self.style.WARNING(f"⚠️ {app} no está en INSTALLED_APPS")
                )

    def check_configurators(self):
        """Verifica los configuradores de agentes"""
        self.stdout.write("\n🤖 Verificando configuradores de agentes...")

        try:
            from agents.services.configurators import AgentConfiguratorFactory

            supported_models = AgentConfiguratorFactory.get_supported_models()
            self.stdout.write(f"✅ Configuradores disponibles: {supported_models}")

            # Verificar cada configurador
            for model_type in supported_models:
                try:
                    # Simular creación sin crear realmente
                    configurator_class = AgentConfiguratorFactory._configurators[
                        model_type
                    ]
                    self.stdout.write(
                        f"  ✅ {model_type}: {configurator_class.__name__}"
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f"  ⚠️ {model_type}: Error - {e}")
                    )

        except ImportError as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Error importando configuradores: {e}")
            )
