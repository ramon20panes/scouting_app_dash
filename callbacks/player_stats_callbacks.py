from utils.data_viz import load_team_data, create_player_callbacks
from dash.dependencies import Input, Output, State
from dash import html, dcc

def register_player_stats_callbacks(app):
    """
    Registra los callbacks para la página de estadísticas de jugadores
    """
    try:
        # Cargar datos de jugadores
        df = load_team_data('data/ATM_24_25.csv')
        
        # Obtener las funciones de callback sin registrarlas
        callbacks = create_player_callbacks(app, df)
        
        # Registrar cada callback manualmente
        @app.callback(
            Output('jugadores-dropdown', 'options'),
            [Input('posicion-dropdown', 'value')]
        )
        def actualizar_jugadores_dropdown(posicion_seleccionada):
            return callbacks['actualizar_jugadores_dropdown'](posicion_seleccionada)
        
        @app.callback(
            Output('grafico-linea', 'figure'),
            [Input('jornada-slider', 'value'),
             Input('jugadores-dropdown', 'value'),
             Input('metrica-evolucion-dropdown', 'value')]
        )
        def actualizar_grafico_linea(rango_jornadas, jugadores_seleccionados, metrica):
            return callbacks['actualizar_grafico_linea'](rango_jornadas, jugadores_seleccionados, metrica)
        
        @app.callback(
            Output('grafico-barras', 'figure'),
            [Input('jornada-barras-dropdown', 'value'),
             Input('metrica-barras-dropdown', 'value')]
        )
        def actualizar_grafico_barras(jornada_seleccionada, metrica):
            return callbacks['actualizar_grafico_barras'](jornada_seleccionada, metrica)
        
        @app.callback(
            Output('grafico-histograma', 'figure'),
            [Input('jornada-slider', 'value'),
             Input('metrica-histograma-dropdown', 'value')]
        )
        def actualizar_grafico_histograma(rango_jornadas, metrica):
            return callbacks['actualizar_grafico_histograma'](rango_jornadas, metrica)
        
        @app.callback(
            Output('grafico-scatter', 'figure'),
            [Input('jornada-scatter-dropdown', 'value'),
             Input('metrica-x-dropdown', 'value'),
             Input('metrica-y-dropdown', 'value')]
        )
        def actualizar_grafico_scatter(jornada_seleccionada, metrica_x, metrica_y):
            return callbacks['actualizar_grafico_scatter'](jornada_seleccionada, metrica_x, metrica_y)
        
        @app.callback(
            Output('descargar-pdf', 'data'),
            [Input('exportar-pdf-btn', 'n_clicks')],
            [State('jornada-slider', 'value'),
             State('metrica-evolucion-dropdown', 'value'),
             State('jugadores-dropdown', 'value')],
            prevent_initial_call=True
        )
        def exportar_pdf(n_clicks, rango_jornadas, estadistica, jugadores):
            return callbacks['exportar_pdf'](n_clicks, rango_jornadas, estadistica, jugadores)
        
        # Nuevo callback para actualizar el mensaje de estado del PDF
        @app.callback(
            Output('pdf-status', 'children'),
            [Input('exportar-pdf-btn', 'n_clicks')],
            prevent_initial_call=True
        )
        # Y en la función actualizar_pdf_status:
        def actualizar_pdf_status(n_clicks):
            if n_clicks:
                return html.Span("¡PDF generado con éxito!", 
                            className="ms-2 fw-bold", 
                            style={"color": "#4CAF50"})  # Color verde para confirmación
            return ""
            
    except Exception as e:
        print(f"Error al registrar callbacks: {str(e)}")