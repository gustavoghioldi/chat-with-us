import csv
import io

from rest_framework import serializers

from main.settings import KNOWKEDGE_CSV_MAX_ROWS


class KnowledgeCSVSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    content = serializers.CharField(
        required=True,
        allow_blank=False,
        help_text="Contenido del CSV como texto plano, con formato CSV válido.",
    )

    def validate_content(self, value):
        """Validar que el contenido tenga formato CSV válido."""
        try:
            # Crear un StringIO para simular un archivo
            csv_file = io.StringIO(value)

            # Intentar leer el CSV
            reader = csv.reader(csv_file)
            rows = list(reader)

            # Validaciones adicionales
            if not rows:
                raise serializers.ValidationError(
                    "El archivo CSV no puede estar vacío."
                )

            # Verificar que todas las filas tengan el mismo número de columnas
            if len(rows) > 1:
                header_columns = len(rows[0])
                for i, row in enumerate(rows[1:], start=2):
                    if len(row) != header_columns:
                        raise serializers.ValidationError(
                            f"La fila {i} tiene {len(row)} columnas, pero se esperaban {header_columns} "
                            f"columnas (basado en el encabezado)."
                        )

            # Verificar que el encabezado no tenga columnas vacías
            if rows and any(not column.strip() for column in rows[0]):
                raise serializers.ValidationError(
                    "El encabezado del CSV no puede contener columnas vacías."
                )

            # Limitar el número de filas para evitar archivos excesivamente grandes
            max_rows = KNOWKEDGE_CSV_MAX_ROWS
            if len(rows) > max_rows:
                raise serializers.ValidationError(
                    f"El CSV no puede tener más de {max_rows:,} filas. "
                    f"Actualmente tiene {len(rows):,} filas."
                )

            return value

        except csv.Error as e:
            raise serializers.ValidationError(f"Formato CSV inválido: {str(e)}")
        except Exception as e:
            raise serializers.ValidationError(f"Error al procesar el CSV: {str(e)}")
