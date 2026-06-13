"""
escape_room/config.py
======================
Carga las variables de entorno desde el archivo .env y configura LangSmith.

Este módulo debe ser importado PRIMERO en main.py para que todas las
variables estén disponibles antes de que se construya el grafo o el LLM.

Variables de entorno esperadas (ver .env.example):
  AZURE_OPENAI_API_KEY      — Clave de API de Azure OpenAI
  AZURE_OPENAI_ENDPOINT     — Endpoint del recurso Azure
  AZURE_OPENAI_DEPLOYMENT   — Nombre del deployment (ej. gpt-4o)
  AZURE_OPENAI_API_VERSION  — Versión de la API

  LANGCHAIN_TRACING_V2      — "true" para activar tracing en LangSmith
  LANGCHAIN_API_KEY         — Clave de API de LangSmith
  LANGCHAIN_PROJECT         — Nombre del proyecto en LangSmith
"""

import os
from pathlib import Path

# Carga automática del .env si existe (requiere python-dotenv)
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        print(f"[CONFIG] Variables cargadas desde {env_path}")
    else:
        print("[CONFIG] Archivo .env no encontrado — usando variables del entorno del sistema.")
except ImportError:
    print("[CONFIG] python-dotenv no instalado — usando variables del entorno del sistema.")


# ── LangSmith: valores por defecto si no están definidos en el entorno ────────
os.environ.setdefault("LANGCHAIN_TRACING_V2", "true")
os.environ.setdefault("LANGCHAIN_PROJECT", "escape-room-dungeon-master")

# ── Validación básica de credenciales Azure ───────────────────────────────────
_REQUIRED_VARS = [
    "AZURE_OPENAI_API_KEY",
    "AZURE_OPENAI_ENDPOINT",
]

def validate_env() -> None:
    """
    Verifica que las variables de entorno críticas estén definidas.
    Lanza un EnvironmentError con instrucciones si faltan.
    """
    missing = [var for var in _REQUIRED_VARS if not os.environ.get(var)]
    if missing:
        raise EnvironmentError(
            f"\n[CONFIG] Faltan las siguientes variables de entorno:\n"
            + "\n".join(f"  - {v}" for v in missing)
            + "\n\nCopia .env.example como .env y rellena tus credenciales."
        )
    print("[CONFIG] Credenciales Azure verificadas ✓")
    tracing = os.environ.get("LANGCHAIN_TRACING_V2", "false")
    project = os.environ.get("LANGCHAIN_PROJECT", "—")
    print(f"[CONFIG] LangSmith tracing: {tracing} | Proyecto: {project}")
