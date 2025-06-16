import json
from typing import Any, Dict, Optional

from agno.tools import Toolkit

try:
    import requests
    from requests.auth import HTTPBasicAuth
except ImportError:
    raise ImportError(
        "`requests` not installed. Please install using `pip install requests`"
    )


class RequestToolkit(Toolkit):
    """
    Toolkit para realizar llamadas HTTP GET a APIs externas.
    Específicamente configurado para llamar a MockAPI users endpoint.
    """

    def __init__(self, name, url, instructions: Optional[str] = None):
        super().__init__(name="request_toolkit")
        self.url = url
        self.name = name
        # Registrar las herramientas disponibles
        self.instructions = instructions
        self.add_instructions = True if instructions is None else False
        self.register(self.get_by_id)
        self.register(self.get)

    def get_by_id(self) -> Dict[str, Any]:
        """
        Obtiene la lista completa de usuarios desde la API MockAPI.

        Returns:
            Dict con la respuesta de la API o información del error
        """
        try:
            response = requests.get(self.url, timeout=10)
            response.raise_for_status()  # Lanza excepción si hay error HTTP

            return {
                "success": True,
                "status_code": response.status_code,
                "data": response.json(),
                "message": f"Se obtuvieron {len(response.json())} usuarios exitosamente",
            }

        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Error al realizar la llamada a la API",
            }
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": "Respuesta no válida de la API",
                "message": "La API no devolvió un JSON válido",
            }

    def get(self, user_id: str) -> Dict[str, Any]:
        """
        Obtiene un usuario específico por su ID desde la API MockAPI.

        Args:
            user_id: ID del usuario a obtener

        Returns:
            Dict con la respuesta de la API o información del error
        """
        try:
            url = f"{self.url}/{user_id}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            return {
                "success": True,
                "status_code": response.status_code,
                "data": response.json(),
                "message": f"Usuario {user_id} obtenido exitosamente",
            }

        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Error al obtener el usuario {user_id}",
            }
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": "Respuesta no válida de la API",
                "message": "La API no devolvió un JSON válido",
            }
