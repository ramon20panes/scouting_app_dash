# utils/auth.py
from flask_login import UserMixin, current_user
from dash import html, dcc
import dash_bootstrap_components as dbc
from config import ROLES
from utils.db import get_user_by_id, init_db, check_user

# Inicializar la base de datos si es necesario
init_db()

class User(UserMixin):
    def __init__(self, user_data):
        self.id = user_data.get('username', '')
        self.name = user_data.get('name', '')
        self.role = user_data.get('role', '')
        self.permissions = ROLES.get(self.role, {}).get('permissions', [])
        self.player_id = user_data.get('player_id', None)
    
    def can_view_player_data(self, player_name=None, player_id=None):
        """
        Determina si el usuario puede ver los datos de un jugador específico
        
        Args:
            player_name: Nombre del jugador a verificar
            player_id: ID del jugador a verificar
        
        Returns:
            bool: True si tiene permiso, False en caso contrario
        """
        # Administradores siempre pueden ver todos los datos
        if self.role == 'admin' or 'view_all' in self.permissions:
            return True
            
        # Entrenadores pueden ver datos de todo el equipo
        if self.role == 'coach' or 'view_team' in self.permissions:
            return True
            
        # Para jugadores verificamos si son sus propios datos
        if self.role == 'player':
            # Si se proporciona un ID de jugador, verificar coincidencia
            if player_id is not None:
                return player_id == self.player_id
                
            # Si se proporciona un nombre, verificar si es el nombre del jugador
            if player_name is not None:
                # Normalizar nombres para comparación (quitar tildes, convertir a minúsculas)
                import unicodedata
                def normalize_name(name):
                    if not name:
                        return ""
                    return ' '.join(unicodedata.normalize('NFKD', str(name).lower())
                                    .encode('ASCII', 'ignore')
                                    .decode('ASCII')
                                    .split())
                
                user_name_normalized = normalize_name(self.name)
                player_name_normalized = normalize_name(player_name)
                
                # Verificar si el nombre normalizado del jugador contiene el nombre normalizado del usuario
                # o viceversa
                return (user_name_normalized in player_name_normalized or 
                        player_name_normalized in user_name_normalized)
            
            # Si no hay suficiente información para verificar, denegar por defecto
            return False
            
        # Para otros roles no especificados, denegar por defecto
        return False

def load_user(user_id):
    """
    Carga un usuario desde la base de datos por su ID (username)
    """
    user_data = get_user_by_id(user_id)
    if user_data:
        return User(user_data)
    return None

def authenticate_user(username, password):
    """
    Autentica al usuario verificando sus credenciales
    """
    user_data = check_user(username, password)
    if user_data:
        return User(user_data)
    return None

def check_user_permissions(required_permissions=None):
    """
    Comprueba si el usuario actual tiene los permisos requeridos
    """
    if not current_user.is_authenticated:
        return False
        
    if required_permissions is None:
        return True
        
    # Si es admin, tiene todos los permisos
    if 'admin' == current_user.role:
        return True
        
    # Comprueba si el usuario tiene alguno de los permisos requeridos
    for permission in required_permissions:
        if permission in current_user.permissions:
            return True
            
    return False

def protect_route(required_permissions=None):
    """
    Decorator para proteger rutas basadas en permisos
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                return dcc.Location(pathname='/login', id='redirect')
                
            if not check_user_permissions(required_permissions):
                return html.Div([
                    html.H1("Acceso Denegado", className="text-center"),
                    html.P("No tienes los permisos necesarios para acceder a esta página.", 
                           className="text-center"),
                    dbc.Button("Volver", href="/", color="primary", className="mx-auto d-block")
                ])
                
            return func(*args, **kwargs)
        return wrapper
    return decorator

def get_player_id_by_name(player_name):
    """
    Busca el ID de un jugador por su nombre en la base de datos
    
    Args:
        player_name: Nombre del jugador a buscar
    
    Returns:
        int: ID del jugador o None si no se encuentra
    """
    from utils.db import get_player_id_from_name
    return get_player_id_from_name(player_name)