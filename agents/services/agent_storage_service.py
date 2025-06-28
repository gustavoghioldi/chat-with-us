from agents.services.storage_factory import StorageServiceFactory


class AgentSessionService:
    """
    Servicio para gestionar el almacenamiento de sesiones de agentes.

    Utiliza StorageServiceFactory para crear servicios de almacenamiento configurables.
    """

    def __init__(self, storage_type: str = "postgres", storage_config: dict = None):
        """
        Inicializa el servicio de sesiones con el tipo de almacenamiento especificado.

        Args:
            storage_type: Tipo de almacenamiento ('postgres', 'redis', 'memory')
            storage_config: Configuración específica para el almacenamiento
        """
        # Configuración por defecto si no se proporciona
        if storage_config is None:
            storage_config = self._get_default_config(storage_type)

        # Crear servicio de almacenamiento usando el factory
        self.__storage_service = StorageServiceFactory.create_storage_service(
            storage_type=storage_type, config=storage_config
        )

    def _get_default_config(self, storage_type: str) -> dict:
        """
        Obtiene la configuración por defecto según el tipo de almacenamiento.

        Args:
            storage_type: Tipo de almacenamiento

        Returns:
            dict: Configuración por defecto
        """
        default_configs = {
            "postgres": {
                "db_url": "postgresql+psycopg://ai:ai@localhost:5532/ai",
                "table_name": "ai_sessions",
            },
            "redis": {"redis_url": "redis://localhost:6379/0"},
            "memory": {},
        }

        return default_configs.get(storage_type, {})

    def get_storage(self):
        """
        Obtiene la instancia de almacenamiento configurada.

        Returns:
            Storage: Instancia de almacenamiento
        """
        return self.__storage_service.get_storage()
