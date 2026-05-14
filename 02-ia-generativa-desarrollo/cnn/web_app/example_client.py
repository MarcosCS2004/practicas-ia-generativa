"""
Ejemplo de cómo usar la aplicación web desde Python
Para invocar la predicción del servidor
"""

import requests
from PIL import Image
import json
from pathlib import Path

# URL del servidor
SERVER_URL = "http://localhost:5000"

def predict_image(image_path):
    """
    Realiza una predicción para una imagen
    
    Args:
        image_path (str): Ruta a la imagen
        
    Returns:
        dict: Respuesta con el dígito predicho y confianza
    """
    with open(image_path, 'rb') as f:
        files = {'image': f}
        response = requests.post(f"{SERVER_URL}/predict", files=files)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error: {response.text}")

def check_server_health():
    """
    Verifica que el servidor esté disponible
    
    Returns:
        bool: True si el servidor está disponible
    """
    try:
        response = requests.get(f"{SERVER_URL}/health")
        data = response.json()
        print(f"✅ Servidor disponible")
        print(f"   Modelo cargado: {'Sí' if data['model_loaded'] else 'No'}")
        return data['model_loaded']
    except:
        print("❌ Servidor no disponible")
        return False

def batch_predict(folder_path):
    """
    Realiza predicciones para todas las imágenes en una carpeta
    
    Args:
        folder_path (str): Ruta a la carpeta con imágenes
    """
    folder = Path(folder_path)
    images = list(folder.glob('*.png')) + list(folder.glob('*.jpg'))
    
    results = []
    for img_path in images:
        try:
            result = predict_image(str(img_path))
            result['image'] = str(img_path)
            results.append(result)
            print(f"✅ {img_path.name}: {result['digit']} (Confianza: {result['confidence']}%)")
        except Exception as e:
            print(f"❌ {img_path.name}: Error - {e}")
    
    return results

if __name__ == "__main__":
    print("=" * 60)
    print("Ejemplo de Uso de la API de Reconocimiento de Dígitos")
    print("=" * 60)
    print()
    
    # Verificar que el servidor esté disponible
    if not check_server_health():
        print("\n⚠️  Inicia el servidor primero con: python app.py")
        exit(1)
    
    print()
    
    # Ejemplo 1: Predecir una sola imagen
    print("Ejemplo 1: Predecir una sola imagen")
    print("-" * 60)
    # Cambiar por tu ruta de imagen
    try:
        result = predict_image("imagen_digito.png")
        print(f"Dígito predicho: {result['digit']}")
        print(f"Confianza: {result['confidence']}%")
        print(f"Probabilidades: {json.dumps(result['probabilities'], indent=2)}")
    except Exception as e:
        print(f"Nota: {e}")
        print("(Asegúrate de tener una imagen llamada 'imagen_digito.png')")
    
    print()
    
    # Ejemplo 2: Predicciones en lote
    print("Ejemplo 2: Predicciones en lote (descomentar para usar)")
    print("-" * 60)
    print("# results = batch_predict('./imagenes')")
    
    print()
    print("✅ Listo para usar!")
