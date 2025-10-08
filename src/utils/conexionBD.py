#Librerias para la conexión a Supabase
import os
from supabase import create_client, Client
import streamlit as st

# Obtener las variables de entorno  
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
#funcion para crear el cliente de supabase
def init_supabase() -> Client:
    """
    Inicializa el cliente de Supabase y lo almacena en st.session_state.
    Así, la conexión persiste a través de los reruns de Streamlit.
    """
    if "supabase_client" not in st.session_state:
        
        SUPABASE_URL = os.getenv("SUPABASE_URL")
        SUPABASE_KEY = os.getenv("SUPABASE_KEY")
        if not SUPABASE_URL or not SUPABASE_KEY:
            st.error("Por favor, configura las variables de entorno SUPABASE_URL y SUPABASE_KEY.")
            st.stop()

        try:
            st.session_state.supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
            st.success("Conexión a Supabase establecida.")
        except Exception as e:
            st.error(f"Error al conectar con Supabase: {e}")
            st.stop()
    return st.session_state.supabase_client