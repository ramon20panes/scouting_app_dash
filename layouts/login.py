# login.py
import dash_bootstrap_components as dbc
from dash import html, dcc

def create_login_layout():
    """
    Crea el layout de la página de login
    """
    return dbc.Container(
        [
            dbc.Row(
                dbc.Col(
                    html.Img(
                        src="/assets/escudos/atm.png",
                        style={"maxHeight": "120px"},
                        className="mx-auto d-block mt-5 mb-3"
                    ),
                    width={"size": 6, "offset": 3},
                    md={"size": 4, "offset": 4},
                )
            ),
            dbc.Row(
                dbc.Col(
                    html.H2("Club Atlético de Madrid", 
                           className="text-center",
                           style={"color": "#D81E05"}),
                    width={"size": 6, "offset": 3},
                    md={"size": 4, "offset": 4},
                )
            ),
            dbc.Row(
                dbc.Col(
                    html.H4("Área primera plantilla", 
                           className="text-center mb-4",
                           style={"color": "#262E62"}),
                    width={"size": 6, "offset": 3},
                    md={"size": 4, "offset": 4},
                )
            ),
            dbc.Row(
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.Div(
                                    [
                                        dbc.Label("Usuario"),
                                        dbc.InputGroup([
                                            dbc.Input(
                                                id="login-username",
                                                type="text",
                                                placeholder="Ingresa tu usuario",
                                                className="mb-1"
                                            ),
                                            dbc.InputGroupText(
                                                html.I(className="fas fa-check-circle text-success"),
                                                id="username-check",
                                                style={"display": "none"}
                                            ),
                                        ]),
                                        dbc.FormText(
                                            id="username-feedback",
                                            className="mb-3",
                                        ),
                                        
                                        dbc.Label("Contraseña"),
                                        dbc.InputGroup([
                                            dbc.Input(
                                                id="login-password",
                                                type="password",
                                                placeholder="Ingresa tu contraseña",
                                                className="mb-1"
                                            ),
                                            dbc.InputGroupText(
                                                html.I(className="fas fa-check-circle text-success"),
                                                id="password-check",
                                                style={"display": "none"}
                                            ),
                                        ]),
                                        dbc.FormText(
                                            id="password-feedback",
                                            className="mb-3"
                                        ),
                                        
                                        dbc.Button(
                                            [
                                                "Login ",
                                                dbc.Spinner(
                                                    size="sm", 
                                                    id="login-spinner", 
                                                    color="light", 
                                                    spinner_style={"display": "none"}  
                                                )
                                            ],
                                            id="login-button",
                                            color="primary",
                                            className="w-100 mb-3",
                                            style={"backgroundColor": "#D81E05", 
                                                   "borderColor": "#D81E05"}
                                        ),
                                        
                                        dbc.Alert(
                                            id="login-error",
                                            color="danger",
                                            is_open=False,
                                            dismissable=True,
                                            className="mt-3 mb-0"
                                        ),
                                        
                                        dbc.Alert(
                                            [
                                                html.I(className="fas fa-check-circle me-2"),
                                                "Acceso correcto. Redirigiendo..."
                                            ],
                                            id="login-success",
                                            color="success",
                                            is_open=False,
                                            className="mt-3 mb-0"
                                        ),
                                    ]
                                )
                            ]
                        ),
                        style={"boxShadow": "0 4px 8px rgba(0, 0, 0, 0.1)"}
                    ),
                    width={"size": 6, "offset": 3},
                    md={"size": 4, "offset": 4},
                )
            ),
            dbc.Row(
                dbc.Col(
                    html.P("Acceso restringido", 
                          className="text-center mt-3 text-muted small"),
                    width={"size": 6, "offset": 3},
                    md={"size": 4, "offset": 4},
                )
            ),
            # Este es un componente oculto para las redirecciones
            dcc.Location(id="login-redirect", refresh=True)
        ],
        fluid=True,
        className="login-container"
    )