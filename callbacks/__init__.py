# callbacks/__init__.py
from callbacks.auth_callbacks import register_auth_callbacks
from callbacks.player_stats_callbacks import register_player_stats_callbacks
from callbacks.navbar_callbacks import register_navbar_callbacks

def register_callbacks(app):
    """
    Registra todos los callbacks de la aplicación
    """
    register_auth_callbacks(app)
    register_player_stats_callbacks(app)
    register_navbar_callbacks(app)