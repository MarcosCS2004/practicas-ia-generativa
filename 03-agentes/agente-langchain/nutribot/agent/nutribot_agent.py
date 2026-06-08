"""
NutriBot Agent - Agente nutricional con LangGraph
Arquitectura: StateGraph -> LLM -> Conditional Edge (Tools / END)
"""

import os
from typing import Annotated, TypedDict, Union, List

from langchain_openai import AzureChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages

from tools.nutrition_tools import calcular_imc, buscar_calorias, registrar_comida

# ---------------------------------------------------------------------------
# Definición del Estado
# ---------------------------------------------------------------------------

class AgentState(TypedDict):
    """El estado del agente, que incluye el historial de mensajes."""
    messages: Annotated[List[BaseMessage], add_messages]

# ---------------------------------------------------------------------------
# Configuración de herramientas y LLM
# ---------------------------------------------------------------------------

tools = [calcular_imc, buscar_calorias, registrar_comida]
tool_node = ToolNode(tools)

def get_llm():
    deployment_name = os.environ.get("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME", "gpt-4o-mini")
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    api_key = os.environ.get("AZURE_OPENAI_API_KEY")
    api_version = os.environ.get("OPENAI_API_VERSION", "2024-02-15-preview")
    
    if api_key:
        llm = AzureChatOpenAI(
            api_key=api_key,
            azure_endpoint=endpoint,
            azure_deployment=deployment_name,
            api_version=api_version,
            temperature=0
        )
    else:
        token_provider = get_bearer_token_provider(
            DefaultAzureCredential(), 
            "https://ai.azure.com/.default"
        )
        llm = AzureChatOpenAI(
            azure_ad_token_provider=token_provider,
            azure_endpoint=endpoint,
            azure_deployment=deployment_name,
            api_version=api_version,
            temperature=0
        )
    return llm.bind_tools(tools)

# ---------------------------------------------------------------------------
# Nodos del Grafo
# ---------------------------------------------------------------------------

def call_model(state: AgentState):
    """Llamada al modelo LLM."""
    messages = state['messages']
    
    system_prompt = """Eres NutriBot, un asistente nutricional experto y amigable. 
Ayudas a los usuarios con:

1. **Cálculo de IMC**: Cuando el usuario proporcione peso y altura, usa la herramienta calcular_imc.
2. **Búsqueda de calorías e información nutricional**: Cuando pregunten por las calorías o nutrientes de un alimento, usa buscar_calorias para buscar la información en internet en tiempo real.
3. **Registro de comida**: Cuando quieran registrar lo que han comido, usa registrar_comida.

Responde siempre en español, de forma clara y motivadora.
Para la búsqueda de calorías, analiza los resultados de internet que obtengas y extrae los valores más precisos para la cantidad solicitada.

Si el usuario quiere terminar la conversación (dice "adios", "salir", "fin", "terminar"), 
despídete amablemente y di que puede volver cuando quiera.

Nunca inventes información nutricional; si no sabes algo, usa buscar_calorias o dilo honestamente."""

    # Insertar system prompt si no está ya
    if not any(isinstance(m, SystemMessage) for m in messages):
        messages = [SystemMessage(content=system_prompt)] + messages
    
    llm = get_llm()
    response = llm.invoke(messages)
    return {"messages": [response]}

def should_continue(state: AgentState):
    """Determina si continuar con las herramientas o terminar."""
    messages = state['messages']
    last_message = messages[-1]
    
    if last_message.tool_calls:
        return "tools"
    return END

# ---------------------------------------------------------------------------
# Construcción del Grafo
# ---------------------------------------------------------------------------

def create_nutribot_agent():
    """Crea y compila el grafo de LangGraph."""
    workflow = StateGraph(AgentState)

    # Definir nodos
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", tool_node)

    # Definir entrada
    workflow.set_entry_point("agent")

    # Definir bordes condicionales
    workflow.add_conditional_edges(
        "agent",
        should_continue,
    )

    # Borde de herramientas de vuelta al agente
    workflow.add_edge("tools", "agent")

    return workflow.compile()

# ---------------------------------------------------------------------------
# Funciones de ejecución (compatibles con app.py)
# ---------------------------------------------------------------------------

def detect_end_intent(message: str) -> bool:
    """Detecta si el usuario quiere terminar la conversación."""
    end_keywords = ["adios", "adiós", "salir", "fin", "terminar", "bye", "exit", "hasta luego", "chao"]
    return any(kw in message.lower() for kw in end_keywords)

def run_agent(compiled_graph, user_input: str, chat_history: list) -> dict:
    """
    Ejecuta el grafo de LangGraph y devuelve la respuesta.
    """
    if detect_end_intent(user_input):
        farewell = "¡Hasta pronto! 👋 Ha sido un placer ayudarte con tu nutrición. ¡Recuerda mantener una alimentación equilibrada!"
        return {
            "response": farewell,
            "end_conversation": True,
            "chat_history": chat_history + [
                {"role": "user", "content": user_input},
                {"role": "assistant", "content": farewell}
            ],
        }

    # Preparar el estado inicial a partir del historial
    initial_messages = []
    for msg in chat_history:
        if msg["role"] == "user":
            initial_messages.append(HumanMessage(content=msg["content"]))
        else:
            initial_messages.append(AIMessage(content=msg["content"]))
    
    initial_messages.append(HumanMessage(content=user_input))
    
    # Ejecutar el grafo
    final_state = compiled_graph.invoke({"messages": initial_messages})
    
    # Obtener la última respuesta del modelo
    all_messages = final_state["messages"]
    last_ai_message = next(m for m in reversed(all_messages) if isinstance(m, AIMessage))
    response = last_ai_message.content

    # Actualizar historial para el frontend
    updated_history = chat_history + [
        {"role": "user", "content": user_input},
        {"role": "assistant", "content": response},
    ]

    return {
        "response": response,
        "end_conversation": False,
        "chat_history": updated_history,
    }
