# Importación de bibliotecas

import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from flask_login import LoginManager, current_user
import flask

from layouts.login import create_login_layout
from layouts.player_stats_layout import player_stats_layout
from layouts.physical_data_layout import physical_data_layout
from layouts.player_stats_layout import load_team_data
from callbacks.player_stats_callbacks import register_player_stats_callbacks
from utils.auth import User, load_user
from utils.db import init_db
from callbacks import register_callbacks
from callbacks.physical_data_callbacks import register_physical_data_callbacks
from callbacks.player_stats_callbacks import register_player_stats_callbacks
from utils.heatmap_generator import generar_heatmap
from config import CONFIG
from components.navbar import create_navbar  

# Inicializar la base de datos
init_db()

# Inicializa la aplicación
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        'https://use.fontawesome.com/releases/v5.15.4/css/all.css'
    ],
    suppress_callback_exceptions=True,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)

server = app.server

# Configuración del servidor Flask
server.config.update(
    SECRET_KEY='una_clave_secreta_muy_larga_y_segura',
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax'
)

# Configuración de Flask-Login
login_manager = LoginManager()
login_manager.init_app(server)
login_manager.login_view = '/login'

@login_manager.user_loader
def load_user_callback(user_id):
    """
    Carga el usuario cuando Flask-Login lo necesita
    """
    return load_user(user_id)

# Endpoint para servir imágenes de heatmap de jugadores
@server.route('/heatmap/<id_sofascore>')
def serve_heatmap(id_sofascore):
    """Genera y sirve un heatmap para un jugador específico"""
    # Verificar autenticación
    if not current_user.is_authenticated:
        return "No autorizado", 401
    
    try:
        # Generar el heatmap
        heatmap_base64 = generar_heatmap(id_sofascore)
        # Devolver la imagen
        return flask.Response(
            f'<img src="data:image/png;base64,{heatmap_base64}" alt="Heatmap">',
            mimetype='text/html'
        )
    except Exception as e:
        print(f"Error al generar heatmap: {str(e)}")
        return f"Error al generar heatmap: {str(e)}", 500

# Layout base de la aplicación
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Location(id='logout-redirect', refresh=True),
    html.Div(id='page-content')
])

# Registro de callbacks
register_callbacks(app)

# Callback para manejar la navegación
@app.callback(
    dash.dependencies.Output('page-content', 'children'),
    [dash.dependencies.Input('url', 'pathname')]
)
def display_page(pathname):
    """
    Maneja la navegación entre páginas
    """
    if pathname == '/login' or pathname == '/':
        return create_login_layout()
        
    # Comprueba si el usuario está autenticado
    if not current_user.is_authenticated:
        return create_login_layout()
        
    # Aquí van las distintas páginas protegidas
    if pathname == '/dashboard' or pathname == '/home':
        return html.Div([
            create_navbar(),
            html.Div([
                html.H1(f"Bienvenido, {current_user.name}", className="text-center mb-4"),
                html.P("Selecciona una opción del menú para comenzar.", className="text-center mb-4"),
            
                # Tarjetas para navegar a las diferentes secciones
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            # Añadir imagen
                            html.Img(
                                src="/assets/imagenes/partido.jpg",  # Ruta a la imagen
                                className="card-img-top",
                                style={"height": "200px", "objectFit": "cover"}
                            ),
                            dbc.CardBody([
                                html.H4("Dashboard de Rendimiento", className="card-title"),
                                html.P("Comparativa", className="card-text"),
                                dbc.Button("Ver estadísticas", href="/player-stats", color="primary",
                                           style={"backgroundColor": CONFIG["team_colors"]["primary"]})
                            ])
                        ])
                    ], width=12, md=6, className="mb-4"),
                
                    dbc.Col([
                        dbc.Card([
                            # Añadir imagen
                            html.Img(
                                src="/assets/imagenes/entrenamiento.jpg",  # Ruta a la imagen
                                className="card-img-top",
                                style={"height": "200px", "objectFit": "cover"}
                            ),
                            dbc.CardBody([
                                html.H4("Datos Condicionales", className="card-title"),
                                html.P("Por jugador", className="card-text"),
                                dbc.Button("Ver parámetros", href="/physical-data", color="primary",
                                        style={"backgroundColor": CONFIG["team_colors"]["primary"]})
                            ])
                        ])
                    ], width=12, md=6, className="mb-4")
                ], className="mt-4"),

                # Añadir firma al final
                dbc.Row([
                    dbc.Col([
                        html.P("Ramón González MPAD", 
                               className="text-end fw-bold fs-5 mt-4 me-3", 
                               style={"color": CONFIG["team_colors"]["primary"]})
                    ], width=12)
                ])
            ], className="container")
        ])
    elif pathname == '/player-stats':
        return html.Div([
            create_navbar(),
            html.Div([
                player_stats_layout()
            ], className="container-fluid py-3")
        ])
    elif pathname == '/physical-data':
        return html.Div([
            create_navbar(),
            html.Div([
                physical_data_layout(),
                
                # Añadir firma al final
                dbc.Row([
                    dbc.Col([
                        html.P("Ramón González MPAD", 
                               className="text-end fw-bold fs-5 mt-4 me-3", 
                               style={"color": CONFIG["team_colors"]["primary"]})
                    ], width=12)
                ])
            ], className="container-fluid py-3")
        ])
        
    # Página 404
    return html.Div([
        create_navbar(),
        html.Div([
            html.H1("404 - Página no encontrada", className="text-center my-5"),
            dbc.Button("Volver al inicio", href="/dashboard", color="primary", className="d-block mx-auto")
        ], className="container")
    ])

# Iniciar el servidor
if __name__ == '__main__':
    app.run_server(debug=True)