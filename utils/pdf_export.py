import io
import os
import tempfile
from xhtml2pdf import pisa
from dash import dcc
from datetime import datetime
import json
import base64
import requests
import traceback
from PIL import Image

def convert_html_to_pdf(source_html, output_filename=None):
    """Convierte HTML a PDF utilizando xhtml2pdf"""
    # Si no se especifica un archivo de salida, usa BytesIO para almacenar el PDF
    if output_filename is None:
        result_file = io.BytesIO()
    else:
        # Si se especifica, abre el archivo para escritura binaria
        result_file = open(output_filename, "w+b")

    # Convertir HTML a PDF
    pisa_status = pisa.CreatePDF(
        source_html,           # el HTML a convertir
        dest=result_file)      # destino para recibir el resultado

    # Si es BytesIO, vuelve al principio para lectura
    if output_filename is None:
        result_file.seek(0)
        pdf_bytes = result_file.read()
        result_file.close()
        return pdf_bytes
    else:
        # Si es un archivo, ciérralo
        result_file.close()
        return pisa_status.err == 0  # Devuelve True si no hay errores

def crear_placeholders_graficos(tipo):
    """Crea descripciones de placeholders para los gráficos"""
    if tipo == "estadistico":
        return [
            {"titulo": "Gráfico de línea: Evolución de rendimiento", 
             "descripcion": "Muestra la evolución de rendimiento de los jugadores a lo largo de las jornadas."},
            {"titulo": "Gráfico de dispersión: Correlación entre variables", 
             "descripcion": "Visualiza la correlación entre diferentes métricas de rendimiento."},
            {"titulo": "Gráfico de barras: Comparativa entre jugadores", 
             "descripcion": "Compara métricas clave entre los jugadores seleccionados."},
            {"titulo": "Histograma: Distribución de métricas", 
             "descripcion": "Muestra la distribución estadística de diferentes métricas."}
        ]
    else:  # físico
        return [
            {"titulo": "Evolución por jornadas", 
             "descripcion": "Muestra la evolución de métricas físicas a lo largo de las jornadas."},
            {"titulo": "Perfil condicional", 
             "descripcion": "Visualiza el perfil físico completo del jugador mediante un gráfico radar."},
            {"titulo": "Relación entre variables", 
             "descripcion": "Analiza la correlación entre diferentes métricas físicas."}
        ]

def generar_html_estadistico(jugadores, rango_jornadas, graficos_base64=None):
    """Genera HTML para informe estadístico con gráficos"""
    # Encabezado y estilos CSS
    html = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Informe Estadístico ATM</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1 {{ color: #003366; }}
            h2 {{ color: #003366; }}
            h3 {{ color: #003366; margin-top: 20px; }}
            h4 {{ color: #003366; margin-top: 15px; }}
            .jugadores {{ margin-bottom: 15px; }}
            .seccion {{ margin-top: 20px; margin-bottom: 20px; }}
            .grafico {{ margin-top: 15px; margin-bottom: 15px; border: 1px solid #cccccc; padding: 10px; }}
            .grafico img {{ max-width: 100%; height: auto; }}
            .caption {{ font-style: italic; font-size: 12px; color: #666666; }}
            .descripcion {{ margin-top: 5px; margin-bottom: 10px; }}
            .pie {{ font-size: 10px; color: #666666; text-align: center; margin-top: 30px; }}
            hr {{ border: 1px solid #cccccc; }}
        </style>
    </head>
    <body>
        <h1>Informe Estadístico ATM</h1>
        <h2>Jugadores: {', '.join(jugadores)} - Jornadas: {rango_jornadas[0]} a {rango_jornadas[1]}</h2>
        
        <div class="seccion">
            <h3>Detalles del análisis</h3>
            <p>Este informe contiene un análisis estadístico de los jugadores seleccionados durante el rango de jornadas especificado.</p>
            <p>Los jugadores analizados son: {', '.join(jugadores)}</p>
            <p>El rango de jornadas analizado es: {rango_jornadas[0]} a {rango_jornadas[1]}</p>
        </div>
        
        <div class="seccion">
            <h3>Gráficos generados</h3>
    """
    
    # Obtener información de gráficos (placeholders o imágenes reales)
    if graficos_base64 and any(graficos_base64):
        # Si hay imágenes base64, usarlas
        placeholders = crear_placeholders_graficos("estadistico")
        for i, (placeholder, imagen_base64) in enumerate(zip(placeholders, graficos_base64)):
            if imagen_base64:
                html += f"""
                <div class="grafico">
                    <h4>{placeholder["titulo"]}</h4>
                    <img src="{imagen_base64}" alt="{placeholder["titulo"]}" />
                    <p class="descripcion">{placeholder["descripcion"]}</p>
                </div>
                """
    else:
        # Si no hay imágenes, mostrar solo la lista
        html += """
            <p>Se han generado los siguientes gráficos en la aplicación:</p>
            <ul>
                <li>Gráfico de línea: Evolución de rendimiento</li>
                <li>Gráfico de dispersión: Correlación entre variables</li>
                <li>Gráfico de barras: Comparativa entre jugadores</li>
                <li>Histograma: Distribución de métricas</li>
            </ul>
            <p><i>Nota: Para visualizar los gráficos completos, por favor consulte la aplicación web.</i></p>
        """
    
    # Continuar con el resto del informe
    html += """
        </div>
        
        <div class="seccion">
            <h3>Resumen de hallazgos</h3>
            <p>El análisis estadístico realizado muestra patrones consistentes en el rendimiento de los jugadores seleccionados a lo largo de las jornadas analizadas. Las métricas físicas y técnicas muestran correlaciones significativas que pueden ser de interés para el cuerpo técnico.</p>
        </div>
        
        <hr>
        
        <div class="pie">
    """
    
    html += f"""
            <p>Informe generado el {datetime.now().strftime('%d/%m/%Y a las %H:%M:%S')}</p>
            <p>Departamento de Análisis - Atlético de Madrid</p>
        </div>
    </body>
    </html>
    """
    
    return html

def generar_html_fisico(jugador_nombre, rango_jornadas, graficos_base64=None, foto_base64=None, heatmap_base64=None):
    """Genera HTML para informe físico con gráficos"""
    # Encabezado y estilos CSS
    html = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Informe Físico ATM - {jugador_nombre}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1 {{ color: #003366; }}
            h2 {{ color: #003366; }}
            h3 {{ color: #003366; margin-top: 20px; }}
            h4 {{ color: #003366; margin-top: 15px; }}
            .jugador {{ margin-bottom: 15px; font-weight: bold; }}
            .seccion {{ margin-top: 20px; margin-bottom: 20px; }}
            .grafico {{ margin-top: 15px; margin-bottom: 15px; border: 1px solid #cccccc; padding: 10px; }}
            .grafico img {{ max-width: 100%; height: auto; }}
            .caption {{ font-style: italic; font-size: 12px; color: #666666; }}
            .descripcion {{ margin-top: 5px; margin-bottom: 10px; }}
            .foto-heatmap {{ display: flex; align-items: center; margin-bottom: 20px; }}
            .foto {{ margin-right: 20px; width: 150px; }}
            .heatmap {{ flex-grow: 1; }}
            .pie {{ font-size: 10px; color: #666666; text-align: center; margin-top: 30px; }}
            hr {{ border: 1px solid #cccccc; }}
        </style>
    </head>
    <body>
        <h1>Informe Físico ATM</h1>
        <h2>Jugador: {jugador_nombre} - Jornadas: {rango_jornadas[0]} a {rango_jornadas[1]}</h2>
        
        <div class="seccion">
            <h3>Información del jugador</h3>
            <p class="jugador">{jugador_nombre}</p>
            <p>El análisis físico realizado cubre el rango de jornadas {rango_jornadas[0]} a {rango_jornadas[1]}.</p>
    """
    
    # Incluir foto y heatmap si están disponibles
    if foto_base64 or heatmap_base64:
        html += """
        <div class="foto-heatmap">
        """
        
        if foto_base64:
            html += f"""
            <div class="foto">
                <img src="{foto_base64}" alt="{jugador_nombre}" />
            </div>
            """
            
        if heatmap_base64:
            html += f"""
            <div class="heatmap">
                <img src="{heatmap_base64}" alt="Mapa de calor" />
                <p class="caption">Mapa de calor de posiciones</p>
            </div>
            """
            
        html += """
        </div>
        """
    
    html += """
        </div>
        
        <div class="seccion">
            <h3>Análisis físico</h3>
    """
    
    # Obtener información de gráficos (placeholders o imágenes reales)
    if graficos_base64 and any(graficos_base64):
        # Si hay imágenes base64, usarlas
        placeholders = crear_placeholders_graficos("fisico")
        for i, (placeholder, imagen_base64) in enumerate(zip(placeholders, graficos_base64)):
            if imagen_base64:
                html += f"""
                <div class="grafico">
                    <h4>{placeholder["titulo"]}</h4>
                    <img src="{imagen_base64}" alt="{placeholder["titulo"]}" />
                    <p class="descripcion">{placeholder["descripcion"]}</p>
                </div>
                """
    else:
        # Si no hay imágenes, mostrar solo la lista
        html += """
            <p>Se han analizado los siguientes elementos:</p>
            <ul>
                <li>Carta completa con datos del jugador</li>
                <li>Mapa de calor de posiciones en el campo</li>
                <li>Evolución por jornadas (gráfico de barras)</li>
                <li>Datos detallados por jornadas</li>
                <li>Perfil condicional (gráfico radar)</li>
                <li>Relación entre variables (gráfico de dispersión)</li>
            </ul>
            <p><i>Nota: Para visualizar los gráficos completos, por favor consulte la aplicación web.</i></p>
        """
    
    # Continuar con el resto del informe
    html += """
        </div>
        
        <div class="seccion">
            <h3>Resumen del análisis físico</h3>
    """
    
    html += f"""
            <p>El análisis físico de {jugador_nombre} muestra patrones consistentes en las métricas de rendimiento físico. Se destacan valores significativos en distancia recorrida y sprints realizados.</p>
            <p>El mapa de calor y el perfil condicional disponibles en la aplicación proporcionan una visualización detallada de su rendimiento físico y zonas de influencia en el campo.</p>
        </div>
        
        <hr>
        
        <div class="pie">
            <p>Informe generado el {datetime.now().strftime('%d/%m/%Y a las %H:%M:%S')}</p>
            <p>Departamento de Análisis - Atlético de Madrid</p>
        </div>
    </body>
    </html>
    """
    
    return html

# Modificar tus callbacks para capturar las imágenes

def procesar_figura_a_base64(figura):
    """Intenta extraer la representación base64 de una figura"""
    try:
        if isinstance(figura, dict) and 'data' in figura:
            figure_json = json.dumps(figura)
            import re
            
            # Buscar patrones de imagen base64 en el JSON
            pattern = r'data:image/[^;]+;base64,[a-zA-Z0-9+/]+=*'
            matches = re.findall(pattern, figure_json)
            if matches:
                return matches[0]
    except:
        pass
    
    return None

# Funciones para exportar
def exportar_pdf_stats(n_clicks, graficos, jugadores, rango_jornadas):
    """Exporta PDF de estadísticas"""
    if not n_clicks:
        return None
    
    try:
        # Generar nombre de archivo
        nombre_archivo = f"Informe_Estadistico_ATM_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        # Procesar gráficos para obtener representaciones base64 si es posible
        graficos_base64 = []
        if graficos:
            graficos_base64 = [procesar_figura_a_base64(g) for g in graficos]
        
        # Generar HTML
        html_content = generar_html_estadistico(jugadores, rango_jornadas, graficos_base64)
        
        # Convertir a PDF
        pdf_bytes = convert_html_to_pdf(html_content)
        
        return dcc.send_bytes(pdf_bytes, nombre_archivo)
    except Exception as e:
        print(f"Error en exportar_pdf_stats: {str(e)}")
        traceback.print_exc()
        return None

def exportar_pdf_fisico(n_clicks, jugador_nombre, foto_path, graficos, heatmap, table_img, rango_jornadas):
    """Exporta PDF físico"""
    if not n_clicks:
        return None
    
    try:
        # Generar nombre de archivo
        nombre_archivo = f"Informe_Fisico_{jugador_nombre}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        # Procesar gráficos para obtener representaciones base64 si es posible
        graficos_base64 = []
        if graficos:
            graficos_base64 = [procesar_figura_a_base64(g) for g in graficos]
        
        # Procesar heatmap
        heatmap_base64 = procesar_figura_a_base64(heatmap) if heatmap else None
        
        # Procesar foto si existe
        foto_base64 = None
        if foto_path and os.path.exists(foto_path):
            try:
                with open(foto_path, 'rb') as f:
                    encoded = base64.b64encode(f.read()).decode('utf-8')
                    foto_base64 = f"data:image/png;base64,{encoded}"
            except:
                pass
        
        # Generar HTML
        html_content = generar_html_fisico(jugador_nombre, rango_jornadas, graficos_base64, foto_base64, heatmap_base64)
        
        # Convertir a PDF
        pdf_bytes = convert_html_to_pdf(html_content)
        
        return dcc.send_bytes(pdf_bytes, nombre_archivo)
    except Exception as e:
        print(f"Error en exportar_pdf_fisico: {str(e)}")
        traceback.print_exc()
        return None

# Función de compatibilidad con el código existente
def exportar_pdf(n_clicks, graficos, titulo, estadistica, rango_jornadas, jugadores=None):
    """
    Función de compatibilidad con código existente
    """
    if not n_clicks:
        return None
    
    try:
        # Si es un informe físico (basado en el título)
        if "Físico" in titulo and jugadores and (isinstance(jugadores, str) or len(jugadores) == 1):
            jugador_nombre = jugadores[0] if isinstance(jugadores, list) else jugadores
            foto_path = f"assets/fotos/{jugador_nombre.lower().replace(' ', '_')}.png"
            if not os.path.exists(foto_path):
                foto_path = None
                
            return exportar_pdf_fisico(
                n_clicks, 
                jugador_nombre, 
                foto_path,
                graficos if isinstance(graficos, list) else [graficos],
                None,  # heatmap
                None,  # table_img
                rango_jornadas
            )
        else:
            # Para informes de estadísticas y otros tipos
            if isinstance(jugadores, list):
                return exportar_pdf_stats(n_clicks, 
                                         graficos if isinstance(graficos, list) else [graficos], 
                                         jugadores, 
                                         rango_jornadas)
            else:
                return exportar_pdf_stats(n_clicks, 
                                         graficos if isinstance(graficos, list) else [graficos], 
                                         [jugadores] if jugadores else [], 
                                         rango_jornadas)
    except Exception as e:
        print(f"Error en exportar_pdf: {str(e)}")
        traceback.print_exc()
        return None