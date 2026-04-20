
import re # expresiones regulares (buscar, validar, reemplazar texto).
import os # manejo de rutas de archivos
from fpdf import FPDF # manejo y generacion de PDF
import questionary
from questionary import Choice
import tkinter as tk
from tkinter import filedialog
from PIL import Image  # Para manejar imágenes
import tempfile

# ficheros locales
import parametros

"""
    seleccionarTecnico():
    Permite al usuario seleccionar un técnico de un archivo de técnicos o ingresar uno nuevo
"""
def seleccionarTecnico():
    parametros.nombreTecnico = mostrar_arch("tecnicos", 2)
    parametros.rutaFirmaTec = buscar_en_arch("tecnicos", parametros.nombreTecnico)
    # si no existe el tecnico, lo creo
    if parametros.rutaFirmaTec is None:
        parametros.nombreTecnico = input("Ingrese el nombre del tecnico: ")
        parametros.rutaFirmaTec = solicitar_ruta_firma()
        escribir_arch("tecnicos", parametros.nombreTecnico, parametros.rutaFirmaTec)

"""
solicitar_ruta_firma()
Solicita la ruta de una imagen de firma, la convierte a una ruta absoluta si es necesario y la valida,
repite el proceso hasta que se ingrese una ruta existente y con permisos de escritura
"""
def solicitar_ruta_firma():
    while True:
        # Solicitar la ruta o nombre del archivo al usuario
        rutaFirma = input("Ingrese la ruta de la imagen de la firma seguido de '\\nombre_imagen.[png/jpg/jpeg]': ")

        # Si solo se ingresa el nombre del archivo, construir la ruta completa
        if not os.path.isabs(rutaFirma):  # Verifica si la ruta no es absoluta
            rutaFirma = os.path.join(os.getcwd(), rutaFirma)  # Une el directorio actual con el nombre del archivo

        # Verificar si la ruta es accesible
        if os.path.exists(rutaFirma) and os.access(os.path.dirname(rutaFirma), os.W_OK):
            return rutaFirma
        else:
            print("Error: La ruta no es válida, inténtalo de nuevo.")

"""
escribir_arch(arch, text):
Escribe dos líneas de texto con un salto de línea entre ellas
Si el archivo no existe, lo crea
"""
def escribir_arch(arch_name, text1="", text2=""):
    arch = "arch/" + arch_name + ".txt"
    with open(arch, 'a',  encoding="utf-8") as f: # Abre el archivo en modo append (agregar al final)
        if text1 != "":
            f.write(text1 + '\n')
        if text2 != "":
            f.write(text2 + '\n')

"""
buscar_en_arch(arch_name, search_text):
Busca una línea que comience con search_text en un archivo de texto y devuelve la línea siguiente
"""
def buscar_en_arch(arch_name, search_text, nextLine=True):
    arch = "arch/" + arch_name + ".txt"
    if search_text == "Nuevo tecnico": return None  # no hay ruta de imagen
    try:
        with open(arch, 'r') as f:
            encontrado = False
            for linea in f:
                if encontrado:
                    return linea.strip()  # Devolver la línea siguiente
                if linea.startswith(search_text):
                    if nextLine == False: # devuelvo la linea con coincidencia
                        return linea.strip()
                    else:   # por default, devuelvo la siguiente linea en el proximo bucle
                        encontrado = True
        return None  # Si no encuentra o no hay línea siguiente
    except FileNotFoundError:
        print(f"El archivo '{arch}' no existe.")
        return None
    
"""
mostrar_arch(arch_name, multiplo):
Muestra las líneas de un archivo de texto, filtrando por un múltiplo dado
Si multiplo es -1, muestra las líneas impares
Si multiplo es 1, muestra todas las líneas
Si multiplo es un número positivo, muestra las líneas que son múltiplos de ese número
Si el archivo no existe, devuelve None
"""
def mostrar_arch(arch_name, multiplo):
    arch = "arch/" + arch_name + ".txt"
    lineas_visibles = []
    try:
        with open(arch, 'r') as f:
            for i, linea in enumerate(f):
                if multiplo == -1: # Si multiplo es -1, muestro lineas impares
                    if i % 2 == 1:
                        lineas_visibles.append(linea.strip())
                elif i % multiplo == 0: # muestro lineas que son multiplo de 'multiplo'
                    lineas_visibles.append(linea.strip())

        if not lineas_visibles:
            print("No hay lineas para mostrar.")
            return None

        seleccion = questionary.select(
            "Use las flechas para seleccionar una opcion y presione Enter para continuar:",
            choices=lineas_visibles
        ).ask()

        return seleccion

    except FileNotFoundError:
        print(f"El archivo '{arch}' no existe.")
        return None

from questionary import Choice
import questionary
import parametros

def mostrar_arch_equipo(arch_name):
    """
    Muestra las líneas de un archivo de equipos para selección, incluyendo 'Nuevo equipo'.
    Almacena Edificio, Sector, Marca, Modelo, y SN en 'parametros', y retorna el Código (ID).
    (Ajustado para 6 columnas: Código | Descripción | Edificio | Sector | Modelo/Serie | Ubicación)
    """
    arch = "arch/" + arch_name + ".txt"
    lineas_filtradas = []
    
    try:
        with open(arch, 'r', encoding='utf-8') as f:
            for linea in f:
                lineas_filtradas.append(linea.strip())
        
        if not lineas_filtradas:
            print("No hay equipos para mostrar en el archivo.")
            return None
        
        # 1. Crear la lista de opciones (Choice objects)
        opciones_questionary = []
        for linea in lineas_filtradas:
            linea_limpia = linea.strip()
            
            # Deshabilitar encabezados y separadores, pero permitir la selección de "Nuevo equipo"
            if linea_limpia.startswith("Codigo") or linea_limpia.startswith("---"):
                opcion = Choice(title=linea_limpia, value=linea_limpia, disabled=True)
            else:
                opcion = Choice(title=linea_limpia, value=linea_limpia, disabled=False)
            
            opciones_questionary.append(opcion)

        # 2. Obtener la selección
        seleccion = questionary.select(
            "Seleccione un equipo de la lista o use las flechas para navegar:",
            choices=opciones_questionary
        ).ask()

        # --- Lógica de Extracción y Asignación ---
        if seleccion == "Nuevo equipo":
            return "Nuevo equipo"
        
        # 3. Separar los campos por el delimitador " | " (pipe con espacios)
        # Índice: [0] Código, [1] Descripción, [2] Edificio, [3] Sector, [4] Modelo/Serie, [5] Ubicación
        campos = [c.strip() for c in seleccion.split('|')]
        
        # 4. Verificar el número de campos (Esperamos 6)
        if len(campos) < 6:
            print(f"\n¡Error de formato! La línea no tiene suficientes campos (Esperado: 6): {seleccion}\n")
            return None
            
        # 5. Extraer datos usando los índices correctos para 6 columnas
        codigo = campos[0]
        descripcion_completa = campos[1] 
        edificio = campos[2] 
        sector = campos[3]
        modelo_sn_completo = campos[4] 
        ubicacion = campos[5]

        # 6. Procesar Modelo/Serie para separar Modelo y SN (ANTES ERA PASO 7)
        if '#' in modelo_sn_completo:
            modelo, sn = modelo_sn_completo.split('#', 1)
            modelo = modelo.strip()
            sn = sn.strip()
        else:
            modelo = modelo_sn_completo.strip()
            sn = ""
            
        # La Marca es el texto restante de la descripción_completa al eliminar modelo_sn_completo.
        marca = descripcion_completa.replace(modelo_sn_completo, '').strip()

        # 8. Almacenar en las variables de 'parametros'
        parametros.sedeEEM = edificio
        parametros.sectorEEM = sector
        parametros.ubicacionEEM = ubicacion
        parametros.marcaEEM = marca 
        parametros.modeloEEM = modelo
        parametros.snEEM = sn

        # 9. Retornar el Código (ID)
        return codigo

    except FileNotFoundError:
        print(f"El archivo '{arch}' no existe.")
        return None
    except Exception as e:
        print(f"Ocurrió un error al procesar la selección: {e}")
        return None

"""
seleccionar_archivo_equipo():
Permite al usuario seleccionar un archivo de equipo de la carpeta "arch/equipos".
"""
def seleccionar_archivo_equipo():
    carpeta = "arch/equipos"
    try:
        archivos = [f for f in os.listdir(carpeta) if f.endswith(".txt")]
        if not archivos:
            print("No hay archivos .txt en la carpeta.")
            return None

        # Remover la extensión .txt para mostrar
        nombres_visibles = [os.path.splitext(f)[0] for f in archivos]

        seleccion = questionary.select(
            "Seleccione equipo a ensayar:",
            choices=nombres_visibles
        ).ask()

        return seleccion  # Retorna el nombre sin .txt

    except FileNotFoundError:
        print(f"La carpeta '{carpeta}' no existe.")
        return None
    
"""
agregar_idequipo()
Solicita los datos del nuevo equipo, los formatea y los escribe en el archivo.
"""
def agregar_idequipo():
    parametros.marcaEEM = input("Marca: ")
    parametros.modeloEEM = input("Modelo: ")
    parametros.snEEM = input("Número de serie: ")
    parametros.sedeEEM = input("Sede: ")
    parametros.sectorEEM = input("Sector: ")
    parametros.ubicacionEEM = input("Ubicación: ")

    descripcion = f"{parametros.marcaEEM} {parametros.modeloEEM} #{parametros.snEEM}"
    modelo_sn = f"{parametros.modeloEEM} #{parametros.snEEM}"
    ubi = f"{parametros.sedeEEM}-{parametros.sectorEEM}-{parametros.ubicacionEEM}"

    # Ajusto anchos para que queden en fase las columnas
    anchos = [10, 29, 10, 13, 26, 33]

    nueva_linea = (
        f"{parametros.idEquipo:<{anchos[0]}}| "
        f"{descripcion:<{anchos[1]}}| "
        f"{parametros.sedeEEM:<{anchos[2]}}| "
        f"{parametros.sectorEEM:<{anchos[3]}}| "
        f"{modelo_sn:<{anchos[4]}}| "
        f"{ubi:<{anchos[5]}}"
    )

    # Escribo todos los datos del nuevo equipo
    if parametros.tipoEquipo:
        escribir_arch("equipos/" + parametros.tipoEquipo, nueva_linea)

"""
cargar_planilla(arch_name) --> MANTENIMIENTO PREVENTIVO
Carga la planilla completa, leida del txt x equipo, en un diccionario.
Cada sección es una clave y cada item un subdiccionario.
"""
def cargar_planilla(arch_name):
    secciones = {}

    arch = "arch/planilla/" + arch_name + ".txt"

    try:
        with open(arch, 'r', encoding="utf-8") as f:
            seccion_actual = None

            for linea in f:
                linea = linea.strip()
                if not linea:
                    continue

                # Separadores de seccion
                if linea.startswith("[") and linea.endswith("]"):
                    seccion_actual = linea[1:-1]
                    secciones[seccion_actual] = {
                        "encabezados": [],
                        "items": []
                    }

                # Detecta encabezados
                elif linea.startswith("ENCABEZADOS:"):
                    if seccion_actual:
                        encabezados = [p.strip() for p in linea.replace("ENCABEZADOS:", "").split("|")]
                        secciones[seccion_actual]["encabezados"] = encabezados

                # items
                else:
                    if seccion_actual and secciones[seccion_actual]["encabezados"]:
                        partes = [p.strip() for p in linea.split("|")]
                        encabezados = secciones[seccion_actual]["encabezados"]

                        item = {}
                        for i, encabezado in enumerate(encabezados):
                            item[encabezado] = partes[i] if i < len(partes) else ""
                        secciones[seccion_actual]["items"].append(item)

        return secciones

    except FileNotFoundError:
        print(f"Archivo '{arch}' no encontrado.")
        return None

"""
comprimir_imagen()
    Comprime y convierte imágenes a JPG para reducir tamaño.
    Maneja PNG con transparencia agregando fondo blanco.
    Guarda archivo temporal en carpeta del sistema.
"""
def comprimir_imagen(path_in, quality=60, max_width=1400):

    try:
        img = Image.open(path_in)

        # Si tiene RGBA (PNG con transparencia), convertimos a RGB
        if img.mode == "RGBA":
            fondo = Image.new("RGB", img.size, (255, 255, 255))
            fondo.paste(img, mask=img.split()[3])
            img = fondo
        else:
            img = img.convert("RGB")

        w, h = img.size

        # Redimensionar si supera el ancho permitido
        if w > max_width:
            new_h = int(h * (max_width / w))
            img = img.resize((max_width, new_h))

        # Crear archivo temporal en misma carpeta
        carpeta = os.path.dirname(path_in)
        nombre = os.path.basename(path_in)
        nombre_sin_ext = os.path.splitext(nombre)[0]

        temporal = os.path.join(carpeta, nombre_sin_ext + "_COMP.jpg")

        img.save(temporal, "JPEG", quality=quality)

        return temporal

    except Exception as e:
        print(f"[ERROR] No se pudo comprimir {path_in}: {e}")
        return path_in

"""
seleccionar_imagenes()
Permite seleccionar una imagen de tu carpeta
"""
def seleccionar_imagenes():
    root = tk.Tk()
    root.withdraw()

    root.lift()
    root.attributes("-topmost", True)

    archivos = filedialog.askopenfilenames(
        title="Selecciona imágenes",
        filetypes=[("Archivos de imagen", "*.png *.jpg *.jpeg *.bmp *.gif")]
    )

    root.destroy()
    return list(archivos) if archivos else []


"""
iniciar_pagina_imagenes()
Agrego pagina en el PDF para poner las imagenes
"""
def iniciar_pagina_imagenes(pdf):
    pdf.add_page()
    pdf.recuadro(10, pdf.get_y(), 190, 8,
                 texto="IMAGENES", align="C",
                 bold=True, fondo=(220, 220, 220), border=1)

    x_start = pdf.l_margin
    y_start = pdf.get_y() + 4
    return x_start, y_start


"""
agregar_imagen()
Agrega imágenes COMPRIMIDAS al PDF en recuadros con leyendas
"""
def agregar_imagen(pdf):
    figura_num = 1        # número de figura a nivel global (no se reinicia)
    max_w, max_h = 90, 50 # tamaño del recuadro
    temp_files = []       # lista de temporales para borrar después

    hayImagenCargada = False

    while True:
        opcion = questionary.select(
            "¿Quiere agregar una nueva imagen?",
            choices=[
                questionary.Choice(title="Sí", value="s"),
                questionary.Choice(title="No", value="n")
            ]
        ).ask()

        if opcion == "n":
            break

        # Si es la primera vez que el usuario carga imágenes
        if not hayImagenCargada:
            x_start, y_start = iniciar_pagina_imagenes(pdf)
            x, y = x_start, y_start
            col = 0
            hayImagenCargada = True

        # Seleccionar imágenes
        imagenes = seleccionar_imagenes()
        if not imagenes:
            continue

        for img_path in imagenes:
            try:
                # --- COMPRESIÓN ---
                img_comp = comprimir_imagen(img_path)
                temp_files.append(img_comp)  # se borrarán al final

                # Tamaño de imagen comprimida
                with Image.open(img_comp) as im:
                    w, h = im.size

                if w == 0 or h == 0:
                    continue

                # Escalado máximo
                ratio = min(max_w / w, max_h / h)
                new_w, new_h = w * ratio, h * ratio

                img_x = x + (max_w - new_w) / 2
                img_y = y + (max_h - new_h) / 2

                # Insertar imagen
                pdf.image(img_comp, img_x, img_y, w=new_w, h=new_h)

                # Pedir descripción
                descripcion = questionary.text(
                    f"Ingrese descripción para Figura {figura_num}:"
                ).ask() or ""

                # Escribir leyenda
                pdf.set_xy(x, y + max_h + 3)
                pdf.set_font("Helvetica", size=10)
                pdf.multi_cell(max_w, 5,
                               f"Figura {figura_num}: {descripcion}",
                               0, "C")

                figura_num += 1

                # --- MOVER A SIGUIENTE COLUMNA / FILA ---
                if col == 0:
                    x += max_w + 10
                    col = 1
                else:
                    x = x_start
                    y += max_h + 20
                    col = 0

                    # Si no entra en la página → nueva página
                    if y + max_h + 30 > pdf.h - pdf.t_margin:
                        x_start, y_start = iniciar_pagina_imagenes(pdf)
                        x, y = x_start, y_start
                        col = 0

            except Exception as e:
                print(f"No se pudo agregar la imagen {img_path}: {e}")

    # Borro archivos temporales
    for tmp in temp_files:
        try:
            if os.path.exists(tmp):
                os.remove(tmp)
        except:
            pass


# ---------- FUNCIONES SE ----------

"""
    solicitar_ruta():
    Solicita al usuario una ruta de archivo CSV a través de un diálogo de selección de archivos.
    Si el usuario selecciona un archivo válido, devuelve la ruta absoluta del archivo.
    Si no se selecciona un archivo válido, imprime un mensaje de error y devuelve None.
"""
def solicitar_ruta():
    # Crear ventana oculta de tkinter
    root = tk.Tk()
    root.withdraw()  # Ocultar ventana principal

    # Forzar que el diálogo esté en primer plano
    root.lift()
    root.attributes("-topmost", True)

    # Abrir diálogo para seleccionar archivo CSV
    ruta = filedialog.askopenfilename(
        title="Seleccionar archivo CSV",
        filetypes=[("Archivos CSV", "*.csv")]
    )

    root.destroy()  # Cerrar ventana oculta

    if ruta and os.path.exists(ruta):
        return ruta
    else:
        print("No se seleccionó un archivo válido.")
        return None

"""
seleccionar_tipo_ensayo():
Permite al usuario seleccionar el tipo de ensayo a realizar
"""
def seleccionar_tipo_ensayo():
    opciones = [
        questionary.Choice(title="Ensayo antes de poner en servicio", value="1"),
        questionary.Choice(title="Ensayo recurrente", value="2"),
        questionary.Choice(title="Ensayo después de la reparación", value="3")
    ]

    seleccion = questionary.select(
        "Seleccione el tipo de ensayo:",
        choices=opciones
    ).ask()

    return seleccion

"""
leer_fecha_calibracion():
Lee la fecha de calibración desde un archivo de texto. Si el archivo no existe, devuelve None.
arch definido en parametros: arch/fluke_calib_date.txt
"""
def leer_fecha_calibracion():
    if os.path.exists(parametros.archivo_calibracion):
        with open(parametros.archivo_calibracion, 'r') as file:
            return file.read().strip()
    return None

"""
guardar_fecha_calibracion(fecha):
Guarda la fecha de calibración en un archivo de texto. Si el archivo no existe, lo crea
"""
def guardar_fecha_calibracion(fecha):
    with open(parametros.archivo_calibracion, 'w') as file:
        file.write(fecha)

"""
verificar_fecha_calibracion(leer_fecha_func, guardar_fecha_func):
Verifica la fecha de calibración del equipo. Si la fecha guardada es correcta, la devuelve
Si no es correcta o no existe, solicita una nueva fecha y la guarda
"""
def verificar_fecha_calibracion(leer_fecha_func, guardar_fecha_func):
    # Leer la fecha guardada
    fluke_calib_date = leer_fecha_func()

    if fluke_calib_date:
        print(f"La última calibración del equipo fue: {fluke_calib_date}")
        confirmacion = questionary.select(
            "¿Es correcta esta fecha?",
            choices=[
                questionary.Choice(title="Si", value="s"),
                questionary.Choice(title="No", value="n")
            ]
        ).ask()
    else:
        confirmacion = 'n'

    # Si no es correcta o no existe, pedir nueva fecha
    if confirmacion != 's':
        fluke_calib_date = input("Ingrese la última fecha de calibración (DD/MM/AAAA): ").strip()
        guardar_fecha_func(fluke_calib_date)

    return fluke_calib_date
    
"""
recopilar_datos(lines):
Toma como entrada una lista de líneas de texto (lines), y va extrayendo información con regex, 
llenando variables globales del diccionario definido en el fichero de parametros 

--> mejorar la recopilacion de SN, el del analizador esta hardcodeado para evitar duplicados con el del equipo
"""
def recopilar_datos(lines):
    
    lines_iter = iter(lines) # convierto la lista de líneas en un iterador
    i_pa = 0 # bandera para detectar el inicio de las partes aplicables

    for line in lines_iter:  # recorro las líneas del archivo usando el iterador
        # Si encuentra cabecera "AP Name,AP Type,AP Num", activo flag parte_aplicable
        if line.strip() == "AP Name,AP Type,AP Num":
            parametros.parte_aplicable = True
            i_pa = 1
            continue  # paso a la siguiente línea

        # si luego hay dato, mantengo flag activo (hay PA), sino lo desactivo (no hay PA)
        if parametros.parte_aplicable and i_pa < 3:
            # primera linea en blanco, la salteo
            if i_pa == 1:
                i_pa = i_pa + 1
                continue
            # en esta linea deberia haber texto si tiene PA
            if i_pa == 2:
                if line.strip() == "":  # si la linea esta vacia
                    parametros.parte_aplicable = False
                check_pa = True  # corto la busqueda de PA
                i_pa = i_pa + 1

        # detecto partes aplicables
        if parametros.parte_aplicable:
            match = re.match(parametros.pa_pattern, line)   # busco coincidencias linea por linea
            # si hay coincidencia, las almaceno en el diccionario data
            if match and parametros.pa_index < 100:
                parametros.data["PA nombre"][parametros.pa_index] = match.group(1).strip()
                parametros.data["PA tipo"][parametros.pa_index] = match.group(2).strip()
                parametros.data["PA numero"][parametros.pa_index] = match.group(3).strip()
                parametros.pa_index += 1  # incremento índice

        # busco en el diccionario de patterns
        for key, pattern in parametros.patterns.items():
            match = re.search(pattern, line)
            if match:
                # si es el SN y ya esta capturado, lo ignoro (hardcodeo SN analizador para evitar duplicados en el SN del equipo)
                if key == "Número de serie" and parametros.data[key] is not None:
                    continue
                parametros.data[key] = match.group(1).strip()

        # busco en el diccionario de test patterns
        for key, pattern in parametros.test_patterns.items():
            match = re.search(pattern, line)
            if match:
                parametros.data[key] = [
                    match.group(1),  # Valor medido
                    match.group(2),  # Unidad
                    match.group(3) if match.group(3) != "-" else None,  # Límite superior
                    match.group(4) if match.group(4) != "-" else None,  # Límite inferior
                    match.group(5)  # Cumple (P o F)
                ]

        # Extraer valores de corriente para partes aplicables
        if "Direct Applied Part Leakage" in line:
            line = next(lines_iter)  # Avanzo a la siguiente línea
            if "Normal Condition" in line:
                line = next(lines_iter)  # Avanzo a la siguiente línea
                for i in range(parametros.pa_index): # Recorro tantas lineas como partes aplicables haya (corriente normal)
                    match = re.search(parametros.Current_pa_patterns["Corriente normal"], line)
                    if match:
                            parametros.data["Corriente normal value"][i] = match.group(2)  # Valor medido
                            parametros.data["Corriente normal unit"][i] = match.group(3)  # Unidad
                            parametros.data["Corriente normal high"][i] = match.group(4)  # Límite superior
                            parametros.data["Corriente normal low"][i] = match.group(5)  # Límite inferior
                            parametros.data["Corriente normal status"][i] = match.group(6)  # Estado (P o F)
                            line = next(lines_iter)  # Avanzo a la siguiente línea
            if "Normal Condition- Reversed Mains" in line:
                line = next(lines_iter)  # Avanzo a la siguiente línea
                for i in range(parametros.pa_index): # Recorro tantas lineas como partes aplicables haya (corriente invertida)
                    match = re.search(parametros.Current_pa_patterns["Corriente invertida"], line)
                    if match:
                        parametros.data["Corriente invertida value"][i] = match.group(2)  # Valor medido
                        parametros.data["Corriente invertida unit"][i] = match.group(3)  # Unidad
                        parametros.data["Corriente invertida high"][i] = match.group(4)  # Límite superior
                        parametros.data["Corriente invertida low"][i] = match.group(5)  # Límite inferior
                        parametros.data["Corriente invertida status"][i] = match.group(6)  # Estado (P o F)
                        # chequeo si hay mas lineas para seguir avanzando
                        try:
                            line = next(lines_iter)  # Avanzo a la siguiente línea
                        except StopIteration:
                            break  # Si no hay más líneas, salgo del bucle

"""
seleccionar_comentario():
Permite al usuario seleccionar un comentario predefinido o ingresar uno personalizado
"""
def seleccionar_comentario():
    opcion = questionary.select(
        "Ingrese valoracion global del ensayo",
        choices=[
            questionary.Choice(title="Equipo apto", value="apto"),
            questionary.Choice(title="Otros comentarios...", value="otro")
        ]
    ).ask()

    if opcion == "apto":
        return "Equipo pasa satisfactoriamente el ensayo de Seguridad Eléctrica."
    else:
        comentario = questionary.text("Ingrese su comentario:").ask()
        return comentario.strip()
