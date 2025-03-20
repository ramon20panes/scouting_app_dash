import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from config import CONFIG

def format_stat_name(stat_name):
    """
    Formatea el nombre de la estadística para mostrar
    """
    return ' '.join(word.capitalize() for word in stat_name.split('_'))

def crear_grafico_linea(df, rango_jornadas, jugadores_seleccionados, metrica, colores_jugadores):
    """
    Crea un gráfico de línea para la evolución de métricas por jornada
    """
    if not jugadores_seleccionados or not metrica:
        return go.Figure()

    # Filtrar por rango de jornadas
    df_filtrado = df[(df['Jornada'] >= rango_jornadas[0]) & (df['Jornada'] <= rango_jornadas[1])]

    # Filtrar por jugadores seleccionados
    df_filtrado = df_filtrado[df_filtrado['Nombre'].isin(jugadores_seleccionados)]

    # Agrupar por jornada y jugador, calculando la media de la métrica
    df_agrupado = df_filtrado.groupby(['Jornada', 'Nombre'])[metrica].mean().reset_index()

    # Crear gráfico de línea con colores personalizados
    fig = go.Figure()

    for jugador in jugadores_seleccionados:
        if jugador in df_agrupado['Nombre'].values:
            df_jugador = df_agrupado[df_agrupado['Nombre'] == jugador]
            color = colores_jugadores.get(jugador, '#000000')  # Negro por defecto
        
            fig.add_trace(go.Scatter(
                x=df_jugador['Jornada'],
                y=df_jugador[metrica],
                mode='lines+markers',
                name=jugador,
                line=dict(color=color, width=3),
                marker=dict(color=color, size=8)
            ))

    # Personalizar gráfico
    fig.update_layout(
        title=f"{format_stat_name(metrica)} por Jornada",
        xaxis_title="Jornada",
        yaxis_title=format_stat_name(metrica),
        template='plotly_white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(
            tickmode='linear', 
            dtick=1,
            title_font=dict(color="#001F3F"),
            tickfont=dict(color="#001F3F"),
            gridcolor='rgba(0, 31, 63, 0.1)'
        ),
        yaxis=dict(
            title_font=dict(color="#001F3F"),
            tickfont=dict(color="#001F3F"),
            gridcolor='rgba(0, 31, 63, 0.1)'
        ),
        plot_bgcolor='rgba(240,240,240,0.5)',
        paper_bgcolor='#ffffff',
        font=dict(family="Arial, sans-serif", size=12, color="#001F3F")
    )

    return fig

def crear_grafico_barras(df, jornada_seleccionada, metrica):
    """
    Crea un gráfico de barras para una jornada específica
    """
    if not jornada_seleccionada or not metrica:
        return go.Figure()
    
    # Filtrar por jornada seleccionada
    df_filtrado = df[df['Jornada'] == jornada_seleccionada]
    
    # Ordenar por valor de métrica descendente
    df_filtrado = df_filtrado.sort_values(by=metrica, ascending=False)
    
    # Crear gráfico de barras
    fig = px.bar(
        df_filtrado, 
        x='Nombre', 
        y=metrica,
        color='Nombre',
        title=f"{format_stat_name(metrica)} - Jornada {jornada_seleccionada}",
        labels={'Nombre': 'Jugador', metrica: format_stat_name(metrica)}
    )
    
    # Personalizar gráfico
    fig.update_layout(
        template='plotly_white',
        showlegend=False,
        xaxis={
            'categoryorder':'total descending',
            'title_font': {'color': "#001F3F"},
            'tickfont': {'color': "#001F3F"},
            'gridcolor': 'rgba(0, 31, 63, 0.1)'
        },
        yaxis={
            'title_font': {'color': "#001F3F"},
            'tickfont': {'color': "#001F3F"},
            'gridcolor': 'rgba(0, 31, 63, 0.1)'
        },
        plot_bgcolor='rgba(240,240,240,0.5)',
        paper_bgcolor='#ffffff',
        font=dict(family="Arial, sans-serif", size=12, color="#001F3F")
    )
    
    return fig

def crear_grafico_histograma(df, rango_jornadas, metrica):
    """
    Crea un gráfico de barras con línea de tendencia para un rango de jornadas
    """
    if not metrica:
        return go.Figure()

    # Filtrar por rango de jornadas
    df_filtrado = df[(df['Jornada'] >= rango_jornadas[0]) & (df['Jornada'] <= rango_jornadas[1])]

    # Calcular promedio de la métrica por jornada
    df_agrupado = df_filtrado.groupby('Jornada')[metrica].mean().reset_index()

    # Crear gráfico de barras con línea
    fig = px.bar(
        df_agrupado, 
        x='Jornada', 
        y=metrica,
        title=f"Evolución de {format_stat_name(metrica)} por Jornada",
        labels={'Jornada': 'Jornada', metrica: format_stat_name(metrica)},
        color_discrete_sequence=[CONFIG["team_colors"]["primary"]]
    )

    # Añadir línea de tendencia
    fig.add_scatter(
        x=df_agrupado['Jornada'], 
        y=df_agrupado[metrica], 
        mode='lines', 
        name='Tendencia',
        line=dict(color=CONFIG["team_colors"]["secondary"], width=3)
    )

    # Personalizar gráfico
    fig.update_layout(
        template='plotly_white',
        bargap=0.3,
        xaxis=dict(
            tickmode='linear', 
            dtick=1,
            title_font=dict(color="#001F3F"),
            tickfont=dict(color="#001F3F"),
            gridcolor='rgba(0, 31, 63, 0.1)'
        ),
        yaxis=dict(
            title_font=dict(color="#001F3F"),
            tickfont=dict(color="#001F3F"),
            gridcolor='rgba(0, 31, 63, 0.1)'
        ),
        plot_bgcolor='rgba(240,240,240,0.5)',
        paper_bgcolor='#ffffff',
        font=dict(family="Arial, sans-serif", size=12, color="#001F3F")
    )

    return fig

def crear_grafico_scatter(df, jornada_seleccionada, metrica_x, metrica_y, colores_por_posicion):
    """
    Crea un scatter plot para comparar dos métricas en una jornada específica
    """
    if not jornada_seleccionada or not metrica_x or not metrica_y:
        return go.Figure()

    # Filtrar por jornada seleccionada
    df_filtrado = df[df['Jornada'] == jornada_seleccionada]

    # Crear scatter plot con colores por posición
    fig = go.Figure()

    # Agrupar por posición para la leyenda
    posiciones_unicas = df_filtrado['Posicion'].unique()

    for posicion in posiciones_unicas:
        df_pos = df_filtrado[df_filtrado['Posicion'] == posicion]
        color = colores_por_posicion.get(posicion, '#000000')  # Negro por defecto
    
        fig.add_trace(go.Scatter(
            x=df_pos[metrica_x],
            y=df_pos[metrica_y],
            mode='markers+text',
            name=posicion,
            text=df_pos['Nombre'],
            textposition='top center',
            marker=dict(color=color, size=12),
            textfont=dict(size=10, color="#001F3F")
        ))

    # Personalizar gráfico
    fig.update_layout(
        title=f"{format_stat_name(metrica_x)} vs {format_stat_name(metrica_y)} - Jornada {jornada_seleccionada}",
        xaxis_title=format_stat_name(metrica_x),
        yaxis_title=format_stat_name(metrica_y),
        template='plotly_white',
        xaxis=dict(
            title_font=dict(color="#001F3F"),
            tickfont=dict(color="#001F3F"),
            gridcolor='rgba(0, 31, 63, 0.1)'
        ),
        yaxis=dict(
            title_font=dict(color="#001F3F"),
            tickfont=dict(color="#001F3F"),
            gridcolor='rgba(0, 31, 63, 0.1)'
        ),
        plot_bgcolor='rgba(240,240,240,0.5)',
        paper_bgcolor='#ffffff',
        font=dict(family="Arial, sans-serif", size=12, color="#001F3F"),
        margin=dict(l=80, r=80, t=100, b=80),
        height=450,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    # Ampliar el rango del gráfico para que quepan las etiquetas
    x_min = df_filtrado[metrica_x].min() * 0.7 if df_filtrado[metrica_x].min() > 0 else df_filtrado[metrica_x].min() * 1.3
    x_max = df_filtrado[metrica_x].max() * 1.3
    y_min = df_filtrado[metrica_y].min() * 0.7 if df_filtrado[metrica_y].min() > 0 else df_filtrado[metrica_y].min() * 1.3
    y_max = df_filtrado[metrica_y].max() * 1.3

    fig.update_xaxes(range=[x_min, x_max])
    fig.update_yaxes(range=[y_min, y_max])

    return fig