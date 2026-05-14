# 🎨 Mini Aplicación Web - Reconocimiento de Dígitos CNN

Una aplicación web simple y moderna para reconocer dígitos handwritten usando el modelo CNN entrenado con MNIST.

## 📋 Características

✅ **Dos formas de entrada:**
- Subir una imagen de tu computadora
- Dibujar un dígito directamente en la web

✅ **Resultados en tiempo real:**
- Predicción del dígito
- Porcentaje de confianza
- Probabilidades para cada dígito (0-9)

✅ **Interfaz moderna y responsiva:**
- Diseño limpio con gradientes
- Compatible con dispositivos móviles
- Animaciones suaves

## 🚀 Cómo Ejecutar

### 1. Instalar Dependencias

```bash
# Navega a la carpeta web_app
cd web_app

# Instala las dependencias necesarias
pip install -r requirements.txt
```

### 2. Ejecutar la Aplicación

```bash
python app.py
```

La aplicación se abrirá en: **http://localhost:5000**

### 3. Usar la Aplicación

**Opción 1: Subir Imagen**
1. Haz click en "📤 Subir Imagen"
2. Selecciona una imagen de un dígito
3. Haz click en "🔮 Predecir"

**Opción 2: Dibujar**
1. Haz click en "✏️ Dibujar"
2. Dibuja un dígito en el canvas blanco
3. Haz click en "🔮 Predecir"

## 📁 Estructura del Proyecto

```
web_app/
├── app.py                          # Servidor Flask
├── requirements.txt                # Dependencias
├── README.md                       # Este archivo
└── templates/
    └── index.html                  # Interfaz web
```

## 🔧 Requisitos

- Python 3.8 o superior
- El modelo `cnn_mnist_ruteo_paquetes.keras` debe estar en la carpeta padre

## ⚙️ Configuración del Modelo

El servidor carga automáticamente el modelo desde:
```
../cnn_mnist_ruteo_paquetes.keras
```

Si tienes problemas, verifica que:
1. El modelo existe en la ubicación correcta
2. El archivo tiene extensión `.keras`
3. El modelo fue entrenado correctamente

## 🎯 Cómo Funciona el Reconocimiento

1. **Preprocesamiento:**
   - Redimensiona la imagen a 28x28 píxeles
   - Convierte a escala de grises
   - Normaliza los valores entre 0-1

2. **Predicción:**
   - Envía la imagen al modelo CNN
   - Obtiene las probabilidades para cada dígito

3. **Resultados:**
   - Muestra el dígito con mayor probabilidad
   - Porcentaje de confianza
   - Desglose de probabilidades

## 📊 Endpoints API

### GET `/health`
Verifica el estado del servidor y si el modelo está cargado.

**Respuesta:**
```json
{
    "status": "ok",
    "model_loaded": true
}
```

### POST `/predict`
Realiza una predicción basada en una imagen.

**Parámetros:**
- `image` (file): Archivo de imagen

**Respuesta:**
```json
{
    "digit": 5,
    "confidence": 99.87,
    "probabilities": {
        "0": 0.01,
        "1": 0.02,
        "2": 0.05,
        ...
        "5": 99.87,
        ...
        "9": 0.01
    }
}
```

## 🐛 Solución de Problemas

**Problema:** `Error al cargar el modelo`
- **Solución:** Verifica que `cnn_mnist_ruteo_paquetes.keras` esté en la carpeta correcta

**Problema:** `Puerto 5000 ya está en uso`
- **Solución:** Cambia el puerto en `app.py`: `app.run(port=5001)`

**Problema:** `ImportError: No module named 'tensorflow'`
- **Solución:** Instala las dependencias: `pip install -r requirements.txt`

## 💡 Consejos para Mejores Predicciones

1. **Dibuja números claros:** Números grandes y centrados funcionan mejor
2. **Contraste:** Asegúrate de tener buen contraste entre el dígito y el fondo
3. **Tamaño:** Si subes una imagen, asegúrate de que el dígito ocupe la mayor parte de la imagen
4. **Orientación:** Los dígitos deben estar en posición normal



