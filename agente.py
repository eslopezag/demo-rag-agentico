"""El agente: un modelo de OpenRouter, tres herramientas y memoria por conversación.

ARCHIVO INCOMPLETO: cada bloque marcado con TODO se escribe durante la
sesión, en el orden en que están. Las instrucciones están en el README, en
la sección "Llenar el código que falta" (paso 3).

    uv run python -i agente.py       # abre el bucle de prueba del final
"""
import os
from datetime import date

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_openrouter import ChatOpenRouter
from langgraph.checkpoint.memory import InMemorySaver

from catalogo import buscar_productos
from pedidos import Contexto, cancelar_pedido, consultar_pedidos

load_dotenv()

# 1. El modelo de chat
# TODO: crear `modelo` con ChatOpenRouter. El nombre del modelo sale de la
#       variable de entorno MODELO, con anthropic/claude-haiku-4.5 por defecto,
#       y temperature=0 para que las respuestas sean estables.

# 2. Las instrucciones del sistema, que el agente recibe en cada turno. Vienen
#    escritas para leerlas y comentarlas, en vez de teclearlas en vivo. Fíjense
#    en la fecha (el modelo no sabe qué día es), en las tres tareas con el
#    nombre de su herramienta, y en las reglas que evitan que invente productos
#    o cancele sin confirmar.
INSTRUCCIONES = f"""Eres el asistente de compras de Tienda Cóndor, un comercio electrónico
colombiano. Hoy es {date.today()}.

Ayudas a los clientes a:
- encontrar productos del catálogo, con la herramienta buscar_productos;
- consultar sus pedidos, con consultar_pedidos;
- cancelar pedidos que no han salido de la bodega, con cancelar_pedido.

Reglas:
- Recomienda sólo productos que hayas encontrado con buscar_productos. No inventes
  productos, precios ni pedidos.
- Si una búsqueda no trae nada útil, prueba otra consulta u otros filtros antes de rendirte.
- Antes de cancelar, confirma con el cliente el número del pedido y el producto.
- Escribe los precios en pesos colombianos, con puntos de miles: $129.900.
- Responde en español, en pocas líneas y con tono cordial."""

# 3. El agente
# TODO: crear `agente` con create_agent(...), pasándole el modelo, la lista de
#       las tres herramientas, system_prompt=INSTRUCCIONES,
#       context_schema=Contexto (el cliente de la sesión, que el modelo no
#       controla) y checkpointer=InMemorySaver() para la memoria del hilo.

if __name__ == "__main__":
    config = {"configurable": {"thread_id": "prueba"}}
    contexto = Contexto(usuario_id=1)
    while (pregunta := input("Tú: ")) != "salir":
        respuesta = agente.invoke(
            {"messages": [{"role": "user", "content": pregunta}]}, config, context=contexto)
        print("Agente:", respuesta["messages"][-1].content)
