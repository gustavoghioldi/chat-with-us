from agno.agent import Agent, RunResponse
from agno.models.ollama import Ollama
from agno.utils.pprint import pprint_run_response


class MathWorkflow:
    """
    Workflow que procesa un número a través de tres agentes secuencialmente:
    1. Suma 1
    2. Divide por 2
    3. Multiplica por 3
    """

    def __init__(self):
        """Inicializar el workflow y sus agentes."""

        # Agente 1: Suma 1
        self.suma_agent = Agent(
            name="Agente Suma",
            model=Ollama(id="gemma3:12b"),
            description="Agente que suma 1 a un número",
            instructions=[
                "Recibirás un número.",
                "Tu tarea es sumar 1 a ese número.",
                "Responde ÚNICAMENTE con el resultado numérico, sin explicaciones adicionales.",
                "Ejemplo: si recibes 5, responde 6",
            ],
        )

        # Agente 2: Divide por 2
        self.division_agent = Agent(
            name="Agente División",
            model=Ollama(id="gemma3:12b"),
            description="Agente que divide un número por 2",
            instructions=[
                "Recibirás un número.",
                "Tu tarea es dividir ese número por 2.",
                "Responde ÚNICAMENTE con el resultado numérico, sin explicaciones adicionales.",
                "Si el resultado es decimal, manténlo como decimal.",
                "Ejemplo: si recibes 6, responde 3",
            ],
        )

        # Agente 3: Multiplica por 3
        self.multiplicacion_agent = Agent(
            name="Agente Multiplicación",
            model=Ollama(id="gemma3:12b"),
            description="Agente que multiplica un número por 3",
            instructions=[
                "Recibirás un número.",
                "Tu tarea es multiplicar ese número por 3.",
                "Responde ÚNICAMENTE con el resultado numérico, sin explicaciones adicionales.",
                "Ejemplo: si recibes 3, responde 9",
            ],
        )

    def run(self, numero: float) -> RunResponse:
        """
        Ejecuta el workflow secuencial en modo batch.

        Args:
            numero: El número inicial a procesar

        Returns:
            RunResponse: El resultado final después de todas las operaciones
        """
        import uuid

        # Generar un run_id único para este workflow
        run_id = str(uuid.uuid4())

        # Paso 1: Suma 1
        print(f"🔢 Número inicial: {numero}")
        resultado_suma: RunResponse = self.suma_agent.run(
            f"Suma 1 a este número: {numero}"
        )
        numero_paso1 = float(resultado_suma.content.strip())
        print(f"➕ Después de sumar 1: {numero_paso1}")

        # Paso 2: Divide por 2
        resultado_division: RunResponse = self.division_agent.run(
            f"Divide este número por 2: {numero_paso1}"
        )
        numero_paso2 = float(resultado_division.content.strip())
        print(f"➗ Después de dividir por 2: {numero_paso2}")

        # Paso 3: Multiplica por 3
        resultado_multiplicacion: RunResponse = self.multiplicacion_agent.run(
            f"Multiplica este número por 3: {numero_paso2}"
        )
        numero_final = float(resultado_multiplicacion.content.strip())
        print(f"✖️ Después de multiplicar por 3: {numero_final}")

        # Crear el resultado final consolidado
        resultado_final = RunResponse(
            run_id=run_id,
            content=f"""
## Resultado del Workflow Matemático

**Número inicial:** {numero}

### Proceso paso a paso:
1. **Suma 1:** {numero} + 1 = {numero_paso1}
2. **Divide por 2:** {numero_paso1} ÷ 2 = {numero_paso2}
3. **Multiplica por 3:** {numero_paso2} × 3 = {numero_final}

### 🎯 **Resultado final: {numero_final}**

*Fórmula aplicada: ((x + 1) ÷ 2) × 3*
            """.strip(),
        )

        return resultado_final


if __name__ == "__main__":
    # Crear instancia del workflow
    workflow = MathWorkflow()

    # Número de ejemplo
    numero_inicial = 10

    print("🚀 Iniciando Workflow Matemático Secuencial")
    print("=" * 50)

    # Ejecutar el workflow en modo batch (resultado único)
    resultado: RunResponse = workflow.run(numero_inicial)

    print("\n" + "=" * 50)
    print("📋 RESULTADO FINAL:")
    print("=" * 50)

    # Mostrar el resultado final
    pprint_run_response(resultado, markdown=True, show_time=True)
