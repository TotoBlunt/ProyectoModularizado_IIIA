import supabase
from src.utils.conexionBD import init_supabase
import os
import streamlit as st
import json
from supabase import create_client, Client
import pandas as pd

Client = init_supabase()

def crear_prediccion(predicction_data):
    st.subheader('Ingresando registro...')
    try:
        
        # Convertir el diccionario a JSON
        #json_data = json.loads(predicction_data)  # json.dumps crea el formato correcto
        #st.write("Datos en formato JSON_loads:", json_data)

        # Insertar datos en Supabase
        # Agrega este código para verificar el esquema de tu tabla
        response = Client.table('predicciones').insert(predicction_data).execute()

        # Mostrar la respuesta completa para depuración (opcional)
        #st.write("Respuesta de Supabase:", response)

        # Verificar si la operación fue exitosa
        if response.data:
            st.success('Registro creado con éxito')
        elif response.error:
            st.error(f"Error al crear el registro: {response.error}")
        else:
            st.error("Respuesta inesperada de Supabase")

    except Exception as e:
        st.error(e)

def ver_predicciones_guardadas():
    """
    Muestra las predicciones almacenadas en Supabase en formato de tabla
    """
    
    # 1. Consulta a la base de datos
    try:
        response = Client.table('predicciones').select("*").order("created_at", desc=True).execute()
        
        if not response.data:
            st.warning("No hay predicciones almacenadas aún")
            return
        
        # 3. Convertir a DataFrame y formatear
        df = pd.DataFrame(response.data)
        
        # Formatear columnas numéricas a 4 decimales
        columnas_numericas = ['prePorcMort', 'prePorcCon', 'preICA', 'prePeProFin']
        for col in columnas_numericas:
            if col in df.columns:
                df[col] = df[col].round(2)
        
        # 4. Mostrar en Streamlit
        st.subheader("📊 Predicciones Guardadas")
        st.dataframe(
            df,
            use_container_width=True,
            column_config={
                "created_at": st.column_config.DatetimeColumn("Fecha creación"),
                "prePorcMort": "Mortalidad (%)",
                "prePorcCon": "Consumo (%)",
                "preICA": "ICA",
                "prePeProFin": "Peso Final (kg)"
            }
        )
        
        # 5. Opción para descargar
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "⬇️ Descargar datos",
            data=csv,
            file_name="predicciones_avicolas.csv",
            mime="text/csv"
        )
        
    except Exception as e:
        st.error(f"Error al cargar predicciones: {str(e)}")

def listar_registros():
    st.subheader('Registros:')
    try:
        # Obtener los datos de la tabla 'datos_predicciones'
        response = Client.table('predicciones').select('*').execute()
        
        # Verificar si la respuesta contiene datos
        if response.data:
            # Mostrar los datos en una tabla en Streamlit
            st.table(response.data)
        else:
            st.write("No hay registros para mostrar.")
    
    except Exception as e:
        st.error(f"Ocurrió un error al listar los registros: {e}")

def eliminar_prediccion_rpc(prediccion_id):
    """
    Llama a la función almacenada en Supabase para eliminar un registro por ID.
    
    :param prediccion_id: ID del registro a eliminar.
    :return: True si se eliminó correctamente, False en caso contrario.
    """
    try:
        # Llamar a la función RPC para eliminar el registro
        response = Client.rpc('eliminar_prediccion', {'prediccion_id': prediccion_id})

        # Verificar si el código de estado es 200 o 204, que indican éxito
        if response.status_code in [200, 204]:
            st.success(f"Registro con ID {prediccion_id} eliminado correctamente.")
            return True
        else:
            # Si no fue exitosa, muestra el código de estado
            st.error(f"Error al eliminar la predicción. Código de estado: {response.status_code}")
            return False
    except Exception as e:
        # Captura cualquier excepción inesperada
        st.error(f"Error inesperado: {e}")
        return False