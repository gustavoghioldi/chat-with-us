import os
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone

from documents.models import DocumentModel


class Command(BaseCommand):
    """
    Comando para limpiar documentos antiguos e inactivos.

    Uso:
    python manage.py cleanup_documents --days=30 --dry-run
    python manage.py cleanup_documents --inactive-only
    python manage.py cleanup_documents --hard-delete
    """

    help = "Limpia documentos antiguos e inactivos del sistema"

    def add_arguments(self, parser):
        """Agregar argumentos del comando"""
        parser.add_argument(
            "--days",
            type=int,
            default=90,
            help="Número de días para considerar documentos antiguos (default: 90)",
        )

        parser.add_argument(
            "--inactive-only",
            action="store_true",
            help="Solo eliminar documentos marcados como inactivos",
        )

        parser.add_argument(
            "--hard-delete",
            action="store_true",
            help="Eliminar archivos físicamente del sistema",
        )

        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Mostrar qué se eliminaría sin hacer cambios reales",
        )

        parser.add_argument(
            "--tenant-id",
            type=int,
            help="ID del tenant específico para limpiar (opcional)",
        )

    def handle(self, *args, **options):
        """Ejecutar el comando"""
        days = options["days"]
        inactive_only = options["inactive_only"]
        hard_delete = options["hard_delete"]
        dry_run = options["dry_run"]
        tenant_id = options.get("tenant_id")

        # Calcular fecha límite
        cutoff_date = timezone.now() - timedelta(days=days)

        # Construir query
        query = Q(created_at__lt=cutoff_date)

        if inactive_only:
            query &= Q(is_active=False)

        if tenant_id:
            query &= Q(tenant_id=tenant_id)

        # Obtener documentos a eliminar
        documents_to_delete = DocumentModel.objects.filter(query)
        total_count = documents_to_delete.count()

        if total_count == 0:
            self.stdout.write(
                self.style.SUCCESS(
                    "No se encontraron documentos que cumplan los criterios de eliminación."
                )
            )
            return

        # Mostrar información
        self.stdout.write(f"Documentos encontrados: {total_count}")
        self.stdout.write(f"Criterios:")
        self.stdout.write(
            f'  - Más antiguos que: {cutoff_date.strftime("%Y-%m-%d %H:%M:%S")}'
        )
        if inactive_only:
            self.stdout.write(f"  - Solo inactivos: Sí")
        if tenant_id:
            self.stdout.write(f"  - Tenant ID: {tenant_id}")
        self.stdout.write(
            f'  - Eliminación física: {"Sí" if hard_delete else "No (soft delete)"}'
        )

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    "\n=== MODO DRY-RUN: No se realizarán cambios reales ===\n"
                )
            )

            # Mostrar muestra de documentos
            sample_docs = documents_to_delete[:10]
            for doc in sample_docs:
                self.stdout.write(
                    f'  - {doc.title} ({doc.tenant.name}) - {doc.created_at.strftime("%Y-%m-%d")}'
                )

            if total_count > 10:
                self.stdout.write(f"  ... y {total_count - 10} más")

            return

        # Confirmar eliminación
        if not self._confirm_deletion(total_count, hard_delete):
            self.stdout.write(self.style.WARNING("Operación cancelada."))
            return

        # Realizar eliminación
        deleted_count = 0
        error_count = 0

        for document in documents_to_delete:
            try:
                if hard_delete:
                    # Eliminar archivo físico
                    if document.file and os.path.exists(document.file.path):
                        os.remove(document.file.path)
                        self.stdout.write(f"Archivo eliminado: {document.file.path}")

                    # Eliminar registro
                    document.delete()
                    deleted_count += 1
                else:
                    # Soft delete
                    document.is_active = False
                    document.save()
                    deleted_count += 1

            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(
                        f"Error eliminando documento {document.id}: {str(e)}"
                    )
                )

        # Mostrar resultados
        if deleted_count > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Eliminados exitosamente: {deleted_count} documentos"
                )
            )

        if error_count > 0:
            self.stdout.write(self.style.ERROR(f"Errores encontrados: {error_count}"))

        # Limpiar directorios vacíos si es hard delete
        if hard_delete:
            self._cleanup_empty_directories()

    def _confirm_deletion(self, count, hard_delete):
        """Confirmar la eliminación con el usuario"""
        delete_type = "físicamente" if hard_delete else "lógicamente (soft delete)"

        self.stdout.write(
            self.style.WARNING(
                f"\n¿Está seguro de que desea eliminar {delete_type} {count} documento(s)?"
            )
        )

        while True:
            response = input(
                'Escriba "yes" para confirmar, "no" para cancelar: '
            ).lower()
            if response in ["yes", "y", "sí", "si"]:
                return True
            elif response in ["no", "n"]:
                return False
            else:
                self.stdout.write('Por favor, escriba "yes" o "no".')

    def _cleanup_empty_directories(self):
        """Limpiar directorios vacíos después de eliminación física"""
        try:
            from django.conf import settings

            media_root = settings.MEDIA_ROOT
            documents_path = os.path.join(media_root, "documents")

            if not os.path.exists(documents_path):
                return

            # Recorrer directorios y eliminar los vacíos
            for root, dirs, files in os.walk(documents_path, topdown=False):
                for directory in dirs:
                    dir_path = os.path.join(root, directory)
                    try:
                        if not os.listdir(dir_path):  # Directorio vacío
                            os.rmdir(dir_path)
                            self.stdout.write(f"Directorio vacío eliminado: {dir_path}")
                    except OSError:
                        pass  # Directorio no vacío o error de permisos

        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f"Error limpiando directorios vacíos: {str(e)}")
            )
