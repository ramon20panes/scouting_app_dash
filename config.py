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
        "accent": "#FFFFFF",     # Blanco
        "text_primary": "#001F3F",  # Color principal de texto (azul)
        "text_secondary": "#6c757d",  # Color secundario de texto
        "text_titles": "#00346B",  # Color para títulos
        "text_labels": "#001F3F"  # Color para etiquetas
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

# Estilos reusables para componentes
GRAPH_STYLE = {
  'height': '300px',
  'width': '100%',
  'minWidth': '300px'
}

# Configuración de la base de datos
DB_CONFIG = {
    "db_path": os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "atm_login.db")
}