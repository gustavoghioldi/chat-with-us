from agents.models import AgentModel
from tools.kit.api_call_toolkit import RequestToolkit


class ToolkitService:
    def __init__(self, agent: str):
        self.agent_model = AgentModel.objects.get(name=agent)

    def get_toolkit(self):
        """Obtener las herramientas del toolkit del agente."""
        api_tools = self.agent_model.api_call_models.all()
        tools = []
        for api_tool in api_tools:
            tool = RequestToolkit(
                name=api_tool.name,
                url=api_tool.url,
                instructions=api_tool.instructions,
            )
            tools.append(tool)
        return tools
