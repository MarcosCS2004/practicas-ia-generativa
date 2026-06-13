"""
escape_room/game_loop.py
=========================
Bucle principal del juego en consola.

Responsabilidades:
  - Inicializar el estado con los valores del escenario activo.
  - Mostrar la narración inicial (primer turno sin input del jugador).
  - Leer el input del jugador e invocar el grafo en cada turno.
  - Detectar la condición de victoria y finalizar la partida.

Este módulo no contiene lógica de juego — delega todo al grafo.
Solo se encarga de la interacción con la terminal (I/O).
"""

from langchain_core.messages import HumanMessage, AIMessage

from escape_room.graph import build_graph
from escape_room.state import AgentState
from escape_room.scenario import (
    INITIAL_ROOM_STATE,
    INITIAL_INVENTORY,
    SCENARIO_DESCRIPTION,
    VICTORY_KEY,
    SUGGESTED_ACTIONS,
)


# ── Constantes de presentación ────────────────────────────────────────────────
_DIVIDER = "─" * 60
_QUIT_COMMANDS = {"salir", "exit", "quit", "q"}


def _get_last_ai_message(state: AgentState) -> str | None:
    """Devuelve el contenido del último mensaje del RoomMaster, o None si no existe."""
    for msg in reversed(state["messages"]):
        if isinstance(msg, AIMessage):
            return msg.content
    return None


def _print_narration(state: AgentState) -> None:
    """Imprime la última respuesta del RoomMaster en pantalla."""
    narration = _get_last_ai_message(state)
    if narration:
        print(f"\n🎙️  MAESTRO DE SALA:\n{narration}\n")


def _print_options() -> None:
    """Muestra las opciones de comandos sugeridos."""
    print("💡 OPCIONES:")
    for opt in SUGGESTED_ACTIONS:
        print(f"  • {opt}")
    print()


def _build_initial_state() -> AgentState:
    """Crea el estado inicial de la partida a partir del escenario cargado."""
    return {
        "messages": [],
        "inventory": list(INITIAL_INVENTORY),
        "room_state": dict(INITIAL_ROOM_STATE),
        "feedback_msg": "",
        "action_type": "observation",
    }


def run_game() -> None:
    """
    Bucle principal del juego.

    Flujo:
      1. Imprime la descripción del escenario.
      2. Invoca el grafo con "miro alrededor" para generar la narración inicial.
      3. Entra en el bucle de turnos:
           a. Lee el input del jugador.
           b. Añade el mensaje al historial de estado.
           c. Invoca el grafo.
           d. Imprime la narración resultante.
           e. Comprueba la condición de victoria.
    """
    print(SCENARIO_DESCRIPTION)

    graph = build_graph()
    state = _build_initial_state()

    # ── Turno 0: narración inicial ─────────────────────────────────────────────
    print("[Generando descripción inicial...]\n")
    initial_state = {
        **state,
        "messages": [HumanMessage(content="miro alrededor por primera vez")],
    }
    state = graph.invoke(initial_state)
    _print_narration(state)
    _print_options()
    print(_DIVIDER)

    # ── Bucle de turnos ────────────────────────────────────────────────────────
    while True:
        # Comprobar victoria antes de pedir input
        if state["room_state"].get(VICTORY_KEY, False):
            print("\n🏆 ¡HAS ESCAPADO! La celda espacial queda atrás.")
            print("El trace completo de esta partida está disponible en LangSmith.")
            break

        # Leer input del jugador
        try:
            user_input = input("> Tu acción: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\nJuego interrumpido. ¡Hasta pronto!")
            break

        if not user_input:
            continue

        if user_input.lower() in _QUIT_COMMANDS:
            print("\nAbandonando la celda... (juego terminado)")
            break

        # Preparar el estado para este turno con el nuevo mensaje del jugador
        current_state: AgentState = {
            **state,
            "messages": list(state["messages"]) + [HumanMessage(content=user_input)],
        }

        # Invocar el grafo y actualizar el estado global
        try:
            state = graph.invoke(current_state)
        except Exception as exc:
            print(f"\n[ERROR] Problema al procesar la acción: {exc}")
            continue

        # Mostrar narración del turno
        _print_narration(state)
        _print_options()
        print(_DIVIDER)
