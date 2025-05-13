from agno.storage.postgres import PostgresStorage

class AgentSessionService: 
    def __init__(self, *args, **kwargs):
        db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"

    # Get existing session if user doesn't want a new one
        self.__agent_storage = PostgresStorage(
        table_name="ai_sessions",
        db_url=db_url
    )
        
    def get_storage(self):
        return self.__agent_storage
    