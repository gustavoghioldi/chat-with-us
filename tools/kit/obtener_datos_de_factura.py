from agno.agent import Agent
from agno.media import Image
from agno.models.ollama import Ollama
from agno.tools import tool

from tools.dtos.invoices_dto import FacturaDTO


@tool(
    name="obtener_datos_de_factura",  # Custom name for the tool (otherwise the function name is used)
    description="Obtine los datos de una factura",  # Custom description (otherwise the function docstring is used)
    show_result=True,  # Show result after function call
    stop_after_tool_call=True,  # Return the result immediately after the tool call and stop the agent
    cache_results=True,  # Enable caching of results
    cache_dir="/tmp/agno_cache",  # Custom cache directory
    cache_ttl=3600,  # Cache TTL in seconds (1 hour)
)
def obtener_datos_de_factura(url_de_factura) -> FacturaDTO:
    agent = Agent(
        model=Ollama(id="gemma3:12b"),
        response_model=FacturaDTO,
    )
    result = agent.run(
        "analisas esta factura? quiero un detalle de los productos, precios y totales. Segun el formato de la factura.",
        images=[Image(url=url_de_factura)],
    )
    return result.content.dict()
