import joblib
import streamlit as st
import pandas as pd
from xgboost import XGBRegressor

# Cargar modelos
model_porcMort = joblib.load('modelosPkl/model_porcMort2.pkl')
model_porcConsumo = joblib.load('modelosPkl/model_porcConsumo2.pkl')
model_ica = joblib.load('modelosPkl/model_ica2.pkl')
model_pesoProm = joblib.load('modelosPkl/model_pesoProm2.pkl')

# Funciones de predicción
def predict_porcMort(X):
    return model_porcMort.predict(X)

def predict_porcConsumo(X):
    return model_porcConsumo.predict(X)

def predict_ica(X):
    return model_ica.predict(X)

def predict_pesoProm(X):
    return model_pesoProm.predict(X)

def predict_all(X):
    porcMort = predict_porcMort(X)
    porcConsumo = predict_porcConsumo(X)
    ica = predict_ica(X)
    pesoProm = predict_pesoProm(X)
    # Realizar predicciones
    resultados = {
        'Porcentaje de Mortalidad': predict_porcMort(X)[0],
        'Porcentaje de Consumo': predict_porcConsumo(X)[0],
        'ICA': predict_ica(X)[0],
        'Peso Promedio Final': predict_pesoProm(X)[0]
    }
    
    # Crear DataFrame con los resultados
    df_resultados = pd.DataFrame.from_dict(resultados, orient='index', columns=['Valor'])
    
    # Mostrar resultados
    st.subheader('Resultados de las Predicciones')
    st.dataframe(df_resultados.style.format({'Valor': '{:.2f}'}), use_container_width=True)
    st.success('Predicciones realizadas con éxito!')
    return df_resultados