def formatear_valores(datos_predichos, decimales=4):
    return [round(float(item['Valor']), decimales) for item in datos_predichos]