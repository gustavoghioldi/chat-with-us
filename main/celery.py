import os

import django
from celery import Celery
from celery.signals import worker_ready

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main.settings")

# Setup Django antes de crear la app de Celery
django.setup()

app = Celery("main")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@worker_ready.connect
def at_start(sender, **k):
    """
    Se ejecuta cuando el worker de Celery está listo.
    Aquí nos aseguramos de que todos los signals estén cargados.
    """
    try:
        # Importar y cargar todos los signals
        import agents.signals.telegram_new_message  # noqa: F401

        print("✅ Signals cargados exitosamente en Celery worker")
    except ImportError as e:
        print(f"❌ Error cargando signals en Celery worker: {e}")


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
