"""
escape_room/nodes/puzzle_engine.py
====================================
Nodo 2: PUZZLE ENGINE — Motor Determinista de Puzles.

Responsabilidad única:
  Evaluar la acción del jugador mediante REGLAS CODIFICADAS (sin LLM),
  actualizar el estado de la sala y el inventario, y producir un
  feedback_msg preciso para el RoomMaster.

Principio de diseño clave (anti-alucinación):
  Este nodo NO usa el LLM. Toda la lógica es código Python puro.
  Esto garantiza que los cambios de estado sean 100% deterministas
  y que el RoomMaster nunca narre algo que no haya ocurrido realmente.

Permisos de escritura: `inventory`, `room_state`, `feedback_msg`.
Permisos de lectura:   `messages`, `inventory`, `room_state`.
"""

from langchain_core.messages import HumanMessage
from escape_room.state import AgentState


# ── Tipo para una regla de puzle ─────────────────────────────────────────────
# Cada regla es un dict con:
#   keywords     — palabras clave que activan la regla
#   condition_fn — función que evalúa si la acción es posible dado el estado
#   effect_fn    — función que aplica el efecto sobre inventory y room_state
#   success_msg  — feedback si la condición se cumple
#   failure_msg  — feedback si la condición NO se cumple (función para más contexto)


def _get_last_human_message(state: AgentState) -> str:
    """Extrae el texto del último mensaje del jugador en minúsculas."""
    for msg in reversed(state["messages"]):
        if isinstance(msg, HumanMessage):
            return msg.content.lower()
    return ""


# ── Reglas del escenario "Celda Espacial" ────────────────────────────────────
# Cada función _rule_* devuelve (inventory, room_state, feedback) tras evaluar la acción.
# El orden importa: las reglas más específicas deben ir antes de las genéricas.

def _rule_recoger_cable(
    action: str,
    inventory: list[str],
    room_state: dict[str, bool],
) -> tuple[list[str], dict[str, bool], str] | None:
    """Regla 1: Recoger el cable suelto del suelo."""
    keywords = ["cojo", "coge", "recojo", "tomo", "agarro", "coger", "cable"]
    if not any(kw in action for kw in keywords):
        return None  # Esta regla no aplica

    if not room_state["cable_recogido"]:
        new_inventory = inventory + ["cable_suelto"]
        new_state = {**room_state, "cable_recogido": True}
        feedback = (
            "ÉXITO: El jugador recogió el cable suelto del suelo. "
            "El cable está ahora en su inventario."
        )
    else:
        new_inventory = inventory
        new_state = room_state
        feedback = "FALLO: El cable ya fue recogido anteriormente. No queda nada en el suelo."

    return new_inventory, new_state, feedback


def _rule_usar_cable_panel(
    action: str,
    inventory: list[str],
    room_state: dict[str, bool],
) -> tuple[list[str], dict[str, bool], str] | None:
    """Regla 2: Conectar el cable al panel de control para encenderlo."""
    keywords = ["uso", "usar", "conecto", "enchufo", "inserto", "panel"]
    # Excluir si la intención es claramente sobre otro objeto sin mencionar panel
    if not any(kw in action for kw in keywords):
        return None

    if "cable_suelto" in inventory and not room_state["panel_encendido"]:
        new_inventory = [item for item in inventory if item != "cable_suelto"]
        new_state = {**room_state, "panel_encendido": True}
        feedback = (
            "ÉXITO: El jugador conectó el cable al panel de control. "
            "Un zumbido eléctrico llena la sala y el panel cobra vida. "
            "El cable fue consumido en el proceso."
        )
    elif room_state["panel_encendido"]:
        new_inventory = inventory
        new_state = room_state
        feedback = "FALLO: El panel ya está encendido. No necesita más energía."
    else:
        new_inventory = inventory
        new_state = room_state
        feedback = (
            "FALLO: El jugador intentó interactuar con el panel "
            "pero no tiene el cable en su inventario. Necesita encontrarlo primero."
        )

    return new_inventory, new_state, feedback


def _rule_abrir_puerta(
    action: str,
    inventory: list[str],
    room_state: dict[str, bool],
) -> tuple[list[str], dict[str, bool], str] | None:
    """Regla 3: Abrir la puerta magnética (requiere panel encendido)."""
    keywords = ["abro", "abrir", "puerta", "salida", "interactúo"]
    if not any(kw in action for kw in keywords):
        return None

    if room_state["panel_encendido"] and not room_state["puerta_abierta"]:
        new_state = {**room_state, "puerta_abierta": True}
        feedback = (
            "ÉXITO: El panel encendido desbloqueó el sistema magnético. "
            "La puerta metálica se abre con un siseo hidráulico. "
            "El corredor oscuro al otro lado te llama."
        )
    elif not room_state["panel_encendido"]:
        new_state = room_state
        feedback = (
            "FALLO: La puerta no responde. El sistema de bloqueo magnético sigue activo. "
            "Necesitas energía en el panel de control."
        )
    else:
        new_state = room_state
        feedback = "INFO: La puerta ya está abierta. El camino hacia la libertad te espera."

    return inventory, new_state, feedback


def _rule_escapar(
    action: str,
    inventory: list[str],
    room_state: dict[str, bool],
) -> tuple[list[str], dict[str, bool], str] | None:
    """Regla 4: Salir por la puerta abierta (condición de victoria)."""
    keywords = ["salgo", "salir", "escapo", "escapar", "cruzo", "paso por"]
    if not any(kw in action for kw in keywords):
        return None

    if room_state["puerta_abierta"]:
        new_state = {**room_state, "escape_completado": True}
        feedback = "VICTORIA: ¡El jugador cruzó la puerta y escapó de la celda espacial!"
    else:
        new_state = room_state
        feedback = "FALLO: La puerta sigue cerrada. No hay por donde salir todavía."

    return inventory, new_state, feedback


# ── Lista ordenada de reglas ──────────────────────────────────────────────────
# El motor las evalúa en orden. La primera que devuelva un resultado se aplica.
_RULES = [
    _rule_escapar,       # Primero escapar (más específico)
    _rule_abrir_puerta,
    _rule_usar_cable_panel,
    _rule_recoger_cable, # Al final porque "cable" puede solaparse con otras
]


def puzzle_engine_node(state: AgentState) -> dict:
    """
    Nodo PuzzleEngine del grafo.

    Flujo:
      1. Extrae el último mensaje del jugador.
      2. Evalúa cada regla en orden hasta encontrar una que aplique.
      3. Aplica el efecto (modifica inventory y/o room_state).
      4. Genera el feedback_msg para el RoomMaster.
      5. Si ninguna regla aplica, devuelve feedback neutro.

    Args:
        state: Estado actual (lee `messages`, `inventory`, `room_state`).

    Returns:
        dict con `inventory`, `room_state` y `feedback_msg` actualizados.
    """
    action = _get_last_human_message(state)
    inventory = list(state["inventory"])
    room_state = dict(state["room_state"])
    feedback = f"INFO: La acción '{action}' no produjo ningún efecto sobre los objetos de la sala."

    for rule in _RULES:
        result = rule(action, inventory, room_state)
        if result is not None:
            inventory, room_state, feedback = result
            break

    print(f"\n[PUZZLE ENGINE] {feedback}")
    print(f"[PUZZLE ENGINE] Inventario: {inventory}")
    print(f"[PUZZLE ENGINE] Sala: {room_state}")

    return {
        "inventory": inventory,
        "room_state": room_state,
        "feedback_msg": feedback,
    }
