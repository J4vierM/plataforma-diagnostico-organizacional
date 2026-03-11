# reports.py
from fpdf import FPDF
import datetime
import matplotlib.pyplot as plt
import os

# Definimos el color corporativo principal (Verde Oscuro Konantu)
# Valores RGB aproximados para un verde corporativo elegante
# Definimos la paleta de colores oficial de Konantu para el reporte
COLORES_DISC = {'D': '#FF0000', 'I': '#FF9900', 'S': '#008000', 'C': '#0000FF'}
NOMBRES_DISC = {'D': 'Dominante', 'I': 'Influyente', 'S': 'Estable', 'C': 'Concienzudo'}
ORDEN_DISC = ['D', 'I', 'S', 'C']


K_VERDE_R, K_VERDE_G, K_VERDE_B = 26, 92, 46

class ReporteDISC(FPDF):
    def header(self):
        # Logo sobre fondo blanco
        if os.path.exists("Konantu_sin_fondo.png"):
            # Ajustamos coordenadas para que quede alineado a la izquierda
            self.image("Konantu_sin_fondo.png", 10, 15, 30)

        self.set_font("Arial", "B", 20)
        # Usamos el color definido arriba
        self.set_text_color(K_VERDE_R, K_VERDE_G, K_VERDE_B)
        
        # Movmeos la celda a la derecha para no pisar el logo
        self.cell(40)
        self.cell(150, 25, "Informe de Perfil Conductual DISC", 0, 0, "R")
        self.ln(35) #Salto de línea para separar del cuerpo

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.set_text_color(128, 128, 128)
        #Gris neutro para el pie de página
        self.cell(0, 10, f"Página {self.page_no()} - Consultoría Konantu - Confidencial", 0, 0, "C")


def generar_grafico_temp (resultados):
    # Paleta corporativa.
    labels = [NOMBRES_DISC[dim] for dim in ORDEN_DISC]
    values = [resultados.get(dim, 0) for dim in ORDEN_DISC]
    colores = [COLORES_DISC[dim] for dim in ORDEN_DISC]

    fig, ax = plt.subplots(figsize=(5,4))

    # Añadimos un circulo blanco al centro para hacerlo tipo "Donut Chart" (más moderno)
    ax.pie(values, labels = labels, autopct = '%1.0f%%', startangle=90, colors = colores, pctdistance=0.75, wedgeprops=dict(width=0.5, edgecolor='w'))
    ax.axis('equal')

    temp_filename = "temp_chart.png"
    plt.savefig(temp_filename, transparent = True, bbox_inches='tight')
    plt.close()
    return temp_filename

def obtener_interpretacion(resultados):
    """Retorna el párrafo descriptivo según el rasgo más alto"""
    rasgo_max = max(resultados, key=resultados.get)
    descripciones = {
        'D': "Su perfil destaca por una alta orientación a resultados y toma de decisiones rápida. Es una persona que se siente cómoda liderando desafíos y buscando eficiencia.",
        'I': "Usted posee una gran capacidad de influencia y optimismo. Su fortaleza reside en la habilidad para motivar a otros y generar ambientes de colaboración entusiasta.",
        'S': "Su estilo se caracteriza por la lealtad y la búsqueda de estabilidad. Es un pilar fundamental en equipos que requieren constancia, paciencia y armonía.",
        'C': "Usted tiene un alto enfoque en la precisión y la calidad. Su metodología se basa en el análisis riguroso de datos y el respeto por los estándares técnicos."
    }
    return descripciones.get(rasgo_max, "")

def generar_pdf_disc(nombre_usuario, resultados):
    pdf = ReporteDISC()
    pdf.add_page()

    # Datos del evaluado en negro estándar
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, f"Evaluado: {nombre_usuario}", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 7, f"Fecha de emisión: {datetime.date.today().strftime('%d-%m-%Y')}", ln=True)
    pdf.ln(5)

    # Insertar el gráfico centrado
    grafico_path = generar_grafico_temp(resultados)
    pdf.image(grafico_path, x=65, y=65, w=80)
    pdf.ln(85)

    # Tabla en orden D-I-S-C
    pdf.set_fill_color(235, 245, 235) 
    pdf.set_font("Arial", "B", 12)
    pdf.set_text_color(K_VERDE_R, K_VERDE_G, K_VERDE_B) 
    pdf.cell(95, 10, "Rasgo Conductual", 1, 0, 'C', True)
    pdf.cell(95, 10, "Puntaje Obtenido", 1, 1, 'C', True)

    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "", 12)
    for dim in ORDEN_DISC:
        val = resultados.get(dim, 0)
        # Factor con borde 1
        pdf.cell(95, 10, f" {NOMBRES_DISC[dim]}", 1) 
        pdf.cell(95, 10, f"{int(round(val*100))}%", 1, 1, 'C')

    # Sección de Interpretación Cualitativa
    pdf.ln(10)
    pdf.set_text_color(K_VERDE_R, K_VERDE_G, K_VERDE_B)
    pdf.set_font("Arial", "B", 13)
    pdf.cell(0, 10, "Análisis del Perfil Predominante:", ln=True) 

    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "", 11)
    texto_analisis = obtener_interpretacion(resultados)
    pdf.multi_cell(0, 7, texto_analisis)

    # Nota Técnica
    pdf.ln(10)
    pdf.set_font("Arial", "I", 9)
    pdf.set_text_color(100, 100, 100)
    pdf.multi_cell(0, 6, "Nota: Este informe es una herramienta de apoyo para el diagnóstico organizacional y debe ser interpretado por un consultor experto de Konantu.")

    filename = f"Konantu_DISC_{nombre_usuario.replace(' ', '_')}_{datetime.date.today().strftime('%d-%m-%Y')}.pdf"
    pdf.output(filename)
    
    if os.path.exists(grafico_path):
        os.remove(grafico_path)
    return filename