import dash_bootstrap_components as dbc
from dash import html, dcc
import pandas as pd
from utils.auth import protect_route
from config import CONFIG

@protect_route(['view_team', 'view_all'])
def player_stats_layout():
    """
    Layout para el dashboard de estadísticas de jugadores
    """
    try:
        # Cargar datos de jugadores
        df = load_team_data('data/ATM_24_25.csv')
        
        # Obtener posiciones únicas
        posiciones = sorted(df['Posicion'].unique())
        
        # Obtener lista de jugadores
        todos_jugadores = sorted(df['Nombre'].unique())
        
        # Jugadores iniciales
        jugadores_iniciales = [j for j in jugadores_predeterminados if j in todos_jugadores]
        if not jugadores_iniciales:
            jugadores_iniciales = todos_jugadores[:3] if len(todos_jugadores) >= 3 else todos_jugadores
        
        # Obtener jornadas únicas
        jornadas = sorted(df['Jornada'].unique())
        
        # Obtener estadísticas disponibles (excluyendo columnas no numéricas)
        columnas_no_stats = ['Jornada', 'Partido', 'Nombre', 'Posicion', 'Dorsal', 'Nacionalidad', 'Edad']
        estadisticas = [col for col in df.columns if col not in columnas_no_stats]
        
        return html.Div([
            html.H1("Estadísticas partido", className="text-center mb-4"),
            html.Hr(),
            
            # Contenedor principal
            html.Div([                
                # Primera fila de gráficos - Línea y Scatter
                dbc.Row([
                    # Gráfico 1: Evolución por posición (Gráfico de líneas)
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader([
                                html.H4("Evolución por Posición", className="card-title fw-bold fs-4"),
                                # Filtros de posición y jugadores en la misma línea
                                dbc.Row([
                                    dbc.Col([
                                        html.Label("Posición:", className="me-2 fw-semibold fs-6"),
                                        dcc.Dropdown(
                                            id='posicion-dropdown',
                                            options=[{'label': pos, 'value': pos} for pos in posiciones] + 
                                                    [{'label': 'Todas', 'value': 'TODAS'}],
                                            value='TODAS',
                                            className="mb-2"
                                        ),
                                    ], width=4),
                                    dbc.Col([
                                        html.Label("Jugadores:", className="me-2 fw-semibold fs-6"),
                                        dcc.Dropdown(
                                            id='jugadores-dropdown',
                                            options=[{'label': jugador, 'value': jugador} for jugador in todos_jugadores],
                                            value=jugadores_iniciales,
                                            multi=True,
                                            className="mb-2"
                                        ),
                                    ], width=8),
                                ]),
                            ]),
                            dbc.CardBody([
                                # Gráfico
                                dcc.Loading(
                                    id="loading-grafico-linea",
                                    type="circle",
                                    children=dcc.Graph(id='grafico-linea', style={"height": "450px"})
                                ),
                                # Selector de métrica debajo del gráfico
                                html.Div([
                                    html.Label("Métrica:", className="me-2 mt-3 fw-semibold fs-6"),
                                    dcc.Dropdown(
                                        id='metrica-evolucion-dropdown',
                                        options=[{'label': format_stat_name(stat), 'value': stat} for stat in estadisticas],
                                        value='Min' if 'Min' in estadisticas else estadisticas[0],
                                        style={"width": "100%", "margin-top": "0.5rem"}
                                    )
                                ])
                            ])
                        ], className="h-100")
                    ], width=6, className="mb-4"),
            
                    # Gráfico 2: Correlación (Scatter)
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader([
                                html.H4("Correlación entre Métricas", className="card-title fw-bold fs-4"),
                                # Selección de métricas X e Y en la misma línea
                                dbc.Row([
                                    dbc.Col([
                                        html.Label("Eje X:", className="me-2 fw-semibold fs-6"),
                                        dcc.Dropdown(
                                            id='metrica-x-dropdown',
                                            options=[{'label': format_stat_name(stat), 'value': stat} for stat in estadisticas],
                                            value='Num_toques' if 'Num_toques' in estadisticas else estadisticas[0],
                                            placeholder="Eje X"
                                        )
                                    ], width=6),
                                    dbc.Col([
                                        html.Label("Eje Y:", className="me-2 fw-semibold fs-6"),
                                        dcc.Dropdown(
                                            id='metrica-y-dropdown',
                                            options=[{'label': format_stat_name(stat), 'value': stat} for stat in estadisticas],
                                            value='Pases_compl' if 'Pases_compl' in estadisticas else (estadisticas[1] if len(estadisticas) > 1 else estadisticas[0]),
                                            placeholder="Eje Y"
                                        )
                                    ], width=6)
                                ]),
                            ]),
                            dbc.CardBody([
                                # Gráfico
                                dcc.Loading(
                                    id="loading-grafico-scatter",
                                    type="circle",
                                    children=dcc.Graph(id='grafico-scatter', style={"height": "450px"})
                                ),
                                # Jornada debajo del gráfico
                                html.Div([
                                    html.Label("Jornada:", className="me-2 mt-2 fw-semibold fs-6"),
                                    dcc.Dropdown(
                                        id='jornada-scatter-dropdown',
                                        options=[{'label': f'Jornada {j}', 'value': j} for j in jornadas],
                                        value=jornadas[0] if jornadas else None,
                                        style={"width": "100%", "margin-top": "0.5rem"}
                                    )
                                ])
                            ])
                        ], className="h-100")
                    ], width=6, className="mb-4")
                ]),

                # Segunda fila de gráficos - Histograma y Barras
                dbc.Row([
                    # Gráfico 3: Distribución (Histograma)
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader([
                                html.H4("Tendencia equipo", className="card-title fw-bold fs-4"),
                            ]),
                            dbc.CardBody([
                                # Gráfico
                                dcc.Loading(
                                    id="loading-grafico-histograma",
                                    type="circle",
                                    children=dcc.Graph(id='grafico-histograma', style={"height": "450px"})       
                                ),
                                # Selector de métrica debajo del gráfico
                                html.Div([
                                    html.Label("Métrica:", className="me-2 mt-2 fw-semibold fs-6"),
                                    dcc.Dropdown(
                                        id='metrica-histograma-dropdown',
                                        options=[{'label': format_stat_name(stat), 'value': stat} for stat in estadisticas],
                                        value='Gls' if 'Gls' in estadisticas else estadisticas[0],
                                        style={"width": "100%"}
                                    )
                                ])
                            ])
                        ], className="h-100")
                    ], width=6, className="mb-4"),
            
                    # Gráfico 4: Comparativa por jornada (Gráfico de barras)
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader([
                                html.H4("Participantes en partido", className="card-title fw-bold fs-4"),
                            ]),
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
                                        html.Label("Jornada:", className="me-2 mt-2 fw-semibold fs-6"),
                                        dcc.Dropdown(
                                            id='jornada-barras-dropdown',
                                            options=[{'label': f'Jornada {j}', 'value': j} for j in jornadas],
                                            value=1 if 1 in jornadas else jornadas[0],
                                        )
                                    ], width=6),
                                    dbc.Col([
                                        html.Label("Métrica:", className="me-2 mt-2 fw-semibold fs-6"),
                                        dcc.Dropdown(
                                            id='metrica-barras-dropdown',
                                            options=[{'label': format_stat_name(stat), 'value': stat} for stat in estadisticas],
                                            value='%_pases' if '%_pases' in estadisticas else estadisticas[0],
                                        )
                                    ], width=6)
                                ])
                            ])
                        ], className="h-100")
                    ], width=6, className="mb-4")
                ]),
                    
                # Fila final - Botón PDF y firma
                dbc.Row([
                    # Botón de exportar PDF
                    dbc.Col([
                        html.Div([
                            dcc.Download(id="descargar-pdf-stats"),
                            dbc.Button(
                                "Generar PDF",
                                id="exportar-pdf-btn-stats",
                                color="primary",
                                className="me-2"
                            ),
                            html.Span(id="pdf-status-stats", className="ms-2")                    
                        ], className="d-flex align-items-center")
                    ], width=6),
            
                    # Firma personal
                    dbc.Col([
                        html.Div([
                            html.P("Ramón González MPAD", className="text-end fw-bold fs-5")
                        ])
                    ], width=6)
                ], className="mt-4")
            ])
        ])
    except Exception as e:
        return html.Div([
            html.H1("Error al cargar los datos", className="text-center text-danger mb-4"),
            html.P(f"Detalles del error: {str(e)}", className="text-center")
        ])

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

# Jugadores predeterminados para mostrar al inicio
jugadores_predeterminados = ['Antoine Griezmann', 'Julián Álvarez', 'Pablo Barrios']

# Colores por posición - Trasladados desde data_viz.py
colores_por_posicion = {
    'GK': '#FFFF00',   # Amarillo para porteros
    'CB': '#1E88E5',   # Azul para defensas centrales
    'LB': '#42A5F5',   # Azul claro para laterales izquierdos
    'RB': '#90CAF9',   # Azul más claro para laterales derechos
    'WB': '#64B5F6',   # Otro azul para carrileros
    'CM': '#4CAF50',   # Verde para centrocampistas
    'AM': '#FF9800',   # Naranja para mediapuntas
    'LM': '#FFA726',   # Naranja claro para extremos izquierdos
    'RM': '#FFB74D',   # Naranja más claro para extremos derechos
    'FW': '#F44336'    # Rojo para delanteros
}

# Mapeo de jugadores a posiciones
jugadores_posiciones = {
    'Jan Oblak': 'GK',
    'Juan Musso': 'GK',
    'Robin Le Normand': 'CB',
    'José María Giménez': 'CB',
    'César Azpilicueta': 'CB',
    'Axel Witsel': 'CB',
    'Nahuel Molina': 'RB',
    'Reinildo Mandava': 'LB',
    'Rodrigo Riquelme': 'LB',
    'Koke': 'CM',
    'Rodrigo De Paul': 'CM',
    'Pablo Barrios': 'CM',
    'Conor Gallagher': 'CM',
    'Marcos Llorente': 'RM',
    'Antoine Griezmann': 'AM',
    'Ángel Correa': 'AM',
    'Samuel Lino': 'LM',
    'Giuliano Simeone': 'LM',
    'Julián Álvarez': 'FW',
    'Alexander Sørloth': 'FW'
}

# Crear colores para cada jugador basados en su posición
colores_jugadores = {}
for jugador, posicion in jugadores_posiciones.items():
    colores_jugadores[jugador] = colores_por_posicion.get(posicion, '#000000')