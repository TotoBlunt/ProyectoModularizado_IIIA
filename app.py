import joblib
import streamlit as st
import pandas as pd
from xgboost import XGBRegressor
from utils.predicciones import predict_all
from utils.CRUD import crear_prediccion

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
    predicciones = predict_all(input_data)

else:
    st.info('Ingrese los datos y haga clic en el botón para realizar las predicciones.')
    
#Datos para guardar en la base de datos
#Tranformar dataframe predicciones a diccionario
datos_predicciones = predicciones.to_dict(orient='records')[0]
datos_ingresados = {
    'nombre': nombre_user,
    'cargo': cargo_user,
    'areaGranja': areaAn,
    'sexo': sexo,   
    'EdadSacrificio': edadHTs,
    'EdadVenta': edadventa
}
#Concatenar los diccionarios
datos_supabase = {**datos_ingresados, **datos_predicciones}

    
if st.button('Guardar predicciones'):
    # Guardar las predicciones en la base de datos
    crear_prediccion(datos_supabase)
