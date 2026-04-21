
# Variables globales
IDinforme = "PREV-MON-MUL-057" # ID del informe --> modificar segun planilla

marcaEEM = "" # marca del equipo
modeloEEM = "" # modelo del equipo
snEEM = "" # numero de serie del equipo
fechaRevision = "" # fecha de revision del equipo
sedeEEM = "" # sede del equipo
sectorEEM = "" # sector del equipo
ubicacionEEM = "" # ubicacion del equipo

nombreTecnico = "" # nombre del tecnico
rutaFirmaTec = "" # ruta de la imagen de la firma del tecnico
tipoEquipo = "" # nombre de arch en arch/equipos
idEquipo = ""   # codigo de identificacion cargado en el archivo de tipo de equipo
archSE = "" 

archivo_calibracion = "arch/fluke_calib_date.txt" # archivo para almacenar fecha de calib
fluke_calib_date = "" # fecha de calibracion del analizador de seguridad electrica
opcion = "" # opcion seleccionada por el usuario para el tipo de ensayo

archivo_calib_prosim = "arch/prosim_calib_date.txt" # archivo para almacenar fecha de calib
prosim_calib_date = "" # fecha de calibracion del analizador de seguridad electrica

# variables para la deteccion de partes aplicables
parte_aplicable = False # si hay parte aplicable o no
pa_index = 0 # cuantas partes aplicables diferentes tiene


# Diccionario para almacenar los valores extraídos
data = {
    "Fecha": None,
    "Código de identificación": None,
    "Estándar": None,
    "Versión de firmware": None,
    "Fabricante": None,
    "Modelo": None,
    "Número de serie": None,
    "Ubicación": None,
    "Clase de protección": None,
    # valores de ensayo
    "Resistencia de protección a tierra": [None] * 5,
    "Resistencia de aislación entre vivo y tierra": [None] * 5,
    "Vivo a neutro": [None] * 5,
    "Neutro a tierra": [None] * 5,
    "Vivo a tierra": [None] * 5,
    "Corriente de fuga del chasis a tierra cerrada": [None] * 5,
    # parte aplicable
    "Resistencia de aislación entre vivo y parte aplicable": [None] * 5,
    "Corriente del equipo": [None] * 5,
    "Corriente de fuga del chasis a tierra abierta": [None] * 5,
    "Fuga del chasis a tierra abierta con alimentación invertida": [None] * 5,
    "PA nombre": [None] * 100,
    "PA tipo": [None] * 100,
    "PA numero": [None] * 100,
    
    "Corriente normal value": [None] * 100,
    "Corriente normal unit": [None] * 100,
    "Corriente normal high": [None] * 100,
    "Corriente normal low": [None] * 100,
    "Corriente normal status": [None] * 100,
    "Corriente invertida unit": [None] * 100,
    "Corriente invertida value": [None] * 100,
    "Corriente invertida high": [None] * 100,
    "Corriente invertida low": [None] * 100,
    "Corriente invertida status": [None] * 100
}

# Expresiones regulares
patterns = {
    "Fecha": r"Date\s*:\s*(\d{1,2}/\d{1,2}/\d{4})", #DD/MM/AAAA
    "Estándar": r"Standard\s*:\s*,*,([\w-]+)", # ([\w-]+) letras, números y guiones
    "Código de identificación": r"Equipment Number\s*:\s*,*,([\w-]+)", 
    "Versión de firmware": r"Firmware Version\s*:\s*,*,([\d.]+)", # ([\d.]+) numeros y puntos 
    "Fabricante": r"Manufacturer\s*:\s*,*,([\w&-]+)",
    "Modelo": r"Model\s*:\s*,*,([\w-]+)",
    "Número de serie": r"Serial Number\s*:\s*,*,([\w-]+)",  
    "Ubicación": r"Location\s*:\s*,*,([\w-]+)",
    "Clase de protección": r"Classification\s*:\s*,*,([\w-]+)"
}

# Valores de ensayo
test_patterns = {
    "Resistencia de protección a tierra": r"Protective Earth Resistance,,,,, ([\d.]+) (\w+),([\d.-]+),([\d.-]+),(\w+)",
    "Resistencia de aislación entre vivo y tierra": r"Mains to Protective Earth,,,, ([\d.]+) (\w+),([\d.-]+),([\d.-]+),(\w+)",
    "Vivo a neutro": r"Live to Neutral,,,, ([\d.]+) (\w+),([\d.-]+),([\d.-]+),(\w+)",
    "Neutro a tierra": r"Neutral to Earth,,,, ([\d.]+) (\w+),([\d.-]+),([\d.-]+),(\w+)",
    "Vivo a tierra": r"Live to Earth,,,, ([\d.]+) (\w+),([\d.-]+),([\d.-]+),(\w+)",
    "Corriente de fuga del chasis a tierra cerrada": r"Closed Earth,,,, ([\d.]+) (\w+),([\d.-]+),([\d.-]+),(\w+)",
    # parte aplicable
    "Resistencia de aislación entre vivo y parte aplicable": r"Mains to Applied Parts,,,, ([\d.]+) (\w+),([\d.-]+),([\d.-]+),(\w+)",
    "Corriente del equipo": r"Equipment Current,,,,, ([\d.]+) (\w+),([\d.-]+),([\d.-]+),(\w+)",
    "Corriente de fuga del chasis a tierra abierta": r"Open Earth,,,, ([\d.]+) (\w+),([\d.-]+),([\d.-]+),(\w+)",
    "Corriente de fuga del chasis a tierra abierta con alimentación invertida": r"Open Earth- Reversed Mains,,,, ([\d.]+) (\w+),([\d.-]+),([\d.-]+),(\w+)"
}

# Parte apicable
pa_pattern = r"([\w\s-]+),([\w\s-]+),([\w\s-]+)"

Current_pa_patterns = {
    "Corriente normal": r",,([\w\s-]+),,, ([\d.]+) (\w+),([\d.-]+),([\d.-]+),(\w+)",
    "Corriente invertida": r",,([\w\s-]+),,, ([\d.]+) (\w+),([\d.-]+),([\d.-]+),(\w+)"
}