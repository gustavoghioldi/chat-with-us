"""
Servicio para formateo de contenido a Markdown.
Convierte datos JSON y CSV a formato Markdown estructurado.
"""

import csv
import io
import json


class ContentFormatterService:
    """Servicio para formatear contenido en diferentes formatos a Markdown."""

    @staticmethod
    def json_to_markdown(json_data, title):
        """Convertir datos JSON a formato Markdown."""
        markdown = f"# {title}\n\n"
        markdown += "## Datos JSON\n\n"

        if isinstance(json_data, list):
            if json_data and isinstance(json_data[0], dict):
                # Si es una lista de objetos, crear formato con IDs autogenerados
                markdown += ContentFormatterService._json_list_to_formatted_sections(
                    json_data
                )
            else:
                # Si es una lista simple, crear lista con viñetas
                markdown += "### Lista de elementos:\n\n"
                for i, item in enumerate(json_data, 1):
                    markdown += f"{i}. {item}\n"
        elif isinstance(json_data, dict):
            # Si es un objeto, crear sección estructurada con ID
            markdown += f"### ID:1\n"
            for key, value in json_data.items():
                markdown += f"- {key}: {value}\n"
            markdown += "\n"
        else:
            # Si es un valor simple
            markdown += f"**Valor:** {json_data}\n"

        markdown += f"\n---\n\n### Datos originales en JSON:\n\n```json\n{json.dumps(json_data, indent=2, ensure_ascii=False)}\n```\n"

        return markdown

    @staticmethod
    def _json_list_to_formatted_sections(json_list):
        """Convertir lista de objetos JSON a formato con IDs autogenerados."""
        markdown = ""

        for i, item in enumerate(json_list, 1):
            if isinstance(item, dict):
                # Buscar si el objeto ya tiene un campo 'id' o 'ID'
                item_id = item.get("id") or item.get("ID") or i

                markdown += f"### ID:{item_id}\n"

                # Agregar cada campo como item de lista
                for key, value in item.items():
                    # Omitir el campo id/ID si ya lo usamos
                    if key.lower() != "id":
                        markdown += f"- {key}: {value}\n"

                markdown += "\n"

        return markdown

    @staticmethod
    def csv_to_markdown(csv_content, title):
        """Convertir contenido CSV a formato Markdown."""
        markdown = f"# {title}\n\n"
        markdown += "## Datos CSV\n\n"

        try:
            # Parsear el CSV
            csv_file = io.StringIO(csv_content)
            reader = csv.reader(csv_file)
            rows = list(reader)

            if not rows:
                return markdown + "No hay datos para mostrar.\n"

            headers = rows[0]
            data_rows = rows[1:]

            # Crear formato con IDs autogenerados para cada fila
            for i, row in enumerate(data_rows, 1):
                # Buscar si hay una columna 'id' o 'ID' en los headers
                id_value = i  # Por defecto usar el índice

                # Verificar si existe columna ID
                id_column_index = None
                for idx, header in enumerate(headers):
                    if header.lower() == "id":
                        id_column_index = idx
                        break

                if id_column_index is not None and len(row) > id_column_index:
                    id_value = row[id_column_index] or i

                markdown += f"### ID:{id_value}\n"

                # Agregar cada campo como item de lista
                for j, (header, cell) in enumerate(zip(headers, row)):
                    # Omitir la columna ID si ya la usamos
                    if j != id_column_index:
                        # Asegurar que tenemos valor para la celda
                        cell_value = cell if j < len(row) else ""
                        markdown += f"- {header}: {cell_value}\n"

                markdown += "\n"

            # Agregar estadísticas
            markdown += f"### Estadísticas\n\n"
            markdown += f"- **Total de filas:** {len(data_rows)}\n"
            markdown += f"- **Total de columnas:** {len(headers)}\n"
            markdown += f"- **Columnas:** {', '.join(headers)}\n\n"

            # Agregar datos originales
            markdown += (
                f"---\n\n### Datos originales en CSV:\n\n```csv\n{csv_content}\n```\n"
            )

        except Exception as e:
            markdown += f"Error al procesar CSV: {str(e)}\n\n"
            markdown += f"### Contenido original:\n\n```\n{csv_content}\n```\n"

        return markdown

    @staticmethod
    def json_list_to_table(json_list):
        """Convertir lista de objetos JSON a tabla Markdown (método auxiliar)."""
        if not json_list or not isinstance(json_list[0], dict):
            return ""

        # Obtener todas las claves únicas
        all_keys = set()
        for item in json_list:
            if isinstance(item, dict):
                all_keys.update(item.keys())

        headers = sorted(list(all_keys))

        # Crear encabezado de tabla
        table = "| " + " | ".join(headers) + " |\n"
        table += "|" + "|".join([" --- " for _ in headers]) + "|\n"

        # Agregar filas
        for item in json_list:
            if isinstance(item, dict):
                row_values = []
                for header in headers:
                    value = item.get(header, "")
                    # Escapar caracteres especiales de Markdown
                    str_value = str(value).replace("|", "\\|").replace("\n", " ")
                    row_values.append(str_value)
                table += "| " + " | ".join(row_values) + " |\n"

        return table + "\n"

    @staticmethod
    def json_object_to_markdown(json_object, level=3):
        """Convertir objeto JSON a secciones Markdown (método auxiliar)."""
        markdown = ""

        for key, value in json_object.items():
            markdown += f"{'#' * level} {key}\n\n"

            if isinstance(value, dict):
                markdown += ContentFormatterService.json_object_to_markdown(
                    value, level + 1
                )
            elif isinstance(value, list):
                if value and isinstance(value[0], dict):
                    markdown += ContentFormatterService.json_list_to_table(value)
                else:
                    for i, item in enumerate(value, 1):
                        markdown += f"{i}. {item}\n"
                    markdown += "\n"
            else:
                markdown += f"**{value}**\n\n"

        return markdown
