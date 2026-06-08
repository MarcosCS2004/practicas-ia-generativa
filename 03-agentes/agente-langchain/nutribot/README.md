# 🥗 NutriBot — Agente Nutricional con LangChain + Streamlit

Agente conversacional de nutrición construido con **LangChain** y **Streamlit**.

## Arquitectura

```
Agente (LangChain OpenAI Tools Agent)
├── Tools
│   ├── calcular_imc          → Calcula IMC y categoría OMS
│   ├── buscar_calorias        → Información nutricional por alimento
│   └── registrar_comida       → Diario nutricional (JSON local)
├── RAG (ChromaDB + OpenAI Embeddings)
│   └── buscar_en_documentos   → Libros de recetas + Guías de salud
└── END                        → Detección de intención de salida
```

## Requisitos

- Python 3.10+
- API Key de OpenAI

## Instalación

```bash
# 1. Clonar / descomprimir el proyecto
cd nutribot

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate         # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar API Key
cp .env.example .env
# Editar .env y poner tu OPENAI_API_KEY

# 5. Ejecutar
streamlit run app.py
```

## Estructura del proyecto

```
nutribot/
├── app.py                      # Frontend Streamlit
├── requirements.txt
├── .env.example
├── agent/
│   └── nutribot_agent.py       # Agente LangChain + lógica END
├── tools/
│   └── nutrition_tools.py      # 3 tools: IMC, calorías, registro
├── rag/
│   └── rag_chain.py            # RAG con ChromaDB
└── data/
    ├── docs/                   # Añade aquí tus .txt con recetas/guías
    ├── chroma_db/              # Vector store (se genera automáticamente)
    └── registro_comidas.json   # Diario (se genera automáticamente)
```

## Añadir documentos al RAG

Coloca archivos `.txt` en `data/docs/` y elimina `data/chroma_db/` para que se reconstruya la base vectorial.

## Ejemplos de uso

- *"Calcula mi IMC, peso 68kg y mido 172cm"*
- *"¿Cuántas calorías tiene 150g de salmón?"*
- *"Registra que comí un plátano en el desayuno"*
- *"Dame una receta alta en proteínas"*
- *"¿Qué porcentaje de grasas debería consumir al día?"*
- *"Adiós"* → finaliza la conversación

## Notas

- El registro de comidas se guarda en `data/registro_comidas.json`
- Los documentos de ejemplo (recetas y guías) ya están incluidos en el código
- El agente usa `gpt-4o-mini` por defecto (económico y eficiente)
