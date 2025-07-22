# 🐔 Sistema Inteligente de Predicción de Parámetros Avícolas

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://proypro3a.streamlit.app/)


Este proyecto es una aplicación web interactiva desarrollada en Python con Streamlit, diseñada para optimizar la producción avícola mediante la predicción de Indicadores Clave de Rendimiento (KPIs). La herramienta permite a los productores, veterinarios y administradores de granjas tomar decisiones informadas basadas en datos para mejorar la eficiencia y rentabilidad.


---

## 📋 Características Principales

*   **Predicción de 4 KPIs Críticos:**
    *   Porcentaje de Mortalidad
    *   Porcentaje de Consumo de Alimento
    *   Índice de Conversión Alimenticia (ICA)
    *   Peso Promedio Final
*   **Doble Modo de Operación:**
    1.  **Predicción Manual:** Ingresa los datos de un solo lote a través de un formulario intuitivo.
    2.  **Predicción por Lote:** Sube un archivo CSV o Excel con datos de múltiples lotes para obtener predicciones masivas de forma instantánea.
*   **Persistencia de Datos:** Guarda los resultados de las predicciones manuales en una base de datos **Supabase** para un seguimiento y análisis histórico.
*   **Interfaz de Usuario Amigable:** Desarrollada con Streamlit para una experiencia de usuario limpia y fácil de usar.
*   **Descarga de Resultados:** Exporta las predicciones por lote a un archivo CSV con un solo clic.

---

## 🛠️ Tecnologías Utilizadas

*   **Lenguaje:** Python 3.9+
*   **Framework Web:** Streamlit
*   **Machine Learning:** Scikit-learn, XGBoost
*   **Análisis de Datos:** Pandas, NumPy
*   **Base de Datos:** Supabase (PostgreSQL)
*   **Manejo de Fechas:** Pytz
*   **Dependencias:** Joblib, Chardet

---

## 🚀 Instalación y Puesta en Marcha

Sigue estos pasos para ejecutar el proyecto en tu máquina local.

### Prerrequisitos

*   Python 3.9 o superior
*   Git

### 1. Clonar el Repositorio
```bash
git clone https://github.com/TotoBlunt/ProyectoModularizado_IIIA.git
cd ProyectoModularizado_IIIA
```
### 2.Crear un Entorno Virtual(Recomendado)
```bash
# Crear el entorno
python -m venv venv

# Activar el entorno
# En Windows:
venv\Scripts\activate
# En macOS/Linux:
source venv/bin/activate
```
### 3.Instalar Dependencias
Asegúrate de tener un archivo requirements.txt en tu proyecto. Si no lo tienes, puedes generarlo con pip freeze > requirements.txt.
```bash
pip install -r requirements.txt
```
### 4. Configurar Variables de Entorno
Para conectarse a Supabase, la aplicación necesita credenciales que no deben estar escritas directamente en el código.
1.Crea un archivo llamado .env en la raíz del proyecto.
2.Copia el contenido del archivo .env.example (si no lo tienes, usa esta plantilla) y pégalo en tu nuevo archivo .env:
```bash
# .env
SUPABASE_URL="TU_URL_DEL_PROYECTO_SUPABASE"
SUPABASE_KEY="TU_CLAVE_ANON_PUBLIC_DE_SUPABASE"
```
3.Reemplaza los valores con tus credenciales reales de supabase.
Importante: Asegúrate de que tu archivo .gitignore contenga la línea venv/ y .env para no subir el entorno virtual ni tus credenciales secretas a GitHub.
O ingresa las credenciales directamente en la plataforma de Streamlit(Secrets)

### 5.Ejecutar Aplicación
Una vez instaladas las dependencias y configurado el entorno, inicia la aplicación con Streamlit:
```bash
streamlit run tu_archivo_principal.py
```
(Reemplaza tu_archivo_principal.py con el nombre real de tu script principal, por ejemplo, app.py)

## 📈 Uso de la Aplicación

### Predicción Manual
1.Ingresa tu nombre y cargo.
2.Selecciona los parámetros del lote (Área, Sexo, Edad HTS, etc.) en los formularios.
3.Haz clic en "Realizar Predicción Manual".
4.Los resultados aparecerán en pantalla.
5.Selecciona "Supabase" o "Sharepoint" como destino y haz clic en "Guardar predicciones" para almacenar el registro.
### Predicción por Archivo
1.En la sección "Predicción desde Archivo", haz clic en "Selecciona tu archivo".
2.Sube un archivo CSV o Excel que contenga las columnas obligatorias: Sexo, Area, Edad HTS, Edad Granja.
3.La aplicación procesará el archivo y mostrará una tabla con los resultados.
4.Haz clic en "Descargar resultados como CSV" para guardar el archivo con las predicciones.

## 🗃️ Estructura del Proyecto
```bash
.
├── tu_archivo_principal.py    # Script principal de Streamlit
├── modelosPkl/                # Carpeta donde se guardan los modelos .pkl/.joblib
│   ├── modelo_ica2.pkl
│   ├── modelo_pesoProm2.pkl
│   ├── modelo_porcConsumo2.pkl
│   └── modelo_porcMort2.pkl
├── utils/                     # Módulos con lógica de negocio separada
│   ├── CRUD.py                # Funciones para guardar,leer, eliminar las predicciones
│   ├── conexionBD.py          # Funcion para interactuar con Supabase
│   ├── formateoValoresdicy.py # Funcion para Formatear los valores decimales
│   ├── sharepointUtill.py     #Funcion para realizar la conexion son SharePoint
│   └── predicciones.py        # Función predict_all()
├── .gitignore                 # Archivos y carpetas a ignorar por Git
└── requirements.txt           # Lista de dependencias de Python
```

## 📄 Licencia
Este proyecto está bajo la Licencia MIT. Consulta el archivo LICENSE para más detalles.

## 👤 Autores
JoseLonga - 
