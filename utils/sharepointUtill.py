# utils/sharepoint_utils.py

import io
import pandas as pd
from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.files.file import File

def append_a_excel_existente(site_url, username, password, carpeta_relativa, nombre_archivo_destino, df_nuevo):
    """
    Agrega una nueva fila a un archivo Excel existente en SharePoint.
    Si el archivo no existe, lo crea.
    """
    ctx_auth = AuthenticationContext(site_url)
    if not ctx_auth.acquire_token_for_user(username, password):
        return False, "Error de autenticación"

    ctx = ClientContext(site_url, ctx_auth)
    folder = ctx.web.get_folder_by_server_relative_url(carpeta_relativa)
    file_url = f"{carpeta_relativa}/{nombre_archivo_destino}"
    
    try:
        # Intentar descargar el archivo existente
        response = File.open_binary(ctx, file_url)
        bytes_file_obj = io.BytesIO()
        bytes_file_obj.write(response.content)
        bytes_file_obj.seek(0)

        df_existente = pd.read_excel(bytes_file_obj)
        df_final = pd.concat([df_existente, df_nuevo], ignore_index=True)
    except Exception:
        # Si no existe, usamos solo el nuevo
        df_final = df_nuevo

    # Guardar nuevo DataFrame en memoria
    output = io.BytesIO()
    df_final.to_excel(output, index=False)
    output.seek(0)

    # Subir el archivo actualizado
    File.save_binary(folder.upload_file(nombre_archivo_destino, output.read()).execute_query())
    return True, "Archivo actualizado correctamente"
