from dash import html, dcc
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from config import CONFIG

from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors

# Paletas de colores por posición (varios tonos para cada posición)
paleta_gk = ['#FFFF00', '#FFD700', '#FFC300']  # Amarillos para porteros
paleta_cb = ['#1E88E5', '#1565C0', '#0D47A1', '#0277BD', '#01579B']  # Azules para defensas centrales
paleta_lb = ['#42A5F5', '#2196F3', '#1976D2']  # Azules para laterales izquierdos
paleta_rb = ['#90CAF9', '#64B5F6', '#4FC3F7']  # Azules claros para laterales derechos
paleta_cm = ['#4CAF50', '#388E3C', '#2E7D32', '#43A047', '#66BB6A']  # Verdes para centrocampistas
paleta_am = ['#FF9800', '#F57C00', '#EF6C00', '#FB8C00', '#FF9100']  # Naranjas para mediapuntas
paleta_lm = ['#FFA726', '#FF8F00', '#FFB74D']  # Naranjas claros para extremos izquierdos
paleta_rm = ['#FFB74D', '#FFA000', '#FFD54F']  # Naranjas más claros para extremos derechos
paleta_fw = ['#F44336', '#E53935', '#D32F2F', '#C62828', '#B71C1C']  # Rojos para delanteros

# Para usar en la función de color por posición
colores_por_posicion = {
    'GK': paleta_gk[0],
    'CB': paleta_cb[0],
    'LB': paleta_lb[0],
    'RB': paleta_rb[0],
    'WB': paleta_rb[1],
    'CM': paleta_cm[0],
    'AM': paleta_am[0],
    'LM': paleta_lm[0],
    'RM': paleta_rm[0],
    'FW': paleta_fw[0]
}

# Mapeo de jugador a posición principal
jugadores_posiciones = {
    # Porteros
    'Jan Oblak': 'GK',
    'Juan Musso': 'GK',
    
    # Defensas centrales
    'Robin Le Normand': 'CB',
    'José María Giménez': 'CB',
    'César Azpilicueta': 'CB',
    'Axel Witsel': 'CB',
    
    # Laterales
    'Nahuel Molina': 'RB',
    'Reinildo Mandava': 'LB',
    'Rodrigo Riquelme': 'LB',
    
    # Centrocampistas
    'Koke': 'CM',
    'Rodrigo De Paul': 'CM',
    'Pablo Barrios': 'CM',
    'Conor Gallagher': 'CM',
    'Marcos Llorente': 'RM',
    
    # Mediapuntas/Extremos
    'Antoine Griezmann': 'AM',
    'Ángel Correa': 'AM',
    'Samuel Lino': 'LM',
    'Giuliano Simeone': 'LM',
    
    # Delanteros
    'Julián Álvarez': 'FW',
    'Alexander Sørloth': 'FW'
}

# Mapeo de colores personalizados para cada jugador
colores_jugadores = {
    # Porteros
    'Jan Oblak': paleta_gk[0],
    'Juan Musso': paleta_gk[1],
    
    # Defensas centrales
    'Robin Le Normand': paleta_cb[0],
    'José María Giménez': paleta_cb[1],
    'César Azpilicueta': paleta_cb[2],
    'Axel Witsel': paleta_cb[3],
    
    # Laterales
    'Nahuel Molina': paleta_rb[0],
    'Reinildo Mandava': paleta_lb[0],
    'Rodrigo Riquelme': paleta_lb[1],
    
    # Centrocampistas
    'Koke': paleta_cm[0],
    'Rodrigo De Paul': paleta_cm[1],
    'Pablo Barrios': paleta_cm[2],
    'Conor Gallagher': paleta_cm[3],
    'Marcos Llorente': paleta_rm[0],
    
    # Mediapuntas/Extremos
    'Antoine Griezmann': paleta_am[0],
    'Ángel Correa': paleta_am[1],
    'Samuel Lino': paleta_lm[0],
    'Giuliano Simeone': paleta_lm[1],
    
    # Delanteros
    'Julián Álvarez': paleta_fw[0],
    'Alexander Sørloth': paleta_fw[1]
}

# Jugadores predeterminados para mostrar al inicio
jugadores_predeterminados = ['Antoine Griezmann', 'Julián Álvarez', 'Pablo Barrios']

# Métricas predeterminadas
metrica_lineas_default = 'Min'  # Minutos para el gráfico de líneas
metrica_barras_default = '%_pases'  # Pases interceptados para el gráfico de barras
metrica_evolucion_default = 'Gls'  # Goles para el histograma
metrica_x_default = 'Num_toques'  # Número de toques para el eje X del scatter
metrica_y_default = 'Pases_compl'  # Pases completados para el eje Y del scatter
jornada_barras_default = 1  # Jornada 1 para el gráfico de barras

# Estilos comunes para aplicar consistentemente
ESTILO_FONDO_PAGINA = {"backgroundColor": "#f0f0f0", "padding": "15px", "borderRadius": "5px"}
ESTILO_TARJETA = {"border": "none", "boxShadow": "none", "backgroundColor": "transparent"}
ESTILO_HEADER = {"backgroundColor": "transparent", "border": "none", "padding": "1rem 1.25rem"}
ESTILO_CUERPO = {"backgroundColor": "transparent", "padding": "1.25rem"}
ESTILO_TITULO = {"color": "#001F3F"}
ESTILO_ETIQUETA = {"color": "#001F3F"}
ESTILO_DROPDOWN = {"fontSize": "0.9rem", "backgroundColor": "#ffffff", "borderColor": "#d0d0d0"}
ESTILO_BOTON = {"backgroundColor": "#001F3F", "borderColor": "#001F3F"}

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
    Formatea el nombre de la estadística para mostrar
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
    
    # Jugadores iniciales (calculados aquí donde todos_jugadores está disponible)
    jugadores_iniciales = [j for j in jugadores_predeterminados if j in todos_jugadores]
    if not jugadores_iniciales:
        jugadores_iniciales = todos_jugadores[:3] if len(todos_jugadores) >= 3 else todos_jugadores
    
    # Obtener jornadas únicas
    jornadas = sorted(df['Jornada'].unique())
    
    # Obtener estadísticas disponibles (excluyendo columnas no numéricas)
    columnas_no_stats = ['Jornada', 'Partido', 'Nombre', 'Posicion', 'Dorsal', 'Nacionalidad', 'Edad']
    estadisticas = [col for col in df.columns if col not in columnas_no_stats]
    
    # Contenedor principal para todos los gráficos
    return html.Div([
        # Slider de jornada (oculto pero funcional)
        html.Div([
            dcc.RangeSlider(
                id='jornada-slider',
                min=df['Jornada'].min(),
                max=df['Jornada'].max(),
                value=[df['Jornada'].min(), df['Jornada'].max()],
                marks={i: str(i) for i in range(df['Jornada'].min(), df['Jornada'].max()+1)},
                className="mb-4"
            )
        ], style={"display": "none"}),  # Oculto pero aún funcional
        
        # Primera fila de gráficos - Línea y Scatter
        dbc.Row([
            # Gráfico 1: Evolución por posición (Gráfico de líneas)
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H4("Evolución por Posición", className="card-title fw-bold fs-4", style=ESTILO_TITULO),
                        # Filtros de posición y jugadores en la misma línea
                        dbc.Row([
                            dbc.Col([
                                html.Label("Posición:", className="me-2 fw-semibold fs-6", style=ESTILO_ETIQUETA),
                                dcc.Dropdown(
                                    id='posicion-dropdown',
                                    options=[{'label': pos, 'value': pos} for pos in posiciones] + 
                                            [{'label': 'Todas', 'value': 'TODAS'}],
                                    value='TODAS',
                                    className="mb-2",
                                    style=ESTILO_DROPDOWN
                                ),
                            ], width=4),
                            dbc.Col([
                                html.Label("Jugadores:", className="me-2 fw-semibold fs-6", style=ESTILO_ETIQUETA),
                                dcc.Dropdown(
                                    id='jugadores-dropdown',
                                    options=[{'label': jugador, 'value': jugador} for jugador in todos_jugadores],
                                    value=jugadores_iniciales,
                                    multi=True,
                                    className="mb-2",
                                    style=ESTILO_DROPDOWN
                                ),
                            ], width=8),
                        ]),
                    ], style=ESTILO_HEADER),
                    dbc.CardBody([
                        # Gráfico
                        dcc.Loading(
                            id="loading-grafico-linea",
                            type="circle",
                            children=dcc.Graph(id='grafico-linea', style={"height": "450px"})
                        ),
                        # Selector de métrica debajo del gráfico
                        html.Div([
                            html.Label("Métrica:", className="me-2 mt-3 fw-semibold fs-6", style=ESTILO_ETIQUETA),
                            dcc.Dropdown(
                                id='metrica-evolucion-dropdown',
                                options=[{'label': format_stat_name(stat), 'value': stat} for stat in estadisticas],
                                value=metrica_lineas_default if metrica_lineas_default in estadisticas else estadisticas[0],
                                style=dict(ESTILO_DROPDOWN, **{"width": "100%", "margin-top": "0.5rem"})
                            )
                        ])
                    ], style=ESTILO_CUERPO)
                ], className="h-100", style=ESTILO_TARJETA)
            ], width=6, className="mb-4"),
    
            # Gráfico 2: Correlación (Scatter)
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H4("Correlación entre Métricas", className="card-title fw-bold fs-4", style=ESTILO_TITULO),
                        # Selección de métricas X e Y en la misma línea
                        dbc.Row([
                            dbc.Col([
                                html.Label("Eje X:", className="me-2 fw-semibold fs-6", style=ESTILO_ETIQUETA),
                                dcc.Dropdown(
                                    id='metrica-x-dropdown',
                                    options=[{'label': format_stat_name(stat), 'value': stat} for stat in estadisticas],
                                    value=metrica_x_default if metrica_x_default in estadisticas else estadisticas[0],
                                    placeholder="Eje X",
                                    style=ESTILO_DROPDOWN
                                )
                            ], width=6),
                            dbc.Col([
                                html.Label("Eje Y:", className="me-2 fw-semibold fs-6", style=ESTILO_ETIQUETA),
                                dcc.Dropdown(
                                    id='metrica-y-dropdown',
                                    options=[{'label': format_stat_name(stat), 'value': stat} for stat in estadisticas],
                                    value=metrica_y_default if metrica_y_default in estadisticas else (estadisticas[1] if len(estadisticas) > 1 else estadisticas[0]),
                                    placeholder="Eje Y",
                                    style=ESTILO_DROPDOWN
                                )
                            ], width=6)
                        ]),
                    ], style=ESTILO_HEADER),
                    dbc.CardBody([
                        # Gráfico
                        dcc.Loading(
                            id="loading-grafico-scatter",
                            type="circle",
                            children=dcc.Graph(id='grafico-scatter', style={"height": "450px"})
                        ),
                        # Jornada debajo del gráfico
                        html.Div([
                            html.Label("Jornada:", className="me-2 mt-2 fw-semibold fs-6", style=ESTILO_ETIQUETA),
                            dcc.Dropdown(
                                id='jornada-scatter-dropdown',
                                options=[{'label': f'Jornada {j}', 'value': j} for j in jornadas],
                                value=jornadas[0] if jornadas else None,
                                style=dict(ESTILO_DROPDOWN, **{"width": "100%", "margin-top": "0.5rem"})
                            )
                        ])
                    ], style=ESTILO_CUERPO)
                ], className="h-100", style=ESTILO_TARJETA)
            ], width=6, className="mb-4")
        ]),

        # Segunda fila de gráficos - Histograma y Lineas
        dbc.Row([
            # Gráfico 3: Distribución (Histograma)
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H4("Tendencia equipo", className="card-title fw-bold fs-4", style=ESTILO_TITULO),
                    ], style=ESTILO_HEADER),
                    dbc.CardBody([
                        # Gráfico
                        dcc.Loading(
                            id="loading-grafico-histograma",
                            type="circle",
                            children=dcc.Graph(id='grafico-histograma', style={"height": "450px"})       
                        ),
                        # Selector de métrica debajo del gráfico
                        html.Div([
                            html.Label("Métrica:", className="me-2 mt-2 fw-semibold fs-6", style=ESTILO_ETIQUETA),
                            dcc.Dropdown(
                                id='metrica-histograma-dropdown',
                                options=[{'label': format_stat_name(stat), 'value': stat} for stat in estadisticas],
                                value=metrica_evolucion_default if metrica_evolucion_default in estadisticas else estadisticas[0],
                                style=dict(ESTILO_DROPDOWN, **{"width": "100%"})
                            )
                        ])
                    ], style=ESTILO_CUERPO)
                ], className="h-100", style=ESTILO_TARJETA)
            ], width=6, className="mb-4"),
    
            # Gráfico 4: Comparativa por jornada (Gráfico de barras)
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H4("Participantes en partido", className="card-title fw-bold fs-4", style=ESTILO_TITULO),
                    ], style=ESTILO_HEADER),
                    dbc.CardBody([
                        # Gráfico más grande
                        dcc.Loading(
                            id="loading-grafico-barras",
                            type="circle",
                            children=dcc.Graph(id='grafico-barras', style={"height": "450px"})
                        ),
                        # Controles debajo del gráfico
                        dbc.Row([
                            dbc.Col([
                                html.Label("Jornada:", className="me-2 mt-2 fw-semibold fs-6", style=ESTILO_ETIQUETA),
                                dcc.Dropdown(
                                    id='jornada-barras-dropdown',
                                    options=[{'label': f'Jornada {j}', 'value': j} for j in jornadas],
                                    value=jornada_barras_default if jornada_barras_default in jornadas else jornadas[0],
                                    style=ESTILO_DROPDOWN
                                )
                            ], width=6),
                            dbc.Col([
                                html.Label("Métrica:", className="me-2 mt-2 fw-semibold fs-6", style=ESTILO_ETIQUETA),
                                dcc.Dropdown(
                                    id='metrica-barras-dropdown',
                                    options=[{'label': format_stat_name(stat), 'value': stat} for stat in estadisticas],
                                    value=metrica_barras_default if metrica_barras_default in estadisticas else estadisticas[0],
                                    style=ESTILO_DROPDOWN
                                )
                            ], width=6)
                        ])
                    ], style=ESTILO_CUERPO)
                ], className="h-100", style=ESTILO_TARJETA)
            ], width=6, className="mb-4")
        ]),
            

        # Fila final - Botón PDF y firma
        dbc.Row([
            # Botón de exportar PDF
            dbc.Col([
                html.Div([
                    dbc.Button(
                        "Generar PDF",
                        id="exportar-pdf-btn",
                        color="primary",
                        className="me-2",
                        style=ESTILO_BOTON
                    ),
                    html.Span(id="pdf-status", className="ms-2"),
                    dcc.Download(id="descargar-pdf")
                ], className="d-flex align-items-center")
            ], width=6),
    
            # Firma personal
            dbc.Col([
                html.Div([
                    html.P("Ramón González MPAD", className="text-end fw-bold fs-5", style=ESTILO_TITULO)
                ])
            ], width=6)
        ], className="mt-4")
    ], style=ESTILO_FONDO_PAGINA)

def create_player_callbacks(app, df):
    """
    Crea y devuelve los callbacks para actualizar los gráficos basados en los filtros seleccionados
    sin registrarlos directamente
    """
    
    # Definimos los callbacks como funciones normales sin registrarlas
    def actualizar_jugadores_dropdown(posicion_seleccionada):
        if posicion_seleccionada == 'TODAS':
            jugadores_filtrados = sorted(df['Nombre'].unique())
        else:
            jugadores_filtrados = sorted(df[df['Posicion'] == posicion_seleccionada]['Nombre'].unique())
        
        return [{'label': jugador, 'value': jugador} for jugador in jugadores_filtrados]
    
    def actualizar_grafico_linea(rango_jornadas, jugadores_seleccionados, metrica):
        if not jugadores_seleccionados or not metrica:
            return go.Figure()
    
        # Filtrar por rango de jornadas
        df_filtrado = df[(df['Jornada'] >= rango_jornadas[0]) & (df['Jornada'] <= rango_jornadas[1])]
    
        # Filtrar por jugadores seleccionados
        df_filtrado = df_filtrado[df_filtrado['Nombre'].isin(jugadores_seleccionados)]
    
        # Agrupar por jornada y jugador, calculando la media de la métrica
        df_agrupado = df_filtrado.groupby(['Jornada', 'Nombre'])[metrica].mean().reset_index()
    
        # Crear gráfico de línea con colores personalizados
        fig = go.Figure()
    
        for jugador in jugadores_seleccionados:
            if jugador in df_agrupado['Nombre'].values:
                df_jugador = df_agrupado[df_agrupado['Nombre'] == jugador]
                color = colores_jugadores.get(jugador, '#000000')  # Negro por defecto si no está en el mapeo
            
                fig.add_trace(go.Scatter(
                    x=df_jugador['Jornada'],
                    y=df_jugador[metrica],
                    mode='lines+markers',
                    name=jugador,
                    line=dict(color=color, width=3),
                    marker=dict(color=color, size=8)
                ))
    
        # Personalizar gráfico
        fig.update_layout(
            title=f"{format_stat_name(metrica)} por Jornada",
            xaxis_title="Jornada",
            yaxis_title=format_stat_name(metrica),
            template='plotly_white',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            xaxis=dict(
                tickmode='linear', 
                dtick=1,
                title_font=dict(color="#001F3F"),
                tickfont=dict(color="#001F3F"),
                gridcolor='rgba(0, 31, 63, 0.1)'
            ),
            yaxis=dict(
                title_font=dict(color="#001F3F"),
                tickfont=dict(color="#001F3F"),
                gridcolor='rgba(0, 31, 63, 0.1)'
            ),
            plot_bgcolor='rgba(240,240,240,0.5)',
            paper_bgcolor='#ffffff',
            font=dict(family="Arial, sans-serif", size=12, color="#001F3F")
        )
    
        return fig
    
    def actualizar_grafico_barras(jornada_seleccionada, metrica):
        if not jornada_seleccionada or not metrica:
            return go.Figure()
        
        # Filtrar por jornada seleccionada
        df_filtrado = df[df['Jornada'] == jornada_seleccionada]
        
        # Ordenar por valor de métrica descendente
        df_filtrado = df_filtrado.sort_values(by=metrica, ascending=False)
        
        # Crear gráfico de barras
        fig = px.bar(
            df_filtrado, 
            x='Nombre', 
            y=metrica,
            color='Nombre',
            title=f"{format_stat_name(metrica)} - Jornada {jornada_seleccionada}",
            labels={'Nombre': 'Jugador', metrica: format_stat_name(metrica)}
        )
        
        # Personalizar gráfico
        fig.update_layout(
            template='plotly_white',
            showlegend=False,
            xaxis={
                'categoryorder':'total descending',
                'title_font': {'color': "#001F3F"},
                'tickfont': {'color': "#001F3F"},
                'gridcolor': 'rgba(0, 31, 63, 0.1)'
            },
            yaxis={
                'title_font': {'color': "#001F3F"},
                'tickfont': {'color': "#001F3F"},
                'gridcolor': 'rgba(0, 31, 63, 0.1)'
            },
            plot_bgcolor='rgba(240,240,240,0.5)',
            paper_bgcolor='#ffffff',
            font=dict(family="Arial, sans-serif", size=12, color="#001F3F")
        )
        
        return fig
    
    def actualizar_grafico_histograma(rango_jornadas, metrica):
        if not metrica:
            return go.Figure()
    
        # Filtrar por rango de jornadas
        df_filtrado = df[(df['Jornada'] >= rango_jornadas[0]) & (df['Jornada'] <= rango_jornadas[1])]
    
        # Calcular promedio de la métrica por jornada
        df_agrupado = df_filtrado.groupby('Jornada')[metrica].mean().reset_index()
    
        # Crear gráfico de línea con barra
        fig = px.bar(
            df_agrupado, 
            x='Jornada', 
            y=metrica,
            title=f"Evolución de {format_stat_name(metrica)} por Jornada",
            labels={'Jornada': 'Jornada', metrica: format_stat_name(metrica)},
            color_discrete_sequence=[CONFIG["team_colors"]["primary"]]  # Color principal del Atlético
        )
    
        # Añadir línea de tendencia
        fig.add_scatter(
            x=df_agrupado['Jornada'], 
            y=df_agrupado[metrica], 
            mode='lines', 
            name='Tendencia',
            line=dict(color=CONFIG["team_colors"]["secondary"], width=3)
        )
    
        # Personalizar gráfico
        fig.update_layout(
            template='plotly_white',
            bargap=0.3,
            xaxis=dict(
                tickmode='linear', 
                dtick=1,
                title_font=dict(color="#001F3F"),
                tickfont=dict(color="#001F3F"),
                gridcolor='rgba(0, 31, 63, 0.1)'
            ),
            yaxis=dict(
                title_font=dict(color="#001F3F"),
                tickfont=dict(color="#001F3F"),
                gridcolor='rgba(0, 31, 63, 0.1)'
            ),
            plot_bgcolor='rgba(240,240,240,0.5)',
            paper_bgcolor='#ffffff',
            font=dict(family="Arial, sans-serif", size=12, color="#001F3F")
        )
    
        return fig
    
    def actualizar_grafico_scatter(jornada_seleccionada, metrica_x, metrica_y):
        if not jornada_seleccionada or not metrica_x or not metrica_y:
            return go.Figure()
    
        # Filtrar por jornada seleccionada
        df_filtrado = df[df['Jornada'] == jornada_seleccionada]
    
        # Crear scatter plot con colores por posición
        fig = go.Figure()
    
        # Agrupar por posición para la leyenda
        posiciones_unicas = df_filtrado['Posicion'].unique()
    
        for posicion in posiciones_unicas:
            df_pos = df_filtrado[df_filtrado['Posicion'] == posicion]
            color = colores_por_posicion.get(posicion, '#000000')  # Negro por defecto
        
            fig.add_trace(go.Scatter(
                x=df_pos[metrica_x],
                y=df_pos[metrica_y],
                mode='markers+text',
                name=posicion,
                text=df_pos['Nombre'],
                textposition='top center',
                marker=dict(color=color, size=12),
                textfont=dict(size=10, color="#001F3F")
            ))
    
        # Personalizar gráfico
        fig.update_layout(
            title=f"{format_stat_name(metrica_x)} vs {format_stat_name(metrica_y)} - Jornada {jornada_seleccionada}",
            xaxis_title=format_stat_name(metrica_x),
            yaxis_title=format_stat_name(metrica_y),
            template='plotly_white',
            xaxis=dict(
                title_font=dict(color="#001F3F"),
                tickfont=dict(color="#001F3F"),
                gridcolor='rgba(0, 31, 63, 0.1)'
            ),
            yaxis=dict(
                title_font=dict(color="#001F3F"),
                tickfont=dict(color="#001F3F"),
                gridcolor='rgba(0, 31, 63, 0.1)'
            ),
            plot_bgcolor='rgba(240,240,240,0.5)',
            paper_bgcolor='#ffffff',
            font=dict(family="Arial, sans-serif", size=12, color="#001F3F"),
            margin=dict(l=80, r=80, t=100, b=80),
            height=450,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
    
        # Ampliar el rango del gráfico para que quepan las etiquetas
        x_min = df_filtrado[metrica_x].min() * 0.7 if df_filtrado[metrica_x].min() > 0 else df_filtrado[metrica_x].min() * 1.3
        x_max = df_filtrado[metrica_x].max() * 1.3
        y_min = df_filtrado[metrica_y].min() * 0.7 if df_filtrado[metrica_y].min() > 0 else df_filtrado[metrica_y].min() * 1.3
        y_max = df_filtrado[metrica_y].max() * 1.3
    
        fig.update_xaxes(range=[x_min, x_max])
        fig.update_yaxes(range=[y_min, y_max])
    
        return fig
    
    def exportar_pdf(n_clicks, rango_jornadas, estadistica, jugadores):
        if not n_clicks:
            return None
        
        # Crear un buffer en memoria para el PDF
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
    
        # Añadir logo y título
        c.setFont("Helvetica-Bold", 18)
        c.drawString(50, 750, "Atlético de Madrid - Informe de Rendimiento")
    
        # Información del informe
        c.setFont("Helvetica", 12)
        c.drawString(50, 725, f"Estadística principal: {format_stat_name(estadistica)}")
        c.drawString(50, 710, f"Jornadas analizadas: {rango_jornadas[0]} a {rango_jornadas[1]}")
    
        # La lista de jugadores puede ser muy larga, así que limitamos
        if len(jugadores) > 5:
            texto_jugadores = ", ".join(jugadores[:5]) + f"... y {len(jugadores) - 5} más"
        else:
            texto_jugadores = ", ".join(jugadores)
            
        c.drawString(50, 695, f"Jugadores: {texto_jugadores}")
    
        # Secciones para los cuatro gráficos
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, 650, "1. Evolución por Jornada")
        c.drawString(50, 450, "4. Correlación entre Métricas")
        c.drawString(50, 250, "3. Evolución por Jornada")
    
        # Segunda página
        c.showPage()
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, 750, "2. Comparativa por Jornada")
    
        # Información adicional
        c.setFont("Helvetica", 12)
        c.drawString(50, 500, "Este informe muestra el análisis completo de las estadísticas")
        c.drawString(50, 485, "seleccionadas para los jugadores del Atlético de Madrid.")
    
        # Fecha actual
        from datetime import datetime
        fecha_actual = datetime.now().strftime("%d/%m/%Y")
        c.drawString(50, 100, f"Fecha del informe: {fecha_actual}")
    
        # Firma
        c.drawString(400, 100, "Ramón González MPAD")
    
        c.showPage()
        c.save()
    
        buffer.seek(0)
        return dcc.send_bytes(buffer.getvalue(), f"AtleticoMadrid_Informe_{estadistica}.pdf")
    
    def actualizar_pdf_status(n_clicks):
        if n_clicks:
            return html.Span("¡PDF generado con éxito!", 
                         className="ms-2 fw-bold", 
                         style={"color": "#4CAF50"})  # Color verde para confirmación
        return ""
    
    # Devolver las funciones de callback para que puedan ser registradas externamente
    return {
        'actualizar_jugadores_dropdown': actualizar_jugadores_dropdown,
        'actualizar_grafico_linea': actualizar_grafico_linea,
        'actualizar_grafico_scatter': actualizar_grafico_scatter,
        'actualizar_grafico_histograma': actualizar_grafico_histograma,        
        'actualizar_grafico_barras': actualizar_grafico_barras,
        'exportar_pdf': exportar_pdf,
        'actualizar_pdf_status': actualizar_pdf_status
    }