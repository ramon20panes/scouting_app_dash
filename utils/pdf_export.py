import io
import plotly.graph_objs as go
import plotly.io as pio
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PIL import Image
from dash import dcc
from datetime import datetime

# Configurar Kaleido para evitar el error de plotlyjs
pio.kaleido.scope.plotlyjs = None

def format_stat_name(stat_name):
    """Formatea el nombre de la estadística para mostrar"""
    return ' '.join(word.capitalize() for word in stat_name.split('_'))

def generar_pdf(graficos, titulo, estadistica, rango_jornadas, jugadores=None):
    """
    Genera un PDF con los gráficos proporcionados
    
    :param graficos: Lista de figuras de Plotly
    :param titulo: Título del informe
    :param estadistica: Estadística principal
    :param rango_jornadas: Rango de jornadas
    :param jugadores: Lista de jugadores (opcional)
    :return: Bytes del PDF
    """
    # Crear un buffer en memoria para el PDF
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter  # Dimensiones de la página

    # Añadir título
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, 750, titulo)

    # Información del informe
    c.setFont("Helvetica", 12)
    c.drawString(50, 725, f"Estadística principal: {format_stat_name(estadistica)}")
    c.drawString(50, 710, f"Jornadas analizadas: {rango_jornadas[0]} a {rango_jornadas[1]}")

    try:
        # Crear directorio temporal para imágenes
        import tempfile
        import os
        temp_dir = tempfile.mkdtemp()
        
        # Convertir y dibujar gráficos
        vertical_pos = 650  # Posición vertical inicial
        
        for i, fig in enumerate(graficos):
            # Verificar espacio disponible
            if vertical_pos < 200:  # Si no hay suficiente espacio, crear una nueva página
                c.showPage()
                vertical_pos = 750
            
            # Añadir título para cada gráfico
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, vertical_pos, f"{i+1}. Gráfico de {format_stat_name(estadistica)}")
            vertical_pos -= 20
            
            # Generar imagen del gráfico
            img_path = os.path.join(temp_dir, f'grafico_{i}.png')
            
            try:
                # Intentar usar kaleido (mejor calidad)
                fig.write_image(img_path, width=500, height=300, scale=2)
            except Exception as e1:
                try:
                    # Alternativa: usar to_image
                    from plotly.io import to_image
                    img_bytes = to_image(fig, format='png', width=500, height=300, scale=2)
                    with open(img_path, 'wb') as f:
                        f.write(img_bytes)
                except Exception as e2:
                    print(f"Error al generar imagen: {e1}, {e2}")
                    c.setFont("Helvetica", 10)
                    c.drawString(70, vertical_pos, f"* Error al generar gráfico: {str(e1)}")
                    vertical_pos -= 15
                    continue
            
            # Añadir imagen al PDF
            img_width, img_height = 450, 270  # Tamaño ajustado para el PDF
            c.drawImage(img_path, 50, vertical_pos - img_height, width=img_width, height=img_height)
            
            # Actualizar posición vertical
            vertical_pos -= (img_height + 30)  # Espacio entre gráficos
            
        # Limpiar archivos temporales
        for i in range(len(graficos)):
            img_path = os.path.join(temp_dir, f'grafico_{i}.png')
            if os.path.exists(img_path):
                os.remove(img_path)
        os.rmdir(temp_dir)
                
    except Exception as e:
        # En caso de error con las imágenes, incluir texto alternativo
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, 680, "Resumen de Gráficos:")
        
        c.setFont("Helvetica", 11)
        for i, fig in enumerate(graficos):
            title = f"Gráfico {i+1}: {fig.layout.title.text if hasattr(fig.layout, 'title') and hasattr(fig.layout.title, 'text') else 'Gráfico sin título'}"
            c.drawString(50, 650 - (i*40), title)
            
            # Añadir nota sobre la disponibilidad del gráfico
            c.drawString(70, 630 - (i*40), "* Este gráfico está disponible en la aplicación web")
            
        c.drawString(50, 630 - ((len(graficos)+1)*40), f"Nota: Error al generar imágenes: {str(e)}")

    # Información de jugadores si está disponible
    if jugadores:
        if len(jugadores) > 5:
            texto_jugadores = ", ".join(jugadores[:5]) + f"... y {len(jugadores) - 5} más"
        else:
            texto_jugadores = ", ".join(jugadores)
        
        c.drawString(50, 100, f"Jugadores: {texto_jugadores}")

    # Fecha actual
    fecha_actual = datetime.now().strftime("%d/%m/%Y")
    c.drawString(50, 50, f"Fecha del informe: {fecha_actual}")

    # Firma
    c.drawString(400, 50, "Ramón González MPAD")

    c.showPage()
    c.save()

    buffer.seek(0)
    return buffer.getvalue()

def exportar_pdf(n_clicks, graficos, titulo, estadistica, rango_jornadas, jugadores=None):
    """
    Función de exportación de PDF para ser usada en callbacks de Dash
    """
    if not n_clicks:
        return None
    
    pdf_bytes = generar_pdf(graficos, titulo, estadistica, rango_jornadas, jugadores)
    return dcc.send_bytes(pdf_bytes, f"Informe_{estadistica}.pdf")