import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, dash_table
import pandas as pd
import sqlite3
import os
import unicodedata
from utils.auth import protect_route
from flask_login import current_user
from utils.pdf_export import exportar_pdf
from config import CONFIG

@protect_route(['view_team', 'view_all'])
def physical_data_layout():
    """
    Layout para el dashboard de datos físicos/condicionales de jugadores
    """
    try:
        # Función para normalizar nombres
        def normalize_name(name):
            if not name:
                return ""
            return ' '.join(unicodedata.normalize('NFKD', str(name).lower())
                            .encode('ASCII', 'ignore')
                            .decode('ASCII')
                            .split())
        
        # Verificar qué columnas tenemos en el archivo maestro
        if os.path.exists('data/jugadores_master.csv'):
            # Leer con el separador correcto (punto y coma)
            jugadores_master = pd.read_csv('data/jugadores_master.csv', sep=';')
        else:
            # Crear archivo maestro con los datos proporcionados
            jugadores_master = pd.DataFrame({...})
            # Guardar con separador punto y coma
            jugadores_master.to_csv('data/jugadores_master.csv', sep=';', index=False)
        
        # Conectar a la base de datos de datos condicionales
        db_path = 'data/ATM_condic_24_25.db'
        if not os.path.exists(db_path):
            
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
        
        # Verificar si existe la tabla datos_fisicos
        if 'datos_fisicos' not in tables_list:
            conn.close()
            return html.Div([
                html.H1("Error: Tabla no encontrada", className="text-center text-danger mb-4"),
                html.P(f"No se encontró la tabla 'datos_fisicos' en la base de datos", className="text-center")
            ])
        
        # Obtener lista de jugadores que tienen datos condicionales
        jugadores_con_datos = pd.read_sql("SELECT DISTINCT Nombre FROM datos_fisicos", conn)
        
        # Obtener las métricas disponibles en la base de datos
        metricas_query = """
        SELECT name FROM pragma_table_info('datos_fisicos')
        WHERE name NOT IN ('id', 'Jornada', 'Nombre', 'Posicion', 'Min', 'Edad')
        """
        metricas_df = pd.read_sql(metricas_query, conn)
        metricas_fisicas = metricas_df['name'].tolist()
        
        # Cargar datos de los jugadores
        jugadores_db = pd.read_sql("SELECT DISTINCT Nombre as nombre, Posicion as posicion, Edad as edad FROM datos_fisicos", conn)
        conn.close()
        
        # Cargar o crear archivo maestro
        if os.path.exists('data/jugadores_master.csv'):
            jugadores_master = pd.read_csv('data/jugadores_master.csv')

        else:
            # Crear archivo maestro con los datos proporcionados
            jugadores_master = pd.DataFrame({
                'nombre_completo': [
                    'Juan Musso', 'José María Giménez', 'César Azpilicueta', 'Conor Gallagher', 
                    'Rodrigo De Paul', 'Koke', 'Antoine Griezmann', 'Pablo Barrios', 
                    'Alexander Sørloth', 'Ángel Correa', 'Thomas Lemar', 'Samuel Lino', 
                    'Jan Oblak', 'Marcos Llorente', 'Clément Lenglet', 'Nahuel Molina', 
                    'Rodrigo Riquelme', 'Julián Álvarez', 'Axel Witsel', 'Javi Galán', 
                    'Giuliano Simeone', 'Reinildo Mandava', 'Robin Le Normand', 'Adrián Niño'
                ],
                'short_name': [
                    'Musso', 'Giménez', 'Azpilcueta', 'Gallagher', 'De Paul', 'Koke', 
                    'Griezmann', 'Barrios', 'Sorloth', 'Correa', 'Lemar', 'Lino', 
                    'Oblak', 'Llorente', 'Lenglet', 'Molina', 'Riquelme', 'Julián', 
                    'Witsel', 'Galán', 'Giuliano', 'Reinildo', 'Le Normand', 'Niño'
                ],
                'id_sofascore': [
                    263651, 325355, 21555, 904970, 249399, 84539, 85859, 1142588, 
                    309078, 316152, 191182, 874705, 69768, 353138, 580550, 831799, 
                    989113, 944656, 35612, 825133, 1099352, 831424, 787751, 1402927
                ],
                'pais': ['ARG', 'URY', 'ESP', 'ENG', 'ARG', 'ESP', 'FRA', 'ESP', 
                       'NOR', 'ARG', 'FRA', 'BRA', 'SVN', 'ESP', 'FRA', 'ARG', 
                       'ESP', 'ARG', 'BEL', 'ESP', 'ARG', 'MOZ', 'FRA', 'ESP']
            })
            
            # Añadir rutas de fotos
            jugadores_master['ruta_foto'] = [f'/assets/players/{i}.png' for i in range(1, 25)]
            
            # Guardar archivo
            os.makedirs('data', exist_ok=True)
            jugadores_master.to_csv('data/jugadores_master.csv', index=False)
        
        # Crear diccionario para mapear nombres
        # Normalizar nombres para comparación
        nombre_dict = {}
        for _, row in jugadores_master.iterrows():
            # Verificar si 'short_name' existe en la columna antes de acceder a ella
            if 'short_name' in jugadores_master.columns:
                nombre_db_norm = normalize_name(str(row['short_name']))
                nombre_dict[nombre_db_norm] = {
                    'nombre_completo': row['nombre_completo'] if 'nombre_completo' in jugadores_master.columns else '',
                    'id_sofascore': row['id_sofascore'] if 'id_sofascore' in jugadores_master.columns else None,
                    'ruta_foto': row['ruta_foto'] if 'ruta_foto' in jugadores_master.columns else None,
                    'pais': row['pais'] if 'pais' in jugadores_master.columns else 'ESP'
                }
        
        # Crear opciones para el dropdown
        options = []
        default_value = None
        unique_values = set()
        
        # Crear opciones para el dropdown
        for _, row in jugadores_db.iterrows():
            nombre_original = row['nombre']

            # Omitir si ya hemos procesado este nombre
            if nombre_original in unique_values:
                continue
    
            unique_values.add(nombre_original)
    
            # Intentar corregir caracteres especiales
            try:
                nombre_mostrar = nombre_original.encode('latin1').decode('utf-8')
            except:
                nombre_mostrar = nombre_original
        
            options.append({'label': nombre_mostrar, 'value': nombre_original})
    
            # Si es Julián Álvarez, establecer como valor por defecto
            if 'julian' in normalize_name(nombre_mostrar):
                default_value = nombre_original
        
        # Si no se encontró Julián Álvarez, usar el primer jugador
        if not default_value and options:
            default_value = options[0]['value']
        
        # Ordenar alfabéticamente
        options.sort(key=lambda x: x['label'])
        
        # Crear dropdown de selección de jugador
        jugador_dropdown = dcc.Dropdown(
            id='jugador-fisico-dropdown',
            options=options,
            value=default_value,
            clearable=False,
            style={'width': '100%'},
            className='mb-3'
        )        
        # Dropdown para métricas del gráfico de barras
        default_metricas_barras = ['Distancia', 'Max_Speed', 'Sprints_Abs_Cnt']
        dropdown_metricas_barras = dcc.Dropdown(
            id='metricas-barras-dropdown',
            options=[{'label': metric.replace('_', ' ').title(), 'value': metric} 
                   for metric in metricas_fisicas],
            value=[m for m in default_metricas_barras if m in metricas_fisicas],
            multi=True,
            clearable=False,
            style={'width': '100%'},
            className='mb-2'
        )        
        # Dropdown para métricas del radar chart (preseleccionar 5)
        default_metricas_radar = ['Distancia', 'Max_Speed', 'Sprints_Abs_Cnt', 'Aceleraciones', 'Deceleraciones']
        dropdown_radar = dcc.Dropdown(
            id='metricas-radar-checklist',  # Mantener el mismo ID para compatibilidad
            options=[{'label': metric.replace('_', ' ').title(), 'value': metric} 
                for metric in metricas_fisicas],
            value=[m for m in default_metricas_radar if m in metricas_fisicas],
            multi=True,
            placeholder="Selecciona métricas (hasta 8)",
            style={'width': '100%'},
            className='mb-2'
        )        
        # Dropdown para eje X del scatter
        dropdown_scatter_x = dcc.Dropdown(
            id='scatter-x-dropdown',
            options=[{'label': metric.replace('_', ' ').title(), 'value': metric} 
                   for metric in metricas_fisicas],
            value='Distancia' if 'Distancia' in metricas_fisicas else metricas_fisicas[0] if metricas_fisicas else None,
            clearable=False,
            style={'width': '100%'},
            className='mb-2'
        )        
        # Dropdown para eje Y del scatter
        dropdown_scatter_y = dcc.Dropdown(
            id='scatter-y-dropdown',
            options=[{'label': metric.replace('_', ' ').title(), 'value': metric} 
                   for metric in metricas_fisicas],
            value='Max_Speed' if 'Max_Speed' in metricas_fisicas else metricas_fisicas[1] if len(metricas_fisicas) > 1 else metricas_fisicas[0] if metricas_fisicas else None,
            clearable=False,
            style={'width': '100%'},
            className='mb-2'
        )        
        # Dropdown para bubble size
        dropdown_scatter_size = dcc.Dropdown(
            id='scatter-size-dropdown',
            options=[{'label': metric.replace('_', ' ').title(), 'value': metric} 
                   for metric in metricas_fisicas],
            value='Sprints_Abs_Cnt' if 'Sprints_Abs_Cnt' in metricas_fisicas else metricas_fisicas[2] if len(metricas_fisicas) > 2 else metricas_fisicas[0] if metricas_fisicas else None,
            clearable=False,
            style={'width': '100%'},
            className='mb-2'
        )     
        # Corrección del final del archivo
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
                            html.H4("Evolución por Jornadas", className="card-title"),
                            html.Label("Selecciona métricas (hasta 3):", className="mt-2"),
                            dropdown_metricas_barras
                        ]),
                        dbc.CardBody([
                            dcc.Graph(id="grafico-barras-fisico")
                        ])
                    ])
                ], md=6, className="mb-4")
            ]),            

            # Segunda fila: DataTable (ocupa todo el ancho)
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H4("Datos por Jornada", className="card-title"),
                            html.Label("Selecciona métricas:", className="mt-2"),
                            dcc.Dropdown(
                                id='metricas-table-dropdown',
                                options=[{'label': metric.replace('_', ' ').title(), 'value': metric} 
                                    for metric in metricas_fisicas],
                                value=['Distancia', 'Max_Speed', 'Sprints_Abs_Cnt'] if all(m in metricas_fisicas for m in ['Distancia', 'Max_Speed', 'Sprints_Abs_Cnt']) else metricas_fisicas[:3] if len(metricas_fisicas) >= 3 else metricas_fisicas,
                                multi=True,
                                placeholder="Selecciona métricas para mostrar en la tabla",
                                style={'width': '100%'},
                                className='mb-2'
                            )
                        ]),
                        dbc.CardBody([
                            dash.dash_table.DataTable(
                                id='datos-fisicos-table',
                                style_table={
                                    'overflowX': 'auto',
                                    'maxHeight': '400px',
                                    'overflowY': 'auto'
                                },
                                style_header={
                                    'backgroundColor': CONFIG['team_colors']['primary'],
                                    'color': CONFIG['team_colors']['accent'],
                                    'fontWeight': 'bold',
                                    'textAlign': 'center',
                                    'border': '1px solid white'
                                },
                                style_cell={
                                    'textAlign': 'center',
                                    'padding': '10px',
                                    'backgroundColor': CONFIG['team_colors']['background'],
                                    'font-family': 'Arial, sans-serif'
                                },
                                style_data_conditional=[
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
                                ],
                                page_size=10,  
                                filter_action='none',
                                sort_action='native',
                                sort_mode='multi'
                            )
                        ])
                    ])
                ], width=12, className="mb-4")
            ]),

            # Tercera fila: Radar Chart y Scatter Plot
            dbc.Row([
                # Radar Chart
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H4("Perfil Condicional (Radar)", className="card-title"),
                            html.Label("Selecciona métricas (hasta 8):", className="mt-2"),
                            dropdown_radar
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
                            html.H4("Relación entre Variables", className="card-title"),
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
                        dcc.Download(id="descargar-pdf-physical"),
                        dbc.Button(
                            "Generar PDF",
                            id="exportar-pdf-btn-physical",
                            color="primary",
                            className="me-2"
                        ),
                        html.Span(id="pdf-status-physical", className="ms-2")
                    ], className="d-flex align-items-center")
                ], width=12)
            ]),
    
            # Div para almacenar datos intermedios
            dcc.Store(id='datos-jugador-store')
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