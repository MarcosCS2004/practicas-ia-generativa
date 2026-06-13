"""
escape_room/__init__.py
========================
Paquete principal del Escape Room Agent.

Estructura:
  escape_room/
  ├── config.py           — Variables de entorno y LangSmith
  ├── state.py            — AgentState (TypedDict global)
  ├── llm.py              — Fábrica del cliente LLM
  ├── game_loop.py        — Bucle interactivo de consola
  ├── graph/
  │   └── builder.py      — Ensamblaje del StateGraph
  ├── nodes/
  │   ├── parser.py       — Nodo 1: clasificador de intención
  │   ├── puzzle_engine.py — Nodo 2: motor determinista de puzles
  │   └── room_master.py  — Nodo 3: narrador LLM
  └── scenario/
      └── celda_espacial.py — Escenario inicial hardcoded
"""
