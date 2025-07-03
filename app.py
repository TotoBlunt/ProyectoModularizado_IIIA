import joblib
import streamlit as st
import pandas as pd
from xgboost import XGBRegressor
from utils.predicciones import predict_all
from utils.CRUD import crear_prediccion, ver_predicciones_guardadas
from utils.formateoValoresdicy import formatear_valores
import io

# Configuración inicial de session state
if 'predicciones' not in st.session_state:
    st.session_state.predicciones = None
if 'uploaded_data' not in st.session_state:
    st.session_state.uploaded_data = None
if 'resultados_completos' not in st.session_state:
    st.session_state.resultados_completos = None

# Configuración de la aplicación
st.title('Predicción de Parámetros Avícolas')
st.subheader('Predicciones de Mortalidad, Consumo, ICA y Peso Promedio Final')

# Mapeos
SEXO_MAP = {'Macho': 1, 'Hembra': 0}
AREA_MAP = {
    'Calidad': 1, 'I. Respiratoria': 2, 'S. esquelético': 3,
    'I. Intestinal': 4, 'Coccidia': 5, 'C. tóxico': 6,
    'C. metabólico': 7, 'S. Inmunitario': 8
}

# Columnas requeridas y mapeo personalizado
REQUIRED_COLUMNS = ['areaAn', 'sexo', 'edadHTs', 'edadventa']
COLUMN_MAPPING = {
    'Sexo': 'sexo',
    'Area': 'areaAn',
    'Edad HTS': 'edadHTs',
    'Edad Granja': 'edadventa'
}

# Opción para elegir el modo de entrada de datos
modo_entrada = st.radio("Seleccione el modo de entrada de datos:",
                        ("Ingreso manual", "Cargar archivo (CSV/Excel)"))

if modo_entrada == "Ingreso manual":
    st.subheader('Ingrese los datos manualmente')
    
    nombre_user = st.text_input('Nombre del usuario*')
    cargo_user = st.text_input('Cargo del usuario*')
    if not nombre_user or not cargo_user:
        st.warning('Por favor, ingrese su nombre y cargo para continuar.')

    col1, col2 = st.columns(2)
    with col1:
        areaAn = st.selectbox('Área de la granja*', list(AREA_MAP.keys()))
        sexo = st.selectbox('Sexo de los pollos*', list(SEXO_MAP.keys()))
    with col2:
        edadHTs = st.selectbox('Edad al sacrificio (días)*', [14, 21, 28, 35])
        edadventa = st.number_input('Edad de venta (días)*', min_value=0, max_value=5000, value=1000)

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

else:  # Modo carga de archivo
    st.subheader('Cargue su archivo con los datos')
    
    nombre_user = st.text_input('Nombre del usuario*')
    cargo_user = st.text_input('Cargo del usuario*')
    if not nombre_user or not cargo_user:
        st.warning('Por favor, ingrese su nombre y cargo para continuar.')
    
    uploaded_file = st.file_uploader("Subir archivo (CSV o Excel)*", type=['csv', 'xlsx'])
    
    if uploaded_file is not None:
        try:
            # Leer el archivo según su extensión
            if uploaded_file.name.endswith('.csv'):
                try:
                    df = pd.read_csv(uploaded_file, encoding='utf-8')
                except UnicodeDecodeError:
                    st.warning("El archivo no está en UTF-8. Usando codificación latin-1...")
                    df = pd.read_csv(uploaded_file, encoding='latin-1')
            else:
                df = pd.read_excel(uploaded_file)
            
            # Renombrar columnas según mapeo
            df.rename(columns=COLUMN_MAPPING, inplace=True)
            
            # Validar columnas requeridas
            missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
            
            if missing_cols:
                st.error(f"Columnas requeridas faltantes: {', '.join(missing_cols)}")
                st.error("Por favor, asegúrese que el archivo contenga las columnas necesarias.")
            else:
                st.session_state.uploaded_data = df
                st.success("¡Archivo cargado y validado correctamente!")
                st.dataframe(df.head())
                
                # Transformar datos según mapeos
                try:
                    df['areaAn'] = df['areaAn'].map(AREA_MAP)
                    df['sexo'] = df['sexo'].map(SEXO_MAP)
                    
                    # Botón para procesar el archivo
                    if st.button('Procesar archivo y realizar predicciones'):
                        input_data = df[REQUIRED_COLUMNS].values.tolist()
                        st.session_state.predicciones = predict_all(input_data)
                        
                        # Unir predicciones con datos originales
                        resultados_completos = pd.concat([df, st.session_state.predicciones], axis=1)
                        st.session_state.resultados_completos = resultados_completos
                        
                        st.success("Predicciones realizadas correctamente para todos los registros!")
                        st.dataframe(resultados_completos)
                        
                        # Botón para descargar resultados
                        csv = resultados_completos.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
                        st.download_button(
                            label="Descargar resultados como CSV",
                            data=csv,
                            file_name='resultados_predicciones.csv',
                            mime='text/csv'
                        )
                        
                except Exception as e:
                    st.error(f"Error al transformar los datos: {str(e)}")
                    st.error("""Asegúrese que:
                    - Los valores en 'Area' coincidan con: Calidad, I. Respiratoria, etc.
                    - Los valores en 'Sexo' sean: Macho o Hembra""")
        
        except Exception as e:
            st.error(f"Error al leer el archivo: {str(e)}")

# Mostrar resultados si existen (para ambos modos)
if st.session_state.predicciones is not None:
    if modo_entrada == "Ingreso manual":
        # Botón para guardar predicciones (solo en modo manual)
        if st.button('Guardar predicciones'):
            # Transformar dataframe predicciones a diccionario
            datos_predichos = formatear_valores(st.session_state.predicciones.to_dict(orient='records'))
            
            datos_ingresados = {
                'nombre': nombre_user,
                'cargo': cargo_user,
                'areaAn': areaAn,
                'sexo': sexo,   
                'edadHTs': edadHTs,
                'edadventa': edadventa,
                'prePorcMort': datos_predichos[0],
                'prePorcCon': datos_predichos[1],
                'preICA': datos_predichos[2],
                'prePeProFin': datos_predichos[3]
            }
            
            try:
                crear_prediccion(datos_ingresados)
                st.success("Predicciones guardadas correctamente en la base de datos!")
            except Exception as e:
                st.error(f"Error al guardar las predicciones: {str(e)}")
    
    if st.button('Ver predicciones guardadas'):
        ver_predicciones_guardadas()
else:
    st.info('Ingrese los datos y haga clic en "Realizar todas las predicciones" o cargue un archivo válido')