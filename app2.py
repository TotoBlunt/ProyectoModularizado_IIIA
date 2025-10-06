import streamlit as st
import pandas as pd
import numpy as np
import joblib
import tensorflow as tf
from tensorflow.keras.models import load_model

# ====================================================================
# CONFIGURACIÓN Y CARGA DE RECURSOS (USANDO CACHING DE STREAMLIT)
# ====================================================================

# Títulos de las variables de entrada y salida
FEATURES = [
    'PorcMortSem4','PorcMortSem5', 'PorcMortSem6','PesoSem4', 'PesoSem5', 'Pob Inicial',
    'Edad HTS', 'Edad Granja', 'Area'
]

TARGETS = ['Peso Prom. Final', 'Porc Consumo', 'ICA', 'Por_Mort._Final']

# @st.cache_resource asegura que el modelo y los escaladores se carguen solo una vez
@st.cache_resource
def load_resources():
    """Carga el modelo y los escaladores para evitar recargas constantes."""
    try:
        model = load_model("modelosPkl/modelo_9vars_multisalida.keras")
        X_scaler = joblib.load("modelosPkl/X_scaler_9vars.pkl")
        y_scaler = joblib.load("modelosPkl/y_scaler_4targets.pkl")
        
        le_area = None
        area_options = None
        try:
            le_area = joblib.load("modelosPkl/label_encoder_tipo_area.pkl")
            area_options = le_area.classes_
        except FileNotFoundError:
            # Si el encoder no existe, Area se maneja como numérica si el usuario la ingresa.
            pass
            
        return model, X_scaler, y_scaler, le_area, area_options
    except FileNotFoundError as e:
        st.error(f"Error: No se encontró el archivo necesario para el despliegue: {e}. Asegúrese de que todos los archivos (.keras, .pkl) están presentes.")
        return None, None, None, None, None

# Cargar todos los recursos al inicio
model, X_scaler, y_scaler, le_area, AREA_OPTIONS = load_resources()

# ====================================================================
# FUNCIÓN DE PREDICCIÓN (DEBE SER MUY EFICIENTE)
# ====================================================================

def predict(input_data_dict):
    """Procesa los datos de entrada, escala, predice e invierte la escala."""
    
    # 1. Convertir a DataFrame en el orden correcto
    df_input = pd.DataFrame([input_data_dict], columns=FEATURES)
    
    # 2. ESCALAR la entrada (X)
    X_input_scaled = X_scaler.transform(df_input)
    
    # 3. PREDICCIÓN
    y_pred_scaled = model.predict(X_input_scaled, verbose=0)
    
    # 4. INVERTIR la predicción (Y) a la escala original
    y_pred_original = y_scaler.inverse_transform(y_pred_scaled)[0]
    
    return y_pred_original

# ====================================================================
# INTERFAZ STREAMLIT
# ====================================================================

st.set_page_config(
    page_title="Predictor MLP Multisalida",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título y descripción
st.title("🧠 Predictor de Rendimiento Acuícola con Redes Neuronales")
st.markdown("---")
st.markdown("Utilice el formulario a continuación para ingresar los parámetros de **9 variables de entrada** y obtener la predicción de **4 variables de rendimiento** mediante un modelo MLP optimizado.")


if model is None:
    st.stop() # Detiene la ejecución si los archivos no se cargaron correctamente

# 1. Crear el formulario principal
with st.form("prediction_form"):
    
    st.header("Datos de Entrada")
    
    # Usar columnas para una entrada más compacta (3 columnas)
    cols = st.columns(3)
    input_values = {}
    
    # Iterar sobre las variables y crear widgets
    for i, feature in enumerate(FEATURES):
        col_index = i % 3 # Determina en qué columna va el widget
        
        if feature == 'Area' and AREA_OPTIONS is not None:
            # Para la variable categórica 'Area', usamos un selectbox
            with cols[col_index]:
                selected_area = st.selectbox(
                    f"**{feature}** (Categoría de Lote)",
                    options=AREA_OPTIONS,
                    key=f'input_{feature}'
                )
                # Almacenar el valor CODIFICADO que el modelo espera
                input_values[feature] = le_area.transform([selected_area])[0]
        else:
            # Para las variables numéricas, usamos number_input
            with cols[col_index]:
                # Asumiendo que la mayoría son floats, usamos un formato genérico
                value = st.number_input(
                    f"**{feature}**",
                    value=0.0,
                    step=0.01,
                    key=f'input_{feature}'
                )
                input_values[feature] = value

    # Botón de envío del formulario
    st.markdown("---")
    submitted = st.form_submit_button("🚀 Predecir Resultados", type="primary")

# 2. Mostrar los resultados después de la predicción
if submitted:
    # Usar un spinner para mejorar la experiencia de usuario
    with st.spinner('Calculando predicciones...'):
        
        # 1. Realizar la predicción
        predictions = predict(input_values)
        
        st.success("✅ Predicción Completada")
        
        st.header("Resultados de la Predicción")
        
        # 2. Usar métricas para un resultado visual y claro
        result_cols = st.columns(4)
        
        for i, target_name in enumerate(TARGETS):
            value = predictions[i]
            
            # Usamos st.metric para un display de número grande y profesional
            with result_cols[i]:
                st.metric(label=target_name, value=f"{value:.4f}")
        
        st.markdown("---")
        st.subheader("Detalle de los Resultados")
        
        # 3. Mostrar los resultados en una tabla para un resumen rápido
        results_df = pd.DataFrame({
            'Variable': TARGETS,
            'Valor Predicho': [f"{v:.4f}" for v in predictions]
        })
        st.table(results_df.set_index('Variable'))
        
        st.balloons() # Pequeña celebración visual para el usuario
