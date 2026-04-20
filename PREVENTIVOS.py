import parametros
import questionary
from pathlib import Path
import funciones 
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import os
import datetime # Necesario para la fecha

"""
Secciones:
1. Info del equipo --> en txt
2. Inspección visual --> pasa/ No pasa --> obs
3. Accesorios --> Tiene? NS? Obs?
4. Funcionamientos --> pasa/ No pasa --> obs
5. SE --> TIENE?
6. Observaciones generales
7. Imágenes (en página aparte)

"""
def planillaBase(pdf):
    """
    Agrega la cabecera básica de la planilla de mantenimiento al PDF,
    leyendo las etiquetas de 'arch/planilla/-PLANILLA BASE-.txt' y llenando
    los valores correspondientes con input de consola para Fecha/Técnico.
    """
    pdf.add_page()
    
    # 1. Definición de la ruta del archivo de etiquetas
    nombre_archivo = "-PLANILLA BASE-.txt"
    ruta_base = Path('arch') / 'planilla'
    ruta_completa = ruta_base / nombre_archivo
    
    etiquetas = []
    
    # 2. Leer las etiquetas desde el archivo
    try:
        with open(ruta_completa, 'r', encoding='utf-8') as f:
            for linea in f:
                etiquetas.extend([e.strip() for e in linea.strip().split('|')])
    except FileNotFoundError:
        # Usar etiquetas predeterminadas si falla la lectura
        etiquetas = [
            "Código de equipo", "Fecha de revisión",
            "Marca", "Sede",
            "Modelo", "Sector",
            "Número de serie", "Ubicación"
        ]
        
    # Usamos questionary para la fecha si está disponible (mejor UX)
    try:
        fecha_pm = questionary.text(
            "Introduzca la fecha de realización del PM (DD/MM/AAAA) o deje en blanco para hoy:",
            default=datetime.date.today().strftime("%d/%m/%Y")
        ).ask()
    except Exception:
        # Fallback a input() simple si questionary no funciona o es cancelado
        fecha_pm = input("Fecha de PM (DD/MM/AAAA): ") or datetime.date.today().strftime("%d/%m/%Y")
    
    # 4. Mapeo de valores a las etiquetas
    # Los valores deben coincidir con las etiquetas leídas o las predeterminadas
    valores = [
        getattr(parametros, 'idEquipo', 'N/A'), 
        fecha_pm,
        getattr(parametros, 'marcaEEM', 'N/A'),
        getattr(parametros, 'sedeEEM', 'N/A'),
        getattr(parametros, 'modeloEEM', 'N/A'),
        getattr(parametros, 'sectorEEM', 'N/A'),
        getattr(parametros, 'snEEM', 'N/A'),
        getattr(parametros, 'ubicacionEEM', 'N/A')
    ]

    # 5. Generación de la tabla en el PDF (4 filas x 4 columnas)
    
    ancho_etiqueta = 40
    ancho_valor = 55
    # Anchos: [Etiqueta, Valor, Etiqueta, Valor]
    
    pdf.recuadro(10, pdf.get_y(), 190, 8, texto="DATOS DEL EQUIPO Y REVISIÓN", align="C", bold=True, fondo=(220,220,220), border=1)
    
    # Posicionar la tabla debajo del recuadro
    y_inicio = pdf.get_y()
    altura_celda = 7 # Altura fija para celdas
    
    for i in range(4): # 4 Filas
        
        # Índices lineales del array:
        idx1 = i * 2     # Etiqueta/Valor de la izquierda (Col 1 y 2: 0, 2, 4, 6)
        idx2 = i * 2 + 1 # Etiqueta/Valor de la derecha (Col 3 y 4: 1, 3, 5, 7)
        
        # --- COLUMNA 1 (Etiqueta) ---
        pdf.set_xy(10, y_inicio)
        pdf.set_font('Arial', 'B', 10) 
        pdf.tabla(pdf.get_x(), pdf.get_y(), [ancho_etiqueta], [[etiquetas[idx1]]], align="L")
        
        # --- COLUMNA 2 (Valor) ---
        pdf.set_xy(10 + ancho_etiqueta, y_inicio)
        pdf.set_font('Arial', '', 10) 
        pdf.tabla(pdf.get_x(), pdf.get_y(), [ancho_valor], [[valores[idx1]]], align="L")

        # --- COLUMNA 3 (Etiqueta) ---
        pdf.set_xy(10 + ancho_etiqueta + ancho_valor, y_inicio)
        pdf.set_font('Arial', 'B', 10)
        pdf.tabla(pdf.get_x(), pdf.get_y(), [ancho_etiqueta], [[etiquetas[idx2]]], align="L")

        # --- COLUMNA 4 (Valor) ---
        pdf.set_xy(10 + ancho_etiqueta * 2 + ancho_valor, y_inicio)
        pdf.set_font('Arial', '', 10)
        pdf.tabla(pdf.get_x(), pdf.get_y(), [ancho_valor], [[valores[idx2]]], align="L")
        
        y_inicio += altura_celda # Mueve la posición a la siguiente fila
    
    # Restaurar la fuente
    pdf.set_font('Arial', '', 10) 
    
    return pdf.get_y()
    
def agregarPREV(pdf):
    
    y = planillaBase(pdf)

    # armo la ruta completa con el nombre del archivo usando pathlib
    nombre_archivo = f"{parametros.tipoEquipo}.txt"
    ruta_base = Path('arch') / 'planilla'
    ruta_completa = ruta_base / nombre_archivo
    if not ruta_completa.is_file():
        print(f"No se encontró el archivo de equipo: {ruta_completa}")
        crear_planillaPM()

    respuestas = ventanaPM(parametros.tipoEquipo)

    for seccion, datos in respuestas.items():
        encabezados = datos.get("encabezados", [])
        items = datos.get("items", [])

        if not encabezados and not items:
            continue

        # Sección
        pdf.recuadro(10, pdf.get_y(), 190, 8, texto=seccion, align="C", bold=True, fondo=(220,220,220), border=1)

        # Armado de columnas
        if items:
            ancho_total = 190

            #Ajustes de anchos por nombre de columna
            anchos = []
            for col in encabezados:
                if col.lower().startswith("código") or col.lower().startswith("6."):
                    anchos.append(12)   # código cortito
                elif col.lower().startswith("Ítem"):
                    anchos.append(25)   # ítem medio
                elif "evaluación" in col.lower():
                    anchos.append(65)   # evaluación grande
                elif "resultado" in col.lower():
                    anchos.append(20)   # resultado corto
                elif "Observación" in col.lower():
                    anchos.append((ancho_total - sum(anchos)) / (len(encabezados) - len(anchos)))   # resultado corto                    
                else:
                    # reparto ancho si no lo reconozco
                    anchos.append((ancho_total - sum(anchos)) / (len(encabezados) - len(anchos)))

            # ENCABEZADOS
            pdf.tabla(10, pdf.get_y(), anchos, [encabezados], align="C")

            # FILAS
            for item in items:
                fila = [str(item.get(col, "")) for col in encabezados]
                pdf.tabla(pdf.get_x(), pdf.get_y(), anchos, [fila], align="L")
                y = pdf.get_y()  # para no perder la posicion despues del multi_cell

        # Para no sobreescribir la conformidad
        if y > 210: # Corregir numero
            pdf.add_page()
            y = 20

"""
ventanaPM: crea la ventana de mantenimiento preventivo
"""
def ventanaPM(arch_name):
    secciones = funciones.cargar_planilla(arch_name)
    if not secciones:
        print("No se pudo cargar la planilla.")
        return None
    
    # Ventana principal
    root = tk.Tk()
    root.title("Mantenimiento Preventivo")
    root.geometry("1200x600") # tamaño inicial

    # Forzar ventana al frente al inicio
    root.lift()
    root.attributes('-topmost', True)
    root.after(100, lambda: root.attributes('-topmost', False))
    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True)
    entry_widgets = {}

    for seccion, datos in secciones.items():
        # Frame principal con scroll
        container = ttk.Frame(notebook)
        notebook.add(container, text=seccion)

        # canvas y scrollbars
        canvas = tk.Canvas(container)
        v_scroll = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        h_scroll = ttk.Scrollbar(container, orient="horizontal", command=canvas.xview)
        scroll_frame = ttk.Frame(canvas)
        scroll_frame.bind(
            "<Configure>",
            lambda e, c=canvas: c.configure(scrollregion=c.bbox("all"))
        )
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        canvas.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")
        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)

        encabezados = datos.get("encabezados", [])
        items = datos.get("items", [])

        # Encabezados de tabla
        for j, encabezado in enumerate(encabezados):
            ttk.Label(
                scroll_frame,
                text=encabezado,
                font=("Helvetica", 10, "bold")
            ).grid(row=0, column=j, padx=10, pady=5, sticky="w")

        entry_widgets[seccion] = []

        # Filas dinamicas
        for i, item in enumerate(items, start=1):
            fila_widgets = {}
            for j, encabezado in enumerate(encabezados):
                valor = item.get(encabezado, "")

                if encabezado in ["Ítem", "Evaluación"]:
                    # ---- Solo lectura ----
                    lbl = ttk.Label(
                        scroll_frame,
                        text=valor,
                        wraplength=250,
                        anchor="w",
                        justify="left",
                        background="#f0f0f0"
                    )
                    lbl.grid(row=i, column=j, padx=10, pady=5, sticky="w")
                    fila_widgets[encabezado] = None

                elif encabezado == "Resultado":
                    # ---- Opciones con Combobox ----
                    combo = ttk.Combobox(
                        scroll_frame,
                        values=["Pasó", "Falló", "No aplica"],
                        state="readonly",
                        width=15
                    )
                    if valor:
                        combo.set(valor)
                    combo.grid(row=i, column=j, padx=10, pady=5)
                    fila_widgets[encabezado] = combo

                else:
                    # ---- Editable ----
                    entry = ttk.Entry(scroll_frame, width=30)
                    entry.insert(0, valor)
                    entry.grid(row=i, column=j, padx=10, pady=5)
                    fila_widgets[encabezado] = entry

            entry_widgets[seccion].append((item, fila_widgets))

    def guardar_y_cerrar():
        for seccion, filas in entry_widgets.items():
            for item, fila_widgets in filas:
                for encabezado, widget in fila_widgets.items():
                    if isinstance(widget, ttk.Combobox):
                        item[encabezado] = widget.get()
                    elif isinstance(widget, ttk.Entry):
                        item[encabezado] = widget.get()
        root.destroy()

    # Botón global para guardar
    btn_guardar = ttk.Button(root, text="Guardar y salir", command=guardar_y_cerrar)
    btn_guardar.pack(pady=10)

    root.mainloop()

    return secciones if secciones else None


def configurar_estilos(root):
    style = ttk.Style(root)
    style.theme_use('clam')

    # --- Estilos de pestañas ---
    style.configure('TNotebook.Tab',
                    font=('Segoe UI', 10, 'bold'),
                    padding=(12, 6, 12, 6))
    style.map('TNotebook.Tab',
              background=[('selected', '#f5f5f5')],
              expand=[('selected', [1, 1, 1, 0])])

    # --- Estilos de celdas ---
    style.configure('HeaderCell.TEntry',
                    fieldbackground='#f5f5f5',
                    foreground='black',
                    font=('Segoe UI', 10, 'bold'),
                    justify='center',
                    relief='solid')

    style.configure('DataCell.TEntry',
                    fieldbackground='white',
                    foreground='black',
                    relief='solid',
                    justify='left')



def crear_planillaPM():
    # --- Cartel de bienvenida ---
    root_temp = tk.Tk()
    root_temp.withdraw()
    root_temp.attributes('-topmost', True)
    messagebox.showinfo(
        "Preparando Planilla de PM",
        f"Por favor, agregue las filas y columnas necesarias para la plantilla de PM para {parametros.tipoEquipo}.",
        parent=root_temp
    )
    root_temp.destroy()

    # --- Ventana principal ---
    root = tk.Tk()
    root.title("Crear Planilla - Mantenimiento Preventivo")
    root.geometry("1200x500")
    configurar_estilos(root)

    # Forzar ventana al frente
    root.lift()
    root.attributes('-topmost', True)
    root.after(200, lambda: root.attributes('-topmost', False))

    secciones = {}
    nombre_refs = {}
    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)

    # --- Función para agregar grilla ---
    def agregar_grilla(frame, seccion):
        cols, filas = 4, 2  # por defecto 4 columnas y 2 filas
        entradas = []

        nombres_encabezados = ["Ítem", "Evaluación", "Resultado", "Observación"]
        texto_item_chasis = "No debe haber daños en la carcasa del equipo"

        for r in range(filas):
            fila_widgets = []
            for c in range(cols):
                if r == 0:
                    estilo = 'HeaderCell.TEntry'
                    valor = nombres_encabezados[c]
                elif r == 1 and c == 0:
                    valor = "Chasis"
                    estilo = 'DataCell.TEntry'
                elif r == 1 and c == 1:
                    valor = texto_item_chasis
                    estilo = 'DataCell.TEntry'
                else:
                    valor = ""
                    estilo = 'DataCell.TEntry'

                e = ttk.Entry(frame, width=25, style=estilo)
                e.insert(0, valor)
                e.grid(row=r, column=c, padx=5, pady=3, sticky="nsew")
                fila_widgets.append(e)
            entradas.append(fila_widgets)
        secciones[seccion]["entradas"] = entradas

    # --- Funciones para agregar/eliminar filas y columnas ---
    def agregar_fila(frame):
        nombre_actual = nombre_refs[frame][0]
        entradas = secciones[nombre_actual]["entradas"]
        r = len(entradas)
        c_total = len(entradas[0])
        fila = []
        for c in range(c_total):
            estilo = 'DataCell.TEntry'
            e = ttk.Entry(frame, width=25, style=estilo)
            e.insert(0, f"Ítem {r}" if c == 0 else "")
            e.grid(row=r, column=c, padx=5, pady=3, sticky="nsew")
            fila.append(e)
        entradas.append(fila)

    def eliminar_fila(frame):
        nombre_actual = nombre_refs[frame][0]
        entradas = secciones[nombre_actual]["entradas"]
        if len(entradas) > 1:
            fila = entradas.pop()
            for e in fila:
                e.destroy()
        else:
            messagebox.showinfo("Aviso", "Debe quedar al menos la fila de encabezados.", parent=root)

    def agregar_columna(frame):
        nombre_actual = nombre_refs[frame][0]
        entradas = secciones[nombre_actual]["entradas"]
        nuevo_indice = len(entradas[0])

        for r, fila in enumerate(entradas):
            estilo = 'HeaderCell.TEntry' if r == 0 else 'DataCell.TEntry'
            e = ttk.Entry(frame, width=25, style=estilo)
            if r == 0:
                e.insert(0, f"Encabezado {nuevo_indice}")
            e.grid(row=r, column=nuevo_indice, padx=5, pady=3, sticky="nsew")
            fila.append(e)

    def eliminar_columna(frame):
        nombre_actual = nombre_refs[frame][0]
        entradas = secciones[nombre_actual]["entradas"]
        if len(entradas[0]) > 1:
            for fila in entradas:
                e = fila.pop()
                e.destroy()
        else:
            messagebox.showinfo("Aviso", "Debe quedar al menos la columna 'Ítem'.", parent=root)

    # --- Función para nueva sección ---
    def nueva_seccion(nombre=None):
        if not nombre:
            nombre = simpledialog.askstring("Nueva sección", "Introduce el nombre de la nueva sección:", parent=root)
            if not nombre:
                return

        container = ttk.Frame(notebook)
        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)

        canvas = tk.Canvas(container, bd=0, highlightthickness=0)
        v_scroll = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        h_scroll = ttk.Scrollbar(container, orient="horizontal", command=canvas.xview)
        frame = ttk.Frame(canvas)
        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=frame, anchor="nw")
        canvas.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        canvas.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")

        btn_frame = ttk.Frame(container)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky="ew")

        notebook.add(container, text=nombre)
        notebook.select(container)
        nombre_refs[frame] = [nombre]
        secciones[nombre] = {"entradas": []}
        agregar_grilla(frame, nombre)

        ttk.Button(btn_frame, text="+ Fila", command=lambda: agregar_fila(frame)).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="- Fila", command=lambda: eliminar_fila(frame)).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="+ Columna", command=lambda: agregar_columna(frame)).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="- Columna", command=lambda: eliminar_columna(frame)).pack(side="left", padx=5)

    # --- Guardar y salir ---
    def guardar_y_salir():
        nombre_arch_base = f"planilla/{parametros.tipoEquipo}"
        arch_path_full = os.path.join("arch", nombre_arch_base + ".txt")
        if os.path.exists(arch_path_full):
            os.remove(arch_path_full)

        for i in range(notebook.index("end")):
            current_tab_id = notebook.tabs()[i]
            container = notebook.nametowidget(current_tab_id)
            canvas = container.winfo_children()[0]
            frame = canvas.winfo_children()[0]
            nombre_actual = nombre_refs[frame][0]
            entradas = secciones[nombre_actual]["entradas"]

            funciones.escribir_arch(nombre_arch_base, f"[{nombre_actual}]")
            if entradas:
                encabezados = [e.get().strip() for e in entradas[0]]
                funciones.escribir_arch(nombre_arch_base, "ENCABEZADOS: " + " | ".join(encabezados))
                for fila in entradas[1:]:
                    valores = [e.get().strip() for e in fila]
                    funciones.escribir_arch(nombre_arch_base, " | ".join(valores))
            funciones.escribir_arch(nombre_arch_base, "")

        messagebox.showinfo(
            "Guardado",
            f"Por favor, complete los campos de la planilla para {parametros.idEquipo}",
            parent=root
        )
        root.destroy()

    # --- Barra superior ---
    top_frame = ttk.Frame(root)
    top_frame.pack(fill="x", padx=10, pady=8)
    ttk.Button(top_frame, text="+ Nueva sección", command=nueva_seccion).pack(side="left", padx=5)
    ttk.Button(top_frame, text="Guardar y salir", command=guardar_y_salir).pack(side="right", padx=5)

    # --- Primera pestaña por defecto ---
    nueva_seccion("INSPECCIÓN VISUAL Y FUNCIONAL")

    root.mainloop()
