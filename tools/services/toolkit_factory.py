"""
Factory para gestionar herramientas (tools) disponibles para los agentes.
"""

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List


class BaseTool(ABC):
    """Clase base abstracta para herramientas"""

    @property
    @abstractmethod
    def name(self) -> str:
        """Nombre único de la herramienta"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Descripción de lo que hace la herramienta"""
        pass

    @property
    @abstractmethod
    def function(self) -> Callable:
        """Función ejecutable de la herramienta"""
        pass

    @property
    def category(self) -> str:
        """Categoría de la herramienta (opcional)"""
        return "general"


class ToolkitFactory:
    """Factory para gestionar herramientas disponibles para agentes"""

    # Registro de herramientas disponibles
    _tools: Dict[str, BaseTool] = {}
    _categories: Dict[str, List[str]] = {}

    @classmethod
    def register_tool(cls, tool: BaseTool):
        """
        Registra una nueva herramienta.

        Args:
            tool: Instancia de la herramienta que hereda de BaseTool

        Raises:
            ValueError: Si la herramienta no hereda de BaseTool o el nombre ya existe
        """
        if not isinstance(tool, BaseTool):
            raise ValueError("La herramienta debe heredar de BaseTool")

        if tool.name in cls._tools:
            raise ValueError(f"La herramienta '{tool.name}' ya está registrada")

        cls._tools[tool.name] = tool

        # Organizar por categorías
        category = tool.category
        if category not in cls._categories:
            cls._categories[category] = []
        cls._categories[category].append(tool.name)

    @classmethod
    def get_tool(cls, tool_name: str) -> BaseTool:
        """
        Obtiene una herramienta por su nombre.

        Args:
            tool_name: Nombre de la herramienta

        Returns:
            BaseTool: Instancia de la herramienta

        Raises:
            ValueError: Si la herramienta no existe
        """
        tool = cls._tools.get(tool_name)
        if not tool:
            available_tools = ", ".join(cls._tools.keys())
            raise ValueError(
                f"Herramienta '{tool_name}' no encontrada. "
                f"Herramientas disponibles: {available_tools}"
            )
        return tool

    @classmethod
    def get_tools(cls, tool_names: List[str] = None) -> Dict[str, Callable]:
        """
        Obtiene múltiples herramientas como diccionario de funciones.

        Args:
            tool_names: Lista de nombres de herramientas. Si es None, retorna todas.

        Returns:
            Dict[str, Callable]: Diccionario con nombre -> función
        """
        if tool_names is None:
            return {name: tool.function for name, tool in cls._tools.items()}

        result = {}
        for tool_name in tool_names:
            try:
                tool = cls.get_tool(tool_name)
                result[tool_name] = tool.function
            except ValueError:
                # Continúa con las otras herramientas si una no existe
                print(f"⚠️ Herramienta '{tool_name}' no encontrada, se omite")
                continue

        return result

    @classmethod
    def get_tools_by_category(cls, category: str) -> Dict[str, Callable]:
        """
        Obtiene todas las herramientas de una categoría específica.

        Args:
            category: Nombre de la categoría

        Returns:
            Dict[str, Callable]: Diccionario con nombre -> función
        """
        if category not in cls._categories:
            available_categories = ", ".join(cls._categories.keys())
            raise ValueError(
                f"Categoría '{category}' no encontrada. "
                f"Categorías disponibles: {available_categories}"
            )

        tool_names = cls._categories[category]
        return cls.get_tools(tool_names)

    @classmethod
    def get_available_tools(cls) -> Dict[str, Dict[str, Any]]:
        """
        Obtiene información completa de todas las herramientas disponibles.

        Returns:
            Dict: Diccionario con información completa de cada herramienta
        """
        return {
            name: {
                "function": tool.function,
                "description": tool.description,
                "category": tool.category,
            }
            for name, tool in cls._tools.items()
        }

    @classmethod
    def get_categories(cls) -> List[str]:
        """
        Retorna la lista de categorías disponibles.

        Returns:
            list: Lista de categorías
        """
        return list(cls._categories.keys())

    @classmethod
    def get_tools_count(cls) -> int:
        """
        Retorna el número total de herramientas registradas.

        Returns:
            int: Número de herramientas
        """
        return len(cls._tools)


# Implementación concreta para herramientas existentes
class FacturaTool(BaseTool):
    """Herramienta para obtener datos de facturas"""

    @property
    def name(self) -> str:
        return "obtener_datos_de_factura"

    @property
    def description(self) -> str:
        return "Obtiene los datos de una factura a partir de su URL."

    @property
    def function(self) -> Callable:
        from tools.kit.obtener_datos_de_factura import obtener_datos_de_factura

        return obtener_datos_de_factura

    @property
    def category(self) -> str:
        return "documentos"


# Auto-registro de herramientas por defecto
def _register_default_tools():
    """Registra las herramientas por defecto"""
    try:
        ToolkitFactory.register_tool(FacturaTool())
    except Exception as e:
        print(f"⚠️ Error registrando herramientas por defecto: {e}")


# Registrar herramientas por defecto al importar el módulo
_register_default_tools()
