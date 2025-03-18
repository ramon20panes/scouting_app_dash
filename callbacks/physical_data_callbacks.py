import pandas as pd
import numpy as np
import sqlite3
import plotly.graph_objects as go
import plotly.express as px
from dash.dependencies import Input, Output, State
from dash import html, dcc
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

def register_physical_data_callbacks(app):
    """
    Registra los callbacks para la página de datos físicos/condicionales
    """
    
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
                jugador = jugador_df.iloc[0].to_dict()
            
                # Agregar estadísticas clave
                if not stats_df.empty:
                    for col in stats_df.columns:
                        if not pd.isna(stats_df[col].iloc[0]):
                            jugador[col] = round(stats_df[col].iloc[0], 1)
            
                # Agregar campos adicionales
                jugador['id_sofascore'] = None
                jugador['foto_url'] = '/assets/imagenes/player_placeholder.png'
                jugador['nacionalidad'] = 'No disponible'
                jugador['pais'] = 'No disponible'
                jugador['altura'] = 'No disponible'
                jugador['peso'] = 'No disponible'
            
                # Intentar buscar información adicional en el archivo maestro
                if os.path.exists('data/jugadores_master.csv'):
                    try:
                        print("Archivo maestro encontrado, buscando coincidencias...")
                        jugadores_master = pd.read_csv('data/jugadores_master.csv')
                    
                        # Imprimir columnas disponibles
                        print(f"Columnas en archivo maestro: {jugadores_master.columns.tolist()}")
                    
                        # Normalizar nombre para búsqueda (quitar acentos, minúsculas)
                        import unicodedata
                        def normalize_name(name):
                            # Normalizar, convertir a minúsculas y quitar espacios extras
                            return ' '.join(unicodedata.normalize('NFKD', str(name).lower())
                                            .encode('ASCII', 'ignore')
                                            .decode('ASCII')
                                            .split())
                    
                        nombre_norm = normalize_name(nombre_jugador)
                        print(f"Nombre normalizado para búsqueda: {nombre_norm}")
                    
                        # Posibles columnas de nombre
                        name_cols = ['nombre_completo', 'short_name']
                    
                        found_match = False
                        for col in name_cols:
                            if col in jugadores_master.columns:
                                # Normalizar nombres del master
                                jugadores_master['nombre_norm'] = jugadores_master[col].apply(normalize_name)
                            
                                # Buscar coincidencias exactas primero
                                exact_matches = jugadores_master[jugadores_master['nombre_norm'] == nombre_norm]
                            
                                if not exact_matches.empty:
                                    matched_row = exact_matches.iloc[0]
                                    print(f"Coincidencia exacta encontrada en columna {col}: {matched_row[col]}")
                                    found_match = True
                                else:
                                    # Buscar coincidencias parciales
                                    partial_matches = jugadores_master[jugadores_master['nombre_norm'].str.contains(nombre_norm, na=False)]
                                
                                    if not partial_matches.empty:
                                        matched_row = partial_matches.iloc[0]
                                        print(f"Coincidencia parcial encontrada en columna {col}: {matched_row[col]}")
                                        found_match = True
                                    else:
                                        # Si no hay coincidencias, intentar con partes del nombre
                                        name_parts = nombre_norm.split()
                                        for part in name_parts:
                                            if len(part) > 3:  # Solo usar partes significativas
                                                part_matches = jugadores_master[jugadores_master['nombre_norm'].str.contains(part, na=False)]
                                                if not part_matches.empty:
                                                    matched_row = part_matches.iloc[0]
                                                    print(f"Coincidencia por parte del nombre '{part}' en columna {col}: {matched_row[col]}")
                                                    found_match = True
                                                    break
                            
                                if found_match:
                                    # Actualizar campos si están disponibles
                                    if 'id_sofascore' in matched_row:
                                        jugador['id_sofascore'] = matched_row['id_sofascore']
                                        print(f"ID Sofascore encontrado: {jugador['id_sofascore']}")
                                
                                    if 'ruta_foto' in matched_row and not pd.isna(matched_row['ruta_foto']):
                                        jugador['foto_url'] = matched_row['ruta_foto']
                                        print(f"URL de foto encontrada: {jugador['foto_url']}")
                                    elif 'image_sofascore' in matched_row and not pd.isna(matched_row['image_sofascore']):
                                        jugador['foto_url'] = matched_row['image_sofascore']
                                        print(f"URL de foto Sofascore encontrada: {jugador['foto_url']}")
                                
                                    if 'pais' in matched_row and not pd.isna(matched_row['pais']):
                                        jugador['nacionalidad'] = matched_row['pais']
                                        jugador['pais'] = matched_row['pais']
                                
                                    break
                    
                        if not found_match:
                            print(f"No se encontraron coincidencias para {nombre_jugador} en el archivo maestro")
                
                    except Exception as e:
                        print(f"Error al acceder al archivo maestro: {e}")
                        import traceback
                        traceback.print_exc()
            
                print(f"Datos finales del jugador: {jugador}")
                return jugador
            else:
                print(f"No se encontraron datos básicos para {nombre_jugador}")
                # Datos por defecto si no se encuentra
                return {
                    'nombre': nombre_jugador,
                    'posicion': 'No disponible',
                    'edad': 'No disponible',
                    'id_sofascore': None,
                    'foto_url': '/assets/imagenes/player_placeholder.png',
                    'nacionalidad': 'No disponible',
                    'pais': 'No disponible',
                    'altura': 'No disponible',
                    'peso': 'No disponible'
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
                'nacionalidad': 'No disponible',
                'pais': 'No disponible',
                'altura': 'No disponible',
                'peso': 'No disponible'
            }
    
    # El resto de las funciones (normalizar_datos, obtener_heatmap) permanecen sin cambios

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
        # En mostrar_info_jugador:
        print(f"Info del jugador: {jugador}")
        print(f"ID Sofascore: {jugador.get('id_sofascore')}")
        if not datos or 'jugador' not in datos:
            return html.Div("Selecciona un jugador para ver su información."), html.Div()
        
        jugador = datos['jugador']
        
        # Crear componente de información del jugador
        info_jugador = html.Div([
            dbc.Row([
                # Imagen del jugador (usar la URL de la imagen si existe)
                dbc.Col([
                    html.Img(
                        src=jugador.get('foto_url', '/assets/imagenes/player_placeholder.png'),
                        style={'max-width': '100%', 'max-height': '150px', 'border-radius': '5px'},
                        className="mb-2"
                    )
                ], width=4),
                
                # Información básica del jugador
                dbc.Col([
                    html.H4(jugador['nombre'], className="mb-2"),
                    html.P([
                        html.Span("Nacionalidad: ", className="fw-bold"),
                        html.Span(jugador.get('nacionalidad', jugador.get('pais', 'No disponible')))
                    ], className="mb-1"),
                    html.P([
                        html.Span("Posición: ", className="fw-bold"),
                        html.Span(jugador.get('posicion', 'No disponible'))
                    ], className="mb-1"),
                    html.P([
                        html.Span("Edad: ", className="fw-bold"),
                        html.Span(str(jugador.get('edad', 'No disponible')))
                    ], className="mb-1"),
                    html.P([
                        html.Span("Altura: ", className="fw-bold"),
                        html.Span(f"{jugador.get('altura', 'No disponible')} cm" if jugador.get('altura') != 'No disponible' else "No disponible")
                    ], className="mb-1"),
                    html.P([
                        html.Span("Peso: ", className="fw-bold"),
                        html.Span(f"{jugador.get('peso', 'No disponible')} kg" if jugador.get('peso') != 'No disponible' else "No disponible")
                    ], className="mb-1"),
                    html.Hr(),
                    html.H5("Estadísticas Destacadas", className="mt-2 mb-2"),
                    html.Div([
                        dbc.Row([
                            dbc.Col([
                                html.P([
                                    html.Span("Distancia media: ", className="fw-bold"),
                                    html.Span(f"{jugador.get('avg_distancia', 'N/A')} m")
                                ], className="mb-1"),
                                html.P([
                                    html.Span("Velocidad máxima: ", className="fw-bold"),
                                    html.Span(f"{jugador.get('max_velocidad', 'N/A')} km/h")
                                ], className="mb-1"),
                            ], width=6),
                            dbc.Col([
                                html.P([
                                    html.Span("Sprints por partido: ", className="fw-bold"),
                                    html.Span(f"{jugador.get('avg_sprints', 'N/A')}")
                                ], className="mb-1"),
                                html.P([
                                    html.Span("Distancia máxima: ", className="fw-bold"),
                                    html.Span(f"{jugador.get('max_distancia', 'N/A')} m")
                                ], className="mb-1"),
                            ], width=6),
                        ])
                    ], className="mt-2")
                ], width=8)
            ])
        ])
        
        # Intentar obtener y mostrar el heatmap
        heatmap_container = html.Div([
            html.H5("Mapa de Calor", className="mb-2"),
            html.P("El mapa de calor no está disponible para este jugador.", className="text-muted")
        ])
        
        # Si tenemos ID de sofascore, generamos el heatmap en un componente aparte
        if 'id_sofascore' in jugador and jugador['id_sofascore']:
            heatmap_container = html.Div([
                html.H5("Mapa de Calor (Posicionamiento)", className="mb-2"),
                html.Div([
                    html.Img(
                        id="heatmap-imagen",
                        src=f"/heatmap/{jugador['id_sofascore']}",  # Esta ruta la manejaremos con una función en el servidor
                        style={'max-width': '100%', 'border-radius': '5px'},
                        className="mt-2"
                    )
                ], id="heatmap-imagen-container")
            ])
        
        return info_jugador, heatmap_container
    # El resto de los callbacks (grafico-barras-fisico, grafico-radar-fisico, etc.) permanecen sin cambios
    
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
    
    # Los demás callbacks (grafico-radar-fisico, grafico-scatter-fisico, etc.) permanecen sin cambios
    
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
        except:
            # Si hay error en la línea de tendencia, seguimos sin ella
            pass
        
        return fig
    
    # Callback para exportar a PDF
    @app.callback(
        Output('descargar-pdf-fisico', 'data'),
        [Input('exportar-pdf-fisico-btn', 'n_clicks')],
        [State('datos-jugador-store', 'data'),
         State('metricas-barras-dropdown', 'value'),
         State('metricas-radar-checklist', 'value')],
        prevent_initial_call=True
    )
    def exportar_pdf_fisico(n_clicks, datos, metricas_barras, metricas_radar):
        if not n_clicks or not datos:
            return None
        
        jugador = datos['jugador']
        nombre_jugador = jugador['nombre']
        
        # Crear un buffer en memoria para el PDF
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        
        # Añadir título
        c.setFont("Helvetica-Bold", 18)
        c.drawString(50, 750, f"Atlético de Madrid - Informe Condicional")
        
        # Información del jugador
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, 720, f"Jugador: {nombre_jugador}")
        
        c.setFont("Helvetica", 12)
        c.drawString(50, 700, f"Posición: {jugador.get('posicion', 'No disponible')}")
        c.drawString(50, 685, f"Edad: {jugador.get('edad', 'No disponible')}")
        
        # Información de métricas analizadas
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, 650, "Métricas Analizadas:")
        
        c.setFont("Helvetica", 12)
        y_pos = 630
        for i, metrica in enumerate(metricas_barras[:3]):
            c.drawString(70, y_pos - i*15, f"• {metrica.replace('_', ' ').title()}")
        
        # Secciones para los gráficos
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, 560, "1. Evolución por Jornada")
        c.drawString(50, 360, "2. Perfil Condicional (Radar)")
        
        # Segunda página
        c.showPage()
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, 750, "3. Relación entre Variables")
        
        # Información adicional
        c.setFont("Helvetica", 12)
        c.drawString(50, 500, "Este informe muestra el análisis condicional completo")
        c.drawString(50, 485, f"para el jugador {nombre_jugador} del Atlético de Madrid.")
        
        # Fecha actual
        from datetime import datetime
        fecha_actual = datetime.now().strftime("%d/%m/%Y")
        c.drawString(50, 100, f"Fecha del informe: {fecha_actual}")
        
        # Firma
        c.drawString(400, 100, "Ramón González MPAD")
        
        c.showPage()
        c.save()
        
        buffer.seek(0)
        return dcc.send_bytes(buffer.getvalue(), f"AtleticoMadrid_Informe_Condicional_{nombre_jugador.replace(' ', '_')}.pdf")
    
    # Callback para mostrar mensaje de éxito del PDF
    @app.callback(
        Output('pdf-fisico-status', 'children'),
        [Input('exportar-pdf-fisico-btn', 'n_clicks')],
        prevent_initial_call=True
    )
    def actualizar_pdf_status_fisico(n_clicks):
        if n_clicks:
            return html.Span("¡PDF generado con éxito!", 
                        className="ms-2 fw-bold", 
                        style={"color": "#4CAF50"})  # Color verde para confirmación
        return ""