import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os

# Configuración de la página
st.set_page_config(
    page_title="ROSphere Monitor - Simple",
    page_icon="🫀",
    layout="wide"
)

# Título
st.title("ROSphere Monitor - Versión Simple")
st.caption("Versión simplificada para diagnóstico")

# Verificar estructura de archivos
st.sidebar.header("Información del Sistema")
st.sidebar.write(f"Directorio actual: {os.getcwd()}")
st.sidebar.write(f"Contenido del directorio:")
for item in os.listdir('.'):
    st.sidebar.write(f"- {item}")

# Crear un medidor básico
def create_gauge(value, title, min_val, max_val, ranges):
    steps = []
    for start, end, color in ranges:
        steps.append(dict(range=[start, end], color=color))
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': title},
        gauge={
            'axis': {'range': [min_val, max_val]},
            'bar': {'color': "darkblue"},
            'steps': steps,
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': value
            }
        }
    ))
    
    return fig

# Crear datos de tendencia de ejemplo
time_points = list(range(10))
map_values = [np.random.randint(65, 95) for _ in range(10)]
co_values = [np.random.randint(3, 7) for _ in range(10)]

# Panel principal
col1, col2 = st.columns(2)

with col1:
    st.subheader("Parámetros Hemodinámicos")
    # Crear controles
    map_val = st.slider("MAP (mmHg)", 40, 140, 75)
    co_val = st.slider("CO (L/min)", 1, 10, 5)
    svv_val = st.slider("SVV (%)", 0, 25, 12)
    pvv_val = st.slider("PVV (%)", 0, 25, 11)
    
    # Calcular riesgo simple
    map_risk = 0.4 if map_val < 65 else 0.2 if map_val < 70 else 0 if map_val <= 100 else 0.3
    co_risk = 0.4 if co_val < 2.5 else 0.2 if co_val < 4.0 else 0 if co_val <= 8.0 else 0.3
    svv_risk = 0 if svv_val <= 13 else 0.15 if svv_val <= 17 else 0.3
    pvv_risk = 0 if pvv_val <= 12 else 0.15 if pvv_val <= 15 else 0.3
    
    sto2_risk = ((map_risk * 0.35) + (co_risk * 0.35) + (svv_risk * 0.15) + (pvv_risk * 0.15)) * 100
    
    st.metric("Riesgo StO2 <65% (10min)", f"{sto2_risk:.1f}%")

with col2:
    st.subheader("Medidor")
    
    # Definir rangos de colores
    map_ranges = [
        (40, 65, "red"),
        (65, 70, "yellow"),
        (70, 100, "green"),
        (100, 140, "red")
    ]
    
    # Crear y mostrar el medidor
    map_gauge = create_gauge(map_val, "MAP", 40, 140, map_ranges)
    st.plotly_chart(map_gauge, use_container_width=True)

# Mostrar tendencias
st.subheader("Visualización de Tendencias")
trend_df = pd.DataFrame({
    'Tiempo': time_points,
    'MAP': map_values,
    'CO': co_values
})

st.line_chart(trend_df.set_index('Tiempo'))

st.info("Esta es una versión simplificada para diagnóstico. Verifica si se muestra correctamente.")