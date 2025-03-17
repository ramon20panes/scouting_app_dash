# callbacks/navbar_callbacks.py
from dash.dependencies import Input, Output, State

def register_navbar_callbacks(app):
    """
    Registra los callbacks relacionados con la barra de navegación
    """
    @app.callback(
        Output("navbar-collapse", "is_open"),
        [Input("navbar-toggler", "n_clicks")],
        [State("navbar-collapse", "is_open")],
    )
    def toggle_navbar_collapse(n, is_open):
        if n:
            return not is_open
        return is_open