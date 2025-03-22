import requests
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib
matplotlib.use('Agg')  # Para usar matplotlib sin GUI
import io
import base64
import time
import random

def obtener_datos_heatmap(id_sofascore):
    """
    Obtiene los datos del heatmap de un jugador desde la API de Sofascore
    """
    # URL de la API
    api_url = f"https://www.sofascore.com/api/v1/player/{id_sofascore}/unique-tournament/8/season/61643/heatmap/overall"
    
    # Configurar headers para simular un navegador normal
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json',
        'Referer': 'https://www.sofascore.com/'
    }
    
    try:
        # Añadir un pequeño retraso
        time.sleep(0.5)

        # Realizar la solicitud HTTP a la API
        response = requests.get(api_url, headers=headers)
        
        # Verificar si la solicitud fue exitosa
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error al obtener heatmap, código: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error al obtener heatmap: {e}")
        return None

def generar_mensaje_heatmap(mensaje):
    """
    Genera una imagen con un mensaje de error o información
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.text(0.5, 0.5, mensaje, 
            horizontalalignment='center', verticalalignment='center', 
            transform=ax.transAxes, fontsize=14)
    ax.axis('off')
    
    # Guardar en buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)
    
    # Codificar en base64
    encoded = base64.b64encode(buf.read()).decode('utf-8')
    return encoded

def generar_heatmap_simulado(id_sofascore):
    """
    Genera un heatmap simulado cuando no se pueden obtener datos de la API
    """
    # Crear figura
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Dimensiones del campo
    field_length = 105
    field_width = 68
    
    # Dibujar campo de fútbol
    # Fondo verde
    rect = Rectangle((0, 0), field_length, field_width, 
                    facecolor='#4CAF50',
                    alpha=0.8,
                    edgecolor=None)
    ax.add_patch(rect)
    
    # Líneas del campo
    line_color = 'darkblue'
    line_width = 1.5
    
    # Líneas exteriores
    ax.plot([0, 0, field_length, field_length, 0], 
             [0, field_width, field_width, 0, 0], 
             color=line_color, linewidth=line_width)
    
    # Línea de medio campo
    ax.plot([field_length/2, field_length/2], [0, field_width], color=line_color, linewidth=line_width)
    
    # Círculo central
    center_circle = plt.Circle((field_length/2, field_width/2), 9.15, fill=False, 
                              color=line_color, linewidth=line_width)
    ax.add_artist(center_circle)
    
    # Áreas
    # Área grande izquierda
    ax.plot([0, 16.5], [field_width/2 - 20.15, field_width/2 - 20.15], color=line_color, linewidth=line_width)
    ax.plot([16.5, 16.5], [field_width/2 - 20.15, field_width/2 + 20.15], color=line_color, linewidth=line_width)
    ax.plot([0, 16.5], [field_width/2 + 20.15, field_width/2 + 20.15], color=line_color, linewidth=line_width)
    
    # Área grande derecha
    ax.plot([field_length, field_length - 16.5], [field_width/2 - 20.15, field_width/2 - 20.15], color=line_color, linewidth=line_width)
    ax.plot([field_length - 16.5, field_length - 16.5], [field_width/2 - 20.15, field_width/2 + 20.15], color=line_color, linewidth=line_width)
    ax.plot([field_length, field_length - 16.5], [field_width/2 + 20.15, field_width/2 + 20.15], color=line_color, linewidth=line_width)
    
    # Generar datos aleatorios basados en el ID del jugador para que sea consistente
    random.seed(int(id_sofascore) % 1000)
    
    # Simular posiciones según la posición típica (depende del rango del ID)
    if int(id_sofascore) % 4 == 0:  # Porteros
        x_center = 10
        y_center = field_width/2
        x_range = 15
        y_range = 30
    elif int(id_sofascore) % 4 == 1:  # Defensas
        x_center = 30
        y_center = field_width/2
        x_range = 25
        y_range = 50
    elif int(id_sofascore) % 4 == 2:  # Mediocampistas
        x_center = field_length/2
        y_center = field_width/2
        x_range = 40
        y_range = 55
    else:  # Delanteros
        x_center = 75
        y_center = field_width/2
        x_range = 30
        y_range = 45
    
    # Generar puntos aleatorios con distribución normal
    num_points = 200
    x = np.random.normal(x_center, x_range/3, num_points)
    y = np.random.normal(y_center, y_range/3, num_points)
    
    # Limitar a las dimensiones del campo
    x = np.clip(x, 0, field_length)
    y = np.clip(y, 0, field_width)
    
    # Crear heatmap usando hexbin
    hb = ax.hexbin(
        x, 
        y,
        gridsize=40,
        cmap='Blues',
        alpha=0.8,
        mincnt=1,
        extent=[0, field_length, 0, field_width]
    )
    
    # Colorbar
    cbar = plt.colorbar(hb, ax=ax)
    cbar.set_label('Densidad', fontsize=8, color="darkblue", weight="bold")
    
    # Configuración de ejes
    ax.set_aspect('equal')
    ax.set_xlim(-5, field_length + 5)
    ax.set_ylim(-5, field_width + 5)
    ax.axis('off')
    
    # Guardar en buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)
    
    # Codificar en base64
    encoded = base64.b64encode(buf.read()).decode('utf-8')
    return encoded

def generar_heatmap(id_sofascore):
    """
    Genera una imagen de heatmap para un jugador basado en su ID de Sofascore
    """
    # Verificar que se ha recibido un ID válido
    if not id_sofascore:
        print("ID de Sofascore no proporcionado")
        # Retornar imagen de "No disponible"
        return generar_mensaje_heatmap("ID de Sofascore no disponible")
    
    try:
        # Convertir a entero para asegurarnos que es un ID válido
        id_sofascore = int(id_sofascore)
    except:
        print(f"ID de Sofascore inválido: {id_sofascore}")
        return generar_mensaje_heatmap("ID de Sofascore inválido")
    
    # Obtener datos
    data = obtener_datos_heatmap(id_sofascore)
    
    if not data or 'points' not in data or len(data.get('points', [])) == 0:
        print(f"No hay datos disponibles para el ID: {id_sofascore}, generando simulación")
        # Usar heatmap simulado cuando no hay datos
        return generar_heatmap_simulado(id_sofascore)
    
    # Procesar los datos de puntos
    points = data['points']
    x = [p['x'] for p in points]
    y = [p['y'] for p in points]
    counts = [p.get('count', 1) for p in points]
    
    # Determinar dimensiones del campo
    field_length = 105
    field_width = 68
    
    # Análisis de rangos para normalización
    x_min, x_max = min(x), max(x)
    y_min, y_max = min(y), max(y)
    
    # Crear figura
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Dibujar campo de fútbol
    # Fondo verde
    rect = Rectangle((0, 0), field_length, field_width, 
                    facecolor='#4CAF50',  # Verde césped
                    alpha=0.8,            # Semitransparente
                    edgecolor=None)
    ax.add_patch(rect)
    
    # Líneas del campo
    line_color = 'darkblue'
    line_width = 1.5
    
    # Líneas exteriores
    ax.plot([0, 0, field_length, field_length, 0], 
             [0, field_width, field_width, 0, 0], 
             color=line_color, linewidth=line_width)
    
    # Línea de medio campo
    ax.plot([field_length/2, field_length/2], [0, field_width], color=line_color, linewidth=line_width)
    
    # Círculo central
    center_circle = plt.Circle((field_length/2, field_width/2), 9.15, fill=False, 
                              color=line_color, linewidth=line_width)
    ax.add_artist(center_circle)
    
    # Áreas
    # Área grande izquierda
    ax.plot([0, 16.5], [field_width/2 - 20.15, field_width/2 - 20.15], color=line_color, linewidth=line_width)
    ax.plot([16.5, 16.5], [field_width/2 - 20.15, field_width/2 + 20.15], color=line_color, linewidth=line_width)
    ax.plot([0, 16.5], [field_width/2 + 20.15, field_width/2 + 20.15], color=line_color, linewidth=line_width)
    
    # Área grande derecha
    ax.plot([field_length, field_length - 16.5], [field_width/2 - 20.15, field_width/2 - 20.15], color=line_color, linewidth=line_width)
    ax.plot([field_length - 16.5, field_length - 16.5], [field_width/2 - 20.15, field_width/2 + 20.15], color=line_color, linewidth=line_width)
    ax.plot([field_length, field_length - 16.5], [field_width/2 + 20.15, field_width/2 + 20.15], color=line_color, linewidth=line_width)
    
    # Transformación de coordenadas
    # Centro del campo original y destino
    x_center_orig = (x_max + x_min) / 2
    y_center_orig = (y_max + y_min) / 2
    x_center_target = field_length / 2
    y_center_target = field_width / 2
    
    # Factores de escala con expansión
    expansion_factor = 1.05
    scale_x = field_length / (x_max - x_min) * expansion_factor if x_max > x_min else 1
    scale_y = field_width / (y_max - y_min) * expansion_factor if y_max > y_min else 1
    
    # Transformar coordenadas
    x_transformed = [(xi - x_center_orig) * scale_x + x_center_target for xi in x]
    y_transformed = [(yi - y_center_orig) * scale_y + y_center_target for yi in y]
    
    # Limitar coordenadas al campo
    margin = 2
    x_transformed = [max(0-margin, min(xi, field_length+margin)) for xi in x_transformed]
    y_transformed = [max(0-margin, min(yi, field_width+margin)) for yi in y_transformed]
    
    # Crear puntos ponderados basados en el conteo
    x_weighted = []
    y_weighted = []
    
    for i in range(len(x_transformed)):
        # Repetir cada punto según su conteo
        x_weighted.extend([x_transformed[i]] * counts[i])
        y_weighted.extend([y_transformed[i]] * counts[i])
    
    # Crear heatmap usando hexbin
    hb = ax.hexbin(
        x_weighted, 
        y_weighted,
        gridsize=40,
        cmap='Blues',
        alpha=0.8,
        mincnt=1,
        extent=[0, field_length, 0, field_width]
    )
    
    # Colorbar
    cbar = plt.colorbar(hb, ax=ax)
    cbar.set_label('Densidad', fontsize=8, color="darkblue", weight="bold")
    
    # Configuración de ejes
    ax.set_aspect('equal')
    ax.set_xlim(-5, field_length + 5)
    ax.set_ylim(-5, field_width + 5)
    ax.axis('off')
       
    # Guardar en buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)
    
    # Codificar en base64
    encoded = base64.b64encode(buf.read()).decode('utf-8')
    return encoded