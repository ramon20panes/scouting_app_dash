import pandas as pd
import numpy as np
import sqlite3
import plotly.graph_objects as go
import plotly.express as px
import dash
from dash.dependencies import Input, Output, State
from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
import requests
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from config import CONFIG
import base64
import json
import os
from flask_login import current_user
import unicodedata
from utils.pdf_export import exportar_pdf
from utils.pdf_export import exportar_pdf_fisico
from utils.heatmap_generator import generar_heatmap


def register_physical_data_callbacks(app):
    """
    Registra los callbacks para la página de datos físicos/condicionales
    """
    
    # Función para normalizar nombres (quitar acentos, minúsculas)
    def normalize_name(name):
        # Normalizar, convertir a minúsculas y quitar espacios extras
        if not name:
            return ""
        
         # Reemplazar caracteres específicos antes de la normalización
        name = str(name).lower()
        name = name.replace('ø', 'o')
        name = name.replace('æ', 'ae')
        name = name.replace('å', 'a')

        return ' '.join(unicodedata.normalize('NFKD', str(name).lower())
                        .encode('ASCII', 'ignore')
                        .decode('ASCII')
                        .split())
    
    # AÑADE ESTA FUNCIÓN - Define el diccionario de jugadores una sola vez
    def get_jugadores_default():
        return {
            'Julián Álvarez': {                            
                'nombre_completo': 'Julián Álvarez',
                'short_name': 'Julián',
                'id_sofascore': 944656,
                'ruta_foto': '/assets/players/19.png'
            },
            'Axel Witsel': {
                'nombre_completo': 'Axel Witsel',
                'short_name': 'Witsel',
                'id_sofascore': 35612,
                'ruta_foto': '/assets/players/20.png'
            },
            'Javi Galán': {
                'nombre_completo': 'Javi Galán',
                'short_name': 'Galán',
                'id_sofascore': 825133,
                'ruta_foto': '/assets/players/21.png'
            },
            'Giuliano Simeone': {
                'nombre_completo': 'Giuliano Simeone',
                'short_name': 'Giuliano',
                'id_sofascore': 1099352,
                'ruta_foto': '/assets/players/22.png'
            },
            'Reinildo Mandava': {
                'nombre_completo': 'Reinildo Mandava',
                'short_name': 'Reinildo',
                'id_sofascore': 831424,
                'ruta_foto': '/assets/players/23.png'
            },
            'Robin Le Normand': {
                'nombre_completo': 'Robin Le Normand',
                'short_name': 'Le Normand',
                'id_sofascore': 787751,
                'ruta_foto': '/assets/players/24.png'
            },
            'Adrián Niño': {
                'nombre_completo': 'Adrián Niño',
                'short_name': 'Niño',
                'id_sofascore': 1402927,
                'ruta_foto': '/assets/players/24.png'
            }
        }
    
    def cargar_archivo_maestro():
        """Carga el archivo maestro de jugadores"""
        try:
            if os.path.exists('data/jugadores_master.csv'):
                # Intentar diferentes configuraciones de lectura
                try:
                    # Intentar leer con tab como separador
                    maestro_df = pd.read_csv('data/jugadores_master.csv', sep='\t', encoding='utf-8')
                    # Verificar si tiene una sola columna con múltiples separadores dentro
                    if len(maestro_df.columns) == 1 and ';' in maestro_df.columns[0]:                        
                        primera_col = maestro_df.columns[0]
                        nuevas_cols = primera_col.split(';')
                        valores_split = [row.split(';') for row in maestro_df[primera_col]]
                        maestro_df = pd.DataFrame(valores_split, columns=nuevas_cols)
                        
                    else:
                        print("Archivo maestro cargado con separador tab")
                except Exception as e1:
                    try:
                        # Intentar con separador punto y coma
                        maestro_df = pd.read_csv('data/jugadores_master.csv', sep=';', encoding='utf-8')
                        
                    except Exception as e2:
                        try:
                            # Intentar con separador coma
                            maestro_df = pd.read_csv('data/jugadores_master.csv', encoding='utf-8')
                        except Exception as e3:                            
                            # CAMBIO AQUÍ - Usar función en lugar del diccionario
                            jugadores_info = get_jugadores_default()
                            return pd.DataFrame.from_dict(jugadores_info, orient='index').reset_index().rename(columns={'index': 'nombre'})

                # Normalizar columnas cruciales
                if 'nombre_completo' in maestro_df.columns:
                    maestro_df['nombre'] = maestro_df['nombre_completo']  # Asegurar que existe columna 'nombre'
            
                if 'nombre_completo' in maestro_df.columns and 'nombre_completo_norm' not in maestro_df.columns:
                    maestro_df['nombre_completo_norm'] = maestro_df['nombre_completo'].apply(normalize_name)
            
                if 'short_name' in maestro_df.columns and 'short_name_norm' not in maestro_df.columns:
                    maestro_df['short_name_norm'] = maestro_df['short_name'].apply(normalize_name)
            
                # Asegurar que 'ruta_foto' comienza con '/'
                if 'ruta_foto' in maestro_df.columns:
                    maestro_df['ruta_foto'] = maestro_df['ruta_foto'].apply(
                        lambda x: '/' + x.lstrip('/') if isinstance(x, str) else x
                    )
            
                # Corregir rutas de fotos específicas (solo en memoria)
                for idx, row in maestro_df.iterrows():
                    if 'nombre_completo' in row and row['nombre_completo'] == 'Julián Álvarez' and 'ruta_foto' in maestro_df.columns:
                        maestro_df.at[idx, 'ruta_foto'] = '/assets/players/19.png'
                    if 'nombre_completo' in row and row['nombre_completo'] == 'Jan Oblak' and 'ruta_foto' in maestro_df.columns:
                        maestro_df.at[idx, 'ruta_foto'] = '/assets/players/13.png'
                    if 'nombre_completo' in row and row['nombre_completo'] == 'Reinildo Mandava' and 'ruta_foto' in maestro_df.columns:
                        maestro_df.at[idx, 'ruta_foto'] = '/assets/players/23.png'
                    
                return maestro_df
            else:
                print("No se encontró el archivo maestro. Usando datos fijos para jugadores clave.")
                # CAMBIO AQUÍ - Usar función en lugar del diccionario
                jugadores_info = get_jugadores_default()
                return pd.DataFrame.from_dict(jugadores_info, orient='index').reset_index().rename(columns={'index': 'nombre'})
        except Exception as e:
            print(f"Error al cargar archivo maestro: {e}")
            import traceback
            traceback.print_exc()
            # CAMBIO AQUÍ - Usar función en lugar del diccionario
            jugadores_info = get_jugadores_default()
            return pd.DataFrame.from_dict(jugadores_info, orient='index').reset_index().rename(columns={'index': 'nombre'})
    
    # Función auxiliar para cargar datos condicionales
    def cargar_datos_fisicos(nombre_jugador):
        """Carga los datos físicos de un jugador desde la BD"""
        conn = sqlite3.connect('data/ATM_condic_24_25.db')
        query = f"""
        SELECT * FROM datos_fisicos 
        WHERE Nombre = ?
        ORDER BY Jornada
        """
        df = pd.read_sql(query, conn, params=[nombre_jugador])
        conn.close()
        return df
    
    # Función auxiliar para cargar datos del jugador
    def cargar_datos_jugador(nombre_jugador):
        """Carga los datos maestros de un jugador"""
        try:
            # Corregir nombre del jugador
            try:
                nombre_jugador_corregido = nombre_jugador.encode('latin1').decode('utf-8')
            except:
                nombre_jugador_corregido = nombre_jugador
        
            # Obtener estadísticas adicionales de los datos físicos
            conn = sqlite3.connect('data/ATM_condic_24_25.db')
        
            # Consultar estadísticas agregadas
            query_stats = """
            SELECT 
                AVG(Distancia) as avg_distancia,
                MAX(Distancia) as max_distancia,
                AVG(Max_Speed) as avg_velocidad,
                MAX(Max_Speed) as max_velocidad,
                AVG(Sprints_Abs_Cnt) as avg_sprints
            FROM datos_fisicos 
            WHERE Nombre = ?
            """
        
            stats_df = pd.read_sql(query_stats, conn, params=[nombre_jugador])
        
            # Consultar datos básicos
            query_basic = """
            SELECT Nombre as nombre, Posicion as posicion, Edad as edad
            FROM datos_fisicos 
            WHERE Nombre = ?
            LIMIT 1
            """
        
            jugador_df = pd.read_sql(query_basic, conn, params=[nombre_jugador])
            conn.close()
        
            if not jugador_df.empty:
                # Datos básicos del jugador
                jugador = jugador_df.iloc[0].to_dict()
            
                # Mostrar nombre corregido si tiene caracteres especiales
                jugador['nombre_display'] = nombre_jugador_corregido
            
                # Agregar estadísticas clave
                if not stats_df.empty:
                    for col in stats_df.columns:
                        if not pd.isna(stats_df[col].iloc[0]):
                            jugador[col] = round(stats_df[col].iloc[0], 1)
            
                # Valores por defecto
                jugador['id_sofascore'] = None
                jugador['foto_url'] = '/assets/imagenes/player_placeholder.png'
                jugador['nacionalidad'] = 'ESP'
            
                # Cargar archivo maestro para datos adicionales
                maestro_df = cargar_archivo_maestro()
            
                if not maestro_df.empty:
                    try:
                        # Normalizar nombre para búsqueda
                        nombre_norm = normalize_name(nombre_jugador_corregido)
                                            
                        # Buscar coincidencia en el archivo maestro
                        for idx, row in maestro_df.iterrows():
                            if 'short_name' in maestro_df.columns:
                                row_short_name_norm = normalize_name(str(row['short_name']))
                            
                                # Si hay coincidencia por nombre
                                if row_short_name_norm == nombre_norm or normalize_name(str(row['nombre_completo'])).find(nombre_norm) >= 0:
                                                                    
                                    # Actualizar datos del jugador
                                    jugador['nombre'] = row['nombre_completo']
                                
                                    if 'id_sofascore' in maestro_df.columns:
                                        jugador['id_sofascore'] = int(float(row['id_sofascore'])) if not pd.isna(row['id_sofascore']) else None
                                
                                    if 'ruta_foto' in maestro_df.columns:
                                        jugador['foto_url'] = row['ruta_foto']
                                    elif 'image_sofascore' in maestro_df.columns:
                                        jugador['foto_url'] = row['image_sofascore']
                                
                                    if 'pais' in maestro_df.columns:
                                        jugador['nacionalidad'] = row['pais']
                                
                                    break
                    
                    except Exception as e:
                        print(f"Error al procesar archivo maestro: {e}")
                        import traceback
                        traceback.print_exc()

                jugadores_respaldo = {
                   'Julián Álvarez': {                            
                        'nombre_completo': 'Julián Álvarez',
                        'short_name': 'Julián',
                        'id_sofascore': 944656,
                        'ruta_foto': '/assets/players/19.png'
                    },
                    'Axel Witsel': {
                        'nombre_completo': 'Axel Witsel',
                        'short_name': 'Witsel',
                        'id_sofascore': 35612,
                        'ruta_foto': '/assets/players/20.png'
                    },
                    'Javi Galán': {
                        'nombre_completo': 'Javi Galán',
                        'short_name': 'Galán',
                        'id_sofascore': 825133,
                        'ruta_foto': '/assets/players/21.png'
                    },
                    'Giuliano Simeone': {
                        'nombre_completo': 'Giuliano Simeone',
                        'short_name': 'Giuliano',
                        'id_sofascore': 1099352,
                        'ruta_foto': '/assets/players/22.png'
                    },
                    'Reinildo Mandava': {
                        'nombre_completo': 'Reinildo Mandava',
                        'short_name': 'Reinildo',
                        'id_sofascore': 831424,
                        'ruta_foto': '/assets/players/23.png'
                    },
                    'Robin Le Normand': {
                        'nombre_completo': 'Robin Le Normand',
                        'short_name': 'Le Normand',
                        'id_sofascore': 787751,
                        'ruta_foto': '/assets/players/24.png'
                    },
                    'Adrián Niño': {
                        'nombre_completo': 'Adrián Niño',
                        'short_name': 'Niño',
                        'id_sofascore': 1402927,
                        'ruta_foto': '/assets/players/24.png'
                    }
                }

                # Buscar por nombre normalizado
                nombre_norm = normalize_name(nombre_jugador_corregido)
                if nombre_norm in jugadores_respaldo:

                    info_respaldo = jugadores_respaldo[nombre_norm]
                    for key, value in info_respaldo.items():
                        jugador[key] = value


                return jugador
            else:
                print(f"No se encontraron datos básicos para {nombre_jugador}")
                # Datos por defecto si no se encuentra
                return {
                    'nombre': nombre_jugador_corregido,
                    'posicion': 'No disponible',
                    'edad': 'No disponible',
                    'id_sofascore': None,
                    'foto_url': '/assets/imagenes/player_placeholder.png',
                    'nacionalidad': 'ESP',
                }
        except Exception as e:
            print(f"Error al cargar datos del jugador {nombre_jugador}: {e}")
            import traceback
            traceback.print_exc()
            # Datos por defecto en caso de error
            return {
                'nombre': nombre_jugador,
                'posicion': 'No disponible',
                'edad': 'No disponible',
                'id_sofascore': None,
                'foto_url': '/assets/imagenes/player_placeholder.png',
                'nacionalidad': 'ESP',
            }

    ## Callback para mostrar la información del jugador y el heatmap
    @app.callback(
        [Output('info-jugador-container', 'children'),
        Output('heatmap-container', 'children')],
        [Input('datos-jugador-store', 'data')]
    )
    def mostrar_info_jugador(datos):
        if not datos:
            return html.Div("Selecciona un jugador para ver su información."), html.Div()
        
        # Verificar si hay restricción de acceso
        if datos.get('restricted', False):
            mensaje_error = html.Div([
                html.Div(className="alert alert-danger", children=[
                    html.H4("Acceso Restringido", className="alert-heading"),
                    html.P("No tienes permiso para ver los datos de este jugador."),
                    html.Hr(),
                    html.P("Solo puedes acceder a tus propios datos físicos.", className="mb-0")
                ])
            ])
            return mensaje_error, mensaje_error
        
        # Resto del código original para mostrar datos
        if 'jugador' not in datos:
            return html.Div("No hay datos disponibles para este jugador."), html.Div()
        
        jugador = datos['jugador']
        
        # Código original para mostrar información del jugador
        info_jugador = html.Div([
            # Tu código actual para mostrar info del jugador...
            dbc.Row([
                # Imagen del jugador
                dbc.Col([
                    html.Img(
                        src=jugador.get('foto_url', '/assets/imagenes/player_placeholder.png'),
                        style={'width': '100%', 'height':'auto', 'max-height': '150px', 'border-radius': '5px', 'object-fit': 'contain'},
                        className="mb-2"
                    )
                ], width=4, style={'paddingRight': '5px'}),
            
                # Información básica del jugador
                dbc.Col([
                    html.H4(jugador.get('nombre', jugador.get('nombre_display', 'No disponible')),
                            className="mb-3", style={'fontSize': '16px'}
                    ),
                    html.P([
                        html.Span("Nacionalidad: ", className="fw-bold"),
                        html.Span(jugador.get('nacionalidad', 'ESP'))
                    ], className="mb-1", style={'fontSize': '14px'}),
                    html.P([
                        html.Span("Posición: ", className="fw-bold"),
                        html.Span(jugador.get('posicion', 'No disponible'))
                    ], className="mb-1", style={'fontSize': '14px'}),
                    html.P([
                        html.Span("Edad: ", className="fw-bold"),
                        html.Span(str(jugador.get('edad', 'No disponible')))
                    ], className="mb-1", style={'fontSize': '14px'}),
                ], width=8, style={'paddingLeft': '5px'})
            ], className="g-0")
        ], style={'overflow': 'hidden'})
    
        # Intentar obtener y mostrar el heatmap
        heatmap_container = html.Div([
            html.P("El mapa de calor no está disponible para este jugador.", className="text-muted")
        ])

        # Si tenemos ID de sofascore, generamos el heatmap
        if 'id_sofascore' in jugador and jugador['id_sofascore']:
            try:
                # Obtener el heatmap base64
                heatmap_base64 = generar_heatmap(jugador['id_sofascore'])
                
                # Verificar que heatmap_base64 tenga un valor
                if heatmap_base64:
                    heatmap_container = html.Div([
                        html.Div([
                            html.Img(
                                src=f"data:image/png;base64,{heatmap_base64}",
                                style={
                                    'max-width': '100%',
                                    'max-height': '300px',  
                                    'border-radius': '5px',
                                    'object-fit': 'contain' 
                                },
                                className="mt-2"
                            )
                        ], id="heatmap-imagen-container", style={'textAlign': 'center'})
                    ])
                else:
                    heatmap_container = html.Div([
                        html.P("No se pudo generar el mapa de calor.", className="text-muted")
                    ])
            except Exception as e:
                print(f"Error al generar heatmap: {e}")
                heatmap_container = html.Div([
                    html.H5("Mapa de Calor", className="mb-2"),
                    html.P(f"Error al generar mapa de calor: {str(e)}", className="text-danger")
                ])
        return info_jugador, heatmap_container

    # Callback para actualizar las opciones del dropdown de jugadores según el rol
    @app.callback(
        Output('jugador-fisico-dropdown', 'options'),
        Output('jugador-fisico-dropdown', 'value'),
        [Input('url', 'pathname')]
    )
    def actualizar_opciones_jugador(pathname):
        # Solo ejecutar este callback en la página de datos físicos
        if pathname != '/physical-data':
            return [], None
        
        # Cargar todos los jugadores disponibles
        conn = sqlite3.connect('data/ATM_condic_24_25.db')
        query = "SELECT DISTINCT Nombre FROM datos_fisicos ORDER BY Nombre"
        df = pd.read_sql(query, conn)
        conn.close()
        
        jugadores = df['Nombre'].tolist()

        # Si el usuario es un jugador, filtrar para mostrar solo su propio nombre
        if current_user.is_authenticated and current_user.role == 'player':
            # Intentar hacer coincidir el nombre del usuario con un jugador
            jugadores_coincidentes = []
            
            # 1. Extraer el nombre del jugador desde el ID de usuario (username)
            # Ejemplos: 'gimenez' -> 'Giménez', 'j_musso' -> 'Musso'
            username_parts = current_user.id.replace('_', ' ').split()
            possible_matches = []
            
            # Añadir el nombre completo del usuario
            if hasattr(current_user, 'name'):
                possible_matches.append(current_user.name)
            
            # Añadir partes del nombre de usuario
            for part in username_parts:
                if len(part) > 3:  # Ignorar palabras muy cortas
                    possible_matches.append(part)
            
            # 2. Buscar coincidencias entre jugadores
            for jugador in jugadores:
                jugador_lower = jugador.lower()
                
                # Comprobar si alguna de las posibles coincidencias está en el nombre del jugador
                for match in possible_matches:
                    match_lower = match.lower()
                    
                    # Intentar normalizar para eliminar acentos
                    try:
                        match_norm = normalize_name(match)
                        jugador_norm = normalize_name(jugador)
                        
                        if (match_lower in jugador_lower or 
                            jugador_lower in match_lower or
                            match_norm in jugador_norm or
                            jugador_norm in match_norm):
                            
                            jugadores_coincidentes.append(jugador)                            
                            break
                    except:
                        # Si falla la normalización, intentar con string directo
                        if match_lower in jugador_lower or jugador_lower in match_lower:
                            jugadores_coincidentes.append(jugador)
                            break
            
            # Comprobación específica para nombres comunes (mapeo manual)
            nombre_mapeo = {
                'j_musso': ['Juan Musso', 'Musso'],
                'gimenez': ['José María Giménez', 'Giménez', 'Jose M. Giménez', 'José Giménez'],
                'gallagher': ['Connor Gallagher', 'Gallagher'],
                'de_paul': ['Rodrigo De Paul', 'De Paul'],
                'koke': ['Koke', 'Jorge Resurreccion', 'Jorge Resurrección'],
                'p_barrios': ['Pablo Barrios', 'Barrios'],
                'sorloth': ['Alexander Sorloth', 'Sorloth', 'Alexander Sørloth', 'Sørloth'],
                'correa': ['Ángel Correa','Angel Correa', 'Correa'],
                'lemar': ['Thomas Lemar', 'Lemar'],
                'lino': ['Samuel Lino', 'Samu Lino', 'Lino'],
                'oblak': ['Jan Oblak', 'Oblak'],
                'Llorente': ['Marcos Llorente', 'Llorente'],
                'lenglet': ['Clement Lenglet', 'Lenglet'],
                'molina': ['Nahuel Molina', 'Molina'],
                'riquelme': ['Rodrigo Riquelme', 'Riquelme'],
                'j_alvarez': ['Julián Álvarez', 'Alvarez', 'J. Álvarez'],
                'witsel': ['Axel Witsel', 'Witsel'],
                'j_galan': ['Javi Galán', 'Galán', 'Javi Galan'],
                'g_simeone': ['Giuliano Simeone', 'Simeone'],
                'reinildo': ['Reinildo Mandava', 'Reinildo'],
                'le_normand': ['Robin Le Normand', 'Le Normand'],
                'a_niño': ['Adrián Niño', 'Adrian Niño', 'Niño'],
                'i_kostis': ['Ilias Kostis', 'Kostis'],
                'azpilicueta': ['César Azpilicueta', 'Azpilicueta', 'Cesar Azpilicueta', 'Azpilcueta']
                # Añadir más mapeos según sea necesario
            }
            
            # Si el usuario actual está en el mapeo, buscar coincidencias
            if current_user.id in nombre_mapeo:
                for posible_nombre in nombre_mapeo[current_user.id]:
                    for jugador in jugadores:
                        if posible_nombre.lower() in jugador.lower():
                            if jugador not in jugadores_coincidentes:
                                jugadores_coincidentes.append(jugador)                                
            
            # Si encontramos coincidencias, usarlas. Si no, mostrar mensaje
            if jugadores_coincidentes:
                # Eliminar duplicados
                jugadores_coincidentes = list(set(jugadores_coincidentes))
                options = [{'label': jugador, 'value': jugador} for jugador in jugadores_coincidentes]
                default_value = jugadores_coincidentes[0]  # Usar el primer jugador como valor predeterminado
                
            else:
                options = []
                default_value = None
                print(f"No se encontró coincidencia para el usuario: {current_user.id}")
        else:
            # AQUÍ ESTÁ EL CAMBIO: Para administradores, crear las opciones sin intentar recodificar
            options = []
            for jugador in jugadores:
                # Agregar el nombre directamente, sin manipulación
                options.append({'label': jugador, 'value': jugador})
            
            # Buscar a jugadores emblemáticos por orden de preferencia
            emblematicos = ['Julián Álvarez', 'Antoine Griezmann', 'Jan Oblak', 'Koke']
            default_value = None
            
            for emblematico in emblematicos:
                for jugador in jugadores:
                    # Usar .lower() para comparación insensible a mayúsculas/minúsculas
                    if emblematico.lower() in jugador.lower() or jugador.lower() in emblematico.lower():
                        default_value = jugador
                        break
                if default_value:
                    break
            
            # Si no encuentra ningún jugador emblemático, usar el primero de la lista
            if not default_value and jugadores:
                default_value = jugadores[0]
        
        return options, default_value
    
    # Callback para actualizar los datos del jugador cuando se selecciona uno nuevo
    @app.callback(
        Output('datos-jugador-store', 'data'),
        [Input('jugador-fisico-dropdown', 'value')]
    )
    def actualizar_datos_jugador(nombre_jugador):
        if not nombre_jugador:
            return {}
        
        # Verificar permisos si el usuario es un jugador
        if current_user.is_authenticated and current_user.role == 'player':
            # Usar el mismo mapeo que en el callback anterior para verificar permisos
            nombre_mapeo = {
                'j_musso': ['Juan Musso', 'Musso'],
                'gimenez': ['José María Giménez', 'Giménez', 'Jose M. Giménez', 'José Giménez'],
                'gallagher': ['Connor Gallagher', 'Gallagher'],
                'de_paul': ['Rodrigo De Paul', 'De Paul'],
                'koke': ['Koke', 'Jorge Resurreccion', 'Jorge Resurrección'],
                'p_barrios': ['Pablo Barrios', 'Barrios'],
                'sorloth': ['Alexander Sorloth', 'Sorloth', 'Alexander Sørloth', 'Sørloth'],
                'correa': ['Ángel Correa','Angel Correa', 'Correa'],
                'lemar': ['Thomas Lemar', 'Lemar'],
                'lino': ['Samuel Lino', 'Samu Lino', 'Lino'],
                'oblak': ['Jan Oblak', 'Oblak'],
                'Llorente': ['Marcos Llorente', 'Llorente'],
                'lenglet': ['Clement Lenglet', 'Lenglet'],
                'molina': ['Nahuel Molina', 'Molina'],
                'riquelme': ['Rodrigo Riquelme', 'Riquelme'],
                'j_alvarez': ['Julián Álvarez', 'Alvarez', 'J. Álvarez'],
                'witsel': ['Axel Witsel', 'Witsel'],
                'j_galan': ['Javi Galán', 'Galán', 'Javi Galan'],
                'g_simeone': ['Giuliano Simeone', 'Simeone'],
                'reinildo': ['Reinildo Mandava', 'Reinildo'],
                'le_normand': ['Robin Le Normand', 'Le Normand'],
                'a_niño': ['Adrián Niño', 'Adrian Niño', 'Niño'],
                'i_kostis': ['Ilias Kostis', 'Kostis'],
                'azpilicueta': ['César Azpilicueta', 'Azpilicueta', 'Cesar Azpilicueta', 'Azpilcueta']
            }
            
            permitido = False
                        
            # Verificar usando el mapeo
            if current_user.id in nombre_mapeo:
                for posible_nombre in nombre_mapeo[current_user.id]:
                    # Normalizar ambos para comparación consistente
                    posible_nombre_norm = normalize_name(posible_nombre)
                    jugador_nombre_norm = normalize_name(nombre_jugador)
                    
                    # Verificar si hay coincidencia parcial en cualquier dirección
                    if (posible_nombre_norm in jugador_nombre_norm or 
                        jugador_nombre_norm in posible_nombre_norm):
                        permitido = True
                        break
            
            # Si no está permitido, devolver error
            if not permitido:
                # Intento adicional para caracteres especiales nórdicos
                user_id_normalized = current_user.id.lower()
                jugador_normalizado = normalize_name(nombre_jugador).replace(' ', '')
                
                # Verificación especial para Sørloth
                if user_id_normalized == 'sorloth' and ('sorloth' in jugador_normalizado or 'srloth' in jugador_normalizado):
                    permitido = True
                                    
                if not permitido:
                    print(f"Acceso denegado: {current_user.id} intentó acceder a {nombre_jugador}")
                    return {
                        'error': 'No tienes permiso para ver estos datos',
                        'restricted': True
                    }
        
        # Si tiene permisos, cargar datos normalmente
        datos_jugador = cargar_datos_jugador(nombre_jugador)
        datos_fisicos = cargar_datos_fisicos(nombre_jugador)
        
        return {
            'jugador': datos_jugador,
            'condicionales': datos_fisicos.to_dict('records') if not datos_fisicos.empty and not datos_fisicos.empty else []
        }
    
    # Callback para el gráfico de barras
    @app.callback(
        Output('grafico-barras-fisico', 'figure'),
        [Input('datos-jugador-store', 'data'),
         Input('metricas-barras-dropdown', 'value')]
    )
    def actualizar_grafico_barras(datos, metricas_seleccionadas):
        # Verificar si hay restricción de acceso primero
        if datos and datos.get('restricted', False):
            fig = go.Figure()
            fig.add_annotation(
                text="Acceso restringido",
                showarrow=False,
                font=dict(size=20)
            )
            return fig
        
        # Crear figura vacía por defecto
        fig = go.Figure()
        
        # Verificar si hay datos
        if not datos or 'condicionales' not in datos or not metricas_seleccionadas:
            fig.add_annotation(
                text="Seleccione un jugador y métricas para visualizar",
                showarrow=False,
                font=dict(size=14)
            )
            return fig
        
        # Convertir a DataFrame
        df = pd.DataFrame(datos['condicionales'])
        
        # Verificar si hay datos en el DataFrame
        if df.empty:
            fig.add_annotation(
                text="No hay datos disponibles para este jugador",
                showarrow=False,
                font=dict(size=14)
            )
            return fig
        
        # Verificar que las métricas seleccionadas estén en el DataFrame
        metricas_disponibles = [m for m in metricas_seleccionadas if m in df.columns]
        if not metricas_disponibles:
            fig.add_annotation(
                text="Las métricas seleccionadas no están disponibles",
                showarrow=False,
                font=dict(size=14)
            )
            return fig
        
        # Limitar a 3 métricas para no saturar el gráfico
        if len(metricas_disponibles) > 3:
            metricas_disponibles = metricas_disponibles[:3]
        
        # Obtener nombre del jugador
        nombre_jugador = datos['jugador'].get('nombre', 'Jugador')
        
        # Crear gráfico de barras
        for i, metrica in enumerate(metricas_disponibles):
            fig.add_trace(go.Bar(
                x=df['Jornada'],
                y=df[metrica],
                name=metrica.replace('_', ' ').title(),
                marker_color=px.colors.qualitative.G10[i % len(px.colors.qualitative.G10)]
            ))
        
        # Actualizar layout
        fig.update_layout(
            xaxis_title="Jornada",
            yaxis_title="Valor",
            template="plotly_white",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            margin=dict(l=40, r=40, t=60, b=40)
        )
        
        return fig
    
    # Callback para el radar chart
    @app.callback(
        Output('grafico-radar-fisico', 'figure'),
        [Input('datos-jugador-store', 'data'),
         Input('metricas-radar-checklist', 'value')]
    )
    def actualizar_grafico_radar(datos, metricas_seleccionadas):
        # Verificar si hay restricción de acceso primero
        if datos and datos.get('restricted', False):
            fig = go.Figure()
            fig.add_annotation(
                text="Acceso restringido",
                showarrow=False,
                font=dict(size=20)
            )
            return fig
        
        # Crear figura vacía por defecto
        fig = go.Figure()
        
        # Verificar si hay datos
        if not datos or 'condicionales' not in datos or not metricas_seleccionadas:
            fig.add_annotation(
                text="Seleccione un jugador y métricas para visualizar",
                showarrow=False,
                font=dict(size=14)
            )
            return fig
        
        # Convertir a DataFrame
        df = pd.DataFrame(datos['condicionales'])
        
        # Verificar si hay datos en el DataFrame
        if df.empty:
            fig.add_annotation(
                text="No hay datos disponibles para este jugador",
                showarrow=False,
                font=dict(size=14)
            )
            return fig
        
        # Verificar que las métricas seleccionadas estén en el DataFrame
        metricas_disponibles = [m for m in metricas_seleccionadas if m in df.columns]
        if not metricas_disponibles:
            fig.add_annotation(
                text="Las métricas seleccionadas no están disponibles",
                showarrow=False,
                font=dict(size=14)
            )
            return fig
        
        # Limitar a 6 métricas para el radar
        if len(metricas_disponibles) > 6:
            metricas_disponibles = metricas_disponibles[:6]
        
        # Obtener nombre del jugador
        nombre_jugador = datos['jugador'].get('nombre', 'Jugador')
        
        try:
            # Calcular promedios
            df_promedio = df[metricas_disponibles].mean().reset_index()
            df_promedio.columns = ['metrica', 'valor']
            
            # Normalizar datos para el radar
            df_otras_posiciones = pd.DataFrame()
            for metrica in metricas_disponibles:
                df_otras_posiciones[metrica] = [df[metrica].mean() * 0.8]  
            
            # Normalizar valores
            df_normalizado = pd.DataFrame()
            for metrica in metricas_disponibles:
                max_val = df[metrica].max() * 1.2  
                min_val = 0
                if max_val > min_val:
                    df_normalizado.loc[0, metrica] = df[metrica].mean() / max_val
                    df_normalizado.loc[1, metrica] = df_otras_posiciones[metrica].iloc[0] / max_val
                else:
                    df_normalizado.loc[0, metrica] = 0
                    df_normalizado.loc[1, metrica] = 0
            
            # Crear figura de radar
            categories = [m.replace('_', ' ').title() for m in metricas_disponibles]
            
            # Crear radr chart
            fig.add_trace(go.Scatterpolar(
                r=df_normalizado.iloc[0].values.tolist(),
                theta=categories,
                fill='toself',
                name=nombre_jugador,
                line_color=CONFIG["team_colors"]["primary"]
            ))
            
            fig.add_trace(go.Scatterpolar(
                r=df_normalizado.iloc[1].values.tolist(),
                theta=categories,
                fill='toself',
                name='Promedio por posición',
                line_color='rgba(216, 30, 5, 0.7)'
            ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 1]
                    )
                ),
                template="plotly_white",
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                margin=dict(l=40, r=40, t=60, b=40)
            )
        except Exception as e:
            print(f"Error en radar chart: {e}")
            fig.add_annotation(
                text=f"Error al generar radar chart: {str(e)}",
                showarrow=False,
                font=dict(size=14)
            )
        
        return fig
    
    # Callback para el scatter plot
    @app.callback(
        Output('grafico-scatter-fisico', 'figure'),
        [Input('datos-jugador-store', 'data'),
         Input('scatter-x-dropdown', 'value'),
         Input('scatter-y-dropdown', 'value'),
         Input('scatter-size-dropdown', 'value')]
    )
    def actualizar_grafico_scatter(datos, metrica_x, metrica_y, metrica_size):
        # Verificar si hay restricción de acceso primero
        if datos and datos.get('restricted', False):
            fig = go.Figure()
            fig.add_annotation(
                text="Acceso restringido",
                showarrow=False,
                font=dict(size=20)
            )
            return fig
        
        # Crear figura vacía por defecto
        fig = go.Figure()
        
        # Verificar si hay datos
        if not datos or 'condicionales' not in datos or not metrica_x or not metrica_y or not metrica_size:
            fig.add_annotation(
                text="Seleccione un jugador y métricas para visualizar",
                showarrow=False,
                font=dict(size=14)
            )
            return fig
        
        # Convertir a DataFrame
        df = pd.DataFrame(datos['condicionales'])
        
        # Verificar si hay datos en el DataFrame
        if df.empty:
            fig.add_annotation(
                text="No hay datos disponibles para este jugador",
                showarrow=False,
                font=dict(size=14)
            )
            return fig
        
        # Verificar que las métricas seleccionadas estén en el DataFrame
        if metrica_x not in df.columns or metrica_y not in df.columns or metrica_size not in df.columns:
            fig.add_annotation(
                text="Alguna de las métricas seleccionadas no está disponible",
                showarrow=False,
                font=dict(size=14)
            )
            return fig
        
        # Obtener nombre del jugador
        nombre_jugador = datos['jugador'].get('nombre', 'Jugador')
        
        try:
            # Crear scatter plot
            fig = px.scatter(
                df,
                x=metrica_x,
                y=metrica_y,
                size=metrica_size,
                color="Jornada",
                hover_name="Jornada",
                size_max=30,
                color_continuous_scale=px.colors.sequential.Blues
            )
            
            # Modificar layout
            fig.update_layout(
                xaxis_title=metrica_x.replace('_', ' ').title(),
                yaxis_title=metrica_y.replace('_', ' ').title(),
                coloraxis_colorbar_title="Jornada",
                template="plotly_white",
                margin=dict(l=40, r=40, t=60, b=40)
            )
            
            # Añadir líneas de tendencia (manejo de error mejorado)
            try:
                # Verificar si hay suficientes puntos para ajustar
                if len(df) > 2 and len(df[metrica_x].unique()) > 1:
                    # Calcular línea de tendencia
                    z = np.polyfit(df[metrica_x], df[metrica_y], 1)
                    p = np.poly1d(z)
                    x_range = np.linspace(df[metrica_x].min(), df[metrica_x].max(), 100)
                    
                    fig.add_trace(
                        go.Scatter(
                            x=x_range,
                            y=p(x_range),
                            mode='lines',
                            line=dict(color='rgba(0, 0, 0, 0.5)', dash='dash'),
                            showlegend=False
                        )
                    )
            except Exception as e:
                print(f"Error en línea de tendencia: {e}")
                # No añadir línea de tendencia si hay error
        except Exception as e:
            print(f"Error en scatter plot: {e}")
            fig.add_annotation(
                text=f"Error al generar scatter plot: {str(e)}",
                showarrow=False,
                font=dict(size=14)
            )
        
        return fig
    
    @app.callback(
        [Output('datos-fisicos-table', 'columns'),
        Output('datos-fisicos-table', 'data'),
        Output('datos-fisicos-table', 'style_data_conditional')],
        [Input('datos-jugador-store', 'data'),
        Input('metricas-table-dropdown', 'value')]
    )
    def actualizar_tabla_datos(datos, metricas_seleccionadas):
        # Configuración de estilos base que siempre se aplican
        style_data_conditional = [
            # Filas alternadas con color de fondo diferente
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': CONFIG['team_colors']['background_secondary']
            },
            # Resaltar la columna de Jornada con texto blanco
            {
                'if': {'column_id': 'Jornada'},
                'fontWeight': 'bold',
                'backgroundColor': '#0A1A2A',
                'color': '#FFFFFF'  # Texto blanco para la columna de jornadas
            }
        ]
        
        # Verificar si hay restricción de acceso
        if datos and datos.get('restricted', False):
            columns = [{'name': 'Mensaje', 'id': 'mensaje'}]
            data = [{'mensaje': 'Acceso restringido - No tienes permiso para ver estos datos'}]
            return columns, data, style_data_conditional
        
        # Verificar si tenemos datos y métricas seleccionadas
        if not datos or 'condicionales' not in datos or not metricas_seleccionadas:
            columns = [{'name': 'Mensaje', 'id': 'mensaje'}]
            data = [{'mensaje': 'Seleccione un jugador y métricas para visualizar'}]
            return columns, data, style_data_conditional
        
        # Convertir a DataFrame
        df = pd.DataFrame(datos['condicionales'])
        
        # Definir las columnas base (siempre mostrar Jornada primero)
        columns = [{'name': 'Jornada', 'id': 'Jornada'}]
        
        # Añadir columnas para cada métrica seleccionada
        for metrica in metricas_seleccionadas:
            nombre_metrica = metrica.replace('_', ' ').title()
            columns.append({'name': nombre_metrica, 'id': metrica})
        
        # Preparar los datos
        data = []
        for i, row in df.iterrows():
            data_row = {'Jornada': str(row['Jornada'])}
            for metrica in metricas_seleccionadas:
                if metrica in row:
                    # Formatear valores numéricos
                    if pd.api.types.is_numeric_dtype(df[metrica]):
                        data_row[metrica] = f"{row[metrica]:.1f}" if isinstance(row[metrica], float) else str(row[metrica])
                    else:
                        data_row[metrica] = str(row[metrica])
            data.append(data_row)
        
        # Diccionario para almacenar referencias a los valores máximos y mínimos por métrica
        max_min_values = {}
        
        # Aplicar estilos para destacar valores máximos y mínimos
        for metrica in metricas_seleccionadas:
            if metrica in df.columns and pd.api.types.is_numeric_dtype(df[metrica]):
                try:
                    # Encontrar valores máximos y mínimos
                    serie_metrica = df[metrica]
                    serie_sin_na = serie_metrica.dropna()
                    
                    if not serie_sin_na.empty:
                        max_value = serie_sin_na.max()
                        min_value = serie_sin_na.min()
                        
                        # Guardamos estos valores para referenciarlos después
                        max_min_values[metrica] = {'max': max_value, 'min': min_value}
                        
                        # Estilo para valores máximos
                        style_data_conditional.append({
                            'if': {
                                'column_id': metrica,
                                'filter_query': f'{{{metrica}}} = "{max_value:.1f}"' if isinstance(max_value, float) else f'{{{metrica}}} = "{max_value}"'
                            },
                            'backgroundColor': 'rgba(76, 175, 80, 0.8)',
                            'fontWeight': 'bold',
                            'color': 'white'
                        })
                        
                        # Estilo para valores mínimos
                        if min_value != max_value:
                            style_data_conditional.append({
                                'if': {
                                    'column_id': metrica,
                                    'filter_query': f'{{{metrica}}} = "{min_value:.1f}"' if isinstance(min_value, float) else f'{{{metrica}}} = "{min_value}"'
                                },
                                'backgroundColor': 'rgba(244, 67, 54, 0.8)',
                                'fontWeight': 'bold',
                                'color': 'white'
                            })
                        
                        # Calcular rangos para valores intermedios
                        rango = max_value - min_value
                        if rango > 0:
                            # Valores altos (75% del rango o más)
                            umbral_alto = min_value + (rango * 0.75)
                            valor_alto_formateado = f"{umbral_alto:.1f}" if isinstance(umbral_alto, float) else str(umbral_alto)
                            max_formateado = f"{max_value:.1f}" if isinstance(max_value, float) else str(max_value)
                            
                            style_data_conditional.append({
                                'if': {
                                    'column_id': metrica,
                                    'filter_query': f'{{{metrica}}} >= "{valor_alto_formateado}" && {{{metrica}}} < "{max_formateado}"'
                                },
                                'backgroundColor': 'rgba(76, 175, 80, 0.4)',
                                'color': 'white'
                            })
                            
                            # Valores bajos (25% del rango o menos)
                            umbral_bajo = min_value + (rango * 0.25)
                            valor_bajo_formateado = f"{umbral_bajo:.1f}" if isinstance(umbral_bajo, float) else str(umbral_bajo)
                            min_formateado = f"{min_value:.1f}" if isinstance(min_value, float) else str(min_value)
                            
                            style_data_conditional.append({
                                'if': {
                                    'column_id': metrica,
                                    'filter_query': f'{{{metrica}}} <= "{valor_bajo_formateado}" && {{{metrica}}} > "{min_formateado}"'
                                },
                                'backgroundColor': 'rgba(244, 67, 54, 0.4)',
                                'color': 'white'
                            })
                except Exception as e:
                    print(f"Error al procesar estilos para métrica {metrica}: {e}")
                    continue

        return columns, data, style_data_conditional
    
    # Callback para exportar PDF físico
    @app.callback(
        [Output('descargar-pdf-physical', 'data'),
        Output('pdf-status-physical', 'children')],
        [Input('exportar-pdf-btn-physical', 'n_clicks')],
        [State('datos-jugador-store', 'data'),
        State('grafico-barras-fisico', 'figure'),
        State('grafico-radar-fisico', 'figure'),
        State('grafico-scatter-fisico', 'figure')],
        prevent_initial_call=True
    )
    def exportar_pdf_fisico_datos(n_clicks, datos, figura_barras, figura_radar, figura_scatter):
        if not n_clicks or not datos:
            return None, ""
        
        try:
            jugador = datos['jugador']
            nombre_jugador = jugador.get('nombre', 'Jugador')
            
            # Usar directamente las figuras actuales que se muestran en la interfaz
            graficos = [figura_barras, figura_radar, figura_scatter]
            
            # Obtener ruta de la foto si existe
            foto_path = None
            if 'nombre' in jugador:
                foto_path = f"assets/fotos/{jugador['nombre'].lower().replace(' ', '_')}.png"
                if not os.path.exists(foto_path):
                    foto_path = None
            
            # Exportar PDF con lo que se ve actualmente
            pdf_bytes = exportar_pdf_fisico(
                n_clicks, 
                nombre_jugador, 
                foto_path, 
                graficos, 
                None,  # No hay heatmap
                None,  # No hay imagen de tabla
                [1, 10]  # Rango genérico
            )
            
            if pdf_bytes:
                return pdf_bytes, html.Span("¡PDF generado!", className="ms-2 fw-bold", style={"color": "#4CAF50"})
            else:
                return None, html.Span("Error generando PDF", className="ms-2 fw-bold", style={"color": "#FF0000"})
        
        except Exception as e:
            print(f"Error al exportar PDF: {str(e)}")
            return None, html.Span(f"Error: {str(e)}", className="ms-2 fw-bold", style={"color": "#FF0000"})