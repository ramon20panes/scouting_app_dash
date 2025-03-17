# config.py
import os

# Configuración de la aplicación

CONFIG = {
    "app_name": "Atlético de Madrid - Dashboard Deportivo",
    "team_colors": {
        "primary": "#001F3F",    # Azul oscuro Atleti 
        "secondary": "#D81E05",  # Rojo Atleti
        "background": "#E6E6E6", # Gris fondo
        "background_secondary": "#D3D3D3", # Gris secundario
        "accent": "#FFFFFF"      # Blanco
    }
}

# Roles y permisos de usuarios
ROLES = {
    'admin': {
        'permissions': ['view_all', 'edit_all']
    },
    'coach': {
        'permissions': ['view_team', 'edit_team']
    },
    'medical': {
        'permissions': ['view_medical', 'edit_medical']
    },
    'player': {
        'permissions': ['view_own_stats', 'view_team']
    }
}

# Configuración de la base de datos
DB_CONFIG = {
    "db_path": os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "atm_login.db")
}