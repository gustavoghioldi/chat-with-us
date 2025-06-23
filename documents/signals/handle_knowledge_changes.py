from django.utils import timezone

from knowledge.models import KnowledgeModel
from main.signals import track_model_changes


@track_model_changes(KnowledgeModel)
def handle_knowledge_changes(
    sender, instance, created, updated_fields, change_type, **kwargs
):
    """
    Handler específico para cambios en KnowledgeModel.
    Registra los cambios y maneja lógica adicional si es necesario.
    """
    if created:
        print(f"✅ Nuevo conocimiento creado: {instance}")
        # Aquí puedes agregar lógica específica para cuando se crea un conocimiento

    else:
        print(f"🔄 Conocimiento actualizado: {instance}")

        if updated_fields:
            print("Campos modificados:")
            for field_info in updated_fields:
                print(
                    f"  - {field_info['field_verbose_name']} ({field_info['field']}): "
                    f"'{field_info['old_value']}' → '{field_info['new_value']}'"
                )

                # Verificar si se modificó el campo recreate a False
                if (
                    field_info["field"] == "recreate"
                    and field_info["old_value"] is True
                    and field_info["new_value"] is False
                ):

                    # Actualizar el DocumentModel relacionado si existe
                    if instance.document:
                        print(
                            f"🔄 Actualizando DocumentModel {instance.document.id} - is_processed = True"
                        )

                        # Actualizar el documento relacionado
                        from documents.models import DocumentModel

                        DocumentModel.objects.filter(id=instance.document.id).update(
                            is_processed=True, processed_at=timezone.now()
                        )

                        print(
                            f"✅ DocumentModel {instance.document.id} marcado como procesado"
                        )
                    else:
                        print("⚠️ No hay DocumentModel relacionado para actualizar")

        # Aquí puedes agregar lógica específica para cuando se actualiza un conocimiento
