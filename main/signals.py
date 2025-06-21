"""
Sistema genérico de signals para trackear cambios en cualquier modelo Django.
Este módulo puede ser usado desde cualquier app del proyecto.
"""

import logging

import django.dispatch
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

# Configurar logger
logger = logging.getLogger(__name__)

# Signal personalizado que se emite cuando un modelo cambia
model_changed = django.dispatch.Signal()

# Diccionario para almacenar el estado previo de los objetos
_model_state_cache = {}


def track_model_changes(*model_classes):
    """
    Decorator genérico para trackear cambios en cualquier modelo.

    Uso:
    from main.signals import track_model_changes

    @track_model_changes(AgentModel, OtherModel)
    def handle_model_change(sender, instance, created, updated_fields, **kwargs):
        # Tu lógica aquí
        pass
    """

    def decorator(func):
        # Conectar la función al signal personalizado para cada modelo
        for model_class in model_classes:
            model_changed.connect(func, sender=model_class)
        return func

    return decorator


@receiver(pre_save)
def capture_model_state(sender, instance, **kwargs):
    """
    Captura el estado previo del modelo antes de guardarlo.
    """
    if not isinstance(instance, models.Model):
        return

    # Solo capturar si el objeto ya existe en la BD
    if instance.pk:
        try:
            # Obtener el objeto original de la base de datos
            original = sender.objects.get(pk=instance.pk)

            # Crear una clave única para este objeto
            cache_key = f"{sender._meta.label}_{instance.pk}"

            # Guardar los valores originales de todos los campos
            original_values = {}
            for field in instance._meta.fields:
                if hasattr(original, field.name):
                    original_values[field.name] = getattr(original, field.name)

            _model_state_cache[cache_key] = original_values

        except sender.DoesNotExist:
            # El objeto no existe, será una creación
            pass


@receiver(post_save)
def detect_model_changes(sender, instance, created, **kwargs):
    """
    Detecta los cambios en el modelo y emite el signal personalizado.
    """
    if not isinstance(instance, models.Model):
        return

    updated_fields = []
    cache_key = f"{sender._meta.label}_{instance.pk}"

    if created:
        # Es un objeto nuevo
        logger.info(f"Nuevo {sender._meta.verbose_name} creado: {instance}")
    else:
        # Es una actualización, comparar con el estado previo
        if cache_key in _model_state_cache:
            original_values = _model_state_cache[cache_key]

            # Comparar cada campo para detectar cambios
            for field in instance._meta.fields:
                field_name = field.name
                if field_name in original_values:
                    old_value = original_values[field_name]
                    new_value = getattr(instance, field_name)

                    # Comparar valores (manejando casos especiales como None)
                    if old_value != new_value:
                        updated_fields.append(
                            {
                                "field": field_name,
                                "old_value": old_value,
                                "new_value": new_value,
                                "field_verbose_name": field.verbose_name,
                            }
                        )

            # Limpiar el cache después de usar
            del _model_state_cache[cache_key]

            if updated_fields:
                logger.info(
                    f"{sender._meta.verbose_name} actualizado: {instance}. Campos modificados: {[f['field'] for f in updated_fields]}"
                )

    # Emitir el signal personalizado con toda la información
    model_changed.send(
        sender=sender,
        instance=instance,
        created=created,
        updated_fields=updated_fields,
        change_type="created" if created else "updated",
    )


# Función helper para conectar signals desde otras apps
def connect_model_signals():
    """
    Función que puede ser llamada desde otras apps para asegurar que
    los signals están conectados. Es útil para importar desde apps.py
    """
    # Los signals ya están conectados automáticamente con @receiver
    # Esta función existe por compatibilidad y para futuras extensiones
    pass


# Ejemplo de cómo usar desde cualquier app
def create_model_handler(models_list, handler_function):
    """
    Función helper para crear handlers desde otras apps.

    Uso:
    from main.signals import create_model_handler
    from myapp.models import MyModel

    def my_handler(sender, instance, created, updated_fields, change_type, **kwargs):
        # Tu lógica aquí
        pass

    create_model_handler([MyModel], my_handler)
    """
    for model_class in models_list:
        model_changed.connect(handler_function, sender=model_class)
