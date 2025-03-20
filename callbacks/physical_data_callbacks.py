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


def register_physical_data_callbacks(app):
    """
    Registra los callbacks para la página de datos físicos/condicionales
    """
    
    # Función para normalizar nombres (quitar acentos, minúsculas)
    def normalize_name(name):
        # Normalizar, convertir a minúsculas y quitar espacios extras
        if not name:
            return ""
        return ' '.join(unicodedata.normalize('NFKD', str(name).lower())
                        .encode('ASCII', 'ignore')
                        .decode('ASCII')
                        .split())
    
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
                        # Si es así, dividir la primera columna
                        primera_col = maestro_df.columns[0]
                        # Crear un nuevo DataFrame con las columnas divididas
                        nuevas_cols = primera_col.split(';')
                        # Dividir los valores
                        valores_split = [row.split(';') for row in maestro_df[primera_col]]
                        # Crear nuevo DataFrame
                        maestro_df = pd.DataFrame(valores_split, columns=nuevas_cols)
                        print("Archivo maestro procesado dividiendo la columna principal")
                    else:
                        print("Archivo maestro cargado con separador tab")
                except Exception as e1:
                    try:
                        # Intentar con separador punto y coma
                        maestro_df = pd.read_csv('data/jugadores_master.csv', sep=';', encoding='utf-8')
                        print("Archivo maestro cargado con separador ;")
                    except Exception as e2:
                        try:
                            # Intentar con separador coma
                            maestro_df = pd.read_csv('data/jugadores_master.csv', encoding='utf-8')
                            print("Archivo maestro cargado con separador ,")
                        except Exception as e3:
                            print(f"No se pudo cargar el archivo con ningún separador conocido: {e1}, {e2}, {e3}")
                            # Crear un diccionario específico para jugadores clave
                            jugadores_info = {
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
                            # Puedes añadir más jugadores según necesites
                        }
                        # Convertir a DataFrame
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
                # Crear un diccionario específico para jugadores clave
                jugadores_info = {
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
                # Convertir a DataFrame
                return pd.DataFrame.from_dict(jugadores_info, orient='index').reset_index().rename(columns={'index': 'nombre'})
        except Exception as e:
            print(f"Error al cargar archivo maestro: {e}")
            import traceback
            traceback.print_exc()
            # Fallback: retornar datos fijos para jugadores clave
            jugadores_info = {
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
            print(f"Buscando datos para jugador: {nombre_jugador}")
        
            # Verificar si hay caracteres mal codificados en el nombre
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
                        print(f"Nombre normalizado para búsqueda: {nombre_norm}")
                    
                        # Buscar coincidencia en el archivo maestro
                        for idx, row in maestro_df.iterrows():
                            if 'short_name' in maestro_df.columns:
                                row_short_name_norm = normalize_name(str(row['short_name']))
                            
                                # Si hay coincidencia por nombre
                                if row_short_name_norm == nombre_norm or normalize_name(str(row['nombre_completo'])).find(nombre_norm) >= 0:
                                    print(f"Coincidencia encontrada: {row['nombre_completo']}")
                                
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
            
                print(f"Datos finales del jugador: {jugador}")

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
                    print(f"Usando información de respaldo para {nombre_jugador_corregido}")
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

    # Callback para actualizar los datos del jugador cuando se selecciona uno nuevo
    @app.callback(
        Output('datos-jugador-store', 'data'),
        [Input('jugador-fisico-dropdown', 'value')]
    )
    def actualizar_datos_jugador(nombre_jugador):
        if not nombre_jugador:
            return {}
        
        # Cargar datos del jugador
        datos_jugador = cargar_datos_jugador(nombre_jugador)
        
        # Cargar datos físicos
        datos_fisicos = cargar_datos_fisicos(nombre_jugador)
        
        # Convertir a diccionario para almacenar
        return {
            'jugador': datos_jugador,
            'condicionales': datos_fisicos.to_dict('records')
        }
    
    # Callback para mostrar la información del jugador y el heatmap
    @app.callback(
        [Output('info-jugador-container', 'children'),
         Output('heatmap-container', 'children')],
        [Input('datos-jugador-store', 'data')]
    )
    def mostrar_info_jugador(datos):
        if not datos or 'jugador' not in datos:
            return html.Div("Selecciona un jugador para ver su información."), html.Div()
    
        jugador = datos['jugador']
        print(f"Info del jugador: {jugador}")
    
        if 'id_sofascore' in jugador:
            print(f"ID Sofascore: {jugador.get('id_sofascore')}")
    
        # Crear componente de información del jugador (simplificado)
        info_jugador = html.Div([
            dbc.Row([
                # Imagen del jugador
                dbc.Col([
                    html.Img(
                        src=jugador.get('foto_url', '/assets/imagenes/player_placeholder.png'),
                        style={'max-width': '100%', 'max-height': '180px', 'border-radius': '5px'},
                        className="mb-2"
                    )
                ], width=4),
            
                # Información básica del jugador
                dbc.Col([
                    html.H4(jugador.get('nombre', jugador.get('nombre_display', 'No disponible')), className="mb-3"),
                    html.P([
                        html.Span("Nacionalidad: ", className="fw-bold"),
                        html.Span(jugador.get('nacionalidad', 'ESP'))
                    ], className="mb-2"),
                    html.P([
                        html.Span("Posición: ", className="fw-bold"),
                        html.Span(jugador.get('posicion', 'No disponible'))
                    ], className="mb-2"),
                    html.P([
                        html.Span("Edad: ", className="fw-bold"),
                        html.Span(str(jugador.get('edad', 'No disponible')))
                    ], className="mb-2"),
                ], width=8)
            ])
        ])
    
        # Intentar obtener y mostrar el heatmap
        heatmap_container = html.Div([
            html.H5("Mapa de Calor", className="mb-2"),
            html.P("El mapa de calor no está disponible para este jugador.", className="text-muted")
        ])
    
        # Si tenemos ID de sofascore, generamos el heatmap
        if 'id_sofascore' in jugador and jugador['id_sofascore']:
            try:
                from utils.heatmap_generator import generar_heatmap
                heatmap_base64 = generar_heatmap(jugador['id_sofascore'])
                heatmap_container = html.Div([
                    html.H5("Mapa de Calor (Posicionamiento)", className="mb-2"),
                   html.Div([
                        html.Img(
                            src=f"data:image/png;base64,{heatmap_base64}",
                            style={'max-width': '100%', 'border-radius': '5px'},
                            className="mt-2"
                        )
                    ], id="heatmap-imagen-container")
                ])
            except Exception as e:
                print(f"Error al generar heatmap: {e}")
                heatmap_container = html.Div([
                    html.H5("Mapa de Calor", className="mb-2"),
                    html.P(f"Error al generar mapa de calor: {str(e)}", className="text-danger")
                ])
    
        return info_jugador, heatmap_container
    
    # Callback para el gráfico de barras
    @app.callback(
        Output('grafico-barras-fisico', 'figure'),
        [Input('datos-jugador-store', 'data'),
         Input('metricas-barras-dropdown', 'value')]
    )
    def actualizar_grafico_barras(datos, metricas_seleccionadas):
        if not datos or 'condicionales' not in datos or not metricas_seleccionadas:
            return go.Figure()
        
        # Convertir a DataFrame
        df = pd.DataFrame(datos['condicionales'])
        nombre_jugador = datos['jugador']['nombre']
        
        # Limitar a 3 métricas
        if len(metricas_seleccionadas) > 3:
            metricas_seleccionadas = metricas_seleccionadas[:3]
        
        # Crear figura
        fig = go.Figure()
        
        for metrica in metricas_seleccionadas:
            fig.add_trace(go.Bar(
                x=df['Jornada'],
                y=df[metrica],
                name=metrica.replace('_', ' ').title(),
                marker_color=px.colors.qualitative.G10[metricas_seleccionadas.index(metrica) % len(px.colors.qualitative.G10)]
            ))
        
        # Actualizar layout
        fig.update_layout(
            title=f"Evolución de métricas por jornada - {nombre_jugador}",
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
        if not datos or 'condicionales' not in datos or not metricas_seleccionadas:
            return go.Figure()
        
        # Limitar a 8 métricas
        if len(metricas_seleccionadas) > 8:
            metricas_seleccionadas = metricas_seleccionadas[:8]
        
        # Convertir a DataFrame
        df = pd.DataFrame(datos['condicionales'])
        nombre_jugador = datos['jugador']['nombre']
        
        # Calcular promedios
        df_promedio = df[metricas_seleccionadas].mean().reset_index()
        df_promedio.columns = ['metrica', 'valor']
        
        # Normalizar datos para el radar
        df_otras_posiciones = pd.DataFrame()
        for metrica in metricas_seleccionadas:
            # Simular datos para comparación (esto se podría reemplazar con datos reales)
            df_otras_posiciones[metrica] = [df[metrica].mean() * 0.8]  # 80% del promedio como ejemplo
        
        # Normalizar valores
        df_normalizado = pd.DataFrame()
        for metrica in metricas_seleccionadas:
            max_val = df[metrica].max() * 1.2  # Usar 120% del max para dar margen
            min_val = 0
            if max_val > min_val:
                df_normalizado.loc[0, metrica] = df[metrica].mean() / max_val
                df_normalizado.loc[1, metrica] = df_otras_posiciones[metrica].iloc[0] / max_val
            else:
                df_normalizado.loc[0, metrica] = 0
                df_normalizado.loc[1, metrica] = 0
        
        # Crear figura de radar
        categories = [m.replace('_', ' ').title() for m in metricas_seleccionadas]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=df_normalizado.iloc[0].values.tolist(),
            theta=categories,
            fill='toself',
            name=nombre_jugador,
            line_color=CONFIG["team_colors"]["secondary"]
        ))
        
        fig.add_trace(go.Scatterpolar(
            r=df_normalizado.iloc[1].values.tolist(),
            theta=categories,
            fill='toself',
            name='Promedio por posición',
            line_color='rgba(0, 0, 255, 0.7)'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )
            ),
            title=f"Perfil condicional - {nombre_jugador}",
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
    
    # Callback para el scatter plot
    @app.callback(
        Output('grafico-scatter-fisico', 'figure'),
        [Input('datos-jugador-store', 'data'),
         Input('scatter-x-dropdown', 'value'),
         Input('scatter-y-dropdown', 'value'),
         Input('scatter-size-dropdown', 'value')]
    )
    def actualizar_grafico_scatter(datos, metrica_x, metrica_y, metrica_size):
        if not datos or 'condicionales' not in datos or not metrica_x or not metrica_y or not metrica_size:
            return go.Figure()
        
        # Convertir a DataFrame
        df = pd.DataFrame(datos['condicionales'])
        nombre_jugador = datos['jugador']['nombre']
        
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
            title=f"Relación entre {metrica_x.replace('_', ' ').title()} y {metrica_y.replace('_', ' ').title()}",
            xaxis_title=metrica_x.replace('_', ' ').title(),
            yaxis_title=metrica_y.replace('_', ' ').title(),
            coloraxis_colorbar_title="Jornada",
            template="plotly_white",
            margin=dict(l=40, r=40, t=60, b=40)
        )
        
        # Añadir líneas de tendencia
        try:
            # Calcular línea de tendencia
            z = np.polyfit(df[metrica_x], df[metrica_y], 1)
            p = np.poly1d(z)
            x_range = np.linspace(df[metrica_x].min(), df[metrica_x].max(), 100)
            
            fig.add_trace(
                go.Scatter(
                    x=x_range,
                    y=p(x_range),
                    mode='lines',
                    name='Tendencia',
                    line=dict(color='rgba(0, 0, 0, 0.5)', dash='dash')
                )
            )
        except Exception as e:
            # Si hay error en la línea de tendencia, seguimos sin ella
            print(f"Error en línea de tendencia: {e}")
            pass
        
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
            # Resaltar la columna de Jornada
            {
                'if': {'column_id': 'Jornada'},
                'fontWeight': 'bold',
                'backgroundColor': f'rgba({int(CONFIG["team_colors"]["primary"][1:3], 16)}, {int(CONFIG["team_colors"]["primary"][3:5], 16)}, {int(CONFIG["team_colors"]["primary"][5:7], 16)}, 0.1)'
            }
        ]
        
        # Verificar si tenemos datos y métricas seleccionadas
        if not datos or 'condicionales' not in datos or not metricas_seleccionadas:
            return [], [], style_data_conditional  # Devolver estilos base incluso sin datos
        
        # Convertir a DataFrame
        df = pd.DataFrame(datos['condicionales'])
        
        # Definir las columnas base (siempre mostrar Jornada primero)
        columns = [{'name': 'Jornada', 'id': 'Jornada'}]
        
        # Añadir columnas para cada métrica seleccionada
        for metrica in metricas_seleccionadas:
            # Obtener nombre legible para la métrica
            nombre_metrica = metrica.replace('_', ' ').title()
            columns.append({'name': nombre_metrica, 'id': metrica})
        
        # Filtrar los datos para mostrar solo las columnas seleccionadas
        data = []
        for i, row in df.iterrows():
            data_row = {'Jornada': row['Jornada']}
            for metrica in metricas_seleccionadas:
                if metrica in row:
                    # Formatear valores numéricos
                    if pd.api.types.is_numeric_dtype(df[metrica]):
                        data_row[metrica] = f"{row[metrica]:.1f}" if isinstance(row[metrica], float) else str(row[metrica])
                    else:
                        data_row[metrica] = str(row[metrica])
            data.append(data_row)
        
        # Enfoque más simple: usar directamente los índices para los valores máximos y mínimos
        for metrica in metricas_seleccionadas:
            if metrica in df.columns and pd.api.types.is_numeric_dtype(df[metrica]):
                try:
                    # Encontrar índices de valores máximos y mínimos
                    serie_metrica = df[metrica]
                    serie_sin_na = serie_metrica.dropna()
                    if not serie_sin_na.empty:
                        idx_max = serie_sin_na.idxmax()
                        idx_min = serie_sin_na.idxmin()
                        
                        # Convertir a índices de lista si es necesario
                        if isinstance(idx_max, (int, np.integer)):
                            idx_max_list = df.index.get_loc(idx_max)
                        else:
                            idx_max_list = df.index.tolist().index(idx_max)
                            
                        if isinstance(idx_min, (int, np.integer)):
                            idx_min_list = df.index.get_loc(idx_min)
                        else:
                            idx_min_list = df.index.tolist().index(idx_min)
                        
                        # Añadir estilo para valor máximo
                        style_data_conditional.append({
                            'if': {'row_index': idx_max_list, 'column_id': metrica},
                            'backgroundColor': 'rgba(76, 175, 80, 0.7)',  # Verde
                            'fontWeight': 'bold',
                            'color': 'white'
                        })
                        
                        # Añadir estilo para valor mínimo (solo si es diferente del máximo)
                        if idx_min != idx_max:
                            style_data_conditional.append({
                                'if': {'row_index': idx_min_list, 'column_id': metrica},
                                'backgroundColor': 'rgba(244, 67, 54, 0.7)',  # Rojo
                                'fontWeight': 'bold',
                                'color': 'white'
                            })
                            
                except Exception as e:
                    print(f"Error al procesar estilos para métrica {metrica}: {e}")
                    continue
        
        return columns, data, style_data_conditional
    
    # Callback para exportar PDF incluyendo la DataTable
    @app.callback(
        [Output('descargar-pdf-physical', 'data'),
        Output('pdf-status-physical', 'children')],
        [Input('exportar-pdf-btn-physical', 'n_clicks')],
        [State('url', 'pathname'),
        State('datos-jugador-store', 'data'),
        State('metricas-barras-dropdown', 'value'),
        State('metricas-radar-checklist', 'value'),
        State('scatter-x-dropdown', 'value'),
        State('scatter-y-dropdown', 'value'),
        State('scatter-size-dropdown', 'value'),
        State('metricas-table-dropdown', 'value')],
        prevent_initial_call=True
    )
    def exportar_pdf_physical_data(n_clicks, pathname, datos, metricas_barras, metricas_radar, 
                                scatter_x, scatter_y, scatter_size, metricas_table):
        ctx = dash.callback_context
        print(f"Physical PDF callback triggered: {n_clicks}, pathname: {pathname}")

        if not ctx.triggered or not n_clicks or pathname != '/physical-data':
            return None, ""

        if not datos:
            return None, ""

        # Información del jugador
        jugador = datos['jugador']
        nombre_jugador = jugador.get('nombre', 'Jugador')
        print(f"Generando PDF para {nombre_jugador}") 

        # Generar gráficos usando las métricas seleccionadas
        grafico_barras = actualizar_grafico_barras(datos, metricas_barras)
        grafico_radar = actualizar_grafico_radar(datos, metricas_radar)
        grafico_scatter = actualizar_grafico_scatter(
            datos, 
            scatter_x, 
            scatter_y, 
            scatter_size
        )

        # Obtener datos actuales de la tabla - CORREGIR ESTA LÍNEA
        tabla_columnas, tabla_datos, _ = actualizar_tabla_datos(datos, metricas_table)  # Ahora desempaquetamos 3 valores, ignorando el tercero (_)

        # Crear una figura de tabla para el PDF
        # Extraer nombres de columnas y datos
        encabezados = [col['name'] for col in tabla_columnas]
        
        tabla_df = pd.DataFrame(tabla_datos)
        
        # Solo incluir hasta 10 filas para que quepa en el PDF
        if len(tabla_df) > 10:
            tabla_df = tabla_df.head(10)
        
        # Crear figura de tabla
        fig_tabla = go.Figure(data=[go.Table(
            header=dict(
                values=encabezados,
                fill_color=CONFIG['team_colors']['primary'],
                align='center',
                font=dict(color=CONFIG['team_colors']['accent'], size=12)
            ),
            cells=dict(
                values=[tabla_df[col['id']] if col['id'] in tabla_df else [] for col in tabla_columnas],
                fill_color=CONFIG['team_colors']['background'],
                align='center'
            )
        )])
        
        fig_tabla.update_layout(
            title=f"Datos por jornada - {nombre_jugador}"
        )

        # Preparar gráficos para exportación
        graficos = [grafico_barras, grafico_radar, grafico_scatter, fig_tabla]

        # Exportar PDF
        pdf_bytes = exportar_pdf(
            n_clicks, 
            graficos, 
            f"Atlético de Madrid - Informe Físico de {nombre_jugador}", 
            "Métricas Físicas", 
            [1, 10],  # Rango de jornadas 
            [nombre_jugador]
        )

        return pdf_bytes, html.Span("¡PDF de Datos Físicos generado!", 
                        className="ms-2 fw-bold", 
                        style={"color": "#4CAF50"})