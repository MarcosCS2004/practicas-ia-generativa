"""
escape_room/nodes/room_master.py
==================================
Nodo 3: ROOM MASTER — Narrador Inmersivo.

Responsabilidad única:
  Leer el estado actual del grafo (room_state, inventory, feedback_msg)
  y generar una respuesta narrativa atmosférica en segunda persona.

Principio anti-alucinación:
  El prompt del sistema PROHÍBE explícitamente inventar objetos o eventos.
  El contexto de estado se serializa y se inyecta en cada llamada al LLM,
  así el modelo solo puede narrar lo que existe en el estado.

Permisos de escritura: `messages` (append), `feedback_msg` (limpia a "").
Permisos de lectura:   `room_state`, `inventory`, `feedback_msg`.
"""

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from escape_room.state import AgentState
from escape_room.llm import get_llm


# ── Prompt del sistema del RoomMaster ────────────────────────────────────────
_SYSTEM_PROMPT = """Eres el Maestro de Sala de un Escape Room espacial de ciencia ficción.
Tu rol es narrar los eventos del juego de forma inmersiva, en segunda persona, en español.

REGLAS ESTRICTAS (anti-alucinación):
1. SOLO puedes mencionar objetos que estén en INVENTARIO o cuyo estado figure en ESTADO DE SALA.
2. SOLO puedes describir consecuencias que estén literalmente en FEEDBACK_MSG.
3. NO inventes objetos, personajes, pistas ni eventos que no existan en el estado proporcionado.
4. Si el feedback empieza por "FALLO:", narra el fracaso con tensión dramática.
5. Si el feedback empieza por "ÉXITO:", narra la victoria con detalle sensorial (sonidos, luz, temperatura).
6. Si el feedback empieza por "INFO:" o no hay feedback, describe el entorno usando room_state.
7. Si el feedback empieza por "VICTORIA:", proclama el escape con narración épica y cierra el juego.
8. Tus respuestas deben tener entre 2 y 5 frases. Concisas pero evocadoras.

Al final de tu respuesta, si el juego NO ha terminado, añade esta línea exacta:
[INVENTARIO: {lista de objetos en inventario, o "vacío" si está vacío}]"""


def _build_state_context(state: AgentState) -> str:
    """
    Serializa el estado relevante del juego en texto estructurado para el LLM.

    Al pasar el estado explícitamente como contexto (no como instrucción vaga),
    se reduce drásticamente el riesgo de que el modelo alucine objetos o eventos.
    """
    room_state = state["room_state"]
    inventory = state["inventory"]
    feedback = state.get("feedback_msg", "")

    inventory_text = ", ".join(inventory) if inventory else "vacío"
    feedback_text = feedback if feedback else "El jugador observó la sala sin interactuar con ningún objeto."

    return f"""ESTADO ACTUAL DE LA SALA:
- cable_recogido   : {room_state.get('cable_recogido', False)}
- panel_encendido  : {room_state.get('panel_encendido', False)}
- puerta_abierta   : {room_state.get('puerta_abierta', False)}
- escape_completado: {room_state.get('escape_completado', False)}

INVENTARIO DEL JUGADOR: {inventory_text}

RESULTADO DE LA ÚLTIMA ACCIÓN: {feedback_text}"""


def room_master_node(state: AgentState) -> dict:
    """
    Nodo RoomMaster del grafo.

    Flujo:
      1. Serializa el estado actual como contexto para el LLM.
      2. Invoca el LLM con el sistema prompt de narración.
      3. Añade la narración como AIMessage al historial.
      4. Limpia feedback_msg (ya fue consumido en esta narración).

    Args:
        state: Estado actual (lee `room_state`, `inventory`, `feedback_msg`).

    Returns:
        dict con `messages` actualizado (append) y `feedback_msg` limpiado.
    """
    llm = get_llm()
    context = _build_state_context(state)

    response = llm.invoke([
        SystemMessage(content=_SYSTEM_PROMPT),
        HumanMessage(content=context),
    ])

    narration = response.content.strip()
    print(f"\n[ROOM MASTER] Narración generada ({len(narration)} chars).")

    return {
        "messages": [AIMessage(content=narration)],
        "feedback_msg": "",  # El feedback fue consumido — se limpia para el próximo ciclo
    }
