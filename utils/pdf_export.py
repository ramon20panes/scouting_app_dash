import io
import os
from xhtml2pdf import pisa
from dash import dcc, html
from datetime import datetime
import base64
import dash_bootstrap_components as dbc

def convert_html_to_pdf(source_html):
    """Convierte HTML a PDF utilizando xhtml2pdf"""
    buffer = io.BytesIO()
    
    # Convertir HTML a PDF
    pisa_status = pisa.CreatePDF(
        source_html,           # el HTML a convertir
        dest=buffer)           # destino para recibir el resultado

    # Preparar el buffer para lectura
    buffer.seek(0)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes

def generar_template_estadistico(jugadores, rango_jornadas):
    """Genera un template HTML para el informe estadístico"""
    fecha_generacion = datetime.now().strftime('%d/%m/%Y a las %H:%M:%S')
    
    # Cargar escudo - PRUEBA AMBAS RUTAS
    escudo_base64 = ""
    posibles_rutas = [
        "assets/escudosatm.png",
        "assets/escudos/atm.png",
        "assets/img/atm.png",
        "assets/logos/atm.png"
    ]
    
    for ruta in posibles_rutas:
        try:
            if os.path.exists(ruta):
                with open(ruta, "rb") as img_file:
                    escudo_bytes = img_file.read()
                    escudo_base64 = base64.b64encode(escudo_bytes).decode('utf-8')
                print(f"Escudo encontrado en: {ruta}")
                break
        except Exception as e:
            print(f"Error cargando escudo desde {ruta}: {str(e)}")
    
    # Crear HTML profesional con colores del Atleti
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Informe Estadístico Atleti</title>
        <style>
            body {{ 
                font-family: Arial, sans-serif; 
                margin: 20px; 
                color: #333333;
            }}
            h1 {{ 
                color: #003366; 
                font-size: 24pt;
                margin-top: 10px;
            }}
            h2 {{ 
                color: #003366; 
                font-size: 16pt;
                border-bottom: 2px solid #003366;
                padding-bottom: 5px;
            }}
            h3 {{ 
                color: #c70101; 
                font-size: 14pt;
            }}
            .header {{ 
                display: flex; 
                align-items: center; 
                margin-bottom: 20px;
            }}
            .logo {{ 
                margin-right: 20px; 
            }}
            .info {{ 
                background-color: #f0f5fa; 
                padding: 15px; 
                margin: 15px 0; 
                border-left: 5px solid #003366;
            }}
            .section {{ 
                margin: 20px 0; 
            }}
            .metric {{
                margin-bottom: 15px;
                padding-left: 10px;
            }}
            .footer {{ 
                font-size: 10px; 
                text-align: center; 
                margin-top: 30px;
                border-top: 1px solid #cccccc;
                padding-top: 10px;
                color: #666666;
            }}
        </style>
    </head>
    <body>
        <div class="header">
    """
    
    # Agregar logo si está disponible
    if escudo_base64:
        html += f'<div class="logo"><img src="data:image/png;base64,{escudo_base64}" width="80" height="80" alt="Atleti Logo"></div>'
    
    html += f"""
            <h1>INFORME ESTADÍSTICO ATLETI</h1>
        </div>
        
        <div class="info">
            <h2>Información del Análisis</h2>
            <p><strong>Jugadores analizados:</strong> {', '.join(jugadores)}</p>
            <p><strong>Jornadas analizadas:</strong> {rango_jornadas[0]} a {rango_jornadas[1]}</p>
            <p><strong>Fecha de generación:</strong> {fecha_generacion}</p>
        </div>
        
        <div class="section">
            <h2>Análisis de Rendimiento</h2>
            
            <div class="metric">
                <h3>Evolución de Rendimiento</h3>
                <p>Muestra la evolución del rendimiento de cada jugador a lo largo de las jornadas seleccionadas.</p>
            </div>
            
            <div class="metric">
                <h3>Correlación entre Variables</h3>
                <p>Analiza la relación entre diferentes métricas de rendimiento para identificar patrones significativos.</p>
            </div>
            
            <div class="metric">
                <h3>Comparativa entre Jugadores</h3>
                <p>Facilita la comparación directa entre los jugadores seleccionados en términos de métricas clave.</p>
            </div>
            
            <div class="metric">
                <h3>Distribución Estadística</h3>
                <p>Muestra la distribución de frecuencias de las métricas analizadas para evaluar consistencia.</p>
            </div>
        </div>
        
        <div class="section">
            <h2>Conclusiones</h2>
            <p>El análisis estadístico realizado muestra patrones consistentes en el rendimiento de los jugadores 
            seleccionados a lo largo de las jornadas analizadas.</p>
            <p>Las métricas físicas y técnicas muestran correlaciones significativas que pueden ser de interés para el cuerpo técnico.</p>
        </div>
        
        <div class="footer">
            <p>Documento confidencial - Atlético de Madrid | Departamento de Análisis</p>
        </div>
    </body>
    </html>
    """
    
    return html

def generar_template_fisico(jugador_nombre, rango_jornadas):
    """Genera un template HTML para el informe físico"""
    fecha_generacion = datetime.now().strftime('%d/%m/%Y a las %H:%M:%S')
    
    # Cargar escudo - PRUEBA AMBAS RUTAS
    escudo_base64 = ""
    posibles_rutas = [
        "assets/escudosatm.png",
        "assets/escudos/atm.png",
        "assets/img/atm.png",
        "assets/logos/atm.png"
    ]
    
    for ruta in posibles_rutas:
        try:
            if os.path.exists(ruta):
                with open(ruta, "rb") as img_file:
                    escudo_bytes = img_file.read()
                    escudo_base64 = base64.b64encode(escudo_bytes).decode('utf-8')
                print(f"Escudo encontrado en: {ruta}")
                break
        except Exception as e:
            print(f"Error cargando escudo desde {ruta}: {str(e)}")
    
    # Crear HTML profesional con colores del Atleti
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Informe Físico Atleti</title>
        <style>
            body {{ 
                font-family: Arial, sans-serif; 
                margin: 20px; 
                color: #333333;
            }}
            h1 {{ 
                color: #003366; 
                font-size: 24pt;
                margin-top: 10px;
            }}
            h2 {{ 
                color: #003366; 
                font-size: 16pt;
                border-bottom: 2px solid #003366;
                padding-bottom: 5px;
            }}
            h3 {{ 
                color: #c70101; 
                font-size: 14pt;
            }}
            .header {{ 
                display: flex; 
                align-items: center; 
                margin-bottom: 20px;
            }}
            .logo {{ 
                margin-right: 20px; 
            }}
            .info {{ 
                background-color: #f0f5fa; 
                padding: 15px; 
                margin: 15px 0; 
                border-left: 5px solid #003366;
            }}
            .section {{ 
                margin: 20px 0; 
            }}
            .metric {{
                margin-bottom: 15px;
                padding-left: 10px;
            }}
            .footer {{ 
                font-size: 10px; 
                text-align: center; 
                margin-top: 30px;
                border-top: 1px solid #cccccc;
                padding-top: 10px;
                color: #666666;
            }}
            .jugador-nombre {{
                font-size: 18pt;
                font-weight: bold;
                color: #003366;
                margin: 10px 0;
            }}
        </style>
    </head>
    <body>
        <div class="header">
    """
    
    # Agregar logo si está disponible
    if escudo_base64:
        html += f'<div class="logo"><img src="data:image/png;base64,{escudo_base64}" width="80" height="80" alt="Atleti Logo"></div>'
    
    html += f"""
            <h1>INFORME FÍSICO ATLETI</h1>
        </div>
        
        <div class="info">
            <h2>Información del Jugador</h2>
            <p class="jugador-nombre">{jugador_nombre}</p>
            <p><strong>Jornadas analizadas:</strong> {rango_jornadas[0]} a {rango_jornadas[1]}</p>
            <p><strong>Fecha de generación:</strong> {fecha_generacion}</p>
        </div>
        
        <div class="section">
            <h2>Análisis Físico</h2>
            
            <div class="metric">
                <h3>Carta completa con datos del jugador</h3>
                <p>Información completa del jugador, incluyendo datos personales y características principales.</p>
            </div>
            
            <div class="metric">
                <h3>Mapa de calor de posiciones</h3>
                <p>Visualiza las zonas del campo donde el jugador ha tenido mayor presencia durante las jornadas analizadas.</p>
            </div>
            
            <div class="metric">
                <h3>Evolución por jornadas</h3>
                <p>Muestra la progresión de métricas físicas clave a lo largo de las jornadas seleccionadas.</p>
            </div>
            
            <div class="metric">
                <h3>Perfil condicional</h3>
                <p>Gráfico radar que representa el perfil físico completo del jugador en comparación con valores de referencia.</p>
            </div>
            
            <div class="metric">
                <h3>Relación entre variables</h3>
                <p>Análisis de correlación entre diferentes métricas físicas para identificar patrones de rendimiento.</p>
            </div>
        </div>
        
        <div class="section">
            <h2>Conclusiones</h2>
            <p>El análisis físico de {jugador_nombre} muestra patrones consistentes en las métricas de rendimiento físico.</p>
            <p>Se destacan valores significativos en distancia recorrida y sprints realizados.</p>
            <p>El mapa de calor y el perfil condicional proporcionan una visualización detallada de su rendimiento físico 
            y zonas de influencia en el campo.</p>
        </div>
        
        <div class="footer">
            <p>Documento confidencial - Atlético de Madrid | Departamento de Análisis</p>
        </div>
    </body>
    </html>
    """
    
    return html

def exportar_pdf_stats(n_clicks, graficos, jugadores, rango_jornadas):
    """Exporta PDF de estadísticas"""
    if not n_clicks:
        return None
    
    try:
        # Generar HTML
        html_content = generar_template_estadistico(jugadores, rango_jornadas)
        
        # Convertir a PDF
        pdf_bytes = convert_html_to_pdf(html_content)
        
        # Generar nombre de archivo
        fecha_hora = datetime.now().strftime('%Y%m%d_%H%M%S')
        nombre_archivo = f"Informe_Estadistico_Atleti_{fecha_hora}.pdf"
        
        return dcc.send_bytes(pdf_bytes, nombre_archivo)
    except Exception as e:
        print(f"Error en exportar_pdf_stats: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def exportar_pdf_fisico(n_clicks, jugador_nombre, foto_path, graficos, heatmap, table_img, rango_jornadas):
    """Exporta PDF físico"""
    if not n_clicks:
        return None
        
    try:
        # Si no hay nombre de jugador, usar un valor por defecto
        if not jugador_nombre:
            jugador_nombre = "Jugador"
            
        # Si no hay rango de jornadas o es inválido, usar valores por defecto
        if not rango_jornadas or len(rango_jornadas) < 2:
            rango_jornadas = [1, 38]
            
        # Generar HTML
        html_content = generar_template_fisico(jugador_nombre, rango_jornadas)
        
        # Convertir a PDF
        pdf_bytes = convert_html_to_pdf(html_content)
        
        # Generar nombre de archivo
        fecha_hora = datetime.now().strftime('%Y%m%d_%H%M%S')
        nombre_archivo = f"Informe_Fisico_Atleti_{jugador_nombre}_{fecha_hora}.pdf"
        
        return dcc.send_bytes(pdf_bytes, nombre_archivo)
    except Exception as e:
        print(f"Error en exportar_pdf_fisico: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def crear_boton_exportar_pdf():
    """Crea un botón estilizado para exportar a PDF estadístico"""
    return dbc.Button(
        "Exportar PDF",
        id="exportar-pdf-btn-stats",
        color="primary",  # Color azul
        className="me-2"
    )

def crear_boton_exportar_pdf_fisico():
    """Crea un botón estilizado para exportar a PDF físico"""
    return dbc.Button(
        "Exportar PDF",
        id="exportar-pdf-btn-physical",
        color="primary",  # Color azul
        className="me-2"
    )

# Función de compatibilidad
def exportar_pdf(n_clicks, graficos, titulo, estadistica, rango_jornadas, jugadores=None):
    """Función de compatibilidad con código existente"""
    if not n_clicks:
        return None
    
    try:
        # Si es un informe físico
        if "Físico" in titulo:
            jugador_nombre = jugadores[0] if isinstance(jugadores, list) and len(jugadores) > 0 else jugadores
            return exportar_pdf_fisico(
                n_clicks, 
                jugador_nombre, 
                None,  # foto_path
                graficos,
                None,  # heatmap
                None,  # table_img
                rango_jornadas
            )
        else:
            # Para informes de estadísticas
            if isinstance(jugadores, list):
                return exportar_pdf_stats(n_clicks, graficos, jugadores, rango_jornadas)
            else:
                return exportar_pdf_stats(n_clicks, graficos, [jugadores] if jugadores else [], rango_jornadas)
    except Exception as e:
        print(f"Error en exportar_pdf: {str(e)}")
        import traceback
        traceback.print_exc()
        return None