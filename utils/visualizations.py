import plotly.graph_objects as go
from plotly.subplots import make_subplots

def create_gauge_with_trend(value, title, min_val, max_val, ranges, trend_data):
    """Crea un medidor semicircular con gráfico de tendencia"""
    # Crear figura con dos subplots: medidor arriba, tendencia abajo
    try:
        fig = make_subplots(
            rows=2, cols=1, 
            row_heights=[0.7, 0.3],
            specs=[[{"type": "indicator"}], [{"type": "scatter"}]],
            vertical_spacing=0.05  # Reducido para un diseño más compacto
        )
        
        # Configurar pasos del medidor según los rangos
        steps = []
        for start, end, color in ranges:
            steps.append(dict(range=[start, end], color=color))
        
        # Añadir el medidor principal
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=value,
                domain={'y': [0, 1], 'x': [0, 1]},
                title={'text': title, 'font': {'size': 16, 'color': 'white'}},
                gauge={
                    'axis': {
                        'range': [min_val, max_val], 
                        'tickwidth': 1, 
                        'tickcolor': "white",
                        'tickmode': 'array', 
                        'tickvals': [min_val, *[r[0] for r in ranges[1:]], max_val]
                    },
                    'bar': {'color': "white"},
                    'bgcolor': "rgba(50, 50, 50, 0.8)",
                    'borderwidth': 2,
                    'bordercolor': "gray",
                    'steps': steps,
                    'threshold': {
                        'line': {'color': "white", 'width': 4},
                        'thickness': 0.75,
                        'value': value
                    }
                },
                number={'font': {'size': 28, 'color': 'white'}, 'valueformat': ',d'}
            ),
            row=1, col=1
        )
        
        # Añadir gráfico de tendencia
        if trend_data and len(trend_data['x']) > 0:
            fig.add_trace(
                go.Scatter(
                    x=trend_data['x'],
                    y=trend_data['y'],
                    mode='lines+markers',
                    line=dict(color='red', width=2),  # Líneas rojas
                    marker=dict(size=5, color='red'),  # Puntos rojos
                    fill='tozeroy',
                    fillcolor='rgba(255, 0, 0, 0.1)'  # Relleno rojo transparente
                ),
                row=2, col=1
            )
        
        # Configuración del layout más compacto
        fig.update_layout(
            height=220,  # Reducida la altura para hacerlo más compacto
            margin=dict(l=5, r=5, t=10, b=5),  # Márgenes mínimos
            paper_bgcolor="rgba(30, 30, 30, 0.9)",
            plot_bgcolor="rgba(30, 30, 30, 0.9)",
            font=dict(color="white")
        )
        
        # Configurar ejes para la tendencia
        fig.update_xaxes(
            title_text="",  # Sin título para ahorrar espacio
            showgrid=True,
            gridcolor="rgba(255, 255, 255, 0.1)",
            tickfont=dict(size=8),  # Texto más pequeño
            row=2, col=1
        )
        
        fig.update_yaxes(
            showgrid=True,
            gridcolor="rgba(255, 255, 255, 0.1)",
            tickfont=dict(size=8),  # Texto más pequeño
            row=2, col=1
        )
        
        return fig
    except Exception as e:
        # En caso de error, devolver un gráfico simple
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=value,
            title={'text': title},
            gauge={'axis': {'range': [min_val, max_val]}}
        ))
        return fig

# Función especial para el medidor StO2 (más grande)
def create_sto2_gauge(value, title, min_val, max_val, ranges, trend_data):
    """Crea un medidor StO2 más grande con gráfico de tendencia"""
    try:
        # Similar a la función anterior pero con ajustes de tamaño
        fig = make_subplots(
            rows=2, cols=1, 
            row_heights=[0.7, 0.3],
            specs=[[{"type": "indicator"}], [{"type": "scatter"}]],
            vertical_spacing=0.05
        )
        
        steps = []
        for start, end, color in ranges:
            steps.append(dict(range=[start, end], color=color))
        
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=value,
                domain={'y': [0, 1], 'x': [0, 1]},
                title={'text': title, 'font': {'size': 20, 'color': 'white'}},
                gauge={
                    'axis': {
                        'range': [min_val, max_val], 
                        'tickwidth': 1, 
                        'tickcolor': "white",
                        'tickmode': 'array', 
                        'tickvals': [min_val, *[r[0] for r in ranges[1:]], max_val]
                    },
                    'bar': {'color': "white"},
                    'bgcolor': "rgba(50, 50, 50, 0.8)",
                    'borderwidth': 2,
                    'bordercolor': "gray",
                    'steps': steps,
                    'threshold': {
                        'line': {'color': "white", 'width': 4},
                        'thickness': 0.75,
                        'value': value
                    }
                },
                number={'font': {'size': 36, 'color': 'white'}, 'valueformat': ',d'}
            ),
            row=1, col=1
        )
        
        if trend_data and len(trend_data['x']) > 0:
            fig.add_trace(
                go.Scatter(
                    x=trend_data['x'],
                    y=trend_data['y'],
                    mode='lines+markers',
                    line=dict(color='red', width=2),
                    marker=dict(size=6, color='red'),
                    fill='tozeroy',
                    fillcolor='rgba(255, 0, 0, 0.1)'
                ),
                row=2, col=1
            )
        
        fig.update_layout(
            height=280,  # Más alto que los otros medidores
            margin=dict(l=5, r=5, t=10, b=5),
            paper_bgcolor="rgba(30, 30, 30, 0.9)",
            plot_bgcolor="rgba(30, 30, 30, 0.9)",
            font=dict(color="white")
        )
        
        fig.update_xaxes(
            title_text="",
            showgrid=True,
            gridcolor="rgba(255, 255, 255, 0.1)",
            tickfont=dict(size=10),
            row=2, col=1
        )
        
        fig.update_yaxes(
            showgrid=True,
            gridcolor="rgba(255, 255, 255, 0.1)",
            tickfont=dict(size=10),
            row=2, col=1
        )
        
        return fig
    except Exception as e:
        # En caso de error, devolver un gráfico simple
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=value,
            title={'text': title},
            gauge={'axis': {'range': [min_val, max_val]}}
        ))
        return fig

# Definir rangos de colores para cada parámetro
def get_map_ranges():
    return [
        (0, 65, "red"),
        (65, 70, "yellow"),
        (70, 100, "green"),
        (100, 140, "red")
    ]

def get_co_ranges():
    return [
        (0, 2.5, "red"),
        (2.5, 4.0, "yellow"),
        (4.0, 8.0, "green"),
        (8.0, 10, "red")
    ]

def get_svv_ranges():
    return [
        (0, 13, "green"),
        (13, 17, "yellow"),
        (17, 25, "red")
    ]

def get_pvv_ranges():
    return [
        (0, 12, "green"),
        (12, 15, "yellow"),
        (15, 25, "red")
    ]

def get_sto2_ranges():
    return [
        (0, 65, "red"),
        (65, 75, "orange"),
        (75, 85, "yellow"),
        (85, 100, "green")
    ]