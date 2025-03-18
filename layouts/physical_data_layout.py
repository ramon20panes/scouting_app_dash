import dash_bootstrap_components as dbc
from dash import html, dcc
import pandas as pd
import sqlite3
import os
from utils.auth import protect_route
from flask_login import current_user

@protect_route(['view_team', 'view_all'])
def physical_data_layout():
    """
    Layout para el dashboard de datos físicos/condicionales de jugadores
    """
    try:
        # Verificar qué columnas tenemos en el archivo maestro
        if os.path.exists('data/jugadores_master.csv'):
            # Primero leer solo la primera fila para ver las columnas
            jugadores_df_headers = pd.read_csv('data/jugadores_master.csv', nrows=1)
            columns = jugadores_df_headers.columns.tolist()
            print(f"Columnas en jugadores_master.csv: {columns}")
            
            # Cargar el archivo completo
            jugadores_df = pd.read_csv('data/jugadores_master.csv')
            
            # Verificar si tenemos alguna columna de nombre que podamos usar
            # Y asignar un nombre de la mejor manera posible
            if 'nombre_completo' in columns:
                jugadores_df['nombre'] = jugadores_df['nombre_completo']
            elif 'short_name' in columns:
                jugadores_df['nombre'] = jugadores_df['short_name']
            else:
                # Buscar otras columnas que podrían contener nombres
                name_columns = [col for col in columns if 'name' in col.lower() or 'nombre' in col.lower()]
                if name_columns:
                    jugadores_df['nombre'] = jugadores_df[name_columns[0]]
                else:
                    # Si no hay columnas de nombre, usar id_unico o similar
                    id_columns = [col for col in columns if 'id' in col.lower()]
                    if id_columns:
                        jugadores_df['nombre'] = jugadores_df[id_columns[0]].astype(str)
                    else:
                        # Si todo falla, usamos el índice
                        jugadores_df['nombre'] = [f"Jugador {i+1}" for i in range(len(jugadores_df))]
        else:
            # El archivo no existe
            print("El archivo jugadores_master.csv no existe")
            jugadores_df = pd.DataFrame()
        
        # Conectar a la base de datos de datos condicionales
        db_path = 'data/ATM_condic_24_25.db'
        if not os.path.exists(db_path):
            print(f"Base de datos no encontrada en: {db_path}")
            return html.Div([
                html.H1("Error: Base de datos no encontrada", className="text-center text-danger mb-4"),
                html.P(f"No se encontró la base de datos en: {db_path}", className="text-center")
            ])
            
        conn = sqlite3.connect(db_path)
        
        # Verificar la estructura de la base de datos
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        tables_list = [table[0] for table in tables]
        print(f"Tablas en la base de datos: {tables_list}")
        
        # Verificar si existe la tabla datos_fisicos
        if 'datos_fisicos' not in tables_list:
            conn.close()
            return html.Div([
                html.H1("Error: Tabla no encontrada", className="text-center text-danger mb-4"),
                html.P(f"No se encontró la tabla 'datos_fisicos' en la base de datos", className="text-center")
            ])
        
        # Verificar las columnas de la tabla datos_fisicos
        cursor.execute("PRAGMA table_info(datos_fisicos);")
        columns_info = cursor.fetchall()
        column_names = [col[1] for col in columns_info]
        print(f"Columnas en la tabla datos_fisicos: {column_names}")
        
        # Obtener lista de jugadores que tienen datos condicionales
        jugadores_con_datos = pd.read_sql("SELECT DISTINCT Nombre FROM datos_fisicos", conn)
        
        # Obtener las métricas disponibles en la base de datos
        metricas_query = """
        SELECT name FROM pragma_table_info('datos_fisicos')
        WHERE name NOT IN ('id', 'Jornada', 'Nombre', 'Posicion', 'Min', 'Edad')
        """
        metricas_df = pd.read_sql(metricas_query, conn)
        metricas_fisicas = metricas_df['name'].tolist()
        
        conn.close()
        
        # Usaremos los datos directamente de la tabla datos_fisicos
        # Esto es más simple y evita problemas de coincidencia de nombres
        conn = sqlite3.connect('data/ATM_condic_24_25.db')
        jugadores_df = pd.read_sql("SELECT DISTINCT Nombre as nombre, Posicion as posicion FROM datos_fisicos", conn)
        conn.close()
        
        # Ordenar por nombre
        jugadores_df = jugadores_df.sort_values('nombre')

        # Eliminar duplicados antes de crear el dropdown
        jugadores_df = jugadores_df.drop_duplicates(subset=['nombre'])
        
        # Crear dropdown de selección de jugador
        jugador_dropdown = dcc.Dropdown(
            id='jugador-fisico-dropdown',
            options=[{'label': row['nombre'], 'value': row['nombre']} for _, row in jugadores_df.iterrows()],
            value=jugadores_df['nombre'].iloc[0] if not jugadores_df.empty else None,
            clearable=False,
            style={'width': '100%'},
            className='mb-3'
        )
        
        # Dropdown para seleccionar métricas para el gráfico de barras
        dropdown_metricas_barras = dcc.Dropdown(
            id='metricas-barras-dropdown',
            options=[{'label': metric.replace('_', ' ').title(), 'value': metric} 
                   for metric in metricas_fisicas],
            value=metricas_fisicas[:3] if len(metricas_fisicas) >= 3 else metricas_fisicas,  # Seleccionar las primeras 3 por defecto
            multi=True,
            clearable=False,
            style={'width': '100%'},
            className='mb-2'
        )
        
        # Checklist para las métricas del radar chart (hasta 8)
        checklist_radar = dbc.Checklist(
            id='metricas-radar-checklist',
            options=[{'label': metric.replace('_', ' ').title(), 'value': metric} 
                   for metric in metricas_fisicas],
            value=metricas_fisicas[:5] if len(metricas_fisicas) >= 5 else metricas_fisicas,  # Seleccionar las primeras 5 por defecto
            inline=True,
            className='mb-2'
        )
        
        # Dropdown para eje X del scatter
        dropdown_scatter_x = dcc.Dropdown(
            id='scatter-x-dropdown',
            options=[{'label': metric.replace('_', ' ').title(), 'value': metric} 
                   for metric in metricas_fisicas],
            value=metricas_fisicas[0] if metricas_fisicas else None,
            clearable=False,
            style={'width': '100%'},
            className='mb-2'
        )
        
        # Dropdown para eje Y del scatter
        dropdown_scatter_y = dcc.Dropdown(
            id='scatter-y-dropdown',
            options=[{'label': metric.replace('_', ' ').title(), 'value': metric} 
                   for metric in metricas_fisicas],
            value=metricas_fisicas[1] if len(metricas_fisicas) > 1 else metricas_fisicas[0] if metricas_fisicas else None,
            clearable=False,
            style={'width': '100%'},
            className='mb-2'
        )
        
        # Dropdown para bubble size (tamaño de burbujas) del scatter
        dropdown_scatter_size = dcc.Dropdown(
            id='scatter-size-dropdown',
            options=[{'label': metric.replace('_', ' ').title(), 'value': metric} 
                   for metric in metricas_fisicas],
            value=metricas_fisicas[2] if len(metricas_fisicas) > 2 else metricas_fisicas[0] if metricas_fisicas else None,
            clearable=False,
            style={'width': '100%'},
            className='mb-2'
        )
        
        return html.Div([
            html.H1("Datos Condicionales", className="text-center mb-4"),
            html.Hr(),
            
            # Selector de jugador
            dbc.Row([
                dbc.Col([
                    html.Label("Selecciona un jugador:", className="fw-bold"),
                    jugador_dropdown
                ], width=12, className="mb-4")
            ]),
            
            # Primera fila: Información del jugador y gráfico de barras
            dbc.Row([
                # Perfil del jugador y heatmap
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("Perfil del Jugador", className="card-title")),
                        dbc.CardBody([
                            html.Div(id="info-jugador-container"),
                            html.Div(id="heatmap-container", className="mt-3")
                        ])
                    ])
                ], md=6, className="mb-4"),
                
                # Gráfico de barras
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H5("Evolución por Jornadas", className="card-title"),
                            html.Label("Selecciona métricas (hasta 3):", className="mt-2"),
                            dropdown_metricas_barras
                        ]),
                        dbc.CardBody([
                            dcc.Graph(id="grafico-barras-fisico")
                        ])
                    ])
                ], md=6, className="mb-4")
            ]),
            
            # Segunda fila: Radar Chart y Scatter Plot
            dbc.Row([
                # Radar Chart
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H5("Perfil Condicional (Radar)", className="card-title"),
                            html.Label("Selecciona métricas (hasta 8):", className="mt-2"),
                            checklist_radar
                        ]),
                        dbc.CardBody([
                            dcc.Graph(id="grafico-radar-fisico")
                        ])
                    ])
                ], md=6, className="mb-4"),
                
                # Scatter/Bubble Chart
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H5("Relación entre Variables", className="card-title"),
                            dbc.Row([
                                dbc.Col([
                                    html.Label("Eje X:", className="mt-2"),
                                    dropdown_scatter_x
                                ], width=4),
                                dbc.Col([
                                    html.Label("Eje Y:", className="mt-2"),
                                    dropdown_scatter_y
                                ], width=4),
                                dbc.Col([
                                    html.Label("Tamaño:", className="mt-2"),
                                    dropdown_scatter_size
                                ], width=4)
                            ])
                        ]),
                        dbc.CardBody([
                            dcc.Graph(id="grafico-scatter-fisico")
                        ])
                    ])
                ], md=6, className="mb-4")
            ]),
            
            # Botón para exportar PDF
            dbc.Row([
                dbc.Col([
                    html.Div([
                        dbc.Button(
                            [html.I(className="fas fa-file-pdf me-2"), "Exportar PDF"],
                            id="exportar-pdf-fisico-btn",
                            color="danger",
                            className="me-2"
                        ),
                        html.Span(id="pdf-fisico-status")
                    ], className="d-flex align-items-center justify-content-end")
                ], width=12)
            ]),
            
            # Div para almacenar datos intermedios
            dcc.Store(id='datos-jugador-store'),
            
            # Descarga de PDF
            dcc.Download(id="descargar-pdf-fisico")
        ])
    except Exception as e:
        import traceback
        traceback_str = traceback.format_exc()
        return html.Div([
            html.H1("Error al cargar los datos", className="text-center text-danger mb-4"),
            html.P(f"Detalles del error: {str(e)}", className="text-center"),
            html.Details([
                html.Summary("Ver detalles técnicos"),
                html.Pre(traceback_str, style={"whiteSpace": "pre-wrap"})
            ], className="mt-3")
        ])