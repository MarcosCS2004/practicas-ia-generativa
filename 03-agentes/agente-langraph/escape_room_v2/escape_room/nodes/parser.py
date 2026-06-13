"""
escape_room/nodes/parser.py
============================
Nodo 1: PARSER — Analizador de Intención del Jugador.

Responsabilidad única:
  Leer el último mensaje del jugador y clasificarlo como:
    - "interaction": el jugador quiere TOCAR, USAR, COGER o ACTIVAR un objeto.
    - "observation": el jugador MIRA, EXAMINA o habla sin interactuar físicamente.

El resultado se guarda en state["action_type"] y es consumido por el enrutador
condicional para decidir si el flujo pasa por el PuzzleEngine o va directo
al RoomMaster.

Protección de estado: este nodo SOLO escribe `action_type`.
"""

from langchain_core.messages import HumanMessage, SystemMessage

from escape_room.state import AgentState
from escape_room.llm import get_llm


# ── Prompt del sistema del Parser ────────────────────────────────────────────
# Está aislado aquí para facilitar ajustes sin tocar la lógica del nodo.
_SYSTEM_PROMPT = """Eres el analizador de intenciones de un juego de Escape Room.
Tu única tarea es clasificar la acción del jugador en UNA de estas dos categorías:

- "interaction": El jugador intenta USAR, COGER, ACTIVAR, INSERTAR, CONECTAR o MOVER un objeto físico.
  Ejemplos: "cojo el cable", "uso el cable en el panel", "abro la puerta", "activo el panel"

- "observation": El jugador MIRA, EXAMINA, LEE, PREGUNTA o simplemente habla sin tocar nada.
  Ejemplos: "miro alrededor", "qué hay en la sala", "examino el panel", "dónde estoy"

Responde ÚNICAMENTE con una de estas dos palabras exactas: interaction  o  observation
No añadas nada más. Solo la palabra."""


def _get_last_human_message(state: AgentState) -> str:
    """Extrae el texto del último mensaje enviado por el jugador."""
    for msg in reversed(state["messages"]):
        if isinstance(msg, HumanMessage):
            return msg.content
    return ""


def parser_node(state: AgentState) -> dict:
    """
    Nodo Parser del grafo.

    Flujo:
      1. Extrae el último mensaje del jugador.
      2. Invoca el LLM con un prompt de clasificación binaria.
      3. Normaliza la respuesta a "interaction" o "observation".
      4. Devuelve solo el campo action_type al estado.

    Args:
        state: Estado actual del grafo (solo se lee `messages`).

    Returns:
        dict con la clave `action_type` actualizada.
    """
    llm = get_llm()
    last_message = _get_last_human_message(state)

    response = llm.invoke([
        SystemMessage(content=_SYSTEM_PROMPT),
        HumanMessage(content=f"Acción del jugador: {last_message}"),
    ])

    raw = response.content.strip().lower()
    action_type = "interaction" if "interaction" in raw else "observation"

    print(f"\n[PARSER] '{action_type}' ← '{last_message}'")

    return {"action_type": action_type}
