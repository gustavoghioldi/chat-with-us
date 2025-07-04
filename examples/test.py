from agno.agent import Agent
from agno.media import Image
from agno.models.ollama import Ollama

agent = Agent(
    model=Ollama(id="gemma3:12b"),
    markdown=True,
)

agent.run(
    "analisa esta factura? quiero un detalle de los productos, precios y totales.",
    images=[
        Image(url="https://templates.invoicehome.com/modelo-factura-es-puro-750px.png")
    ],
)
