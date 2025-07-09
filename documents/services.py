import mimetypes
import os
from typing import Any, Dict, List, Optional

from django.contrib.auth.models import User
from django.core.files.uploadedfile import UploadedFile
from django.db.models import QuerySet
from django.utils import timezone

from tenants.models import TenantModel

from .models import DocumentModel


class DocumentService:
    """
    Servicio para manejar la lógica de negocio de documentos.
    Proporciona métodos para crear, leer, actualizar y eliminar documentos.
    """

    @staticmethod
    def generate_unique_filename(original_filename: str) -> str:
        """
        Genera un nombre de archivo único agregando timestamp y UUID.

        Args:
            original_filename: Nombre original del archivo

        Returns:
            str: Nombre único con timestamp y UUID
        """
        import uuid

        name, ext = os.path.splitext(original_filename)

        # Limpiar el nombre del archivo
        clean_name = "".join(
            c for c in name if c.isalnum() or c in (" ", "-", "_")
        ).rstrip()
        clean_name = clean_name.replace(" ", "_")

        # Generar timestamp único con microsegundos completos
        now = timezone.now()
        timestamp = now.strftime("%Y%m%d_%H%M%S_%f")

        # Agregar parte de UUID para mayor unicidad
        unique_suffix = str(uuid.uuid4())[:8]

        return f"{clean_name}_{timestamp}_{unique_suffix}{ext.lower()}"

    @staticmethod
    def create_document(
        title: str,
        file: UploadedFile,
        tenant: TenantModel,
        uploaded_by: User,
        description: Optional[str] = None,
        document_type: Optional[str] = None,
    ) -> DocumentModel:
        """
        Crea un nuevo documento.

        Args:
            title: Título del documento
            file: Archivo subido
            tenant: Tenant al que pertenece el documento
            uploaded_by: Usuario que sube el documento
            description: Descripción opcional del documento
            document_type: Tipo de documento (se detecta automáticamente si no se proporciona)

        Returns:
            DocumentModel: El documento creado

        Raises:
            ValueError: Si el archivo no es válido o el tipo no está permitido
        """
        # Validar el archivo
        if not file:
            raise ValueError("El archivo es requerido")

        # Detectar tipo de documento si no se proporciona
        if not document_type:
            ext = os.path.splitext(file.name)[1].lower().lstrip(".")
            allowed_types = [choice[0] for choice in DocumentModel.DOCUMENT_TYPES]
            if ext not in allowed_types:
                raise ValueError(f"Tipo de archivo no permitido: {ext}")
            document_type = ext

        # Crear el documento
        document = DocumentModel.objects.create(
            title=title,
            description=description,
            file=file,
            document_type=document_type,
            tenant=tenant,
            uploaded_by=uploaded_by,
        )

        return document

    @staticmethod
    def get_documents_by_tenant(
        tenant: TenantModel,
        is_active: Optional[bool] = True,
        document_type: Optional[str] = None,
        user: Optional[User] = None,
    ) -> QuerySet[DocumentModel]:
        """
        Obtiene documentos filtrados por tenant.

        Args:
            tenant: Tenant del que obtener documentos
            is_active: Filtrar por documentos activos
            document_type: Filtrar por tipo de documento
            user: Filtrar por usuario (opcional)

        Returns:
            QuerySet de documentos
        """
        queryset = DocumentModel.objects.filter(tenant=tenant)

        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)

        if document_type:
            queryset = queryset.filter(document_type=document_type)

        if user:
            queryset = queryset.filter(uploaded_by=user)

        return queryset.select_related("tenant", "uploaded_by").order_by("-created_at")

    @staticmethod
    def get_document_by_id(
        document_id: int, tenant: TenantModel
    ) -> Optional[DocumentModel]:
        """
        Obtiene un documento específico por ID y tenant.

        Args:
            document_id: ID del documento
            tenant: Tenant del documento

        Returns:
            DocumentModel o None si no existe
        """
        try:
            return DocumentModel.objects.select_related("tenant", "uploaded_by").get(
                id=document_id, tenant=tenant
            )
        except DocumentModel.DoesNotExist:
            return None

    @staticmethod
    def update_document(
        document: DocumentModel,
        title: Optional[str] = None,
        description: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> DocumentModel:
        """
        Actualiza un documento existente.

        Args:
            document: Documento a actualizar
            title: Nuevo título (opcional)
            description: Nueva descripción (opcional)
            is_active: Nuevo estado activo (opcional)

        Returns:
            DocumentModel actualizado
        """
        if title is not None:
            document.title = title

        if description is not None:
            document.description = description

        if is_active is not None:
            document.is_active = is_active

        document.save()
        return document

    @staticmethod
    def delete_document(document: DocumentModel, soft_delete: bool = True) -> bool:
        """
        Elimina un documento.

        Args:
            document: Documento a eliminar
            soft_delete: Si True, solo marca como inactivo. Si False, elimina físicamente.

        Returns:
            bool: True si se eliminó correctamente
        """
        try:
            if soft_delete:
                document.is_active = False
                document.save()
            else:
                # Eliminar archivo físico
                if document.file:
                    if os.path.exists(document.file.path):
                        os.remove(document.file.path)

                # Eliminar registro de la base de datos
                document.delete()

            return True
        except Exception:
            return False

    @staticmethod
    def mark_as_processed(document: DocumentModel) -> DocumentModel:
        """
        Marca un documento como procesado.

        Args:
            document: Documento a marcar como procesado

        Returns:
            DocumentModel actualizado
        """
        document.is_processed = True
        document.processed_at = timezone.now()
        document.save()
        return document

    @staticmethod
    def get_document_stats(tenant: TenantModel) -> Dict[str, Any]:
        """
        Obtiene estadísticas de documentos para un tenant.

        Args:
            tenant: Tenant del que obtener estadísticas

        Returns:
            Dict con estadísticas
        """
        documents = DocumentModel.objects.filter(tenant=tenant)

        total_documents = documents.count()
        active_documents = documents.filter(is_active=True).count()
        processed_documents = documents.filter(is_processed=True).count()

        # Estadísticas por tipo
        type_stats = {}
        for doc_type, _ in DocumentModel.DOCUMENT_TYPES:
            count = documents.filter(document_type=doc_type).count()
            if count > 0:
                type_stats[doc_type] = count

        # Tamaño total de archivos
        total_size = sum(doc.file_size or 0 for doc in documents if doc.file_size)

        return {
            "total_documents": total_documents,
            "active_documents": active_documents,
            "processed_documents": processed_documents,
            "unprocessed_documents": total_documents - processed_documents,
            "documents_by_type": type_stats,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2) if total_size else 0,
        }

    @staticmethod
    def validate_file(file: UploadedFile) -> Dict[str, Any]:
        """
        Valida un archivo antes de subirlo.

        Args:
            file: Archivo a validar

        Returns:
            Dict con resultado de validación y errores si los hay
        """
        errors = []
        warnings = []

        # Validar tamaño máximo (50MB)
        max_size = 50 * 1024 * 1024  # 50MB
        if file.size > max_size:
            errors.append(f"El archivo es demasiado grande. Máximo permitido: 50MB")

        # Validar extensión
        ext = os.path.splitext(file.name)[1].lower().lstrip(".")
        allowed_extensions = [choice[0] for choice in DocumentModel.DOCUMENT_TYPES]
        if ext not in allowed_extensions:
            errors.append(f"Extensión no permitida: .{ext}")

        # Validar tipo MIME
        mime_type, _ = mimetypes.guess_type(file.name)
        if mime_type:
            # Tipos MIME permitidos básicos
            allowed_mimes = [
                "application/pdf",
                "application/msword",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "text/plain",
                "text/csv",
                "application/vnd.ms-excel",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "application/json",
                "text/markdown",
            ]

            if mime_type not in allowed_mimes:
                warnings.append(f"Tipo MIME no reconocido: {mime_type}")

        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "file_info": {
                "name": file.name,
                "unique_name_preview": DocumentService.generate_unique_filename(
                    file.name
                ),
                "size": file.size,
                "size_mb": round(file.size / (1024 * 1024), 2),
                "extension": ext,
                "mime_type": mime_type,
            },
        }

    @staticmethod
    def bulk_update_status(
        document_ids: List[int],
        tenant: TenantModel,
        is_active: Optional[bool] = None,
        is_processed: Optional[bool] = None,
    ) -> int:
        """
        Actualiza el estado de múltiples documentos.

        Args:
            document_ids: Lista de IDs de documentos
            tenant: Tenant de los documentos
            is_active: Nuevo estado activo (opcional)
            is_processed: Nuevo estado procesado (opcional)

        Returns:
            int: Número de documentos actualizados
        """
        queryset = DocumentModel.objects.filter(id__in=document_ids, tenant=tenant)

        update_fields = {}
        if is_active is not None:
            update_fields["is_active"] = is_active

        if is_processed is not None:
            update_fields["is_processed"] = is_processed
            if is_processed:
                update_fields["processed_at"] = timezone.now()
            else:
                update_fields["processed_at"] = None

        if update_fields:
            return queryset.update(**update_fields)

        return 0
