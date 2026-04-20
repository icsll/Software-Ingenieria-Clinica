from fpdf import FPDF
from pathlib import Path
import os
import funciones
from pathlib import Path
import parametros

"""
Queda pendiente pasarle como argumento de la clase:
- formato
- tipografia
- tamaño de letra
- funcion de tabla? poco prioritario
"""

class PDF(FPDF):

    def __init__(self):
        super().__init__(orientation='P', unit='mm', format='A4')
        self.tipo_equipo = parametros.tipoEquipo
        self.nombre_usuario = parametros.nombreTecnico
        self.ruta_firma = parametros.rutaFirmaTec

    """
    recuadro():
    Permite armar recuadros, los de texto o tipo subtitulo que ocupa todo el ancho y con color
    Se usa en la clase del PDF
    """
    def recuadro(self, x, y, w, h, texto="", align='C', bold=False, fondo=None, text_size=10, border=0):
        self.set_xy(x, y)

        # Estilo de texto
        self.set_font("Helvetica", style='B' if bold else '', size=text_size)

        # Fondo (si se pasa un color)
        if fondo and border:
            self.set_fill_color(*fondo)  # fondo debe ser tupla RGB, ej: (200, 200, 200)
            self.rect(x, y, w, h, style='DF')  # Dibuja borde + relleno
        elif fondo and not border:
            self.rect(x, y, w, h)  # solo borde
            self.set_fill_color(*fondo)
            self.rect(x, y, w, h, style='F')  # Solo relleno
        elif not fondo and border:
            self.rect(x, y, w, h, style='D')  # Solo borde

        self.cell(w, h, texto, align=align, border=0)
        self.set_xy(x, y + h)
        

    def header(self):
        x, y = 10, 10
        # Recuadro general (borde de toda la página)
        self.rect(x, y, 190, 277)

        # Encabezados
        self.recuadro(x, y, 50, 20, "INGENIERIA CLINICA", bold=True, border=1)
        self.recuadro(x + 50, y, 70, 12, "INFORME DE PREVENTIVOS", bold=True, border=1)
        self.recuadro(x + 50, y + 12, 70, 8, parametros.tipoEquipo, border=1)
        self.recuadro(x + 120, y, 70, 12, "          SANATORIO LAS LOMAS", bold=True, border=1)
        self.recuadro(x + 120, y + 12, 70, 8, parametros.IDinforme, border=1)
        
        # Logo
        logo_path = os.path.join("imagenes", "logo.jpg")
        if os.path.exists(logo_path):
            logo_w = 10
            logo_h = 10
            logo_x = x + 122 
            logo_y = y + (12 - logo_h) / 2
            self.image(logo_path, logo_x, logo_y, logo_w, logo_h)
        else:
            print(f"No se encontró la imagen del logo: {logo_path}")
       
        self.set_y(30)
       
    def footer(self):
        # recuadros para el pie de pag en la firma
        self.recuadro(10, 287, 95, -35, border=1) # A4: 210x197
        self.recuadro(105, 287, 95, -35, border=1)

        self.set_y(-60)     # de abajo para arriba
        y = self.get_y()      
        x = 10
        
        self.set_font("helvetica", size=10)
        self.recuadro(x, y, 95, 40, f"Técnico responsable: {self.nombre_usuario}", align='L')

        # Imagen de firma si existe
        if self.ruta_firma:
            firma_path = Path(self.ruta_firma)
            if firma_path.exists():
                self.image(self.ruta_firma, x=x + 17, y=y + 21, w=30, h=30)
            else:
                print("Firma no encontrada en:", self.ruta_firma)

        # A modificar
        self.recuadro(x + 95 , y, 95, 40, "Supervisa: Carlos Joaquin Perez", align='L')
    
    
    """
    tabla():
    Permite armar tablas con multi_cell y bordes
    """
    def tabla(self, x, y, anchos_columnas, filas, text_size=10, align='L'):
        self.set_font("Helvetica", size=text_size)
        # Variables iniciales de escala
        line_height = 5  # altura constante para multi_cell
        y_inicial = y
        altura_total = 0
        ancho_total = sum(anchos_columnas)

        for fila in filas:
            altos_finales_texto = []
            x_pos_temp = x

            # --- CALCULO DE DIMENSIONES ---
            # Calculo alto de la fila por simulacion
            for col, texto in enumerate(fila):
                texto_str = str(texto)
                ancho_celda = anchos_columnas[col] - 2  # ancho de multi_cell
                y_antes_simulacion = self.get_y() # posición 'y' antes de escribir el texto
                self.set_xy(x_pos_temp + 1, y_antes_simulacion + 1) # +1 mm margen superior e izquierdo
                # Simulo la escritura del texto para calcular el alto real que ocupa
                self.multi_cell(ancho_celda, line_height, texto_str, border=0, align=align)
                
                y_despues_simulacion = self.get_y() # posición 'y' después de escribir el texto                
                altura_texto = y_despues_simulacion - y_antes_simulacion # calculo el alto real usado
                altos_finales_texto.append(altura_texto) # guardo el alto de esta celda
                self.set_y(y_antes_simulacion) # revierto la posición 'y' para la siguiente celda
                x_pos_temp += anchos_columnas[col] # avanzo la posición 'x' para la siguiente celda
            
            # El alto de la fila es el mayor alto de texto calculado + el margen de 1 mm
            max_altura_texto = max(altos_finales_texto)
            alto_fila = max_altura_texto + 1  # agrego 1 mm de margen
            self.set_y(y) # vuelvo a la posición inicial de la fila
            
            # --- BORDES Y TEXTO ---
            self.line(x, y + alto_fila, x + ancho_total, y + alto_fila) # Línea horizontal inferior
            
            # Lineas verticales para separar columnas
            x_pos = x
            for col_ancho in anchos_columnas:
                # Línea vertical derecha
                self.line(x_pos + col_ancho, y, x_pos + col_ancho, y + alto_fila)
                x_pos += col_ancho
                
            # Texto en cada celda
            x_pos = x
            for col, texto in enumerate(fila):

                # Color de relleno del resultado 
                if texto == "Pasó":
                    self.set_fill_color(180, 255, 180)  #Verde
                    fill = True
                elif texto == "Falló":
                    self.set_fill_color(255, 180, 180)  #Rojo
                    fill = True
                else:
                    fill = False  # Sin relleno

                if fill:
                    # Solo rellena el fondo sin tapar el borde
                    self.rect(x_pos+0.1, y+0.1, anchos_columnas[col]-0.2, alto_fila-0.2, style='F')

                # Posición de inicio para el texto: y + 1 (1 mm de margen superior)
                self.set_xy(x_pos + 1, y + 1) 
                # El alto de la multi_cell es line_height, NO alto_fila
                self.multi_cell(anchos_columnas[col] - 2, line_height, str(texto), border=0, align=align)
                x_pos += anchos_columnas[col]

            # Avanzo a la siguiente fila
            y += alto_fila
            self.set_y(y)
            altura_total += alto_fila

        # Dibujo borde externo de cada tabla
        self.rect(x, y_inicial, ancho_total, altura_total)
