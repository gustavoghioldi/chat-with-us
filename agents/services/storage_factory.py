"""
Factory para crear servicios de almacenamiento de sesiones de agentes.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Type


class BaseStorageService(ABC):
    """Clase base abstracta para servicios de almacenamiento"""

    @abstractmethod
    def get_storage(self):
        """
        Retorna una instancia de almacenamiento configurada.

        Returns:
            Storage: Instancia de almacenamiento
        """
        pass


class StorageServiceFactory:
    """Factory para crear servicios de almacenamiento"""

    # Mapeo de tipos de almacenamiento a servicios
    _storage_services = {}

    @classmethod
    def register_storage_service(
        cls, storage_type: str, service_class: Type[BaseStorageService]
    ):
        """
        Registra un servicio de almacenamiento.

        Args:
            storage_type: Tipo de almacenamiento (ej: 'postgres', 'redis', 'memory')
            service_class: Clase del servicio de almacenamiento

        Raises:
            ValueError: Si la clase no hereda de BaseStorageService
        """
        if not issubclass(service_class, BaseStorageService):
            raise ValueError("El servicio debe heredar de BaseStorageService")

        cls._storage_services[storage_type] = service_class

    @classmethod
    def create_storage_service(
        cls, storage_type: str, config: Dict[str, Any] = None
    ) -> BaseStorageService:
        """
        Crea un servicio de almacenamiento del tipo especificado.

        Args:
            storage_type: Tipo de almacenamiento
            config: Configuración opcional para el servicio

        Returns:
            BaseStorageService: Servicio de almacenamiento configurado

        Raises:
            ValueError: Si el tipo de almacenamiento no es soportado
        """
        service_class = cls._storage_services.get(storage_type)

        if not service_class:
            supported_types = ", ".join(cls._storage_services.keys())
            raise ValueError(
                f"Tipo de almacenamiento '{storage_type}' no soportado. "
                f"Tipos soportados: {supported_types}"
            )

        # Crear instancia con configuración si se proporciona
        if config:
            return service_class(**config)
        else:
            return service_class()

    @classmethod
    def get_supported_storage_types(cls) -> list:
        """
        Retorna la lista de tipos de almacenamiento soportados.

        Returns:
            list: Lista de tipos soportados
        """
        return list(cls._storage_services.keys())


# Implementaciones concretas de servicios de almacenamiento
class PostgresStorageService(BaseStorageService):
    """Servicio de almacenamiento usando PostgreSQL"""

    def __init__(self, db_url: str = None, table_name: str = "ai_sessions"):
        self.db_url = db_url or "postgresql+psycopg://ai:ai@localhost:5532/ai"
        self.table_name = table_name

    def get_storage(self):
        from agno.storage.postgres import PostgresStorage

        return PostgresStorage(table_name=self.table_name, db_url=self.db_url)


class MemoryStorageService(BaseStorageService):
    """Servicio de almacenamiento en memoria (para desarrollo/testing)"""

    def __init__(self):
        self._storage = None

    def get_storage(self):
        # Implementación simple en memoria
        if not self._storage:
            # Asumiendo que existe una clase MemoryStorage en agno
            try:
                from agno.storage.memory import MemoryStorage

                self._storage = MemoryStorage()
            except ImportError:
                # Fallback a una implementación simple
                self._storage = {}
        return self._storage


class RedisStorageService(BaseStorageService):
    """Servicio de almacenamiento usando Redis"""

    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.redis_url = redis_url

    def get_storage(self):
        try:
            from agno.storage.redis import RedisStorage

            return RedisStorage(url=self.redis_url)
        except ImportError:
            raise ImportError(
                "RedisStorage no está disponible. "
                "Instale las dependencias de Redis o use otro tipo de almacenamiento."
            )


# Auto-registro de servicios por defecto
def _register_default_storage_services():
    """Registra los servicios de almacenamiento por defecto"""
    try:
        StorageServiceFactory.register_storage_service(
            "postgres", PostgresStorageService
        )
        StorageServiceFactory.register_storage_service("memory", MemoryStorageService)
        StorageServiceFactory.register_storage_service("redis", RedisStorageService)
    except Exception as e:
        print(f"⚠️ Error registrando servicios de almacenamiento: {e}")


# Registrar servicios por defecto al importar el módulo
_register_default_storage_services()
