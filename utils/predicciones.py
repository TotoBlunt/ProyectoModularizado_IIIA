# utils/predicciones.py

import joblib
import pandas as pd
import numpy as np

# --- 1. CARGA ÚNICA Y SEGURA DE MODELOS ---
# Los modelos se cargan una sola vez cuando la aplicación se inicia,
# lo que mejora enormemente el rendimiento.
# Usamos un bloque try-except para dar un error claro si los archivos no se encuentran.

try:
    model_porcMort = joblib.load('modelosPkl/model_porcMort2.pkl')
    model_porcConsumo = joblib.load('modelosPkl/model_porcConsumo2.pkl')
    model_ica = joblib.load('modelosPkl/model_ica2.pkl')
    model_pesoProm = joblib.load('modelosPkl/model_pesoProm2.pkl')
except FileNotFoundError as e:
    print(f"ERROR: No se pudo encontrar un archivo de modelo. {e}")
    print("Asegúrate de que los archivos .pkl estén en la carpeta 'modelosPkl/'.")
    # Si no se cargan los modelos, asignamos None para manejar el error después.
    model_porcMort = model_porcConsumo = model_ica = model_pesoProm = None


def predict_all(data_batch):
    """
    Realiza predicciones en lote para los 4 modelos de forma vectorizada y eficiente.
    Esta función NO interactúa con Streamlit, solo procesa datos.

    Args:
        data_batch (list of lists or numpy array): 
            Un lote de datos donde cada sublista es una fila con las 
            características para la predicción.
            Ejemplo para 1 fila: [[area, sexo, edadHTS, edadVenta]]
            Ejemplo para N filas: [[...], [...], ..., [...]]

    Returns:
        pd.DataFrame: 
            Un DataFrame de Pandas con 4 columnas, una para cada predicción.
            El número de filas del DataFrame será igual al número de filas
            en el 'data_batch' de entrada.
    """
    # --- 2. VERIFICACIÓN DE MODELOS CARGADOS ---
    if model_porcMort is None:
        # Si los modelos no se cargaron, no podemos predecir.
        # Devolvemos un DataFrame vacío para que la app no se caiga.
        return pd.DataFrame()

    # --- 3. PREDICCIONES VECTORIZADAS (LA CORRECCIÓN CLAVE) ---
    # Convertimos la entrada a un array de NumPy para asegurar compatibilidad.
    input_array = np.array(data_batch)

    # Realizamos las predicciones para TODO el lote de datos de una sola vez.
    # Eliminamos el `[0]` para obtener un array completo de predicciones,
    # no solo la primera.
    pred_mort = model_porcMort.predict(input_array)
    pred_consumo = model_porcConsumo.predict(input_array)
    pred_ica = model_ica.predict(input_array)
    pred_peso = model_pesoProm.predict(input_array)

    # **NUEVO: Redondear las predicciones a 2 decimales**
    # Usamos np.round() para redondear los arrays de predicciones.
    pred_mort_redondeado = np.round(pred_mort, 2)
    pred_consumo_redondeado = np.round(pred_consumo, 3)
    pred_ica_redondeado = np.round(pred_ica, 2)
    pred_peso_redondeado = np.round(pred_peso, 3)

    # --- 4. CREACIÓN DEL DATAFRAME DE RESULTADOS ---
    # Creamos un diccionario donde cada clave es el nombre de la columna
    # y cada valor es la lista COMPLETA de predicciones redondeadas.
    resultados_df = pd.DataFrame({
        'prePorcMort': pred_mort_redondeado,
        'prePorcCon': pred_consumo_redondeado,
        'preICA': pred_ica_redondeado,
        'prePeProFin': pred_peso_redondeado
    })



    return resultados_df