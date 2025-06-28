from tools.services.toolkit_factory import ToolkitFactory


class ToolkitService:
    """
    Servicio principal para gestionar herramientas de agentes.

    Utiliza ToolkitFactory para obtener herramientas registradas de manera dinámica.
    """

    @staticmethod
    def get_toolkits(tools: list[str] = None):
        """
        Obtiene herramientas usando el factory pattern.

        Args:
            tools: Lista de nombres de herramientas. Si es None, retorna todas.

        Returns:
            dict: Diccionario con herramientas solicitadas
        """
        return ToolkitFactory.get_tools(tools)

    @staticmethod
    def get_available_tools():
        """
        Obtiene información completa de todas las herramientas disponibles.

        Returns:
            dict: Información completa de herramientas con descripción y categoría
        """
        return ToolkitFactory.get_available_tools()

    @staticmethod
    def get_tools_by_category(category: str):
        """
        Obtiene herramientas de una categoría específica.

        Args:
            category: Nombre de la categoría

        Returns:
            dict: Herramientas de la categoría especificada
        """
        return ToolkitFactory.get_tools_by_category(category)
