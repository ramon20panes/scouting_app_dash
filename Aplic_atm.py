# Aplic_atm.py (modificación para incluir navegación y nuevas páginas)
import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from flask_login import LoginManager, current_user
import flask

from layouts.login import create_login_layout
from layouts.player_stats_layout import player_stats_layout  # Importar la nueva página
from utils.auth import User, load_user
from utils.db import init_db
from callbacks import register_callbacks
from config import CONFIG
from components.navbar import create_navbar  # Asegúrate de crear este componente

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
                            dbc.CardBody([
                                html.H4("Dashboard de Rendimiento", className="card-title"),
                                html.P("Estadísticas por jugador", className="card-text"),
                                dbc.Button("Ver estadísticas", href="/player-stats", color="primary")
                            ])
                        ])
                    ], width=12, md=6, className="mb-4"),
                    
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H4("Datos Físicos", className="card-title"),
                                html.P("Datos condicionales por jugador", className="card-text"),
                                dbc.Button("Ver datos condicionales", href="/physical-data", color="primary")
                            ])
                        ])
                    ], width=12, md=6, className="mb-4")
                ], className="mt-4")
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
        # Esta página la implementaremos después
        return html.Div([
            create_navbar(),
            html.Div([
                html.H1("Datos condicionales", className="text-center mb-4"),
                html.P("Esta página está en desarrollo.", className="text-center")
            ], className="container")
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