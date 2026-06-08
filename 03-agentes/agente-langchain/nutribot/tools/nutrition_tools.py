"""
Tools de nutrición para el agente NutriBot.
- calcular_imc
- buscar_calorias (vía Búsqueda en Internet)
- registrar_comida
"""

import json
import os
import re
from datetime import datetime
from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun


# ---------------------------------------------------------------------------
# Tool 1: Calcular IMC
# ---------------------------------------------------------------------------

@tool
def calcular_imc(peso_kg: float, altura_cm: float) -> str:
    """
    Calcula el Índice de Masa Corporal (IMC) dado el peso en kg y la altura en cm.
    Devuelve el valor del IMC y su categoría (bajo peso, normal, sobrepeso, obesidad).

    Args:
        peso_kg: Peso de la persona en kilogramos (ej: 70.5)
        altura_cm: Altura de la persona en centímetros (ej: 175)
    """
    if peso_kg <= 0 or altura_cm <= 0:
        return "Error: el peso y la altura deben ser valores positivos."

    altura_m = altura_cm / 100
    imc = peso_kg / (altura_m ** 2)
    imc_redondeado = round(imc, 2)

    if imc < 18.5:
        categoria = "Bajo peso"
        consejo = "Considera hablar con un nutricionista para ganar peso de forma saludable."
    elif imc < 25:
        categoria = "Peso normal"
        consejo = "¡Excelente! Mantén tus hábitos alimenticios saludables."
    elif imc < 30:
        categoria = "Sobrepeso"
        consejo = "Una dieta equilibrada y ejercicio regular pueden ayudarte a alcanzar tu peso ideal."
    elif imc < 35:
        categoria = "Obesidad grado I"
        consejo = "Te recomiendo consultar con un médico o nutricionista para un plan personalizado."
    elif imc < 40:
        categoria = "Obesidad grado II"
        consejo = "Es importante consultar con un equipo médico para recibir la atención adecuada."
    else:
        categoria = "Obesidad grado III"
        consejo = "Por favor, consulta con un médico lo antes posible para recibir apoyo profesional."

    return (
        f"**IMC calculado:** {imc_redondeado}\n"
        f"**Categoría:** {categoria}\n"
        f"**Consejo:** {consejo}\n\n"
        f"*(Cálculo: {peso_kg} kg / ({altura_cm/100} m)² = {imc_redondeado})*"
    )


# ---------------------------------------------------------------------------
# Tool 2: Buscar calorías (Búsqueda en Internet)
# ---------------------------------------------------------------------------

search = DuckDuckGoSearchRun()

@tool
def buscar_calorias(alimento: str, cantidad_g: float = 100) -> str:
    """
    Busca la información nutricional (calorías, proteínas, carbohidratos, grasas) de un alimento
    realizando una búsqueda en internet.
    
    Args:
        alimento: Nombre del alimento a buscar (ej: "manzana", "yogur griego", "pan integral")
        cantidad_g: Cantidad en gramos o ml para la que se quiere calcular (por defecto 100)
    """
    try:
        # Realizar la búsqueda
        query = f"información nutricional y calorías de {alimento} por cada 100g"
        resultado = search.run(query)
        
        return (
            f"Resultados de búsqueda en internet para '{alimento}':\n\n"
            f"{resultado}\n\n"
            f"--- \n"
            f"Por favor, NutriBot, analiza esta información y calcula los valores para {cantidad_g}g "
            f"si la información encontrada es por cada 100g."
        )

    except Exception as e:
        return f"Lo siento, no pude realizar la búsqueda en internet en este momento: {str(e)}"


# ---------------------------------------------------------------------------
# Tool 3: Registrar comida
# ---------------------------------------------------------------------------

REGISTRO_FILE = "data/registro_comidas.json"


def _load_registro() -> list:
    os.makedirs("data", exist_ok=True)
    if os.path.exists(REGISTRO_FILE):
        try:
            with open(REGISTRO_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def _save_registro(registro: list):
    os.makedirs("data", exist_ok=True)
    with open(REGISTRO_FILE, "w", encoding="utf-8") as f:
        json.dump(registro, f, ensure_ascii=False, indent=2)


@tool
def registrar_comida(alimento: str, cantidad_g: float, momento: str = "sin especificar") -> str:
    """
    Registra una comida en el diario nutricional del usuario con la fecha y hora actual.

    Args:
        alimento: Nombre del alimento o comida consumida
        cantidad_g: Cantidad en gramos consumida
        momento: Momento del día (desayuno, almuerzo, merienda, cena, sin especificar)
    """
    registro = _load_registro()

    entrada = {
        "id": len(registro) + 1,
        "fecha": datetime.now().strftime("%Y-%m-%d"),
        "hora": datetime.now().strftime("%H:%M"),
        "alimento": alimento,
        "cantidad_g": cantidad_g,
        "momento": momento,
    }

    # Intentar obtener calorías para el registro usando la búsqueda si es posible,
    # aunque en el registro automático es más difícil parsear el texto de búsqueda.
    # Por simplicidad, el agente puede registrarlo y si el usuario pregunta después, 
    # se puede buscar. O el agente puede llamar a buscar_calorias primero.
    
    registro.append(entrada)
    _save_registro(registro)

    # Calcular total del día
    hoy = datetime.now().strftime("%Y-%m-%d")
    entradas_hoy = [e for e in registro if e.get("fecha") == hoy]
    total_calorias_hoy = sum(e.get("calorias_aprox", 0) for e in entradas_hoy)

    return (
        f"✅ **Registrado:** {alimento} — {cantidad_g}g ({momento})\n"
        f"📅 Fecha: {entrada['fecha']} {entrada['hora']}\n\n"
        f"📊 **Total de hoy:** {len(entradas_hoy)} registros | ~{round(total_calorias_hoy)} kcal acumuladas (estimadas)"
    )
