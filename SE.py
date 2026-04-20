from pathlib import Path
import parametros
import funciones

"""
configsSE()
Función para configurar el ensayo de seguridad eléctrica (SE).
carga del archivo .csv, seleccion del tipo de ensayo y verificación de la fecha de calibración del analizador.
"""
def configsSE():
    print("Seleccione el archivo .csv con los datos del ensayo:")
    parametros.archSE = funciones.solicitar_ruta()
    print("Archivo seleccionado: ", parametros.archSE)
    with open(parametros.archSE, "r", encoding="utf-8") as file:
        lines = file.readlines()

    # Seleccionar el tipo de ensayo
    parametros.opcion = funciones.seleccionar_tipo_ensayo()

    # Verificar y obtener la fecha de calibración del equipo
    # En caso de no existir o ser erronea, se solicita al usuario que ingrese la fecha
    parametros.fluke_calib_date = funciones.verificar_fecha_calibracion(funciones.leer_fecha_calibracion, funciones.guardar_fecha_calibracion)
    
    funciones.recopilar_datos(lines) # Busco y extraigo datos con REGEX

def agregarSE(pdf):

    lines=configsSE() # configs iniciales y lineas del archivo csv
    y = 10
    x = 10
    xmed = 105

    pdf.add_page()
    
    y = pdf.get_y()
    ancho_tot = 287

    # RECUADRO "Realiza el ensayo"
    pdf.set_font("Helvetica", size=10)
    pdf.set_xy(x, y)
    pdf.rect(x, y, 95, 20)  # recuadro sin relleno
    pdf.set_xy(x, y)
    pdf.multi_cell(95, 8, f"Realiza el ensayo: {parametros.nombreTecnico}", border=0, align='L')

    # agrego la fecha almacenada debajo del personal que realiza el ensayo
    y=y+8.75
    pdf.set_xy(x, y)
    y=y-8.75
    for key, value in parametros.data.items():
        if key in ["Fecha"]:
            pdf.cell(0, y/2, f"{key}: {value if value else 'fecha nula'}")


    # RECUADRO para las opciones
    pdf.set_xy(xmed, y)
    pdf.rect(xmed, y, 95, 20)  # Solo borde, sin relleno
    # Opciones de ensayo
    opciones = [
        "Ensayo antes de poner en servicio (valor de referencia)",
        "Ensayo recurrente",
        "Ensayo después de la reparación"
    ]

    # Calculo de la posición para centrar las opciones
    altura_opcion = 6
    alto_recuadro_opciones = 20
    espacio_entre_opciones = (alto_recuadro_opciones - (len(opciones) * altura_opcion)) / 2  # Espacio restante para centrar las opciones

    # Dibujo las opciones con cuadros y mostrar cuál fue seleccionada
    for i, opcion_texto in enumerate(opciones):
        y_pos = y + i * altura_opcion + espacio_entre_opciones
        pdf.set_xy(xmed, y_pos)
        # Dibujar un cuadro vacío al lado de cada opción
        pdf.rect(194, y_pos, 5, 5)  # Cuadro vacío al lado de cada opción
        # Si es la opción seleccionada, "tildar" el cuadro (rellenar)
        if parametros.opcion == str(i + 1):
            pdf.line(194, y_pos, 199, y_pos + 5)  # Línea diagonal de "tilda"
            pdf.line(199, y_pos, 194, y_pos + 5)  # Línea diagonal de "tilda"
        # Escribir el texto de la opción
        pdf.cell(95, altura_opcion, opcion_texto)

    pdf.ln(20)  # siguiente seccion



    # RECUADRO "Datos del equipo"
    pdf.set_font("Helvetica", 'B', size=10)
    y = y + 20 # nueva posicion de y
    pdf.set_xy(x, y)
    pdf.set_line_width(0.8)  # Puedes ajustar este valor según lo grueso que quieras el borde
    pdf.rect(x, y, 190, 8, style='D')  # recuadro 'D' para solo dibujar el borde
    pdf.set_line_width(0.2)  # El valor por defecto suele ser 0.2
    pdf.set_fill_color(220, 220, 220)  # Color gris claro (RGB)
    pdf.rect(x, y, 190, 8, style='F')  # recuadro 'F' para solo relleno
    # texto centrado
    pdf.set_xy(x, y)
    pdf.set_font("Helvetica", 'B', size=10)
    pdf.cell(0, 8, "Datos del equipo", align='C')
    pdf.set_font("Helvetica", size=10)


    # Recuadro izquierdo "Datos del equipo"
    pdf.set_xy(x, y)
    y = y + 8 # nueva posicion de y
    pdf.rect(x, y, 95, 20)  # Solo borde, sin relleno
    pdf.set_xy(x, y+1)
    for key, value in parametros.data.items():
        if key in ["Fabricante", "Modelo", "Código de identificación"]:  # Solo los datos del primer recuadro
            pdf.cell(0, 6, f"{key}: {value if value else 'No aplica'}")
            pdf.set_xy(x, pdf.get_y()+6)    # salto de linea en y

    # Recuadro derecho "Datos del equipo"
    pdf.set_xy(xmed, y)
    pdf.rect(xmed, y, 95, 20)  # Solo borde, sin relleno
    pdf.set_xy(xmed, y+1)
    # Datos extraídos (recuadro derecho)
    for key, value in parametros.data.items():
        if key in ["Número de serie", "Clase de protección", "Ubicación"]:  # Solo los datos del primer recuadro
            pdf.cell(95, 6, f"{key}: {value if value else 'No aplica'}")
            pdf.set_xy(xmed, pdf.get_y()+6)  # salto de linea en y
            
    if parametros.parte_aplicable:
        # RECUADRO "Parte Aplicable"
        y = y + 20 # nueva posicion de y
        pdf.set_xy(x, y)
        pdf.set_line_width(0.8)  # Puedes ajustar este valor según lo grueso que quieras el borde
        pdf.rect(x, y, 190, 8, style='D')  # recuadro 'D' para solo dibujar el borde
        pdf.set_line_width(0.2)  # El valor por defecto suele ser 0.2
        pdf.set_fill_color(220, 220, 220)  # Color gris claro (RGB)
        pdf.rect(x, y, 190, 8, style='F')  # recuadro 'F' para solo relleno
        # texto centrado
        pdf.set_xy(x, y)
        pdf.set_font("Helvetica", 'B', size=10)
        pdf.cell(0, 8, "Parte aplicable", align='C')
        pdf.set_font("Helvetica", size=10)

        # NOMBRE "Parte Aplicable"
        y = y + 8 # nueva posicion de y
        pdf.set_xy(x, y)
        pdf.rect(x, y, 190/3, 8)  # Solo borde, sin relleno
        pdf.set_xy(x, y)
        pdf.cell(190/3, 8, "Nombre", align='C')
        y = y + 8 # nueva posicion de y
        pdf.rect(x, y, 190/3, parametros.pa_index*6+1)  # Solo borde, sin relleno
        pdf.set_xy(x, y+1)
        # Escribo datos extraídos
        for i in range(len(parametros.data["PA nombre"])):
            if parametros.data["PA nombre"][i] is not None:  # Solo agregar si hay datos
                pdf.cell(x, 6, parametros.data["PA nombre"][i])
                pdf.set_xy(x, pdf.get_y()+6)  # salto de linea en y

        # TIPO "Parte Aplicable"
        y = y - 8 # nueva posicion de y
        x = x + 190/3
        pdf.set_xy(x, y)
        pdf.rect(x, y, 190/3, 8)  # Solo borde, sin relleno
        pdf.set_xy(x, y)
        pdf.cell(190/3, 8, "Tipo", align='C')
        y = y + 8 # nueva posicion de y
        pdf.set_xy(x, y)
        pdf.rect(x, y, 190/3, parametros.pa_index*6+1)  # Solo borde, sin relleno
        pdf.set_xy(x, y+1)
        # Escribo datos extraídos
        for i in range(len(parametros.data["PA nombre"])):
            if parametros.data["PA tipo"][i] is not None:  # Solo agregar si hay datos
                pdf.cell(x, 6, parametros.data["PA tipo"][i])
                pdf.set_xy(x, pdf.get_y()+6)  # salto de linea en y

        # NUMERO "Parte Aplicable"
        y = y - 8 # nueva posicion de y
        x = x + 190/3
        pdf.set_xy(x, y)
        pdf.rect(x, y, 190/3, 8)  # Solo borde, sin relleno
        pdf.set_xy(x, y)
        pdf.cell(190/3, 8, "Número", align='C')
        y = y + 8 # nueva posicion de y
        pdf.set_xy(x/3, y)
        pdf.rect(x, y, 190/3, parametros.pa_index*6+1)  # Solo borde, sin relleno
        pdf.set_xy(x, y+1)
        # Escribo datos extraídos
        for i in range(len(parametros.data["PA numero"])):
            if parametros.data["PA numero"][i] is not None:  # Solo agregar si hay datos
                pdf.cell(x, 6, parametros.data["PA numero"][i])
                pdf.set_xy(x, pdf.get_y()+6)  # salto de linea en y
        # acomodo los valores de x, y para seguir trabajando
        y = y + parametros.pa_index*6+1 # nueva posicion de y
        x = x - 190*2/3

        
    else:
        # RECUADRO "Parte Aplicable - No aplica"
        y = y + 20 # nueva posicion de y
        pdf.set_xy(x, y)
        pdf.rect(x, y, 190, 8)  # Solo borde, sin relleno
        pdf.set_xy(x, y)
        pdf.cell(0, 8, "Parte Aplicable - NO APLICA", align='C')
        y = y + 8 # nueva posicion de y
        pdf.set_xy(x, y)



    # RECUADRO "Datos del Analizador"
    pdf.set_xy(x, y)
    pdf.set_line_width(0.8)  # Puedes ajustar este valor según lo grueso que quieras el borde
    pdf.rect(x, y, 190, 8, style='D')  # recuadro 'D' para solo dibujar el borde
    pdf.set_line_width(0.2)  # El valor por defecto suele ser 0.2
    pdf.set_fill_color(220, 220, 220)  # Color gris claro (RGB)
    pdf.rect(x, y, 190, 8, style='F')  # recuadro 'F' para solo relleno
    # texto centrado
    pdf.set_xy(x, y)
    pdf.set_font("Helvetica", 'B', size=10)
    pdf.cell(0, 8, "Datos del Analizador", align='C')
    pdf.set_font("Helvetica", size=10)

    # Recuadro izquierdo "Datos del Analizador"
    y = y + 8 # nueva posicion de y
    pdf.set_xy(x, y)
    pdf.rect(x, y, 95, 20)  # Solo borde, sin relleno
    pdf.set_xy(x, y+1)
    pdf.cell(0, 6, "Fabricante: Fluke")
    pdf.set_xy(x, pdf.get_y()+6)
    pdf.cell(0, 6, "Modelo: ESA-615")
    pdf.set_xy(x, pdf.get_y()+6)
    pdf.cell(0, 6, "Número de serie: 5453505")

    # Recuadro derecho "Datos del Analizador"
    pdf.set_xy(xmed, y)
    pdf.rect(xmed, y, 95, 20)  # Solo borde, sin relleno
    pdf.set_xy(xmed, y+1)
    for key, value in parametros.data.items():
        if key in ["Estándar", "Versión de firmware"]:  # Solo los datos del primer recuadro
            pdf.cell(95, 6, f"{key}: {value if value else '-'}")
            pdf.set_xy(xmed, pdf.get_y()+6)  # salto de linea en y

    # Agrego la línea de "Última calibración"
    pdf.cell(95, 6, f"Última calibración: {parametros.fluke_calib_date if parametros.fluke_calib_date else '-'}")
    pdf.set_xy(xmed, pdf.get_y())  # Desplaza en x para mantener la alineación


    # RECUADRO "Ensayo"
    y = y + 20  # nueva posición de y
    pdf.set_xy(x, y)
    pdf.set_line_width(0.8)  # Puedes ajustar este valor según lo grueso que quieras el borde
    pdf.rect(x, y, 190, 8, style='D')  # recuadro 'D' para solo dibujar el borde
    pdf.set_line_width(0.2)  # El valor por defecto suele ser 0.2
    pdf.set_fill_color(220, 220, 220)  # Color gris claro (RGB)
    pdf.rect(x, y, 190, 8, style='F')  # recuadro 'F' para solo relleno
    # texto centrado
    pdf.set_xy(x, y)
    pdf.set_font("Helvetica", 'B', size=10)
    pdf.cell(0, 8, "Ensayo", align='C')
    pdf.set_font("Helvetica", size=10)
    y = y + 8 # nueva posicion de y
    pdf.set_xy(x, y)


    # RECUADRO "Descripcion de la medida"
    pdf.rect(x, y, 105, 10)  # Solo borde, sin relleno
    pdf.set_xy(x, y)
    limLineY = y
    pdf.cell(105, 10, "Medición", align='C')
    y = y + 10
    pdf.set_xy(x, y+1)
    if parametros.data["Resistencia de protección a tierra"][4] is not None:
        pdf.cell(0, 6, "Resistencia de protección a tierra")
        pdf.set_xy(x, pdf.get_y()+6)
    if parametros.data["Resistencia de aislación entre vivo y tierra"][4] is not None:
        pdf.cell(0, 6, "Resistencia de aislación entre vivo y tierra")
        pdf.set_xy(x, pdf.get_y()+6)
    if parametros.data["Vivo a neutro"][4] is not None:
        pdf.cell(0, 6, "Vivo a neutro")
        pdf.set_xy(x, pdf.get_y()+6)
    if parametros.data["Neutro a tierra"][4] is not None:
        pdf.cell(0, 6, "Neutro a tierra")
        pdf.set_xy(x, pdf.get_y()+6)
    if parametros.data["Vivo a tierra"][4] is not None:
        pdf.cell(0, 6, "Vivo a tierra")
        pdf.set_xy(x, pdf.get_y()+6)
    if parametros.data["Corriente de fuga del chasis a tierra cerrada"][4] is not None:
        pdf.cell(0, 6, "Corriente de fuga del chasis a tierra cerrada")
        pdf.set_xy(x, pdf.get_y()+6)

    if parametros.data["Resistencia de aislación entre vivo y parte aplicable"][4] is not None:
        pdf.cell(0, 6, "Resistencia de aislación entre vivo y parte aplicable")
        pdf.set_xy(x, pdf.get_y()+6)
    if parametros.data["Corriente del equipo"][4] is not None:
        pdf.cell(0, 6, "Corriente del equipo")
        pdf.set_xy(x, pdf.get_y()+6)
    if parametros.data["Corriente de fuga del chasis a tierra abierta"][4] is not None:
        pdf.cell(0, 6, "Corriente de fuga del chasis a tierra abierta")
        pdf.set_xy(x, pdf.get_y()+6)
    if parametros.data["Fuga del chasis a tierra abierta con alimentación invertida"][4] is not None:
        pdf.cell(0, 6, "Fuga del chasis a tierra abierta con alimentación invertida")
        pdf.set_xy(x, pdf.get_y()+6)

    if parametros.pa_index > 0:
        for i in range(parametros.pa_index):
            pdf.cell(0, 6, "Corriente normal " + parametros.data["PA nombre"][i])
            pdf.set_xy(x, pdf.get_y()+6)
            pdf.cell(0, 6, "Corriente invertida " + parametros.data["PA nombre"][i])
            pdf.set_xy(x, pdf.get_y()+6)

    altura_linea = pdf.get_y() - limLineY  # altura desde el inicio hasta la posición actual
    pdf.rect(x, limLineY, 105, altura_linea)  # Solo borde, sin relleno


    # RECUADRO "Valor medido"
    ancho = 18
    y = y - 10
    x = x + 105
    pdf.rect(x, y, ancho, 10)  # Solo borde, sin relleno
    pdf.set_xy(x, y)
    pdf.cell(ancho, 6, "Valor", align='C')
    pdf.set_xy(x, y+4)
    pdf.cell(ancho, 6, "Medido", align='C')
    y = y + 10
    pdf.set_xy(x, y+1)
    if parametros.data["Resistencia de protección a tierra"][4] is not None:
        pdf.cell(ancho, 6, str(parametros.data["Resistencia de protección a tierra"][0]) if parametros.data["Resistencia de protección a tierra"][0] is not None else "-", align='C')
        pdf.set_xy(x, pdf.get_y()+6)
    if parametros.data["Resistencia de aislación entre vivo y tierra"][4] is not None:
        pdf.cell(ancho, 6, str(parametros.data["Resistencia de aislación entre vivo y tierra"][0]) if parametros.data["Resistencia de aislación entre vivo y tierra"][0] is not None else "-", align='C')
        pdf.set_xy(x, pdf.get_y()+6)
    if parametros.data["Vivo a neutro"][4] is not None:
        pdf.cell(ancho, 6, str(parametros.data["Vivo a neutro"][0]) if parametros.data["Vivo a neutro"][0] is not None else "-", align='C')
        pdf.set_xy(x, pdf.get_y()+6)
    if parametros.data["Neutro a tierra"][4] is not None:
        pdf.cell(ancho, 6, str(parametros.data["Neutro a tierra"][0]) if parametros.data["Neutro a tierra"][0] is not None else "-", align='C')
        pdf.set_xy(x, pdf.get_y()+6)
    if parametros.data["Vivo a tierra"][4] is not None:
        pdf.cell(ancho, 6, str(parametros.data["Vivo a tierra"][0]) if parametros.data["Vivo a tierra"][0] is not None else "-", align='C')
        pdf.set_xy(x, pdf.get_y()+6)
    if parametros.data["Corriente de fuga del chasis a tierra cerrada"][4] is not None:
        pdf.cell(ancho, 6, str(parametros.data["Corriente de fuga del chasis a tierra cerrada"][0]) if parametros.data["Corriente de fuga del chasis a tierra cerrada"][0] is not None else "-", align='C')
        pdf.set_xy(x, pdf.get_y()+6)

    if parametros.data["Resistencia de aislación entre vivo y parte aplicable"][4] is not None:
        pdf.cell(ancho, 6, str(parametros.data["Resistencia de aislación entre vivo y parte aplicable"][0]) if parametros.data["Resistencia de aislación entre vivo y parte aplicable"][0] is not None else "-", align='C')
        pdf.set_xy(x, pdf.get_y()+6)
    if parametros.data["Corriente del equipo"][4] is not None:
        pdf.cell(ancho, 6, str(parametros.data["Corriente del equipo"][0]) if parametros.data["Corriente del equipo"][0] is not None else "-", align='C')
        pdf.set_xy(x, pdf.get_y()+6)
    if parametros.data["Corriente de fuga del chasis a tierra abierta"][4] is not None:
        pdf.cell(ancho, 6, str(parametros.data["Corriente de fuga del chasis a tierra abierta"][0]) if parametros.data["Corriente de fuga del chasis a tierra abierta"][0] is not None else "-", align='C')
        pdf.set_xy(x, pdf.get_y()+6)
    if parametros.data["Fuga del chasis a tierra abierta con alimentación invertida"][4] is not None:
        pdf.cell(ancho, 6, str(parametros.data["Fuga del chasis a tierra abierta con alimentación invertida"][0]) if parametros.data["Fuga del chasis a tierra abierta con alimentación invertida"][0] is not None else "-", align='C')
        pdf.set_xy(x, pdf.get_y()+6)

    if parametros.pa_index > 0:
        for i in range(parametros.pa_index):
            pdf.cell(ancho, 6, str(parametros.data["Corriente normal value"][i]) if parametros.data["Corriente normal value"][i] is not None else "-", align='C')
            pdf.set_xy(x, pdf.get_y()+6)
            pdf.cell(ancho, 6, str(parametros.data["Corriente invertida value"][i]) if parametros.data["Corriente invertida value"][i] is not None else "-", align='C')
            pdf.set_xy(x, pdf.get_y()+6)

    pdf.rect(x, limLineY, ancho, altura_linea)  # Solo borde, sin relleno


    # RECUADRO "Unidad"
    y = y - 10
    x = x + ancho
    pdf.rect(x, y, ancho, 10)  # Solo borde, sin relleno
    pdf.set_xy(x, y)
    pdf.cell(ancho, 10, "Unidad", align='C')
    y = y + 10
    pdf.set_xy(x, y+1)
    if parametros.data["Resistencia de protección a tierra"][4] is not None:
        pdf.cell(ancho, 6, str(parametros.data["Resistencia de protección a tierra"][1]) if parametros.data["Resistencia de protección a tierra"][1] is not None else "-", align='C')
        pdf.set_xy(x, pdf.get_y()+6)
    if parametros.data["Resistencia de aislación entre vivo y tierra"][4] is not None:
        pdf.cell(ancho, 6, str(parametros.data["Resistencia de aislación entre vivo y tierra"][1]) if parametros.data["Resistencia de aislación entre vivo y tierra"][1] is not None else "-", align='C')
        pdf.set_xy(x, pdf.get_y()+6)
    if parametros.data["Vivo a neutro"][4] is not None:
        pdf.cell(ancho, 6, str(parametros.data["Vivo a neutro"][1]) if parametros.data["Vivo a neutro"][1] is not None else "-", align='C')
        pdf.set_xy(x, pdf.get_y()+6)
    if parametros.data["Neutro a tierra"][4] is not None:
        pdf.cell(ancho, 6, str(parametros.data["Neutro a tierra"][1]) if parametros.data["Neutro a tierra"][1] is not None else "-", align='C')
        pdf.set_xy(x, pdf.get_y()+6)
    if parametros.data["Vivo a tierra"][4] is not None:
        pdf.cell(ancho, 6, str(parametros.data["Vivo a tierra"][1]) if parametros.data["Vivo a tierra"][1] is not None else "-", align='C')
        pdf.set_xy(x, pdf.get_y()+6)
    if parametros.data["Corriente de fuga del chasis a tierra cerrada"][4] is not None:
        pdf.cell(ancho, 6, str(parametros.data["Corriente de fuga del chasis a tierra cerrada"][1]) if parametros.data["Corriente de fuga del chasis a tierra cerrada"][1] is not None else "-", align='C')
        pdf.set_xy(x, pdf.get_y()+6)

    if parametros.data["Resistencia de aislación entre vivo y parte aplicable"][4] is not None:
        pdf.cell(ancho, 6, str(parametros.data["Resistencia de aislación entre vivo y parte aplicable"][1]) if parametros.data["Resistencia de aislación entre vivo y parte aplicable"][1] is not None else "-", align='C')
        pdf.set_xy(x, pdf.get_y()+6)
    if parametros.data["Corriente del equipo"][4] is not None:
        pdf.cell(ancho, 6, str(parametros.data["Corriente del equipo"][1]) if parametros.data["Corriente del equipo"][1] is not None else "-", align='C')
        pdf.set_xy(x, pdf.get_y()+6)
    if parametros.data["Corriente de fuga del chasis a tierra abierta"][4] is not None:
        pdf.cell(ancho, 6, str(parametros.data["Corriente de fuga del chasis a tierra abierta"][1]) if parametros.data["Corriente de fuga del chasis a tierra abierta"][1] is not None else "-", align='C')
        pdf.set_xy(x, pdf.get_y()+6)
    if parametros.data["Fuga del chasis a tierra abierta con alimentación invertida"][4] is not None:
        pdf.cell(ancho, 6, str(parametros.data["Fuga del chasis a tierra abierta con alimentación invertida"][1]) if parametros.data["Fuga del chasis a tierra abierta con alimentación invertida"][1] is not None else "-", align='C')
        pdf.set_xy(x, pdf.get_y()+6)

    if parametros.pa_index > 0:
        for i in range(parametros.pa_index):
            pdf.cell(ancho, 6, str(parametros.data["Corriente normal unit"][i]) if parametros.data["Corriente normal unit"][i] is not None else "-", align='C')
            pdf.set_xy(x, pdf.get_y()+6)
            pdf.cell(ancho, 6, str(parametros.data["Corriente invertida unit"][i]) if parametros.data["Corriente invertida unit"][i] is not None else "-", align='C')
            pdf.set_xy(x, pdf.get_y()+6)

    pdf.rect(x, limLineY, ancho, altura_linea)  # Solo borde, sin relleno


    # RECUADRO "Limite maximo"
    y = y - 10
    x = x + ancho
    pdf.rect(x, y, ancho, 10)  # Solo borde, sin relleno
    pdf.set_xy(x, y)
    pdf.cell(ancho, 6, "Valor", align='C')
    pdf.set_xy(x, y+4)
    pdf.cell(ancho, 6, "Máximo", align='C')
    y = y + 10
    pdf.set_xy(x, y+1)
    if parametros.data["Resistencia de protección a tierra"][4] is not None:
        pdf.cell(ancho, 6, str(parametros.data["Resistencia de protección a tierra"][2]) if parametros.data["Resistencia de protección a tierra"][2] is not None else "-", align='C')
        pdf.set_xy(x, pdf.get_y()+6)
    if parametros.data["Resistencia de aislación entre vivo y tierra"][4] is not None:
        pdf.cell(ancho, 6, str(parametros.data["Resistencia de aislación entre vivo y tierra"][2]) if parametros.data["Resistencia de aislación entre vivo y tierra"][2] is not None else "-", align='C')
        pdf.set_xy(x, pdf.get_y()+6)
    if parametros.data["Vivo a neutro"][4] is not None:
        pdf.cell(ancho, 6, str(parametros.data["Vivo a neutro"][2]) if parametros.data["Vivo a neutro"][2] is not None else "-", align='C')
        pdf.set_xy(x, pdf.get_y()+6)
    if parametros.data["Neutro a tierra"][4] is not None:
        pdf.cell(ancho, 6, str(parametros.data["Neutro a tierra"][2]) if parametros.data["Neutro a tierra"][2] is not None else "-", align='C')
        pdf.set_xy(x, pdf.get_y()+6)
    if parametros.data["Vivo a tierra"][4] is not None:
        pdf.cell(ancho, 6, str(parametros.data["Vivo a tierra"][2]) if parametros.data["Vivo a tierra"][2] is not None else "-", align='C')
        pdf.set_xy(x, pdf.get_y()+6)
    if parametros.data["Corriente de fuga del chasis a tierra cerrada"][4] is not None:
        pdf.cell(ancho, 6, str(parametros.data["Corriente de fuga del chasis a tierra cerrada"][2]) if parametros.data["Corriente de fuga del chasis a tierra cerrada"][2] is not None else "-", align='C')
        pdf.set_xy(x, pdf.get_y()+6)

    if parametros.data["Resistencia de aislación entre vivo y parte aplicable"][4] is not None:
        pdf.cell(ancho, 6, str(parametros.data["Resistencia de aislación entre vivo y parte aplicable"][2]) if parametros.data["Resistencia de aislación entre vivo y parte aplicable"][2] is not None else "-", align='C')
        pdf.set_xy(x, pdf.get_y()+6)
    if parametros.data["Corriente del equipo"][4] is not None:
        pdf.cell(ancho, 6, str(parametros.data["Corriente del equipo"][2]) if parametros.data["Corriente del equipo"][2] is not None else "-", align='C')
        pdf.set_xy(x, pdf.get_y()+6)
    if parametros.data["Corriente de fuga del chasis a tierra abierta"][4] is not None:
        pdf.cell(ancho, 6, str(parametros.data["Corriente de fuga del chasis a tierra abierta"][2]) if parametros.data["Corriente de fuga del chasis a tierra abierta"][2] is not None else "-", align='C')
        pdf.set_xy(x, pdf.get_y()+6)
    if parametros.data["Fuga del chasis a tierra abierta con alimentación invertida"][4] is not None:
        pdf.cell(ancho, 6, str(parametros.data["Fuga del chasis a tierra abierta con alimentación invertida"][2]) if parametros.data["Fuga del chasis a tierra abierta con alimentación invertida"][2] is not None else "-", align='C')
        pdf.set_xy(x, pdf.get_y()+6)

    if parametros.pa_index > 0:
        for i in range(parametros.pa_index):
            pdf.cell(ancho, 6, str(parametros.data["Corriente normal high"][i]) if parametros.data["Corriente normal high"][i] is not None else "-", align='C')
            pdf.set_xy(x, pdf.get_y()+6)
            pdf.cell(ancho, 6, str(parametros.data["Corriente invertida high"][i]) if parametros.data["Corriente invertida high"][i] is not None else "-", align='C')
            pdf.set_xy(x, pdf.get_y()+6)
        
    pdf.rect(x, limLineY, ancho, altura_linea)  # Solo borde, sin relleno


    # RECUADRO "Limite minimo"
    y = y - 10
    x = x + ancho
    pdf.rect(x, y, ancho, 10)  # Solo borde, sin relleno
    pdf.set_xy(x, y)
    pdf.cell(ancho, 6, "Valor", align='C')
    pdf.set_xy(x, y+4)
    pdf.cell(ancho, 6, "Mínimo", align='C')
    y = y + 10
    pdf.set_xy(x, y+1)
    if parametros.data["Resistencia de protección a tierra"][4] is not None:
        pdf.cell(ancho, 6, str(parametros.data["Resistencia de protección a tierra"][3]) if parametros.data["Resistencia de protección a tierra"][3] is not None else "-", align='C')
        pdf.set_xy(x, pdf.get_y()+6)
    if parametros.data["Resistencia de aislación entre vivo y tierra"][4] is not None:
        pdf.cell(ancho, 6, str(parametros.data["Resistencia de aislación entre vivo y tierra"][3]) if parametros.data["Resistencia de aislación entre vivo y tierra"][3] is not None else "-", align='C')
        pdf.set_xy(x, pdf.get_y()+6)
    if parametros.data["Vivo a neutro"][4] is not None:
        pdf.cell(ancho, 6, str(parametros.data["Vivo a neutro"][3]) if parametros.data["Vivo a neutro"][3] is not None else "-", align='C')
        pdf.set_xy(x, pdf.get_y()+6)
    if parametros.data["Neutro a tierra"][4] is not None:
        pdf.cell(ancho, 6, str(parametros.data["Neutro a tierra"][3]) if parametros.data["Neutro a tierra"][3] is not None else "-", align='C')
        pdf.set_xy(x, pdf.get_y()+6)
    if parametros.data["Vivo a tierra"][4] is not None:
        pdf.cell(ancho, 6, str(parametros.data["Vivo a tierra"][3]) if parametros.data["Vivo a tierra"][3] is not None else "-", align='C')
        pdf.set_xy(x, pdf.get_y()+6)
    if parametros.data["Corriente de fuga del chasis a tierra cerrada"][4] is not None:
        pdf.cell(ancho, 6, str(parametros.data["Corriente de fuga del chasis a tierra cerrada"][3]) if parametros.data["Corriente de fuga del chasis a tierra cerrada"][3] is not None else "-", align='C')
        pdf.set_xy(x, pdf.get_y()+6)

    if parametros.data["Resistencia de aislación entre vivo y parte aplicable"][4] is not None:
        pdf.cell(ancho, 6, str(parametros.data["Resistencia de aislación entre vivo y parte aplicable"][3]) if parametros.data["Resistencia de aislación entre vivo y parte aplicable"][3] is not None else "-", align='C')
        pdf.set_xy(x, pdf.get_y()+6)
    if parametros.data["Corriente del equipo"][4] is not None:
        pdf.cell(ancho, 6, str(parametros.data["Corriente del equipo"][3]) if parametros.data["Corriente del equipo"][3] is not None else "-", align='C')
        pdf.set_xy(x, pdf.get_y()+6)
    if parametros.data["Corriente de fuga del chasis a tierra abierta"][4] is not None:
        pdf.cell(ancho, 6, str(parametros.data["Corriente de fuga del chasis a tierra abierta"][3]) if parametros.data["Corriente de fuga del chasis a tierra abierta"][3] is not None else "-", align='C')
        pdf.set_xy(x, pdf.get_y()+6)
    if parametros.data["Fuga del chasis a tierra abierta con alimentación invertida"][4] is not None:
        pdf.cell(ancho, 6, str(parametros.data["Fuga del chasis a tierra abierta con alimentación invertida"][3]) if parametros.data["Fuga del chasis a tierra abierta con alimentación invertida"][3] is not None else "-", align='C')
        pdf.set_xy(x, pdf.get_y()+6)

    if parametros.pa_index > 0:
        for i in range(parametros.pa_index):
            pdf.cell(ancho, 6, str(parametros.data["Corriente normal low"][i]) if parametros.data["Corriente normal low"][i] is not None else "-", align='C')
            pdf.set_xy(x, pdf.get_y()+6)
            pdf.cell(ancho, 6, str(parametros.data["Corriente invertida low"][i]) if parametros.data["Corriente invertida low"][i] is not None else "-", align='C')
            pdf.set_xy(x, pdf.get_y()+6)

    pdf.rect(x, limLineY, ancho, altura_linea)  # Solo borde, sin relleno


    # RECUADRO "Apto"
    y = y - 10
    x = x + ancho
    pdf.rect(x, y, 200-x, 10)  # Solo borde, sin relleno
    pdf.set_xy(x, y)
    pdf.cell(200-x, 10, "Apto", align='C')
    y = y + 10
    pdf.set_xy(x, y+1)
    if parametros.data["Resistencia de protección a tierra"][4] is not None:
        pdf.cell(200-x, 6, str(parametros.data["Resistencia de protección a tierra"][4]) if parametros.data["Resistencia de protección a tierra"][4] is not None else "-", align='C')
        pdf.set_xy(x, pdf.get_y()+6)
    if parametros.data["Resistencia de aislación entre vivo y tierra"][4] is not None:
        pdf.cell(200-x, 6, str(parametros.data["Resistencia de aislación entre vivo y tierra"][4]) if parametros.data["Resistencia de aislación entre vivo y tierra"][4] is not None else "-", align='C')
        pdf.set_xy(x, pdf.get_y()+6)
    if parametros.data["Vivo a neutro"][4] is not None:
        pdf.cell(200-x, 6, str(parametros.data["Vivo a neutro"][4]) if parametros.data["Vivo a neutro"][4] is not None else "-", align='C')
        pdf.set_xy(x, pdf.get_y()+6)
    if parametros.data["Neutro a tierra"][4] is not None:
        pdf.cell(200-x, 6, str(parametros.data["Neutro a tierra"][4]) if parametros.data["Neutro a tierra"][4] is not None else "-", align='C')
        pdf.set_xy(x, pdf.get_y()+6)
    if parametros.data["Vivo a tierra"][4] is not None:
        pdf.cell(200-x, 6, str(parametros.data["Vivo a tierra"][4]) if parametros.data["Vivo a tierra"][4] is not None else "-", align='C')
        pdf.set_xy(x, pdf.get_y()+6)
    if parametros.data["Corriente de fuga del chasis a tierra cerrada"][4] is not None:
        pdf.cell(200-x, 6, str(parametros.data["Corriente de fuga del chasis a tierra cerrada"][4]) if parametros.data["Corriente de fuga del chasis a tierra cerrada"][4] is not None else "-", align='C')
        pdf.set_xy(x, pdf.get_y()+6)

    if parametros.data["Resistencia de aislación entre vivo y parte aplicable"][4] is not None:
        pdf.cell(200-x, 6, str(parametros.data["Resistencia de aislación entre vivo y parte aplicable"][4]) if parametros.data["Resistencia de aislación entre vivo y parte aplicable"][4] is not None else "-", align='C')
        pdf.set_xy(x, pdf.get_y()+6)
    if parametros.data["Corriente del equipo"][4] is not None:
        pdf.cell(200-x, 6, str(parametros.data["Corriente del equipo"][4]) if parametros.data["Corriente del equipo"][4] is not None else "-", align='C')
        pdf.set_xy(x, pdf.get_y()+6)
    if parametros.data["Corriente de fuga del chasis a tierra abierta"][4] is not None:
        pdf.cell(200-x, 6, str(parametros.data["Corriente de fuga del chasis a tierra abierta"][4]) if parametros.data["Corriente de fuga del chasis a tierra abierta"][4] is not None else "-", align='C')
        pdf.set_xy(x, pdf.get_y()+6)
    if parametros.data["Fuga del chasis a tierra abierta con alimentación invertida"][4] is not None:
        pdf.cell(200-x, 6, str(parametros.data["Fuga del chasis a tierra abierta con alimentación invertida"][4]) if parametros.data["Fuga del chasis a tierra abierta con alimentación invertida"][4] is not None else "-", align='C')
        pdf.set_xy(x, pdf.get_y()+6)

    if parametros.pa_index > 0:
        for i in range(parametros.pa_index):
            pdf.cell(200-x, 6, str(parametros.data["Corriente normal status"][i]) if parametros.data["Corriente normal status"][i] is not None else "-", align='C')
            pdf.set_xy(x, pdf.get_y()+6)
            pdf.cell(200-x, 6, str(parametros.data["Corriente invertida status"][i]) if parametros.data["Corriente invertida status"][i] is not None else "-", align='C')
            pdf.set_xy(x, pdf.get_y()+6)

    pdf.rect(x, limLineY, 200-x, altura_linea)  # Solo borde, sin relleno


    # VALORACION GLOBAL
    texto_usuario = funciones.seleccionar_comentario()

    # RECUADRO "Valoración global"
    y = pdf.get_y()
    x = 10
    pdf.set_xy(x, y)
    pdf.set_line_width(0.8)  # Puedes ajustar este valor según lo grueso que quieras el borde
    pdf.rect(x, y, 190, 8, style='D')  # recuadro 'D' para solo dibujar el borde
    pdf.set_line_width(0.2)  # El valor por defecto suele ser 0.2
    pdf.set_fill_color(220, 220, 220)  # Color gris claro (RGB)
    pdf.rect(x, y, 190, 8, style='F')  # recuadro 'F' para solo relleno
    # texto centrado
    pdf.set_xy(x, y)
    pdf.set_font("Helvetica", 'B', size=10)
    pdf.cell(0, 8, "Valoración Global", align='C')
    pdf.set_font("Helvetica", size=10)

    # Agrego comentarios de valoracion general
    y = pdf.get_y()+8
    limLineY = y
    pdf.set_xy(x, y)
    pdf.multi_cell(190, 6, texto_usuario) # escribo texto ajustado a los margenes
