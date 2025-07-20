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
SEXO_MAP = {'Ma': 1, 'He': 0}
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
    edadHTs = st.selectbox('🗖️ Edad al sacrificio(HTS) (días)', [14, 21, 28, 35])
    edadventa = st.number_input('📦 Edad de venta(Granja) (días)', min_value=0, max_value=5000, value=1000)

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
st.header("Predicción desde Archivo")
st.subheader("Sube un archivo `.csv` o `.xlsx` para predicciones en lote")

st.markdown("El archivo debe contener las siguientes columnas obligatorias:")
st.code("Sexo, Area, Edad HTS, Edad Granja")

archivo = st.file_uploader("Selecciona tu archivo", type=["csv", "xlsx", "xlsm"])

if archivo is not None:
    try:
        # --- PASO 1: LEER EL ARCHIVO DE FORMA SEGURA ---
        if archivo.name.endswith('.csv'):
            # Detección de codificación para evitar errores con caracteres especiales
            raw_data = archivo.read()
            resultado_encoding = chardet.detect(raw_data)
            encoding_detectado = resultado_encoding['encoding'] or 'latin1'
            archivo.seek(0) # Volver al inicio del archivo para que pandas pueda leerlo
            df_subido = pd.read_csv(archivo, encoding=encoding_detectado)
        else:
            df_subido = pd.read_excel(archivo)

        st.markdown("#### ✅ Archivo cargado correctamente. Vista previa de los datos:")
        st.dataframe(df_subido.head())

        # --- PASO 2: VALIDAR Y LIMPIAR EL DATAFRAME ---
        # Normalizar nombres de columnas (eliminar espacios extra)
        df_subido.columns = df_subido.columns.str.strip()
        
        # Verificar que todas las columnas necesarias existan
        columnas_necesarias = ['Sexo', 'Area', 'Edad HTS', 'Edad Granja']
        columnas_faltantes = [col for col in columnas_necesarias if col not in df_subido.columns]

        if columnas_faltantes:
            st.error(f"❌ Error: Faltan las siguientes columnas en el archivo: **{', '.join(columnas_faltantes)}**")
        else:
            # Crear una copia para no alterar el dataframe original que se muestra
            df_procesado = df_subido.copy()

            # Limpiar los datos de las columnas de texto ANTES de mapear
            df_procesado['Sexo'] = df_procesado['Sexo'].astype(str).str.strip()
            df_procesado['Area'] = df_procesado['Area'].astype(str).str.strip()

            # --- PASO 3: APLICAR EL MAPEO ---
            df_procesado['sexo_num'] = df_procesado['Sexo'].map(SEXO_MAP)
            df_procesado['area_num'] = df_procesado['Area'].map(AREA_MAP)

            # --- PASO 4: VALIDACIÓN DETALLADA POST-MAPEO ---
            error_encontrado = False
            # Verificar si hay valores nulos en 'sexo_num' (significa que un valor no se pudo mapear)
            if df_procesado['sexo_num'].isnull().any():
                st.error(f"❌ Error en la columna 'Sexo'. Se encontraron valores no reconocidos.")
                st.info(f"Valores válidos para 'Sexo': **{list(SEXO_MAP.keys())}**. Revisa tu archivo.")
                error_encontrado = True
            
            # Verificar si hay valores nulos en 'area_num'
            if df_procesado['area_num'].isnull().any():
                st.error(f"❌ Error en la columna 'Area'. Se encontraron valores no reconocidos.")
                st.info(f"Valores válidos para 'Area': **{list(AREA_MAP.keys())}**. Revisa tu archivo.")
                error_encontrado = True

            # --- PASO 5: REALIZAR PREDICCIONES SI NO HAY ERRORES ---
            if not error_encontrado:
                st.success("✅ Datos validados correctamente. Realizando predicciones...")

                # Preparar los datos para el modelo en el orden correcto
                input_batch = df_procesado[[
                    'area_num', 
                    'sexo_num', 
                    'Edad HTS', 
                    'Edad Granja'
                ]].values.tolist()

                # Llamar a tu función de predicción
                resultados = predict_all(input_batch)
                resultados_format = formatear_valores(resultados.to_dict(orient='records'))
                
                # Si 'resultados_format' no está vacío y su primer elemento NO es una lista (es un float/int),
                # significa que es el resultado de una sola fila. Lo envolvemos en una lista.
                if resultados_format and not isinstance(resultados_format[0], (list, tuple)):
                    resultados_format = [resultados_format]

                # Crear el DataFrame final con los resultados
                df_resultado = df_subido[columnas_necesarias].copy()
                df_resultado['Nombre Usuario'] = nombre_user if nombre_user else "No especificado"
                df_resultado['Cargo Usuario'] = cargo_user if cargo_user else "No especificado"
                df_resultado['prePorcMort'] = [r[0] for r in resultados_format]
                df_resultado['prePorcCon'] = [r[1] for r in resultados_format]
                df_resultado['preICA'] = [r[2] for r in resultados_format]
                df_resultado['prePeProFin'] = [r[3] for r in resultados_format]

                st.markdown("---")
                st.subheader("📈 Resultados de la Predicción")
                st.dataframe(df_resultado)

                # Opción para descargar los resultados
                csv = df_resultado.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Descargar resultados como CSV",
                    data=csv,
                    file_name=f"predicciones_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime='text/csv'
                )

    except Exception as e:
        st.error(f"❌ Ocurrió un error inesperado al procesar el archivo: {str(e)}")