"""
escape_room/scenario/celda_espacial.py
=======================================
Define el escenario "Celda Espacial": estado inicial, inventario y descripción.

Para crear un nuevo escenario, basta con copiar este módulo, cambiar
las constantes y registrarlo en el PuzzleEngine correspondiente.
"""

# ── Estado inicial de los puzles ──────────────────────────────────────────────
# Todos los valores son False al inicio de la partida.
# El PuzzleEngine los modifica según las acciones del jugador.
INITIAL_ROOM_STATE: dict[str, bool] = {
    "cable_recogido": False,     # ¿El jugador recogió el cable del suelo?
    "panel_encendido": False,    # ¿El panel de control tiene energía?
    "puerta_abierta": False,     # ¿La puerta magnética está desbloqueada?
    "escape_completado": False,  # Condición de victoria — finaliza la partida
}

# ── Inventario inicial ────────────────────────────────────────────────────────
# Lista de objetos que el jugador tiene al comenzar.
# En este escenario empieza con las manos vacías.
INITIAL_INVENTORY: list[str] = []

# ── Descripción narrativa del escenario ──────────────────────────────────────
# Texto que se muestra en la intro antes del primer turno.
SCENARIO_DESCRIPTION: str = """
╔══════════════════════════════════════════════════╗
║         🚀  CELDA ESPACIAL  —  SECTOR 7          ║
╚══════════════════════════════════════════════════╝

Estás atrapado en una celda espacial.
La iluminación de emergencia parpadea en rojo.

  OBJETOS VISIBLES:
  ▸ Un PANEL DE CONTROL apagado en la pared norte.
  ▸ Un CABLE SUELTO en el suelo, cerca del panel.
  ▸ Una PUERTA METÁLICA cerrada en la pared sur.

  OBJETIVO: Encuentra la manera de escapar.

  COMANDOS DE EJEMPLO:
  'cojo el cable'          → recoger objeto
  'uso el cable en el panel' → interactuar
  'abro la puerta'         → abrir salida
  'salgo'                  → escapar
  'miro alrededor'         → observar
  'salir'                  → terminar el juego
"""

# ── Clave de condición de victoria ───────────────────────────────────────────
# El GameLoop consulta esta clave en room_state para detectar el fin de partida.
VICTORY_KEY: str = "escape_completado"

# ── Acciones sugeridas (Opciones) ─────────────────────────────────────────────
# Estas se mostrarán al usuario después de cada respuesta del Room Master.
SUGGESTED_ACTIONS: list[str] = [
    "miro alrededor",
    "cojo el cable",
    "uso el cable en el panel",
    "abro la puerta",
    "salgo",
]
