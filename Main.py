import os # manejo de rutas de archivos
from pathlib import Path
import questionary

# ficheros locales
import parametros
import clases
import funciones
import SE
import PREVENTIVOS


# ---------- TECNICO ----------
print("Seleccione tecnico responsable del ensayo:")
funciones.seleccionarTecnico()


# ---------- ID Y TIPO DE EQUIPO ----------
parametros.tipoEquipo = funciones.seleccionar_archivo_equipo() # nombre de arch en arch/equipos
# si quiero crear un nuevo archivo de equipos
if parametros.tipoEquipo == "-NUEVO EQUIPO-":
    parametros.tipoEquipo = input("Ingrese el nombre del tipo de equipo: ")
    parametros.idEquipo = "Nuevo equipo" # para agregar nuevo ID
    funciones.escribir_arch("equipos/" + parametros.tipoEquipo, parametros.idEquipo,"Codigo    | Descripcion                  | Edificio  | Sector       | Modelo/Serie              | Ubicacion\n----------|------------------------------|-----------|--------------|---------------------------|----------------------------------")
# si ya existe el archivo de equipos, cargo el ID del equipo
else:
    parametros.idEquipo = funciones.mostrar_arch_equipo("equipos/" + parametros.tipoEquipo)  # codigo de identificacion cargado en el archivo de tipo de equipo

# agregar un nuevo ID
if parametros.idEquipo == "Nuevo equipo":
    parametros.idEquipo = input("Ingrese el ID del equipo: ")

    funciones.agregar_idequipo()


# ---------- INICIO CLASE  ----------
pdf = clases.PDF()  # Formato A4 con encabezado y pie de pagina


# ---------- MANTENIMIENTO PREVENTIVO  ----------
opcion = questionary.select(
    "Se ha realizado Mantenimiento preventivo?",
    choices=[
        questionary.Choice(title="Si", value="s"),
        questionary.Choice(title="No", value="n")
    ]
).ask()
if opcion == "s":
    PREVENTIVOS.agregarPREV(pdf)

funciones.agregar_imagen(pdf)

# ---------- SEGURIDAD ELECTRICA ----------
opcion = questionary.select(
    "Se ha realizado ensayo de Seguridad Electrica?",
    choices=[
        questionary.Choice(title="Si", value="s"),
        questionary.Choice(title="No", value="n")
    ]
).ask()
if opcion == "s":
    SE.agregarSE(pdf)  


# Guardo el PDF ---> luego renombrar segun planilla
reporte = "PREVENTIVO-" + parametros.idEquipo + ".pdf" # nombre del archivo
ruta_pdf = os.path.join("Reportes pdf", reporte)    # ubicacion de guardado
pdf.output(ruta_pdf) 