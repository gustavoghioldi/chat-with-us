from agno.agent import Agent
from agno.media import Image
from agno.models.ollama import Ollama

agent = Agent(
    model=Ollama(id="gemma3:12b"),
    markdown=True,
)

agent.print_response(
    "que dia vence la factura? ",
    images=[Image(filepath="/Users/gustavo.ghioldi/barba/chat-with-us/doc/image.png")],
)
