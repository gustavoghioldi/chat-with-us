from django.core.cache import cache
from django.db.models.signals import post_save
from django.dispatch import receiver

from agents.models import AgentModel


class AgentCacheService:
    CACHE_KEY_PREFIX = "agent_model_"
    CACHE_TIMEOUT = 3600  # 1 hora

    @classmethod
    def get_cache_key(cls, agent_name: str) -> str:
        """Genera la clave de caché para un agente."""
        return f"{cls.CACHE_KEY_PREFIX}{agent_name}"

    @classmethod
    def get_agent(cls, agent_name: str) -> AgentModel:
        """
        Obtiene un agente del caché o de la base de datos.
        Si no está en caché, lo busca en la base de datos y lo guarda en caché.
        """
        cache_key = cls.get_cache_key(agent_name)
        agent = cache.get(cache_key)

        if agent is None:
            try:
                agent = AgentModel.objects.select_related("tenant").get(name=agent_name)
                cache.set(cache_key, agent, cls.CACHE_TIMEOUT)
            except AgentModel.DoesNotExist:
                return None

        return agent

    @classmethod
    def invalidate_agent_cache(cls, agent: AgentModel) -> None:
        """Invalida el caché para un agente específico."""
        cache_key = cls.get_cache_key(agent.name)
        cache.delete(cache_key)


@receiver(post_save, sender=AgentModel)
def invalidate_agent_cache_on_save(sender, instance, **kwargs):
    """Signal para invalidar el caché cuando se guarda un agente."""
    AgentCacheService.invalidate_agent_cache(instance)
