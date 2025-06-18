from tools.kit.obtener_datos_de_factura import obtener_datos_de_factura


class ToolkitService:
    @staticmethod
    def get_toolkits(tools: list[str] = None):
        # Diccionario completo de herramientas disponibles
        available_tools = {
            "obtener_datos_de_factura": {
                "function": obtener_datos_de_factura,
                "description": "Obtiene los datos de una factura a partir de su URL.",
            }
        }

        # Si no se especifican tools, devolver todas las herramientas
        if tools is None:
            return available_tools

        # Filtrar solo las herramientas solicitadas
        filtered_tools = {}
        for tool_name in tools:
            if tool_name in available_tools:
                filtered_tools[tool_name] = available_tools[tool_name]["function"]

        return filtered_tools
