"""
Mini Aplicación Web para Reconocimiento de Dígitos con CNN
Utiliza el modelo entrenado: cnn_mnist_ruteo_paquetes.keras
"""

from flask import Flask, render_template, request, jsonify
from tensorflow import keras
import numpy as np
from PIL import Image
import io
import base64
import os

app = Flask(__name__)

# Cargar el modelo entrenado
MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'cnn_mnist_ruteo_paquetes.keras')
try:
    model = keras.models.load_model(MODEL_PATH)
    print(f"✓ Modelo cargado exitosamente desde: {MODEL_PATH}")
except Exception as e:
    print(f"✗ Error al cargar el modelo: {e}")
    model = None


def preprocess_image(img):
    """
    Preprocesa la imagen para que sea compatible con el modelo CNN
    - Redimensiona a 28x28 (tamaño de MNIST)
    - Convierte a escala de grises
    - Normaliza los valores
    """
    # Convertir a escala de grises si es necesario
    if img.mode != 'L':
        img = img.convert('L')
    
    # Redimensionar a 28x28
    img = img.resize((28, 28), Image.Resampling.LANCZOS)
    
    # Convertir a array numpy
    img_array = np.array(img)
    
    # Invertir colores (en MNIST, los dígitos son blancos sobre fondo negro)
    img_array = 255 - img_array
    
    # Normalizar a rango [0, 1]
    img_array = img_array / 255.0
    
    # Agregar dimensión de canal (28, 28, 1)
    img_array = img_array.reshape(1, 28, 28, 1)
    
    return img_array


@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
def predict():
    """
    Endpoint para realizar predicciones
    Recibe una imagen y devuelve el dígito predicho
    """
    if model is None:
        return jsonify({'error': 'Modelo no cargado'}), 500
    
    try:
        # Obtener la imagen del request
        if 'image' not in request.files:
            return jsonify({'error': 'No se proporcionó imagen'}), 400
        
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({'error': 'Archivo vacío'}), 400
        
        # Leer la imagen
        img = Image.open(io.BytesIO(file.read()))
        
        # Preprocesar la imagen
        img_processed = preprocess_image(img)
        
        # Realizar la predicción
        prediction = model.predict(img_processed, verbose=0)
        digit = np.argmax(prediction[0])
        confidence = float(prediction[0][digit]) * 100
        
        # Obtener todas las probabilidades
        all_probabilities = {str(i): float(prediction[0][i]) * 100 for i in range(10)}
        
        return jsonify({
            'digit': int(digit),
            'confidence': round(confidence, 2),
            'probabilities': all_probabilities
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'model_loaded': model is not None
    })


if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Servidor de Reconocimiento de Dígitos CNN")
    print("=" * 60)
    print("Accede a la aplicación en: http://localhost:5000")
    print("=" * 60)
    app.run(debug=True, host='127.0.0.1', port=5000)
