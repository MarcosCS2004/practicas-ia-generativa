"""
main.py
========
Punto de entrada de la aplicación Escape Room Agent.

Ejecutar con:
    python main.py

El módulo config se importa primero para garantizar que las variables
de entorno estén cargadas antes de que cualquier otro módulo intente
acceder al LLM o a LangSmith.
"""

# 1. Cargar configuración y credenciales ANTES que todo lo demás
from escape_room.config import validate_env

# 2. Validar que las variables críticas estén presentes
validate_env()

# 3. Iniciar el bucle del juego
from escape_room.game_loop import run_game

if __name__ == "__main__":
    run_game()
