# layouts/player_stats_layout.py
import dash_bootstrap_components as dbc
from dash import html
from utils.data_viz import create_player_stats_layout, load_team_data
from utils.auth import protect_route
from flask_login import current_user

@protect_route(['view_team', 'view_all'])
def player_stats_layout():
    """
    Layout para el dashboard de estadísticas de jugadores
    """
    try:
        # Cargar datos de jugadores
        df = load_team_data('data/ATM_24_25.csv')
        
        return html.Div([
            html.H1("Dashboard estadísticas partido", className="text-center mb-4"),
            html.Hr(),
            create_player_stats_layout(df)
        ])
    except Exception as e:
        return html.Div([
            html.H1("Error al cargar los datos", className="text-center text-danger mb-4"),
            html.P(f"Detalles del error: {str(e)}", className="text-center")
        ])