"""
escape_room/graph/builder.py
=============================
Ensambla el StateGraph de LangGraph con todos los nodos y edges.

Topología del grafo:
  [START]
     │
     ▼
  [parser]  ── conditional edge ──► [puzzle_engine] ──► [room_master] ──► [END]
     │                                                        ▲
     └─────────────── "observation" ─────────────────────────┘

Enrutamiento condicional:
  "interaction" → puzzle_engine → room_master
  "observation" → room_master  (salto directo)
"""

from typing import Literal
from langgraph.graph import StateGraph, START, END

from escape_room.state import AgentState
from escape_room.nodes import parser_node, puzzle_engine_node, room_master_node


def _route_after_parser(
    state: AgentState,
) -> Literal["puzzle_engine", "room_master"]:
    """
    Función de enrutamiento condicional.

    Lee `action_type` del estado (escrito por el Parser) y decide
    el siguiente nodo:
      - "interaction" → PuzzleEngine (valida acción y muta estado)
      - "observation" → RoomMaster  (solo narración, sin cambios de estado)

    Este enrutador es la única pieza que une la clasificación del Parser
    con la lógica de puzles y la narración final.
    """
    if state.get("action_type") == "interaction":
        return "puzzle_engine"
    return "room_master"


def build_graph():
    """
    Construye y compila el StateGraph completo del Escape Room.

    Returns:
        CompiledGraph listo para ser invocado con `.invoke(state)`.
    """
    builder = StateGraph(AgentState)

    # ── Registrar nodos ───────────────────────────────────────────────────────
    builder.add_node("parser", parser_node)
    builder.add_node("puzzle_engine", puzzle_engine_node)
    builder.add_node("room_master", room_master_node)

    # ── Edges fijos ───────────────────────────────────────────────────────────
    builder.add_edge(START, "parser")
    builder.add_edge("puzzle_engine", "room_master")
    builder.add_edge("room_master", END)

    # ── Edge condicional ──────────────────────────────────────────────────────
    builder.add_conditional_edges(
        "parser",
        _route_after_parser,
        {
            "puzzle_engine": "puzzle_engine",
            "room_master": "room_master",
        },
    )

    return builder.compile()
