def formatear_valores(datos_predichos, decimales=2):
    return [round(float(item['Valor']), decimales) for item in datos_predichos]