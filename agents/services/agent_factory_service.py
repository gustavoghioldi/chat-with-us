from typing import overload

from agno.agent import Agent
from agno.memory.v2.db.postgres import PostgresMemoryDb
from agno.memory.v2.memory import Memory
from agno.models.google import Gemini
from agno.models.ollama import Ollama
from agno.storage.postgres import PostgresStorage

from agents.models import AgentModel
from knowledge.services.document_knowledge_base_service import (
    DocumentKnowledgeBaseService,
)


class AgentFactoryService:
    """
    Factory service to create and manage agents.
    """

    def __init__(self, agent_model: AgentModel, session_id=None, user_id=None) -> None:
        self._agent_model = agent_model
        self._session_id = session_id
        self._user_id = user_id
        self._knowledges = DocumentKnowledgeBaseService(agent_model)

    def get_agent(self) -> Agent:
        if self._agent_model.tenant.model == "ollama":
            self.__model = Ollama
        if self._agent_model.tenant.model == "gemini":
            self.__model = Gemini
        return self.configure(self.__model)

    @overload
    def configure(self, model: Gemini) -> Agent: ...

    @overload
    def configure(self, model: Ollama) -> Agent: ...

    def configure(self, model) -> Agent:
        """
        Configura y retorna un agente basado en el modelo especificado.

        Args:
            model: Clase del modelo (Gemini o Ollama)

        Returns:
            Agent: Instancia configurada del agente
        """

        db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"
        memory = Memory(db=PostgresMemoryDb(table_name="agent_memory", db_url=db_url))

        # Configurar storage para sesiones
        storage = PostgresStorage(
            table_name="agent_sessions", db_url=db_url, auto_upgrade_schema=True
        )

        return Agent(
            model=model(id=self._agent_model.agent_model_id),
            description=self._agent_model.description or "Agente de IA",
            instructions=self._agent_model.instructions,
            session_id=str(self._session_id),
            user_id=str(self._user_id),
            memory=memory,
            storage=storage,
            enable_user_memories=True,  # Habilita memorias de usuario
            enable_session_summaries=True,  # Habilita resúmenes de sesión
            add_history_to_messages=True,
            num_history_runs=3,
            knowledge=self._knowledges.get_knowledge_base(),
        )
