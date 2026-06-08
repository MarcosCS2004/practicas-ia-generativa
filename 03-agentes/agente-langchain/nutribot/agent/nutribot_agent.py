"""
NutriBot Agent - Agente nutricional con LangChain
Arquitectura: Agente → Tools (IMC, calorías, registro) + END
"""

from langchain_classic.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

from tools.nutrition_tools import calcular_imc, buscar_calorias, registrar_comida
import os

def create_nutribot_agent(llm=None):
    """Crea y devuelve el agente NutriBot."""

    if llm is None:
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
            # Proveedor de tokens para autenticación basada en identidad (Azure Foundry / Managed Identity)
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

    tools = [calcular_imc, buscar_calorias, registrar_comida]

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

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    agent = create_openai_tools_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=5,
    )

    return agent_executor


def detect_end_intent(message: str) -> bool:
    """Detecta si el usuario quiere terminar la conversación."""
    end_keywords = ["adios", "adiós", "salir", "fin", "terminar", "bye", "exit", "hasta luego", "chao"]
    return any(kw in message.lower() for kw in end_keywords)


def run_agent(agent_executor, user_input: str, chat_history: list) -> dict:
    """
    Ejecuta el agente y devuelve la respuesta.
    
    Returns:
        dict con 'response' (str), 'end_conversation' (bool), 'chat_history' (list)
    """
    if detect_end_intent(user_input):
        farewell = "¡Hasta pronto! 👋 Ha sido un placer ayudarte con tu nutrición. ¡Recuerda mantener una alimentación equilibrada!"
        return {
            "response": farewell,
            "end_conversation": True,
            "chat_history": chat_history,
        }

    # Convertir historial al formato LangChain
    lc_history = []
    for msg in chat_history:
        if msg["role"] == "user":
            lc_history.append(HumanMessage(content=msg["content"]))
        else:
            lc_history.append(AIMessage(content=msg["content"]))

    result = agent_executor.invoke({
        "input": user_input,
        "chat_history": lc_history,
    })

    response = result.get("output", "Lo siento, no pude procesar tu solicitud.")

    # Actualizar historial
    updated_history = chat_history + [
        {"role": "user", "content": user_input},
        {"role": "assistant", "content": response},
    ]

    return {
        "response": response,
        "end_conversation": False,
        "chat_history": updated_history,
    }
