"""
NutriBot - Frontend Streamlit
Interfaz de chat para el agente nutricional.
"""

import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Configuración de página
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="NutriBot 🥗",
    page_icon="🥗",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# CSS personalizado
# ---------------------------------------------------------------------------

st.markdown("""
<style>
    /* Fondo principal */
    .stApp {
        background-color: #f0f7f0;
    }

    /* Header */
    .nutribot-header {
        background: linear-gradient(135deg, #2d6a4f, #52b788);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        text-align: center;
        color: white;
        box-shadow: 0 4px 15px rgba(45, 106, 79, 0.3);
    }
    .nutribot-header h1 { font-size: 2rem; margin: 0; }
    .nutribot-header p { margin: 0.3rem 0 0; opacity: 0.9; font-size: 0.95rem; }

    /* Mensajes de chat */
    .chat-message {
        display: flex;
        align-items: flex-start;
        margin: 0.8rem 0;
        gap: 0.8rem;
    }
    .chat-message.user { flex-direction: row-reverse; }

    .avatar {
        width: 40px; height: 40px;
        border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-size: 1.3rem;
        flex-shrink: 0;
    }
    .avatar.bot { background: #52b788; }
    .avatar.user { background: #2d6a4f; }

    .message-bubble {
        max-width: 75%;
        padding: 0.8rem 1.1rem;
        border-radius: 16px;
        line-height: 1.5;
        font-size: 0.95rem;
    }
    .message-bubble.bot {
        background: white;
        border: 1px solid #d8f3dc;
        border-top-left-radius: 4px;
        color: #1b4332;
    }
    .message-bubble.user {
        background: #2d6a4f;
        color: white;
        border-top-right-radius: 4px;
    }

    /* Sidebar */
    .sidebar-card {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
        border-left: 4px solid #52b788;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    .sidebar-card h4 { color: #2d6a4f; margin: 0 0 0.5rem; }

    /* Status badge */
    .status-badge {
        display: inline-block;
        padding: 0.2rem 0.7rem;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 600;
    }
    .status-online { background: #d8f3dc; color: #2d6a4f; }
    .status-offline { background: #ffe5e5; color: #c0392b; }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Inicialización del estado de sesión
# ---------------------------------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []
if "agent" not in st.session_state:
    st.session_state.agent = None
if "conversation_ended" not in st.session_state:
    st.session_state.conversation_ended = False
if "api_key_set" not in st.session_state:
    st.session_state.api_key_set = bool(os.getenv("AZURE_OPENAI_ENDPOINT"))

# ---------------------------------------------------------------------------
# Carga del agente
# ---------------------------------------------------------------------------

def load_agent():
    """Carga el agente si no está ya cargado."""
    if st.session_state.agent is None and st.session_state.api_key_set:
        try:
            from agent.nutribot_agent import create_nutribot_agent
            st.session_state.agent = create_nutribot_agent()
        except Exception as e:
            st.error(f"Error al iniciar el agente: {e}")
            return False
    return st.session_state.agent is not None

# ---------------------------------------------------------------------------
# Lógica de procesamiento de mensajes
# ---------------------------------------------------------------------------

def process_message(text):
    """Procesa un mensaje del usuario y obtiene respuesta del agente."""
    if not text or not text.strip():
        return

    if load_agent():
        from agent.nutribot_agent import run_agent

        # Realizar la invocación
        result = run_agent(
            st.session_state.agent,
            text.strip(),
            st.session_state.messages,
        )

        st.session_state.messages = result["chat_history"]
        if result["end_conversation"]:
            st.session_state.conversation_ended = True

# ---------------------------------------------------------------------------
# Manejo de entrada pendiente (sugerencias)
# ---------------------------------------------------------------------------

if "pending_input" in st.session_state and st.session_state.pending_input:
    query = st.session_state.pending_input
    st.session_state.pending_input = None # Limpiar para evitar bucles
    process_message(query)

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown("## ⚙️ Configuración")

    status_class = "status-online" if st.session_state.api_key_set else "status-offline"
    status_text = "🟢 Conectado a Azure" if st.session_state.api_key_set else "🔴 Sin Configuración Azure"
    st.markdown(f'<span class="status-badge {status_class}">{status_text}</span>', unsafe_allow_html=True)

    st.divider()

    # Capacidades
    st.markdown("""
    <div class="sidebar-card">
        <h4>🛠️ Herramientas disponibles</h4>
        <p>⚖️ <b>Calcular IMC</b><br>
        Calcula tu índice de masa corporal</p>
        <p>🍎 <b>Buscar calorías</b><br>
        Información nutricional de alimentos</p>
        <p>📝 <b>Registrar comida</b><br>
        Lleva tu diario nutricional</p>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Historial y controles
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Limpiar", use_container_width=True):
            st.session_state.messages = []
            st.session_state.agent = None
            st.session_state.conversation_ended = False
            st.rerun()
    with col2:
        if st.button("🔄 Reiniciar", use_container_width=True):
            st.session_state.conversation_ended = False
            st.rerun()

    st.divider()

    # Info
    st.markdown("""
    <div class="sidebar-card">
        <h4>💡 Ejemplos de uso</h4>
        <small>
        • "Calcula mi IMC, peso 70kg y mido 175cm"<br>
        • "¿Cuántas calorías tiene un aguacate?"<br>
        • "Registra que comí 150g de pollo a la plancha en el almuerzo"<br>
        • "¿Qué es el IMC?"
        </small>
    </div>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Cabecera
# ---------------------------------------------------------------------------

st.markdown("""
<div class="nutribot-header">
    <h1>🥗 NutriBot</h1>
    <p>Tu asistente nutricional inteligente · IMC · Calorías · Seguimiento · Consejos</p>
</div>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Área de chat
# ---------------------------------------------------------------------------

# Mensaje de bienvenida si no hay historial
if not st.session_state.messages:
    st.markdown("""
    <div class="chat-message">
        <div class="avatar bot">🥗</div>
        <div class="message-bubble bot">
            ¡Hola! Soy <b>NutriBot</b>, tu asistente nutricional. 🌿<br><br>
            Puedo ayudarte a:<br>
            ⚖️ Calcular tu <b>IMC</b><br>
            🍎 Buscar <b>calorías</b> de alimentos<br>
            📝 <b>Registrar</b> tus comidas<br><br>
            ¿Por dónde empezamos? 😊
        </div>
    </div>
    """, unsafe_allow_html=True)

# Mostrar historial de mensajes
for msg in st.session_state.messages:
    role = msg["role"]
    content = msg["content"]
    if role == "user":
        st.markdown(f"""
        <div class="chat-message user">
            <div class="avatar user">👤</div>
            <div class="message-bubble user">{content}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="chat-message">
            <div class="avatar bot">🥗</div>
            <div class="message-bubble bot">{content}</div>
        </div>
        """, unsafe_allow_html=True)

# Mensaje de conversación finalizada
if st.session_state.conversation_ended:
    st.markdown("""
    <div style="text-align:center; padding:1rem; color:#2d6a4f; 
                background:#d8f3dc; border-radius:10px; margin-top:1rem;">
        <b>Conversación finalizada.</b> Haz clic en "Reiniciar" para comenzar de nuevo.
    </div>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Input del usuario
# ---------------------------------------------------------------------------

if not st.session_state.conversation_ended:
    if not st.session_state.api_key_set:
        st.warning("⚠️ Asegúrate de tener configurado AZURE_OPENAI_API_KEY y AZURE_OPENAI_ENDPOINT en tu archivo .env para comenzar.")
    else:
        # Sugerencias rápidas
        st.markdown("**Sugerencias:**")
        suggestions = [
            "Calcula mi IMC (70kg, 175cm)",
            "¿Calorías del aguacate?",
            "Registrar 200g de pollo",
            "¿Qué es el IMC?",
        ]
        
        cols = st.columns(len(suggestions))
        for i, (col, sug) in enumerate(zip(cols, suggestions)):
            if col.button(sug, key=f"sug_{i}", use_container_width=True):
                st.session_state.pending_input = sug
                st.rerun()

        # Campo de texto principal
        if user_input := st.chat_input("Escribe tu pregunta nutricional..."):
            with st.spinner("🌿 NutriBot está pensando..."):
                process_message(user_input)
                st.rerun()


# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------

st.markdown("""
<hr style="border:1px solid #d8f3dc; margin-top:2rem;">
<p style="text-align:center; color:#52b788; font-size:0.8rem;">
    NutriBot · Construido con LangChain + Azure OpenAI + Streamlit 
    · <i>Este bot no sustituye el consejo médico profesional</i>
</p>
""", unsafe_allow_html=True)
