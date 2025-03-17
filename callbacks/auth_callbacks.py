# auth_callbacks.py
from dash.dependencies import Input, Output, State
from flask_login import login_user, logout_user
from utils.auth import authenticate_user
import dash
from dash import dcc
import time

def register_auth_callbacks(app):
    """
    Registra los callbacks relacionados con la autenticación
    """
    @app.callback(
        [
            Output("login-redirect", "pathname"),
            Output("login-error", "children"),
            Output("login-error", "is_open"),
            Output("login-success", "is_open"),
            Output("login-spinner", "spinner_style"),
            Output("username-check", "style"),
            Output("password-check", "style"),
        ],
        [Input("login-button", "n_clicks")],
        [
            State("login-username", "value"), 
            State("login-password", "value")
        ],
        prevent_initial_call=True
    )
    def login_callback(n_clicks, username, password):
        """
        Maneja el proceso de login usando la base de datos
        """
        if n_clicks is None:
            return (
                dash.no_update, 
                dash.no_update,
                False,
                False, 
                {"display": "none"},
                {"display": "none"},
                {"display": "none"}
            )
            
        # Mostrar spinner mientras procesamos
        spinner_style = {"display": "inline-block"}
            
        if not username:
            return (
                dash.no_update,
                "Por favor ingresa un nombre de usuario",
                True,
                False,
                {"display": "none"},
                {"display": "none"},
                {"display": "none"}
            )
            
        if not password:
            return (
                dash.no_update,
                "Por favor ingresa tu contraseña",
                True,
                False,
                {"display": "none"},
                {"display": "none"},
                {"display": "none"}
            )
            
        # Autenticar usuario usando la base de datos
        user = authenticate_user(username, password)
        if user:
            # Inicia sesión
            login_user(user)
            # Muestra el check de éxito para ambos campos
            username_check = {"display": "block"}
            password_check = {"display": "block"}
            
            # Muestra alerta de éxito
            return (
                "/dashboard",
                "",
                False,
                True,
                {"display": "none"},
                username_check,
                password_check
            )
            
        return (
            dash.no_update,
            "Usuario o contraseña incorrectos",
            True,
            False,
            {"display": "none"},
            {"display": "none"},
            {"display": "none"}
        )

    @app.callback(
        Output("logout-redirect", "pathname"),
        [Input("logout-button", "n_clicks")],
        prevent_initial_call=True
    )
    def logout_callback(n_clicks):
        """
        Maneja el proceso de logout
        """
        if n_clicks:
            logout_user()
            return "/login"
        return dash.no_update