import dash
from dash.dependencies import Input, Output, State
from dash import html, dcc
import pandas as pd
from utils.data_viz import format_stat_name, crear_grafico_linea, crear_grafico_barras, crear_grafico_histograma, crear_grafico_scatter
from utils.pdf_export import exportar_pdf
from layouts.player_stats_layout import colores_jugadores, colores_por_posicion

def register_player_stats_callbacks(app):
    """
    Registra los callbacks para la página de estadísticas de jugadores
    """
    try:
        # Cargar datos de jugadores
        df = pd.read_csv('data/ATM_24_25.csv')
        
        # Callback para actualizar el dropdown de jugadores según la posición seleccionada
        @app.callback(
            Output('jugadores-dropdown', 'options'),
            [Input('posicion-dropdown', 'value')]
        )
        def actualizar_jugadores_dropdown(posicion_seleccionada):
            if posicion_seleccionada == 'TODAS':
                jugadores_filtrados = sorted(df['Nombre'].unique())
            else:
                jugadores_filtrados = sorted(df[df['Posicion'] == posicion_seleccionada]['Nombre'].unique())
            
            return [{'label': jugador, 'value': jugador} for jugador in jugadores_filtrados]
        
        # Callback para actualizar el gráfico de línea
        @app.callback(
            Output('grafico-linea', 'figure'),
            [Input('jornada-slider', 'value'),
             Input('jugadores-dropdown', 'value'),
             Input('metrica-evolucion-dropdown', 'value')]
        )
        def actualizar_grafico_linea(rango_jornadas, jugadores_seleccionados, metrica):
            return crear_grafico_linea(df, rango_jornadas, jugadores_seleccionados, metrica, colores_jugadores)
        
        # Callback para actualizar el gráfico de barras
        @app.callback(
            Output('grafico-barras', 'figure'),
            [Input('jornada-barras-dropdown', 'value'),
             Input('metrica-barras-dropdown', 'value')]
        )
        def actualizar_grafico_barras(jornada_seleccionada, metrica):
            return crear_grafico_barras(df, jornada_seleccionada, metrica)
        
        # Callback para actualizar el histograma
        @app.callback(
            Output('grafico-histograma', 'figure'),
            [Input('jornada-slider', 'value'),
             Input('metrica-histograma-dropdown', 'value')]
        )
        def actualizar_grafico_histograma(rango_jornadas, metrica):
            return crear_grafico_histograma(df, rango_jornadas, metrica)
        
        # Callback para actualizar el scatter plot
        @app.callback(
            Output('grafico-scatter', 'figure'),
            [Input('jornada-scatter-dropdown', 'value'),
             Input('metrica-x-dropdown', 'value'),
             Input('metrica-y-dropdown', 'value')]
        )
        def actualizar_grafico_scatter(jornada_seleccionada, metrica_x, metrica_y):
            return crear_grafico_scatter(df, jornada_seleccionada, metrica_x, metrica_y, colores_por_posicion)
        
        # Callback para exportar PDF
        @app.callback(
            [Output('descargar-pdf-stats', 'data'),
            Output('pdf-status-stats', 'children')],
            [Input('exportar-pdf-btn-stats', 'n_clicks')],
            [State('url', 'pathname'),
            State('jornada-slider', 'value'),
            State('metrica-evolucion-dropdown', 'value'),
            State('jugadores-dropdown', 'value')],
            prevent_initial_call=True
        )
        def exportar_pdf_player_stats(n_clicks, pathname, rango_jornadas, estadistica, jugadores):
            ctx = dash.callback_context
    
            if not ctx.triggered or not n_clicks or pathname != '/player-stats':
                return None, ""
    
            print(f"Generando PDF de estadísticas para: {jugadores}")
    
            # Genera los gráficos
            grafico_linea = crear_grafico_linea(df, rango_jornadas, jugadores, estadistica, colores_jugadores)
            grafico_scatter = crear_grafico_scatter(df, rango_jornadas[0], 'Num_toques', 'Pases_compl', colores_por_posicion)
            grafico_histograma = crear_grafico_histograma(df, rango_jornadas, estadistica)
            grafico_barras = crear_grafico_barras(df, rango_jornadas[0], estadistica)

            # Lista de gráficos
            graficos = [grafico_linea, grafico_scatter, grafico_histograma, grafico_barras]

            # Exportar PDF
            pdf_bytes = exportar_pdf(
                n_clicks, 
                graficos, 
                "Atlético de Madrid - Informe de Rendimiento", 
                estadistica, 
                rango_jornadas, 
                jugadores
            )

            return pdf_bytes, html.Span("¡PDF de Estadísticas generado!", 
                                className="ms-2 fw-bold", 
                                style={"color": "#4CAF50"})
        
    except Exception as e:
        print(f"Error al registrar callbacks de estadísticas: {str(e)}")
        import traceback
        traceback.print_exc()