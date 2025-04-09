import dash
from dash.dependencies import Input, Output, State
from dash import html, dcc
import pandas as pd
from utils.data_viz import format_stat_name, crear_grafico_linea, crear_grafico_barras, crear_grafico_histograma, crear_grafico_scatter
from utils.pdf_export import exportar_pdf, exportar_pdf_stats
from layouts.player_stats_layout import colores_jugadores, colores_por_posicion

def register_player_stats_callbacks(app):
    """
    Registra los callbacks para la página de estadísticas de jugadores
    """
    try:
        # Cargar datos de jugadores
        df = pd.read_csv('data/players_atm_24_25.csv')
        
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
            [Input('jugadores-dropdown', 'value'),
             Input('metrica-evolucion-dropdown', 'value')]
        )
        def actualizar_grafico_linea(jugadores_seleccionados, metrica):
            rango_jornadas = [df['Jornada'].min(), df['Jornada'].max()]
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
            [Input('metrica-histograma-dropdown', 'value')]
        )
        def actualizar_grafico_histograma(metrica):
            rango_jornadas = [df['Jornada'].min(), df['Jornada'].max()]
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
        
        # Callback para exportar PDF de estadísticas
        @app.callback(
            [Output('descargar-pdf-stats', 'data'),
            Output('pdf-status-stats', 'children')],
            [Input('exportar-pdf-btn-stats', 'n_clicks')],
            [State('jugadores-dropdown', 'value'),
            State('grafico-linea', 'figure'),
            State('grafico-scatter', 'figure'),
            State('grafico-barras', 'figure'),
            State('grafico-histograma', 'figure')],
            prevent_initial_call=True
        )
        def exportar_pdf_estadisticas(n_clicks, jugadores, figura_linea, figura_scatter, figura_barras, figura_histograma):
            if not n_clicks:
                return None, ""
            
            try:
                # Definir el rango de jornadas dentro de la función
                rango_jornadas = [df['Jornada'].min(), df['Jornada'].max()]

                # Usar directamente las figuras actuales que se muestran en la interfaz
                graficos = [figura_linea, figura_scatter, figura_barras, figura_histograma]
                
                # Exportar PDF
                pdf_bytes = exportar_pdf_stats(n_clicks, graficos, jugadores, rango_jornadas)
                if pdf_bytes:
                    return pdf_bytes, html.Span("¡PDF generado!", className="ms-2 fw-bold", style={"color": "#4CAF50"})
                else:
                    return None, html.Span("Error generando PDF", className="ms-2 fw-bold", style={"color": "#FF0000"})
            
            except Exception as e:
                print(f"Error al exportar PDF: {str(e)}")
                return None, html.Span(f"Error: {str(e)}", className="ms-2 fw-bold", style={"color": "#FF0000"})
                                    
    except Exception as e:
        print(f"Error al registrar callbacks de estadísticas: {str(e)}")
        import traceback
        traceback.print_exc()