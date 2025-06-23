from django.utils import timezone

from documents.models import DocumentModel
from main.signals import track_model_changes


@track_model_changes(DocumentModel)
def handle_document_changes(
    sender, instance, created, updated_fields, change_type, **kwargs
):
    """
    Handler específico para cambios en DocumentModel.
    Cuando se modifica un documento, marca como recreate=True todos los
    KnowledgeModel relacionados con ese documento.
    """
    from knowledge.models import KnowledgeModel

    if created:
        print(f"📄 Nuevo documento creado: {instance}")
        # Para documentos nuevos, no hay modelos de conocimiento relacionados aún

    else:
        print(f"🔄 Documento actualizado: {instance}")

        if updated_fields:
            print("Campos del documento modificados:")
            for field_info in updated_fields:
                print(
                    f"  - {field_info['field_verbose_name']} ({field_info['field']}): "
                    f"'{field_info['old_value']}' → '{field_info['new_value']}'"
                )

        # Buscar todos los KnowledgeModel relacionados con este documento
        related_knowledge_models = KnowledgeModel.objects.filter(document=instance)

        if related_knowledge_models.exists():
            count = related_knowledge_models.count()
            print(f"🧠 Encontrados {count} modelo(s) de conocimiento relacionados")

            # Actualizar todos los modelos relacionados para que necesiten recreación
            updated_count = related_knowledge_models.update(recreate=True)

            print(
                f"✅ {updated_count} modelo(s) de conocimiento marcados para recreación"
            )

            # Mostrar detalles de los modelos actualizados
            for knowledge in related_knowledge_models:
                print(f"   - {knowledge.name} (ID: {knowledge.id}) -> recreate = True")

        else:
            print("ℹ️ No hay modelos de conocimiento relacionados con este documento")

    print(f"🏁 Procesamiento de cambios en documento completado")
