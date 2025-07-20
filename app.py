import streamlit as st
import pandas as pd
from datetime import datetime
import chardet
from utils.predicciones import predict_all
from utils.CRUD import crear_prediccion, ver_predicciones_guardadas
from utils.formateoValoresdicy import formatear_valores
from utils.sharepointUtill import append_a_excel_existente
import io
# Configuración inicial de session state
if 'predicciones' not in st.session_state:
    st.session_state.predicciones = None

# Configuración de la aplicación
st.title('🐥 Predicción de Parámetros Avícolas')
st.subheader('Predicciones de Mortalidad, Consumo, ICA y Peso Promedio Final')
st.subheader('Ingrese los datos para realizar las predicciones')



# Mapeos
SEXO_MAP = {'Macho': 1, 'Hembra': 0}
AREA_MAP = {
    'Calidad': 1, 'I. Respiratoria': 2, 'S. esquelético': 3,
    'I. Intestinal': 4, 'Coccidia': 5, 'C. tóxico': 6,
    'C. metabólico': 7, 'S. Inmunitario': 8
}

# Entrada de datos manuales
nombre_user = st.text_input('👤 Nombre del usuario')
cargo_user = st.text_input('💼 Cargo del usuario')
if not nombre_user or not cargo_user:
    st.warning('Por favor, ingrese su nombre y cargo para continuar.')

col1, col2 = st.columns(2)
with col1:
    areaAn = st.selectbox('📍 Área de la granja', list(AREA_MAP.keys()))
    sexo = st.selectbox('🐔 Sexo de los pollos', list(SEXO_MAP.keys()))
with col2:
    edadHTs = st.selectbox('🗖️ Edad al sacrificio (días)', [14, 21, 28, 35])
    edadventa = st.number_input('📦 Edad de venta (días)', min_value=0, max_value=5000, value=1000)

# Transformación de datos
datos_prediccion = {
    'areaAn': AREA_MAP.get(areaAn),
    'sexo': SEXO_MAP.get(sexo),
    'edadHTs': edadHTs,
    'edadventa': edadventa
}

input_data = [[
    datos_prediccion['areaAn'],
    datos_prediccion['sexo'],
    datos_prediccion['edadHTs'],
    datos_prediccion['edadventa']
]]

# Botón para realizar todas las predicciones
if st.button('🔮 Realizar todas las predicciones'):
    st.session_state.predicciones = predict_all(input_data)
    st.success("✅ Predicciones realizadas correctamente!")

# Mostrar resultados si existen
if st.session_state.predicciones is not None:
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

    st.write("📊 Datos a guardar:")
    st.dataframe(pd.DataFrame([datos_ingresados]))

    st.markdown("### 📂 Elige dónde guardar los datos")
    opcion_guardado = st.radio("Destino:", ["Supabase", "SharePoint"])

    if opcion_guardado == "SharePoint":
        st.markdown("#### 🔐 Credenciales de SharePoint")
        site_url = st.text_input("URL del sitio (ej. https://empresa.sharepoint.com/sites/tu-sitio)")
        carpeta_relativa = st.text_input("Ruta relativa de carpeta (ej. /sites/tu-sitio/Shared Documents)")
        username = st.text_input("Correo SharePoint", placeholder="ej. jose@empresa.com")
        password = st.text_input("Contraseña", type="password")

    if st.button("📂 Guardar predicciones"):
        if opcion_guardado == "Supabase":
            try:
                crear_prediccion(datos_ingresados)
                st.success("✅ Predicciones guardadas correctamente en Supabase.")
            except Exception as e:
                st.error(f"❌ Error al guardar en Supabase: {str(e)}")
        elif opcion_guardado == "SharePoint":
            try:
                df = pd.DataFrame([datos_ingresados])
                st.markdown("#### 📄 Vista previa del archivo a subir:")
                st.dataframe(df)

                if st.button("📤 Confirmar subida a SharePoint"):
                    exito, mensaje = append_a_excel_existente(
                        site_url=site_url,
                        username=username,
                        password=password,
                        carpeta_relativa=carpeta_relativa,
                        nombre_archivo_destino="predicciones.xlsx",
                        df_nuevo=df
                    )
                    if exito:
                        st.success(f"✅ {mensaje}")
                    else:
                        st.error(f"❌ {mensaje}")
            except Exception as e:
                st.error(f"❌ Error inesperado: {str(e)}")

    if st.button('🔍 Verificar predicciones'):
        ver_predicciones_guardadas()
else:
    st.info('Ingrese los datos y haga clic en "Realizar todas las predicciones"')

# ============================
# Predicción desde archivo
# ============================

st.markdown("---")
st.markdown("## 📁 Predicción desde archivo CSV o Excel")

st.markdown("Sube un archivo `.csv` o `.xlsx` con las siguientes columnas obligatorias:")
st.code("['Sexo', 'Area', 'Edad HTS', 'Edad Granja']")

archivo = st.file_uploader("Selecciona tu archivo", type=["csv", "xlsx","xlsm"])


if archivo is not None:
    try:
        if archivo.name.endswith('.csv'):
            raw_data = archivo.read()
            resultado_encoding = chardet.detect(raw_data)
            encoding_detectado = resultado_encoding['encoding'] or 'latin1'
            archivo.seek(0)
            df_subido = pd.read_csv(archivo, encoding=encoding_detectado)
        else:
            df_subido = pd.read_excel(archivo)
        df_subido.columns = df_subido.columns.str.strip()  # <- nueva línea para normalizar

        columnas_necesarias = ['Sexo', 'Area', 'Edad HTS', 'Edad Granja']
        if not all(col in df_subido.columns for col in columnas_necesarias):
            faltantes = list(set(columnas_necesarias) - set(df_subido.columns))
            st.write("Columnas detectadas:", df_subido.columns.tolist())  # para depurar
            st.error(f"⚠️ El archivo no contiene las siguientes columnas necesarias: {faltantes}")
        else:
            df_subido['sexo'] = df_subido['Sexo'].map(SEXO_MAP)
            df_subido['areaAn'] = df_subido['Area'].map(AREA_MAP)
            df_subido['edadHTs'] = df_subido['Edad HTS']
            df_subido['edadventa'] = df_subido['Edad Granja']

            if df_subido[['sexo', 'areaAn']].isnull().any().any():
                st.error("⚠️ Hay valores no reconocidos en las columnas 'Sexo' o 'Area'. Verifica que sean válidos.")
            else:
                input_batch = df_subido[['areaAn', 'sexo', 'edadHTs', 'edadventa']].values.tolist()
                resultados = predict_all(input_batch)
                resultados_format = formatear_valores(resultados.to_dict(orient='records'))

                df_resultado = df_subido[columnas_necesarias].copy()
                df_resultado['Nombre Usuario'] = nombre_user
                df_resultado['Cargo Usuario'] = cargo_user
                df_resultado['prePorcMort'] = [r[0] for r in resultados_format]
                df_resultado['prePorcCon'] = [r[1] for r in resultados_format]
                df_resultado['preICA'] = [r[2] for r in resultados_format]
                df_resultado['prePeProFin'] = [r[3] for r in resultados_format]

                st.success("✅ Predicciones realizadas correctamente para el archivo cargado.")
                st.dataframe(df_resultado)

                csv = df_resultado.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📅 Descargar resultados como CSV",
                    data=csv,
                    file_name=f"predicciones_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime='text/csv'
                )

    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {str(e)}")