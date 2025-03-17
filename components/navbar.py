# components/navbar.py
import dash_bootstrap_components as dbc
from dash import html
from flask_login import current_user

def create_navbar():
    """
    Crea la barra de navegación con enlaces a diferentes páginas
    """
    # Determinar qué elementos mostrar según el rol del usuario
    nav_items = [
        dbc.NavItem(dbc.NavLink("Inicio", href="/dashboard")),
        dbc.NavItem(dbc.NavLink("Estadísticas", href="/player-stats")),
        dbc.NavItem(dbc.NavLink("Datos Condicionales", href="/physical-data")),
    ]
    
    # Nombre del usuario y enlace de cierre de sesión
    user_nav = [
        dbc.NavItem(dbc.NavLink("Cerrar sesión", href="#", id="logout-button")),
    ]
    
    # Crear la barra de navegación
    navbar = dbc.Navbar(
        dbc.Container(
            [
                # Logo y título
                html.A(
                    dbc.Row(
                        [
                            dbc.Col(html.Img(src="/assets/escudos/atm.png", height="40px")),
                            dbc.Col(dbc.NavbarBrand("Atlético de Madrid", className="ms-2")),
                        ],
                        align="center",
                        className="g-0",
                    ),
                    href="/dashboard",
                    style={"textDecoration": "none"},
                ),
                # Botón para toggle en móviles
                dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
                # Contenido colapsable
                dbc.Collapse(
                    [
                        dbc.Nav(nav_items, className="me-auto", navbar=True),
                        dbc.Nav(user_nav, navbar=True),
                    ],
                    id="navbar-collapse",
                    navbar=True,
                    is_open=False,
                ),
            ]
        ),
        color="#00008B",
        dark=True,
        className="mb-4",
    )
    
    return navbar