# callbacks/player_stats_callbacks.py
from utils.data_viz import create_player_callbacks, load_team_data

def register_player_stats_callbacks(app):
    """
    Registra los callbacks para la página de estadísticas de jugadores
    """
    try:
        # Cargar datos de jugadores
        df = load_team_data('data/ATM_24_25.csv')
        
        # Registrar callbacks para gráficos y filtros
        create_player_callbacks(app, df)
    except Exception as e:
        print(f"Error al registrar callbacks: {str(e)}")