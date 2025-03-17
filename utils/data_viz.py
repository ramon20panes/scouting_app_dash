# utils/data_viz.py
from dash import html, dcc
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from config import CONFIG

def load_team_data(file_path):
    """
    Carga datos del CSV del equipo con manejo de errores
    """
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        raise Exception(f"El archivo '{file_path}' no fue encontrado.")
    except pd.errors.EmptyDataError:
        raise Exception('El archivo de datos está vacío.')
    except pd.errors.ParserError:
        raise Exception('Error al analizar el archivo de datos.')
    return df

def format_stat_name(stat_name):
    """
    Convierte el nombre a formato título sin cambios específicos
    """
    return ' '.join(word.capitalize() for word in stat_name.split('_'))

def create_player_stats_layout(df):
    """
    Crea el contenido HTML para la pestaña de estadísticas de jugadores
    """
    # Obtener posiciones únicas
    posiciones = sorted(df['Posicion'].unique())
    
    # Obtener lista de jugadores
    todos_jugadores = sorted(df['Nombre'].unique())
    
    # Obtener estadísticas disponibles (excluyendo columnas no numéricas)
    columnas_no_stats = ['Jornada', 'Partido', 'Nombre', 'Posicion', 'Dorsal', 'Nacionalidad', 'Edad']
    estadisticas = [col for col in df.columns if col not in columnas_no_stats]
    
    return html.Div([
        dbc.Row([
            dbc.Col([
                html.H4("Filtros", className="mb-3"),
                html.Label("Jornada:"),
                dcc.RangeSlider(
                    id='jornada-slider',
                    min=df['Jornada'].min(),
                    max=df['Jornada'].max(),
                    value=[df['Jornada'].min(), df['Jornada'].max()],
                    marks={i: str(i) for i in range(df['Jornada'].min(), df['Jornada'].max()+1)},
                    className="mb-4"
                ),
                html.Label("Posición:"),
                dcc.Dropdown(
                    id='Posicion-dropdown',
                    options=[{'label': pos, 'value': pos} for pos in posiciones] + 
                            [{'label': 'Todas', 'value': 'TODAS'}],
                    value='TODAS',
                    className="mb-3"
                ),
                html.Label("Jugadores:"),
                dcc.Dropdown(
                    id='jugadores-dropdown',
                    options=[{'label': jugador, 'value': jugador} for jugador in todos_jugadores],
                    value=[todos_jugadores[0], todos_jugadores[1], todos_jugadores[2]] if len(todos_jugadores) >= 3 else todos_jugadores,
                    multi=True,
                    className="mb-3"
                ),
                html.Label("Estadística:"),
                dcc.Dropdown(
                    id='estadistica-dropdown',
                    options=[{'label': format_stat_name(stat), 'value': stat} for stat in estadisticas],
                    value=estadisticas[0] if estadisticas else None,
                    className="mb-4"
                ),
                dbc.Button(
                    "Exportar a PDF",
                    id="exportar-pdf-btn",
                    color="primary",
                    className="w-100 mb-3",
                    style={"backgroundColor": CONFIG["team_colors"]["primary"]}
                ),
                dcc.Download(id="descargar-pdf")
            ], md=3, className="mb-4"),
            
            dbc.Col([
                dbc.Row([
                    dbc.Col([
                        html.H4("Evolución por Jornada", className="text-center mb-3"),
                        dcc.Loading(
                            id="loading-grafico-linea",
                            type="circle",
                            children=dcc.Graph(id='grafico-linea')
                        )
                    ], md=12, className="mb-4"),
                    
                    dbc.Col([
                        html.H4("Comparativa de Jugadores", className="text-center mb-3"),
                        dcc.Loading(
                            id="loading-grafico-barras",
                            type="circle",
                            children=dcc.Graph(id='grafico-barras')
                        )
                    ], md=12)
                ])
            ], md=9)
        ])
    ])

def create_player_callbacks(app, df):
    """
    Crea los callbacks para actualizar los gráficos basados en los filtros seleccionados
    """
    from dash.dependencies import Input, Output, State
    import plotly.graph_objects as go
    import io
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib import colors
    
    # Callback para actualizar dropdown de jugadores basado en posición seleccionada
    @app.callback(
        Output('jugadores-dropdown', 'options'),
        [Input('posicion-dropdown', 'value')]
    )
    def actualizar_jugadores_dropdown(posicion_seleccionada):
        if posicion_seleccionada == 'TODAS':
            jugadores_filtrados = sorted(df['jugador'].unique())
        else:
            jugadores_filtrados = sorted(df[df['posicion'] == posicion_seleccionada]['jugador'].unique())
        
        return [{'label': jugador, 'value': jugador} for jugador in jugadores_filtrados]
    
    # Callback para actualizar gráfico de línea
    @app.callback(
        Output('grafico-linea', 'figure'),
        [Input('jornada-slider', 'value'),
         Input('jugadores-dropdown', 'value'),
         Input('estadistica-dropdown', 'value')]
    )
    def actualizar_grafico_linea(rango_jornadas, jugadores_seleccionados, estadistica):
        if not jugadores_seleccionados or not estadistica:
            return go.Figure()
        
        # Filtrar por rango de jornadas
        df_filtrado = df[(df['Jornada'] >= rango_jornadas[0]) & (df['Jornada'] <= rango_jornadas[1])]
        
        # Filtrar por jugadores seleccionados
        df_filtrado = df_filtrado[df_filtrado['Nombre'].isin(jugadores_seleccionados)]
        
        # Agrupar por jornada y jugador, calculando la media de la estadística
        df_agrupado = df_filtrado.groupby(['Jornada', 'Nombre'])[estadistica].mean().reset_index()
        
        # Crear gráfico de línea
        fig = px.line(
            df_agrupado, 
            x='Jornada', 
            y=estadistica, 
            color='Nombre', 
            title=f"{format_stat_name(estadistica)} por Jornada",
            labels={'Jornada': 'Jornada', estadistica: format_stat_name(estadistica)}
        )
        
        # Personalizar gráfico
        fig.update_layout(
            template='plotly_white',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            xaxis=dict(tickmode='linear', dtick=1)
        )
        
        fig.update_traces(line=dict(width=3))
        
        return fig
    
    # Callback para actualizar gráfico de barras
    @app.callback(
        Output('grafico-barras', 'figure'),
        [Input('jornada-slider', 'value'),
         Input('jugadores-dropdown', 'value'),
         Input('estadistica-dropdown', 'value')]
    )
    def actualizar_grafico_barras(rango_jornadas, jugadores_seleccionados, estadistica):
        if not jugadores_seleccionados or not estadistica:
            return go.Figure()
        
        # Filtrar por rango de jornadas
        df_filtrado = df[(df['Jornada'] >= rango_jornadas[0]) & (df['Jornada'] <= rango_jornadas[1])]
        
        # Filtrar por jugadores seleccionados
        df_filtrado = df_filtrado[df_filtrado['Nombre'].isin(jugadores_seleccionados)]
        
        # Agrupar por jugador, calculando la media total de la estadística
        df_agrupado = df_filtrado.groupby('Nombre')[estadistica].mean().reset_index()
        
        # Ordenar por valor de estadística descendente
        df_agrupado = df_agrupado.sort_values(by=estadistica, ascending=False)
        
        # Crear gráfico de barras
        fig = px.bar(
            df_agrupado, 
            x='Nombre', 
            y=estadistica, 
            color='Nombre',
            title=f"Comparativa de {format_stat_name(estadistica)} (Promedio)",
            labels={'Nombre': 'Nombre', estadistica: format_stat_name(estadistica)}
        )
        
        # Personalizar gráfico
        fig.update_layout(
            template='plotly_white',
            showlegend=False,
            xaxis={'categoryorder':'total descending'}
        )
        
        return fig
    
    # Callback para exportar a PDF
    @app.callback(
        Output('descargar-pdf', 'data'),
        [Input('exportar-pdf-btn', 'n_clicks')],
        [State('grafico-linea', 'figure'),
         State('grafico-barras', 'figure'),
         State('estadistica-dropdown', 'value'),
         State('jornada-slider', 'value'),
         State('jugadores-dropdown', 'value')],
        prevent_initial_call=True
    )
    def exportar_pdf(n_clicks, fig_linea, fig_barras, estadistica, rango_jornadas, jugadores):
        if not n_clicks:
            return None
            
        # Crear un buffer en memoria para el PDF
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        
        # Añadir logo y título
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, 750, "Atlético de Madrid - Informe de Rendimiento")
        
        # Información del informe
        c.setFont("Helvetica", 12)
        c.drawString(50, 725, f"Estadística: {format_stat_name(estadistica)}")
        c.drawString(50, 710, f"Jornadas: {rango_jornadas[0]} a {rango_jornadas[1]}")
        c.drawString(50, 695, f"Jugadores: {', '.join(jugadores)}")
        
        # Convertir figuras a imágenes y añadirlas al PDF
        # (Nota: Aquí normalmente usaríamos pio para guardar las figuras como imágenes
        # y luego las añadiríamos al PDF, pero para simplificar usaremos texto)
        
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, 650, "Evolución por Jornada")
        c.drawString(50, 400, "Comparativa de Jugadores")
        
        c.showPage()
        c.save()
        
        buffer.seek(0)
        return dcc.send_bytes(buffer.getvalue(), f"AtleticoMadrid_Informe_{estadistica}.pdf")