"""
escape_room/llm.py
==================
Fábrica del cliente LLM.

Centraliza la creación del modelo para que todos los nodos
usen exactamente la misma configuración. Si se cambia el proveedor
(por ejemplo, de Azure a OpenAI estándar), el cambio es en un solo lugar.
"""

import os
from functools import lru_cache
from langchain_openai import AzureChatOpenAI


@lru_cache(maxsize=1)
def get_llm() -> AzureChatOpenAI:
    """
    Devuelve una instancia del LLM configurada con AzureChatOpenAI.

    Usa lru_cache para evitar crear múltiples instancias por ciclo del grafo.
    Las credenciales se leen de las variables de entorno (cargadas desde .env).

    Variables de entorno requeridas:
        AZURE_OPENAI_API_KEY      — Clave de API de Azure OpenAI
        AZURE_OPENAI_ENDPOINT     — Endpoint del recurso Azure
        AZURE_OPENAI_DEPLOYMENT   — Nombre del deployment (ej. gpt-4o)
        AZURE_OPENAI_API_VERSION  — Versión de la API (ej. 2024-08-01-preview)
    """
    return AzureChatOpenAI(
        azure_deployment=os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4o"),
        api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2024-08-01-preview"),
        temperature=0.7,
    )
