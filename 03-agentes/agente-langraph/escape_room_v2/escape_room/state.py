"""
escape_room/state.py
====================
Define el estado global del grafo (AgentState).

Esta TypedDict es la ÚNICA fuente de verdad del sistema.
Cada nodo tiene permisos de escritura restringidos:

  Nodo          | Puede escribir
  ─────────────────────────────────────────────────
  Parser        | action_type
  PuzzleEngine  | inventory, room_state, feedback_msg
  RoomMaster    | messages, feedback_msg (limpia)
  ─────────────────────────────────────────────────

La restricción es por convención arquitectónica, no por mecanismo técnico.
Los comentarios de cada campo documentan quién es el propietario.
"""

from typing import Annotated, Literal
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    # ── Propietario: Parser + RoomMaster (append-only via add_messages) ──
    # Historial completo de la conversación.
    # add_messages garantiza que cada nodo solo añada mensajes, nunca sobreescriba.
    messages: Annotated[list[BaseMessage], add_messages]

    # ── Propietario exclusivo: PuzzleEngine ──
    # Objetos que el jugador lleva encima.
    # Ejemplo: ["cable_suelto", "tarjeta_acceso"]
    inventory: list[str]

    # ── Propietario exclusivo: PuzzleEngine ──
    # Estado lógico de los puzles de la sala.
    # Todos los valores son booleanos para garantizar predicados simples y sin ambigüedad.
    # El RoomMaster solo puede LEER este diccionario, nunca escribirlo.
    room_state: dict[str, bool]

    # ── Canal de comunicación: PuzzleEngine → RoomMaster ──
    # Describe QUÉ ocurrió exactamente (ÉXITO/FALLO + razón).
    # El RoomMaster narra a partir de este mensaje, no de su memoria.
    # Se limpia a "" después de cada ciclo narrativo.
    feedback_msg: str

    # ── Propietario: Parser (uso interno del enrutador) ──
    # Resultado de la clasificación de intención del jugador.
    # "interaction" → flujo pasa por PuzzleEngine antes de RoomMaster.
    # "observation" → flujo va directamente a RoomMaster.
    action_type: Literal["interaction", "observation"]
