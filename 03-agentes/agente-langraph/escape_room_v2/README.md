# 🚀 Escape Room Agent — LangGraph + LangSmith

Sistema multi-agente modularizado que simula un **Escape Room de texto lógico**, construido con LangGraph y con tracing completo en LangSmith.

---

## Estructura del Proyecto

```
escape_room_agent/
│
├── main.py                          # Punto de entrada
├── requirements.txt
├── .env.example                     # Plantilla de credenciales
├── .gitignore
│
└── escape_room/                     # Paquete principal
    ├── __init__.py
    ├── config.py                    # Carga .env + configura LangSmith
    ├── state.py                     # AgentState (TypedDict — fuente de verdad)
    ├── llm.py                       # Fábrica del cliente AzureChatOpenAI
    ├── game_loop.py                 # Bucle interactivo de consola
    │
    ├── graph/
    │   ├── __init__.py
    │   └── builder.py               # Ensamblaje del StateGraph + enrutador
    │
    ├── nodes/
    │   ├── __init__.py
    │   ├── parser.py                # Nodo 1: clasificador de intención (LLM)
    │   ├── puzzle_engine.py         # Nodo 2: motor determinista (sin LLM)
    │   └── room_master.py          # Nodo 3: narrador inmersivo (LLM)
    │
    └── scenario/
        ├── __init__.py
        └── celda_espacial.py       # Escenario inicial: estado, inventario, descripción
```

---

## Arquitectura del Grafo

```
[START]
   │
   ▼
┌──────────┐
│  PARSER  │  ← Clasifica: "interaction" o "observation"
└────┬─────┘
     │
     ├─── interaction ──► ┌────────────────┐
     │                    │ PUZZLE ENGINE  │  ← Lógica pura (sin LLM)
     │                    └───────┬────────┘
     │                            │
     └─── observation ────────────┤
                                  ▼
                          ┌─────────────┐
                          │ ROOM MASTER │  ← Narrador (LLM)
                          └──────┬──────┘
                                 │
                               [END]
```

## Principios de Diseño

### Estado Global (`AgentState`)

| Campo | Propietario de escritura | Propósito |
|-------|--------------------------|-----------|
| `messages` | Parser + RoomMaster | Historial de conversación |
| `inventory` | **Solo PuzzleEngine** | Objetos del jugador |
| `room_state` | **Solo PuzzleEngine** | Estado lógico de puzles |
| `feedback_msg` | PuzzleEngine → RoomMaster | Canal de comunicación entre nodos |
| `action_type` | Parser | Control del enrutador condicional |

### Protección Anti-Alucinación

El **RoomMaster** (LLM) recibe el estado serializado explícitamente en cada llamada. Su prompt le prohíbe inventar objetos o eventos que no estén en ese estado. El **PuzzleEngine** usa código puro (sin LLM) para garantizar que los cambios de estado sean 100% deterministas.

---

## Escenario: Celda Espacial

```
Estado inicial:
  room_state: {
    cable_recogido: False,
    panel_encendido: False,
    puerta_abierta: False,
    escape_completado: False
  }
  inventory: []

Secuencia de escape:
  1. "cojo el cable"            → cable_recogido=True, cable en inventario
  2. "uso el cable en el panel" → panel_encendido=True, cable consumido
  3. "abro la puerta"           → puerta_abierta=True
  4. "salgo"                    → escape_completado=True → VICTORIA
```

---

## Instalación y Ejecución

```bash
# 1. Clonar / descomprimir el proyecto
cd escape_room_agent

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate      # Linux/Mac
# venv\Scripts\activate       # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar credenciales
cp .env.example .env
# Edita .env con tus claves reales de Azure y LangSmith

# 5. Ejecutar
python main.py
```

---

## Tracing en LangSmith

Con `LANGCHAIN_TRACING_V2=true` configurado, cada invocación del grafo genera un trace en [smith.langchain.com](https://smith.langchain.com) bajo el proyecto `escape-room-dungeon-master`.

Cada trace muestra:
- El flujo completo: Parser → (PuzzleEngine) → RoomMaster
- Los inputs/outputs de cada nodo
- La decisión de enrutamiento condicional
- Las llamadas al LLM (Parser y RoomMaster)
- Los tiempos de ejecución por nodo

---

## Extensibilidad

Para añadir un nuevo escenario:
1. Crea `escape_room/scenario/mi_escenario.py` con sus propias constantes.
2. Actualiza `escape_room/scenario/__init__.py` para importarlo.
3. Añade las reglas correspondientes en `puzzle_engine.py`.
