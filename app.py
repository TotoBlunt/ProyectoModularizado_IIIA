import joblib
import streamlit as st
import pandas as pd
from xgboost import XGBRegressor
from utils.predicciones import predict_all
from utils.CRUD import crear_prediccion

# Configuración inicial de session state
if 'predicciones' not in st.session_state:
    st.session_state.predicciones = None

# Configuración de la aplicación
st.title('Predicción de Parámetros Avícolas')
st.subheader('Predicciones de Mortalidad, Consumo, ICA y Peso Promedio Final')
st.subheader('Ingrese los datos para realizar las predicciones')

# Mapeos
SEXO_MAP = {'Macho': 1, 'Hembra': 0}
AREA_MAP = {
    'Calidad': 1, 'I. Respiratoria': 2, 'S. esquelético': 3,
    'I. Intestinal': 4, 'Coccidia': 5, 'C. tóxico': 6,
    'C. metabólico': 7, 'S. Inmunitario': 8
}

# Entrada de datos
nombre_user = st.text_input('Nombre del usuario')
cargo_user = st.text_input('Cargo del usuario')
if not nombre_user or not cargo_user:
    st.warning('Por favor, ingrese su nombre y cargo para continuar.')

col1, col2 = st.columns(2)
with col1:
    areaAn = st.selectbox('Área de la granja', list(AREA_MAP.keys()))
    sexo = st.selectbox('Sexo de los pollos', list(SEXO_MAP.keys()))
with col2:
    edadHTs = st.selectbox('Edad al sacrificio (días)', [14, 21, 28, 35])
    edadventa = st.number_input('Edad de venta (días)', min_value=0, max_value=5000, value=1000)

# Transformación de datos
datos_prediccion = {
    'areaAn': AREA_MAP.get(areaAn),
    'sexo': SEXO_MAP.get(sexo),
    'edadHTs': edadHTs,
    'edadventa': edadventa
}

input_data = [[datos_prediccion['areaAn'], datos_prediccion['sexo'], 
            datos_prediccion['edadHTs'], datos_prediccion['edadventa']]]

# Botón para realizar todas las predicciones
if st.button('Realizar todas las predicciones'):
    # Realizar predicciones
    st.session_state.predicciones = predict_all(input_data)
    st.success("Predicciones realizadas correctamente!")
    
# Mostrar resultados si existen
if st.session_state.predicciones is not None:
    #st.write("Resultados de las predicciones:")
    #st.dataframe(st.session_state.predicciones)
    
    # Botón para guardar predicciones
    if st.button('Guardar predicciones'):
        # Transformar dataframe predicciones a diccionario
        datos_predichos = round(st.session_state.predicciones.to_dict(orient='records'),4)
        datos_ingresados = {
            'nombre': nombre_user,
            'cargo': cargo_user,
            'areaAn': areaAn,
            'sexo': sexo,   
            'edadHTs': edadHTs,
            'edadventa': edadventa,
            'prePorcMort': datos_predichos[0]['Valor'],
            'prePorcCon': datos_predichos[1]['Valor'],
            'preICA': datos_predichos[2]['Valor'],
            'prePeProFin': datos_predichos[3]['Valor']

        }
        # Concatenar los diccionarios
        #datos_supabase = {**datos_ingresados, **datos_predichos}
        st.write("Datos a guardar:", datos_ingresados)
        # Guardar las predicciones en la base de datos
        #try:
            #crear_prediccion(datos_supabase)
            #st.success("Predicciones guardadas correctamente en la base de datos!")
        #except Exception as e:
            #st.error(f"Error al guardar las predicciones: {str(e)}")
else:
    st.info('Ingrese los datos y haga clic en "Realizar todas las predicciones"')