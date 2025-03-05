import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import time
from datetime import datetime, timedelta

# Function to convert hex colors to RGB
def hex_to_rgb(hex_color):
    """
    Converts a hex color to RGB format
    
    Args:
        hex_color (str): Color in hex format (#RRGGBB)
        
    Returns:
        tuple: RGB tuple with values between 0 and 1
    """
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16)/255 for i in (0, 2, 4))

# Configure page settings
st.set_page_config(
    page_title="ROSphere Monitor",
    page_icon="🫁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling
st.markdown("""
<style>
    /* General styles */
    .main {
        background-color: #0a1e30;
        color: white;
        padding: 0 !important;
        margin: 0 !important;
    }
    .stButton button {
        background-color: #ff4b4b;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 8px 15px;
        text-align: center;
        display: inline-block;
        font-size: 14px;
        margin: 2px;
        cursor: pointer;
    }
    
    /* Sidebar with dark background */
    [data-testid="stSidebar"] {
        background-color: #0a1423;
    }
    
    /* Parameter cells with navy blue background */
    .param-box {
        background-color: #0a1e3d;
        color: white;
        border-radius: 5px;
        padding: 6px 10px;
        margin-bottom: 8px;
        text-align: center;
    }
    
    /* Headings */
    h1 {
        color: white;
        font-size: 24px;
        margin-bottom: 5px;
        padding-bottom: 0;
    }
    h2, h3, h4, p, div {
        color: white;
        margin-top: 0;
        margin-bottom: 3px;
        padding-top: 0;
        padding-bottom: 0;
    }
    
    /* Timer display */
    .timer-display {
        background-color: #0a1e3d;
        color: white !important;
        padding: 5px 10px;
        border-radius: 5px;
        text-align: center;
        font-size: 16px;
        margin-bottom: 8px;
    }
    
    /* Parameter value display */
    .slider-value {
        font-size: 22px;
        font-weight: bold;
        text-align: center;
        padding: 3px 8px;
        border-radius: 4px;
        margin-top: 0;
        color: white;
    }
    
    /* Sliders */
    .stSlider {
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        margin-top: 0 !important;
        margin-bottom: 4px !important;
    }
    
    /* Dividers */
    hr {
        margin-top: 5px;
        margin-bottom: 5px;
        border: 0;
        border-top: 1px solid #333;
    }
    
    /* Metric title cells with navy blue background */
    .metric-title {
        background-color: #0a1e3d;
        color: white;
        padding: 5px 10px;
        border-radius: 5px 5px 0 0;
        text-align: center;
        font-weight: bold;
        margin-bottom: 0;
        font-size: 16px;
    }
    
    /* Main trend container */
    .main-trend-container {
        width: 100%;
        margin-top: 5px;
        margin-bottom: 10px;
        background-color: #0a1e3d;
        border-radius: 5px;
        padding: 5px;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
    }
    
    /* Scrollable charts */
    .scrollable-chart {
        overflow-x: auto;
        padding-bottom: 5px;
        margin-bottom: 5px;
    }
    
    /* Patient selector styling */
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        border: 1px solid #0a1e3d !important;
    }
    
    .stSelectbox label, 
    .stSelectbox div[data-baseweb="select"] span, 
    .stSelectbox div[data-baseweb="select"] div {
        color: #00264f !important;
        font-weight: bold !important;
    }
</style>
""", unsafe_allow_html=True)

# Functions to create charts
def create_gauge_chart(value, title, min_val, max_val, thresholds, container_width=400, container_height=150):
    colors = ['#32CD32', '#FFD700', '#FF4500']  # Green, Yellow, Red
    
    # Calculate ranges based on thresholds
    ranges = []
    for i in range(len(thresholds)):
        if i == 0:
            ranges.append([min_val, thresholds[i]])
        else:
            ranges.append([thresholds[i-1], thresholds[i]])
    if thresholds:
        ranges.append([thresholds[-1], max_val])
    
    fig = go.Figure()
    
    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': title, 'font': {'size': 16, 'color': 'white'}},
        gauge={
            'axis': {'range': [min_val, max_val], 'tickwidth': 1, 'tickcolor': "white"},
            'bar': {'color': "white", 'thickness': 0.15},
            'bgcolor': "rgba(0,0,0,0)",
            'borderwidth': 0,
            'steps': [
                {'range': ranges[0], 'color': colors[0]},
                {'range': ranges[1], 'color': colors[1]},
                {'range': ranges[2], 'color': colors[2]},
            ],
            'threshold': {
                'line': {'color': "white", 'width': 2},
                'thickness': 0.75,
                'value': value
            }
        },
        number={'font': {'size': 36, 'color': 'white'}}
    ))
    
    fig.update_layout(
        width=container_width,
        height=container_height,
        margin=dict(l=5, r=5, t=5, b=5),
        paper_bgcolor='rgba(10, 30, 61, 0.7)',
        font={'color': "white", 'family': "Arial"},
    )
    
    return fig

def create_trend_graph(x_data, y_data, title, container_width=400, container_height=80, scrollable=True, 
                      show_thresholds=False, thresholds=None):
    fig = go.Figure()
    
    # Define colors for thresholds
    colors = ['#32CD32', '#FFD700', '#FF4500']  # Green, Yellow, Red
    
    # Add shaded areas for risk levels if requested
    if show_thresholds and thresholds:
        for i in range(len(thresholds)):
            # First threshold
            if i == 0:
                fig.add_trace(go.Scatter(
                    x=x_data,
                    y=[thresholds[i]] * len(x_data),
                    fill=None,
                    mode='lines',
                    line=dict(color=colors[i], width=1, dash='dash'),
                    name=f"Threshold {thresholds[i]}%"
                ))
                
                # Shaded area up to first threshold
                rgb_values = hex_to_rgb(colors[i])
                rgba_color = f'rgba({int(rgb_values[0]*255)}, {int(rgb_values[1]*255)}, {int(rgb_values[2]*255)}, 0.2)'
                
                fig.add_trace(go.Scatter(
                    x=x_data,
                    y=[0] * len(x_data),
                    fill='tonexty',
                    mode='none',
                    fillcolor=rgba_color,
                    showlegend=False
                ))
    
    # Add the trend line
    fig.add_trace(go.Scatter(
        x=x_data, 
        y=y_data,
        mode='lines+markers',
        line=dict(color='red', width=2),
        marker=dict(size=4, color='red'),
        name=title,
        hovertemplate='Time: %{x}<br>Value: %{y:.2f}<extra></extra>'
    ))
    
    # Configure layout
    fig.update_layout(
        title=None,
        width=container_width if not scrollable else max(container_width, len(x_data) * 30),
        height=container_height,
        margin=dict(l=5, r=5, t=0, b=20),
        paper_bgcolor='rgba(10, 30, 61, 0.7)',
        plot_bgcolor='rgba(10, 30, 61, 0.5)',
        font={'color': "white", 'family': "Arial"},
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.1)',
            zeroline=False,
            title=None,
            tickfont=dict(size=8)
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.1)',
            zeroline=False,
            title=None,
            tickfont=dict(size=8)
        ),
        hoverlabel=dict(
            bgcolor='rgba(10, 30, 61, 0.9)',
            font_size=10,
            font_family="Arial"
        )
    )
    
    return fig

def create_risk_gauge(risk_probability, container_width=700, container_height=180):
    # Colors for risk ranges
    risk_colors = [
        {'range': [0, 60], 'color': '#32CD32'},  # Green
        {'range': [60, 80], 'color': '#FFD700'},  # Yellow
        {'range': [80, 90], 'color': '#FF4500'},  # Orange
        {'range': [90, 100], 'color': '#8B0000'}   # Dark red
    ]
    
    # Determine if we're above or below threshold
    is_risk = risk_probability < 65
    arrow_color = '#FF4500' if not is_risk else '#32CD32'
    threshold_text = "<65%" if not is_risk else ">65%"
    
    # Create a figure with subplots
    fig = go.Figure()
    
    # Add the main gauge
    fig.add_trace(
        go.Indicator(
            mode="gauge+number",
            value=risk_probability,
            title={
                'text': "Risk SatO2 <65% 10min",
                'font': {'size': 16, 'color': 'white'}
            },
            gauge={
                'axis': {
                    'range': [0, 100],
                    'tickwidth': 1,
                    'tickcolor': "white",
                    'tickvals': [0, 60, 80, 90, 100],
                    'ticktext': ['0', '60', '80', '90', '100']
                },
                'bar': {'color': "white", 'thickness': 0.15},
                'bgcolor': "rgba(0,0,0,0)",
                'borderwidth': 0,
                'steps': risk_colors,
                'threshold': {
                    'line': {'color': "white", 'width': 2},
                    'thickness': 0.75,
                    'value': risk_probability
                }
            },
            number={
                'font': {'size': 40, 'color': 'white'},
                'suffix': '%'
            }
        )
    )
    
    fig.update_layout(
        width=container_width,
        height=container_height,
        margin=dict(l=10, r=10, t=20, b=20),
        paper_bgcolor='rgba(10, 30, 61, 0.7)',
        font={'color': "white", 'family': "Arial"},
    )
    
    return fig

def create_performance_metrics_card(metrics, container_width=300, container_height=180):
    fig = go.Figure()
    
    # Create a table to display metrics
    fig.add_trace(go.Table(
        header=dict(
            values=["<b>Metric</b>", "<b>Value</b>"],
            line_color='rgba(10, 30, 61, 1)',
            fill_color='#0a1e3d',
            align=['left', 'center'],
            font=dict(color='white', size=12),
            height=25
        ),
        cells=dict(
            values=[
                list(metrics.keys()),
                list(metrics.values())
            ],
            line_color='rgba(60, 60, 60, 1)',
            fill_color='rgba(10, 30, 61, 0.5)',
            align=['left', 'center'],
            font=dict(color='white', size=12),
            height=25
        )
    ))
    
    # Configure layout
    fig.update_layout(
        title={
            'text': "LSTM Algorithm Performance",
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 14, 'color': 'white'}
        },
        width=container_width,
        height=container_height,
        margin=dict(l=5, r=5, t=30, b=10),
        paper_bgcolor='rgba(10, 30, 61, 0.7)',
    )
    
    return fig

def create_main_risk_trend(risk_data, x_data, container_width=800, container_height=150):
    """
    Creates the main risk trend visualization
    """
    # Define colors and thresholds
    thresholds = [60, 80, 90]
    colors = ['#32CD32', '#FFD700', '#FF4500', '#8B0000']  # Green, Yellow, Orange, Dark Red
    
    fig = go.Figure()
    
    # Add shaded areas for risk levels
    for i in range(len(thresholds)):
        # First threshold
        if i == 0:
            fig.add_trace(go.Scatter(
                x=x_data,
                y=[thresholds[i]] * len(x_data),
                fill=None,
                mode='lines',
                line=dict(color=colors[i], width=1, dash='dash'),
                name=f"Threshold {thresholds[i]}%"
            ))
            
            # Shaded area up to first threshold
            rgb_values = hex_to_rgb(colors[i])
            rgba_color = f'rgba({int(rgb_values[0]*255)}, {int(rgb_values[1]*255)}, {int(rgb_values[2]*255)}, 0.2)'
            
            fig.add_trace(go.Scatter(
                x=x_data,
                y=[0] * len(x_data),
                fill='tonexty',
                mode='none',
                fillcolor=rgba_color,
                showlegend=False
            ))
        
        # Intermediate thresholds
        if i < len(thresholds) - 1:
            fig.add_trace(go.Scatter(
                x=x_data,
                y=[thresholds[i+1]] * len(x_data),
                fill=None,
                mode='lines',
                line=dict(color=colors[i+1], width=1, dash='dash'),
                name=f"Threshold {thresholds[i+1]}%"
            ))
            
            # Shaded area between thresholds
            rgb_values = hex_to_rgb(colors[i+1])
            rgba_color = f'rgba({int(rgb_values[0]*255)}, {int(rgb_values[1]*255)}, {int(rgb_values[2]*255)}, 0.2)'
            
            fig.add_trace(go.Scatter(
                x=x_data,
                y=[thresholds[i]] * len(x_data),
                fill='tonexty',
                mode='none',
                fillcolor=rgba_color,
                showlegend=False
            ))
        
        # Last threshold
        if i == len(thresholds) - 1:
            # Shaded area from last threshold
            rgb_values = hex_to_rgb(colors[-1])
            rgba_color = f'rgba({int(rgb_values[0]*255)}, {int(rgb_values[1]*255)}, {int(rgb_values[2]*255)}, 0.2)'
            
            fig.add_trace(go.Scatter(
                x=x_data,
                y=[100] * len(x_data),
                fill='tonexty',
                mode='none',
                fillcolor=rgba_color,
                showlegend=False
            ))
    
    # Add the risk trend line
    fig.add_trace(go.Scatter(
        x=x_data, 
        y=risk_data,
        mode='lines+markers',
        line=dict(color='white', width=2),
        marker=dict(
            size=6, 
            color=risk_data,
            colorscale=[
                [0, colors[0]],         # Green for low values
                [0.6/100, colors[0]],   # Green up to 60%
                [0.6, colors[1]],       # Yellow at 60%
                [0.8, colors[2]],       # Orange at 80%
                [0.9, colors[3]],       # Red at 90%
                [1, colors[3]]          # Red for high values
            ]
        ),
        name="Risk Trend",
        hovertemplate='Time: %{x}<br>Risk: %{y:.2f}%<extra></extra>'
    ))
    
    # Configure layout
    fig.update_layout(
        title={
            'text': "Risk Trend - SatO2 <65% in 10min",
            'font': {'size': 16, 'color': 'white'},
            'y': 0.95,
            'x': 0.5
        },
        width=container_width,
        height=container_height,
        margin=dict(l=10, r=10, t=40, b=10),
        paper_bgcolor='rgba(10, 30, 61, 0.7)',
        plot_bgcolor='rgba(10, 30, 61, 0.5)',
        font={'color': "white", 'family': "Arial"},
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.1)',
            zeroline=False,
            title="Time",
            titlefont=dict(size=10),
            tickfont=dict(size=8)
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.1)',
            zeroline=False,
            title="Risk (%)",
            titlefont=dict(size=10),
            tickfont=dict(size=8),
            range=[0, 100]
        ),
        hoverlabel=dict(
            bgcolor='rgba(10, 30, 61, 0.9)',
            font_size=10,
            font_family="Arial"
        ),
        showlegend=False
    )
    
    return fig

# Function to calculate risk
def calculate_risk(map_val, co_val, svv_val, pvv_val):
    risk_score = 100 - min(100, max(0, (map_val - 60) + (co_val * 10) - 
                                   (svv_val * 0.5) - (pvv_val * 0.5)))
    return risk_score

# Initialize session state if it doesn't exist
if 'simulation_time' not in st.session_state:
    st.session_state.simulation_time = 0
    st.session_state.running = False
    st.session_state.mode = "MANUAL"  # Default to MANUAL
    st.session_state.map = 75
    st.session_state.co = 5.0
    st.session_state.svv = 12
    st.session_state.pvv = 11
    st.session_state.trend_data = {
        'time': [],
        'map': [],
        'co': [],
        'svv': [],
        'pvv': [],
        'risk': []
    }
    st.session_state.x_data = []
    st.session_state.current_patient = None
    st.session_state.excel_data_full = None

# App title
st.markdown("<h1 style='text-align: center; margin: 0; padding: 0;'>ROSphere Monitor</h1>", unsafe_allow_html=True)

# Sidebar content
with st.sidebar:
    st.markdown("<h3 style='margin-top:0'>Simulation Control</h3>", unsafe_allow_html=True)
    
    # Toggle for Manual/Automatic mode
    st.markdown("<div style='margin-bottom: 2px;'>Operation Mode</div>", unsafe_allow_html=True)
    
    # Create a custom toggle switch with HTML
    manual_class = "toggle-option active" if st.session_state.mode == "MANUAL" else "toggle-option"
    auto_class = "toggle-option active" if st.session_state.mode == "AUTOMÁTICO" else "toggle-option"
    
    toggle_html = f"""
    <div class="toggle-container" id="mode-toggle">
        <div class="{manual_class}" id="manual-mode">MANUAL</div>
        <div class="{auto_class}" id="auto-mode">AUTOMATIC</div>
    </div>
    """
    st.markdown(toggle_html, unsafe_allow_html=True)
    
    # Button to change mode
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        toggle_btn = st.button("Change Mode", key="toggle_mode", 
                              help="Switch between MANUAL and AUTOMATIC mode")
        if toggle_btn:
            # Toggle the mode
            if st.session_state.mode == "MANUAL":
                st.session_state.mode = "AUTOMÁTICO"
            else:
                st.session_state.mode = "MANUAL"
                st.session_state.running = False  # Stop simulation when switching to manual
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # Content based on mode
    if st.session_state.mode == "AUTOMÁTICO":
        # Patient selector
        st.markdown("<div style='margin-bottom: 3px;'>Patient</div>", unsafe_allow_html=True)
        patient_options = [f"Patient {i}" for i in range(1, 21)]
        selected_patient = st.selectbox("Select patient", patient_options, label_visibility="collapsed", key="patient_select")
        
        # Extract patient number
        patient_id = int(selected_patient.split()[1])
        
        # Show data loading info
        data_loaded = False
        excel_file = f"{patient_id}.xlsx"
        
        # If patient changed, reset simulation
        if st.session_state.current_patient != patient_id:
            st.session_state.current_patient = patient_id
            st.session_state.simulation_time = 0
            st.session_state.running = False
            
            # For demo purposes, generate random data
            # In real app, this would load from Excel files
            df = pd.DataFrame({
                'time': list(range(100)),
                'MAP': [np.random.randint(65, 95) for _ in range(100)],
                'CO': [round(np.random.uniform(3.0, 7.0), 1) for _ in range(100)],
                'SVV': [np.random.randint(8, 20) for _ in range(100)],
                'PVV': [np.random.randint(7, 18) for _ in range(100)]
            })
            st.session_state.excel_data_full = df
            data_loaded = True
            
            st.markdown(f"<div style='background-color: #0a1e3d; color: white; padding: 5px; border-radius: 5px; margin-top: 5px;'>Data loaded: {excel_file}</div>", unsafe_allow_html=True)
            
            # Reset trend data
            st.session_state.trend_data = {
                'time': [],
                'map': [],
                'co': [],
                'svv': [],
                'pvv': [],
                'risk': []
            }
            st.session_state.x_data = []
        
        st.markdown("<hr>", unsafe_allow_html=True)
        
        # Show simulation time
        st.markdown(f"""
        <div class='timer-display'>
            ⏱️ Time: {st.session_state.simulation_time:.1f} seconds
        </div>
        """, unsafe_allow_html=True)
        
        # Control buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("START", key="start_btn", use_container_width=True, type="primary" if st.session_state.running else "secondary"):
                st.session_state.running = True
        with col2:
            if st.button("STOP", key="stop_btn", use_container_width=True, type="primary" if not st.session_state.running else "secondary"):
                st.session_state.running = False
        
        # Current status
        if st.session_state.running:
            status = "Simulation running"
        else:
            status = "Simulation stopped"
        st.markdown(f"<div style='color: #A0A0A0; margin-top: 5px;'>{status}</div>", unsafe_allow_html=True)
    
    # Always show parameter controls
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<div style='margin-bottom: 2px;'>Simulation Parameters</div>", unsafe_allow_html=True)
    
    # First row of parameters
    param_col1, param_col2 = st.columns(2)
    
    with param_col1:
        # MAP control
        st.markdown("<div class='param-box'>MAP (mmHg)</div>", unsafe_allow_html=True)
        
        # Numeric input
        map_val = st.number_input("MAP input", min_value=40, max_value=140, value=int(st.session_state.map), 
                                  step=1, label_visibility="collapsed", key="map_num")
        
        # Slider
        st.session_state.map = st.slider("MAP slider", 40, 140, int(map_val), 1, 
                                        label_visibility="collapsed", key="map_slider")
        
        st.markdown(f"<div class='slider-value'>{st.session_state.map}</div>", unsafe_allow_html=True)
    
    with param_col2:
        # CO control
        st.markdown("<div class='param-box'>CO (L/min)</div>", unsafe_allow_html=True)
        
        # Numeric input
        co_val = st.number_input("CO input", min_value=1.0, max_value=10.0, value=float(st.session_state.co), 
                                step=0.1, format="%.1f", label_visibility="collapsed", key="co_num")
        
        # Slider
        st.session_state.co = st.slider("CO slider", 1.0, 10.0, float(co_val), 0.1, 
                                      label_visibility="collapsed", key="co_slider")
        
        st.markdown(f"<div class='slider-value'>{st.session_state.co:.1f}</div>", unsafe_allow_html=True)
    
    # Second row of parameters
    param_col3, param_col4 = st.columns(2)
    
    with param_col3:
        # SVV control
        st.markdown("<div class='param-box'>SVV (%)</div>", unsafe_allow_html=True)
        
        # Numeric input
        svv_val = st.number_input("SVV input", min_value=0, max_value=25, value=int(st.session_state.svv), 
                                 step=1, label_visibility="collapsed", key="svv_num")
        
        # Slider
        st.session_state.svv = st.slider("SVV slider", 0, 25, int(svv_val), 1, 
                                       label_visibility="collapsed", key="svv_slider")
        
        st.markdown(f"<div class='slider-value'>{st.session_state.svv}</div>", unsafe_allow_html=True)
    
    with param_col4:
        # PVV control
        st.markdown("<div class='param-box'>PVV (%)</div>", unsafe_allow_html=True)
        
        # Numeric input
        pvv_val = st.number_input("PVV input", min_value=0, max_value=25, value=int(st.session_state.pvv), 
                                 step=1, label_visibility="collapsed", key="pvv_num")
        
        # Slider
        st.session_state.pvv = st.slider("PVV slider", 0, 25, int(pvv_val), 1, 
                                       label_visibility="collapsed", key="pvv_slider")
        
        st.markdown(f"<div class='slider-value'>{st.session_state.pvv}</div>", unsafe_allow_html=True)

# Update simulation button in main area (only visible in automatic mode)
if st.session_state.mode == "AUTOMÁTICO":
    st.button("UPDATE SIMULATION", type="primary", use_container_width=True)

# Function to update data based on mode
def update_trend_data():
    # Automatic mode: load from Excel
    if st.session_state.mode == "AUTOMÁTICO" and 'excel_data_full' in st.session_state and st.session_state.excel_data_full is not none:
    # Automatic simulation (only run in automatic mode and when running)
if st.session_state.mode == "AUTOMÁTICO" and st.session_state.running:
    # Increment simulation time
    st.session_state.simulation_time += 0.1
    
    # Short pause for more realistic simulation
    time.sleep(0.1)
    
    # Use st.rerun() to update the page
    st.rerun()import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import time
from datetime import datetime, timedelta

# Function to convert hex colors to RGB
def hex_to_rgb(hex_color):
    """
    Converts a hex color to RGB format
    
    Args:
        hex_color (str): Color in hex format (#RRGGBB)
        
    Returns:
        tuple: RGB tuple with values between 0 and 1
    """
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16)/255 for i in (0, 2, 4))

# Configure page settings
st.set_page_config(
    page_title="ROSphere Monitor",
    page_icon="🫁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling
st.markdown("""
<style>
    /* General styles */
    .main {
        background-color: #0a1e30;
        color: white;
        padding: 0 !important;
        margin: 0 !important;
    }
    .stButton button {
        background-color: #ff4b4b;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 8px 15px;
        text-align: center;
        display: inline-block;
        font-size: 14px;
        margin: 2px;
        cursor: pointer;
    }
    
    /* Sidebar with dark background */
    [data-testid="stSidebar"] {
        background-color: #0a1423;
    }
    
    /* Parameter cells with navy blue background */
    .param-box {
        background-color: #0a1e3d;
        color: white;
        border-radius: 5px;
        padding: 6px 10px;
        margin-bottom: 8px;
        text-align: center;
    }
    
    /* Headings */
    h1 {
        color: white;
        font-size: 24px;
        margin-bottom: 5px;
        padding-bottom: 0;
    }
    h2, h3, h4, p, div {
        color: white;
        margin-top: 0;
        margin-bottom: 3px;
        padding-top: 0;
        padding-bottom: 0;
    }
    
    /* Timer display */
    .timer-display {
        background-color: #0a1e3d;
        color: white !important;
        padding: 5px 10px;
        border-radius: 5px;
        text-align: center;
        font-size: 16px;
        margin-bottom: 8px;
    }
    
    /* Parameter value display */
    .slider-value {
        font-size: 22px;
        font-weight: bold;
        text-align: center;
        padding: 3px 8px;
        border-radius: 4px;
        margin-top: 0;
        color: white;
    }
    
    /* Sliders */
    .stSlider {
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        margin-top: 0 !important;
        margin-bottom: 4px !important;
    }
    
    /* Dividers */
    hr {
        margin-top: 5px;
        margin-bottom: 5px;
        border: 0;
        border-top: 1px solid #333;
    }
    
    /* Metric title cells with navy blue background */
    .metric-title {
        background-color: #0a1e3d;
        color: white;
        padding: 5px 10px;
        border-radius: 5px 5px 0 0;
        text-align: center;
        font-weight: bold;
        margin-bottom: 0;
        font-size: 16px;
    }
    
    /* Main trend container */
    .main-trend-container {
        width: 100%;
        margin-top: 5px;
        margin-bottom: 10px;
        background-color: #0a1e3d;
        border-radius: 5px;
        padding: 5px;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
    }
    
    /* Scrollable charts */
    .scrollable-chart {
        overflow-x: auto;
        padding-bottom: 5px;
        margin-bottom: 5px;
    }
    
    /* Patient selector styling */
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        border: 1px solid #0a1e3d !important;
    }
    
    .stSelectbox label, 
    .stSelectbox div[data-baseweb="select"] span, 
    .stSelectbox div[data-baseweb="select"] div {
        color: #00264f !important;
        font-weight: bold !important;
    }
</style>
""", unsafe_allow_html=True)

# Functions to create charts
def create_gauge_chart(value, title, min_val, max_val, thresholds, container_width=400, container_height=150):
    colors = ['#32CD32', '#FFD700', '#FF4500']  # Green, Yellow, Red
    
    # Calculate ranges based on thresholds
    ranges = []
    for i in range(len(thresholds)):
        if i == 0:
            ranges.append([min_val, thresholds[i]])
        else:
            ranges.append([thresholds[i-1], thresholds[i]])
    if thresholds:
        ranges.append([thresholds[-1], max_val])
    
    fig = go.Figure()
    
    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': title, 'font': {'size': 16, 'color': 'white'}},
        gauge={
            'axis': {'range': [min_val, max_val], 'tickwidth': 1, 'tickcolor': "white"},
            'bar': {'color': "white", 'thickness': 0.15},
            'bgcolor': "rgba(0,0,0,0)",
            'borderwidth': 0,
            'steps': [
                {'range': ranges[0], 'color': colors[0]},
                {'range': ranges[1], 'color': colors[1]},
                {'range': ranges[2], 'color': colors[2]},
            ],
            'threshold': {
                'line': {'color': "white", 'width': 2},
                'thickness': 0.75,
                'value': value
            }
        },
        number={'font': {'size': 36, 'color': 'white'}}
    ))
    
    fig.update_layout(
        width=container_width,
        height=container_height,
        margin=dict(l=5, r=5, t=5, b=5),
        paper_bgcolor='rgba(10, 30, 61, 0.7)',
        font={'color': "white", 'family': "Arial"},
    )
    
    return fig

def create_trend_graph(x_data, y_data, title, container_width=400, container_height=80, scrollable=True, 
                      show_thresholds=False, thresholds=None, colors=None):
    fig = go.Figure()
    
    # Define colors for thresholds if not provided
    if colors is None:
        colors = ['#32CD32', '#FFD700', '#FF4500']  # Green, Yellow, Red
    
    # Add shaded areas for risk levels if requested
    if show_thresholds and thresholds:
        for i in range(len(thresholds)):
            # First threshold
            if i == 0:
                fig.add_trace(go.Scatter(
                    x=x_data,
                    y=[thresholds[i]] * len(x_data),
                    fill=None,
                    mode='lines',
                    line=dict(color=colors[i], width=1, dash='dash'),
                    name=f"Threshold {thresholds[i]}%"
                ))
                
                # Shaded area up to first threshold
                rgb_values = hex_to_rgb(colors[i])
                rgba_color = f'rgba({int(rgb_values[0]*255)}, {int(rgb_values[1]*255)}, {int(rgb_values[2]*255)}, 0.2)'
                
                fig.add_trace(go.Scatter(
                    x=x_data,
                    y=[0] * len(x_data),
                    fill='tonexty',
                    mode='none',
                    fillcolor=rgba_color,
                    showlegend=False
                ))
    
    # Add the trend line
    fig.add_trace(go.Scatter(
        x=x_data, 
        y=y_data,
        mode='lines+markers',
        line=dict(color='red', width=2),
        marker=dict(size=4, color='red'),
        name=title,
        hovertemplate='Time: %{x}<br>Value: %{y:.2f}<extra></extra>'
    ))
    
    # Configure layout
    fig.update_layout(
        title=None,
        width=container_width if not scrollable else max(container_width, len(x_data) * 30),
        height=container_height,
        margin=dict(l=5, r=5, t=0, b=20),
        paper_bgcolor='rgba(10, 30, 61, 0.7)',
        plot_bgcolor='rgba(10, 30, 61, 0.5)',
        font={'color': "white", 'family': "Arial"},
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.1)',
            zeroline=False,
            title=None,
            tickfont=dict(size=8)
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.1)',
            zeroline=False,
            title=None,
            tickfont=dict(size=8)
        ),
        hoverlabel=dict(
            bgcolor='rgba(10, 30, 61, 0.9)',
            font_size=10,
            font_family="Arial"
        )
    )
    
    return fig

def create_risk_gauge(risk_probability, container_width=700, container_height=180):
    # Colors for risk ranges
    risk_colors = [
        {'range': [0, 60], 'color': '#32CD32'},  # Green
        {'range': [60, 80], 'color': '#FFD700'},  # Yellow
        {'range': [80, 90], 'color': '#FF4500'},  # Orange
        {'range': [90, 100], 'color': '#8B0000'}   # Dark red
    ]
    
    # Determine if we're above or below threshold
    is_risk = risk_probability < 65
    arrow_color = '#FF4500' if not is_risk else '#32CD32'
    threshold_text = "<65%" if not is_risk else ">65%"
    
    # Create a figure with subplots
    fig = go.Figure()
    
    # Add the main gauge
    fig.add_trace(
        go.Indicator(
            mode="gauge+number",
            value=risk_probability,
            title={
                'text': "Risk SatO2 <65% 10min",
                'font': {'size': 16, 'color': 'white'}
            },
            gauge={
                'axis': {
                    'range': [0, 100],
                    'tickwidth': 1,
                    'tickcolor': "white",
                    'tickvals': [0, 60, 80, 90, 100],
                    'ticktext': ['0', '60', '80', '90', '100']
                },
                'bar': {'color': "white", 'thickness': 0.15},
                'bgcolor': "rgba(0,0,0,0)",
                'borderwidth': 0,
                'steps': risk_colors,
                'threshold': {
                    'line': {'color': "white", 'width': 2},
                    'thickness': 0.75,
                    'value': risk_probability
                }
            },
            number={
                'font': {'size': 40, 'color': 'white'},
                'suffix': '%'
            }
        )
    )
    
    fig.update_layout(
        width=container_width,
        height=container_height,
        margin=dict(l=10, r=10, t=20, b=20),
        paper_bgcolor='rgba(10, 30, 61, 0.7)',
        font={'color': "white", 'family': "Arial"},
    )
    
    return fig

def create_performance_metrics_card(metrics, container_width=300, container_height=180):
    fig = go.Figure()
    
    # Create a table to display metrics
    fig.add_trace(go.Table(
        header=dict(
            values=["<b>Metric</b>", "<b>Value</b>"],
            line_color='rgba(10, 30, 61, 1)',
            fill_color='#0a1e3d',
            align=['left', 'center'],
            font=dict(color='white', size=12),
            height=25
        ),
        cells=dict(
            values=[
                list(metrics.keys()),
                list(metrics.values())
            ],
            line_color='rgba(60, 60, 60, 1)',
            fill_color='rgba(10, 30, 61, 0.5)',
            align=['left', 'center'],
            font=dict(color='white', size=12),
            height=25
        )
    ))
    
    # Configure layout
    fig.update_layout(
        title={
            'text': "LSTM Algorithm Performance",
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 14, 'color': 'white'}
        },
        width=container_width,
        height=container_height,
        margin=dict(l=5, r=5, t=30, b=10),
        paper_bgcolor='rgba(10, 30, 61, 0.7)',
    )
    
    return fig

def create_main_risk_trend(risk_data, x_data, container_width=800, container_height=150):
    """
    Creates the main risk trend visualization
    """
    # Define colors and thresholds
    thresholds = [60, 80, 90]
    colors = ['#32CD32', '#FFD700', '#FF4500', '#8B0000']  # Green, Yellow, Orange, Dark Red
    
    fig = go.Figure()
    
    # Add shaded areas for risk levels
    for i in range(len(thresholds)):
        # First threshold
        if i == 0:
            fig.add_trace(go.Scatter(
                x=x_data,
                y=[thresholds[i]] * len(x_data),
                fill=None,
                mode='lines',
                line=dict(color=colors[i], width=1, dash='dash'),
                name=f"Threshold {thresholds[i]}%"
            ))
            
            # Shaded area up to first threshold
            rgb_values = hex_to_rgb(colors[i])
            rgba_color = f'rgba({int(rgb_values[0]*255)}, {int(rgb_values[1]*255)}, {int(rgb_values[2]*255)}, 0.2)'
            
            fig.add_trace(go.Scatter(
                x=x_data,
                y=[0] * len(x_data),
                fill='tonexty',
                mode='none',
                fillcolor=rgba_color,
                showlegend=False
            ))
        
        # Intermediate thresholds
        if i < len(thresholds) - 1:
            fig.add_trace(go.Scatter(
                x=x_data,
                y=[thresholds[i+1]] * len(x_data),
                fill=None,
                mode='lines',
                line=dict(color=colors[i+1], width=1, dash='dash'),
                name=f"Threshold {thresholds[i+1]}%"
            ))
            
            # Shaded area between thresholds
            rgb_values = hex_to_rgb(colors[i+1])
            rgba_color = f'rgba({int(rgb_values[0]*255)}, {int(rgb_values[1]*255)}, {int(rgb_values[2]*255)}, 0.2)'
            
            fig.add_trace(go.Scatter(
                x=x_data,
                y=[thresholds[i]] * len(x_data),
                fill='tonexty',
                mode='none',
                fillcolor=rgba_color,
                showlegend=False
            ))
        
        # Last threshold
        if i == len(thresholds) - 1:
            # Shaded area from last threshold
            rgb_values = hex_to_rgb(colors[-1])
            rgba_color = f'rgba({int(rgb_values[0]*255)}, {int(rgb_values[1]*255)}, {int(rgb_values[2]*255)}, 0.2)'
            
            fig.add_trace(go.Scatter(
                x=x_data,
                y=[100] * len(x_data),
                fill='tonexty',
                mode='none',
                fillcolor=rgba_color,
                showlegend=False
            ))
    
    # Add the risk trend line
    fig.add_trace(go.Scatter(
        x=x_data, 
        y=risk_data,
        mode='lines+markers',
        line=dict(color='white', width=2),
        marker=dict(
            size=6, 
            color=risk_data,
            colorscale=[
                [0, colors[0]],         # Green for low values
                [0.6/100, colors[0]],   # Green up to 60%
                [0.6, colors[1]],       # Yellow at 60%
                [0.8, colors[2]],       # Orange at 80%
                [0.9, colors[3]],       # Red at 90%
                [1, colors[3]]          # Red for high values
            ]
        ),
        name="Risk Trend",
        hovertemplate='Time: %{x}<br>Risk: %{y:.2f}%<extra></extra>'
    ))
    
    # Configure layout
    fig.update_layout(
        title={
            'text': "Risk Trend - SatO2 <65% in 10min",
            'font': {'size': 16, 'color': 'white'},
            'y': 0.95,
            'x': 0.5
        },
        width=container_width,
        height=container_height,
        margin=dict(l=10, r=10, t=40, b=10),
        paper_bgcolor='rgba(10, 30, 61, 0.7)',
        plot_bgcolor='rgba(10, 30, 61, 0.5)',
        font={'color': "white", 'family': "Arial"},
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.1)',
            zeroline=False,
            title="Time",
            titlefont=dict(size=10),
            tickfont=dict(size=8)
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.1)',
            zeroline=False,
            title="Risk (%)",
            titlefont=dict(size=10),
            tickfont=dict(size=8),
            range=[0, 100]
        ),
        hoverlabel=dict(
            bgcolor='rgba(10, 30, 61, 0.9)',
            font_size=10,
            font_family="Arial"
        ),
        showlegend=False
    )
    
    return fig

# Function to calculate risk
def calculate_risk(map_val, co_val, svv_val, pvv_val):
    risk_score = 100 - min(100, max(0, (map_val - 60) + (co_val * 10) - 
                                   (svv_val * 0.5) - (pvv_val * 0.5)))
    return risk_score

# Initialize session state if it doesn't exist
if 'simulation_time' not in st.session_state:
    st.session_state.simulation_time = 0
    st.session_state.running = False
    st.session_state.mode = "MANUAL"  # Default to MANUAL
    st.session_state.map = 75
    st.session_state.co = 5.0
    st.session_state.svv = 12
    st.session_state.pvv = 11
    st.session_state.trend_data = {
        'time': [],
        'map': [],
        'co': [],
        'svv': [],
        'pvv': [],
        'risk': []
    }
    st.session_state.x_data = []
    st.session_state.current_patient = None
    st.session_state.excel_data_full = None

# App title
st.markdown("<h1 style='text-align: center; margin: 0; padding: 0;'>ROSphere Monitor</h1>", unsafe_allow_html=True)

# Sidebar content
with st.sidebar:
    st.markdown("<h3 style='margin-top:0'>Simulation Control</h3>", unsafe_allow_html=True)
    
    # Toggle for Manual/Automatic mode
    st.markdown("<div style='margin-bottom: 2px;'>Operation Mode</div>", unsafe_allow_html=True)
    
    # Create a custom toggle switch with HTML
    manual_class = "toggle-option active" if st.session_state.mode == "MANUAL" else "toggle-option"
    auto_class = "toggle-option active" if st.session_state.mode == "AUTOMÁTICO" else "toggle-option"
    
    toggle_html = f"""
    <div class="toggle-container" id="mode-toggle">
        <div class="{manual_class}" id="manual-mode">MANUAL</div>
        <div class="{auto_class}" id="auto-mode">AUTOMATIC</div>
    </div>
    """
    st.markdown(toggle_html, unsafe_allow_html=True)
    
    # Button to change mode
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        toggle_btn = st.button("Change Mode", key="toggle_mode", 
                              help="Switch between MANUAL and AUTOMATIC mode")
        if toggle_btn:
            # Toggle the mode
            if st.session_state.mode == "MANUAL":
                st.session_state.mode = "AUTOMÁTICO"
            else:
                st.session_state.mode = "MANUAL"
                st.session_state.running = False  # Stop simulation when switching to manual
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # Content based on mode
    if st.session_state.mode == "AUTOMÁTICO":
        # Patient selector
        st.markdown("<div style='margin-bottom: 3px;'>Patient</div>", unsafe_allow_html=True)
        patient_options = [f"Patient {i}" for i in range(1, 21)]
        selected_patient = st.selectbox("Select patient", patient_options, label_visibility="collapsed", key="patient_select")
        
        # Extract patient number
        patient_id = int(selected_patient.split()[1])
        
        # Show data loading info
        data_loaded = False
        excel_file = f"{patient_id}.xlsx"
        
        # If patient changed, reset simulation
        if st.session_state.current_patient != patient_id:
            st.session_state.current_patient = patient_id
            st.session_state.simulation_time = 0
            st.session_state.running = False
            
            # For demo purposes, generate random data
            # In real app, this would load from Excel files
            df = pd.DataFrame({
                'time': list(range(100)),
                'MAP': [np.random.randint(65, 95) for _ in range(100)],
                'CO': [round(np.random.uniform(3.0, 7.0), 1) for _ in range(100)],
                'SVV': [np.random.randint(8, 20) for _ in range(100)],
                'PVV': [np.random.randint(7, 18) for _ in range(100)]
            })
            st.session_state.excel_data_full = df
            data_loaded = True
            
            st.markdown(f"<div style='background-color: #0a1e3d; color: white; padding: 5px; border-radius: 5px; margin-top: 5px;'>Data loaded: {excel_file}</div>", unsafe_allow_html=True)
            
            # Reset trend data
            st.session_state.trend_data = {
                'time': [],
                'map': [],
                'co': [],
                'svv': [],
                'pvv': [],
                'risk': []
            }
            st.session_state.x_data = []
        
        st.markdown("<hr>", unsafe_allow_html=True)
        
        # Show simulation time
        st.markdown(f"""
        <div class='timer-display'>
            ⏱️ Time: {st.session_state.simulation_time:.1f} seconds
        </div>
        """, unsafe_allow_html=True)
        
        # Control buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("START", key="start_btn", use_container_width=True, type="primary" if st.session_state.running else "secondary"):
                st.session_state.running = True
        with col2:
            if st.button("STOP", key="stop_btn", use_container_width=True, type="primary" if not st.session_state.running else "secondary"):
                st.session_state.running = False
        
        # Current status
        if st.session_state.running:
            status = "Simulation running"
        else:
            status = "Simulation stopped"
        st.markdown(f"<div style='color: #A0A0A0; margin-top: 5px;'>{status}</div>", unsafe_allow_html=True)
    
    # Always show parameter controls
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<div style='margin-bottom: 2px;'>Simulation Parameters</div>", unsafe_allow_html=True)
    
    # Only allow editing in manual mode
    disabled = st.session_state.mode != "MANUAL"
    
    # First row of parameters
    param_col1, param_col2 = st.columns(2)
    
    with param_col1:
        # MAP control
        st.markdown("<div class='param-box'>MAP (mmHg)</div>", unsafe_allow_html=True)
        
        # Numeric input
        map_val = st.number_input("MAP input", min_value=40, max_value=140, value=int(st.session_state.map), 
                                  step=1, label_visibility="collapsed", key="map_num", disabled=disabled)
        
        # Slider
        st.session_state.map = st.slider("MAP slider", 40, 140, int(map_val), 1, 
                                        label_visibility="collapsed", key="map_slider", disabled=disabled)
        
        st.markdown(f"<div class='slider-value'>{st.session_state.map}</div>", unsafe_allow_html=True)
    
    with param_col2:
        # CO control
        st.markdown("<div class='param-box'>CO (L/min)</div>", unsafe_allow_html=True)
        
        # Numeric input
        co_val = st.number_input("CO input", min_value=1.0, max_value=10.0, value=float(st.session_state.co), 
                                step=0.1, format="%.1f", label_visibility="collapsed", key="co_num", disabled=disabled)
        
        # Slider
        st.session_state.co = st.slider("CO slider", 1.0, 10.0, float(co_val), 0.1, 
                                      label_visibility="collapsed", key="co_slider", disabled=disabled)
        
        st.markdown(f"<div class='slider-value'>{st.session_state.co:.1f}</div>", unsafe_allow_html=True)
    
    # Second row of parameters
    param_col3, param_col4 = st.columns(2)
    
    with param_col3:
        # SVV control
        st.markdown("<div class='param-box'>SVV (%)</div>", unsafe_allow_html=True)
        
        # Numeric input
        svv_val = st.number_input("SVV input", min_value=0, max_value=25, value=int(st.session_state.svv), 
                                 step=1, label_visibility="collapsed", key="svv_num", disabled=disabled)
        
        # Slider
        st.session_state.svv = st.slider("SVV slider", 0, 25, int(svv_val), 1, 
                                       label_visibility="collapsed", key="svv_slider", disabled=disabled)
        
        st.markdown(f"<div class='slider-value'>{st.session_state.svv}</div>", unsafe_allow_html=True)
    
    with param_col4:
        # PVV control
        st.markdown("<div class='param-box'>PVV (%)</div>", unsafe_allow_html=True)
        
        # Numeric input
        pvv_val = st.number_input("PVV input", min_value=0, max_value=25, value=int(st.session_state.pvv), 
                                 step=1, label_visibility="collapsed", key="pvv_num", disabled=disabled)
        
        # Slider
        st.session_state.pvv = st.slider("PVV slider", 0, 25, int(pvv_val), 1, 
                                       label_visibility="collapsed", key="pvv_slider", disabled=disabled)
        
        st.markdown(f"<div class='slider-value'>{st.session_state.pvv}</div>", unsafe_allow_html=True)

# Add completion to the rest of the app after the sidebar

# Metrics for the model
metrics = {
    "AUC": "0.93",
    "F1-Score": "0.89",
    "Precision": "0.88",
    "Sensitivity": "0.88",
    "Specificity": "0.90",
    "Accuracy": "0.89"
}

# Calculate current risk
risk_score = update_trend_data()

# Create containers for main metrics row
row3_col1, row3_col2 = st.columns([1, 2])

# Metrics row
with row3_col1:
    # Metrics table
    st.markdown("<div class='metric-title'>Algorithm Metrics</div>", unsafe_allow_html=True)
    metrics_chart = create_performance_metrics_card(metrics)
    st.plotly_chart(metrics_chart, use_container_width=True, config={'displayModeBar': False})

with row3_col2:
    # Risk gauge title
    st.markdown("<div class='metric-title'>Risk Prediction SatO2 <65% in 10min</div>", unsafe_allow_html=True)
    
    # Show risk gauge with probability
    risk_gauge = create_risk_gauge(risk_score)
    risk_chart_placeholder = st.empty()
    risk_chart_placeholder.plotly_chart(risk_gauge, use_container_width=True, config={'displayModeBar': False})

# Main risk trend chart
if len(st.session_state.trend_data['risk']) > 0:
    # Container for main trend chart
    st.markdown("<div class='main-trend-container'>", unsafe_allow_html=True)
    
    # Create and display main trend chart
    main_trend_chart = create_main_risk_trend(
        st.session_state.trend_data['risk'],
        st.session_state.x_data if st.session_state.x_data else list(range(len(st.session_state.trend_data['risk'])))
    )
    
    st.plotly_chart(main_trend_chart, use_container_width=True, config={'displayModeBar': False})
    
    st.markdown("</div>", unsafe_allow_html=True)

# Create containers for main parameter charts rows
row1_col1, row1_col2 = st.columns(2)
row2_col1, row2_col2 = st.columns(2)

# First row of charts
with row1_col1:
    # MAP with navy blue title
    st.markdown("<div class='metric-title'>MAP (mmHg)</div>", unsafe_allow_html=True)
    map_gauge = create_gauge_chart(
        value=st.session_state.map,
        title="",
        min_val=40,
        max_val=140,
        thresholds=[65, 95]
    )
    st.plotly_chart(map_gauge, use_container_width=True, config={'displayModeBar': False})
    
    # MAP trend chart with scrolling
    st.markdown("<div class='scrollable-chart'>", unsafe_allow_html=True)
    map_trend = create_trend_graph(
        x_data=st.session_state.x_data,
        y_data=st.session_state.trend_data['map'],
        title="MAP (mmHg)",
        scrollable=True
    )
    st.plotly_chart(map_trend, use_container_width=True, config={'displayModeBar': False})
    st.markdown("</div>", unsafe_allow_html=True)

with row1_col2:
    # CO with navy blue title
    st.markdown("<div class='metric-title'>CO (L/min)</div>", unsafe_allow_html=True)
    co_gauge = create_gauge_chart(
        value=st.session_state.co,
        title="",
        min_val=1,
        max_val=10,
        thresholds=[2.5, 7.5]
    )
    st.plotly_chart(co_gauge, use_container_width=True, config={'displayModeBar': False})
    
    # CO trend chart with scrolling
    st.markdown("<div class='scrollable-chart'>", unsafe_allow_html=True)
    co_trend = create_trend_graph(
        x_data=st.session_state.x_data,
        y_data=st.session_state.trend_data['co'],
        title="CO (L/min)",
        scrollable=True
    )
    st.plotly_chart(co_trend, use_container_width=True, config={'displayModeBar': False})
    st.markdown("</div>", unsafe_allow_html=True)

# Second row of charts
with row2_col1:
    # SVV with navy blue title
    st.markdown("<div class='metric-title'>SVV (%)</div>", unsafe_allow_html=True)
    svv_gauge = create_gauge_chart(
        value=st.session_state.svv,
        title="",
        min_val=0,
        max_val=25,
        thresholds=[8, 17]
    )
    st.plotly_chart(svv_gauge, use_container_width=True, config={'displayModeBar': False})
    
    # SVV trend chart with scrolling
    st.markdown("<div class='scrollable-chart'>", unsafe_allow_html=True)
    svv_trend = create_trend_graph(
        x_data=st.session_state.x_data,
        y_data=st.session_state.trend_data['svv'],
        title="SVV (%)",
        scrollable=True
    )
    st.plotly_chart(svv_trend, use_container_width=True, config={'displayModeBar': False})
    st.markdown("</div>", unsafe_allow_html=True)

with row2_col2:
    # PVV with navy blue title
    st.markdown("<div class='metric-title'>PVV (%)</div>", unsafe_allow_html=True)
    pvv_gauge = create_gauge_chart(
        value=st.session_state.pvv,
        title="",
        min_val=0,
        max_val=25,
        thresholds=[5, 15]
    )
    st.plotly_chart(pvv_gauge, use_container_width=True, config={'displayModeBar': False})
    
    # PVV trend chart with scrolling
    st.markdown("<div class='scrollable-chart'>", unsafe_allow_html=True)
    pvv_trend = create_trend_graph(
        x_data=st.session_state.x_data,
        y_data=st.session_state.trend_data['pvv'],
        title="PVV (%)",
        scrollable=True
    )
    st.plotly_chart(pvv_trend, use_container_width=True, config={'displayModeBar': False})
    st.markdown("</div>", unsafe_allow_html=True)

# Function to update data based on mode
def update_trend_data():
    # Automatic mode: load from Excel
    if st.session_state.mode == "AUTOMÁTICO" and 'excel_data_full' in st.session_state and st.session_state.excel_data_full is not None and st.session_state.running:
        # Find row closest to current time
        time_val = st.session_state.simulation_time
        df = st.session_state.excel_data_full
        
        try:
            # Check available columns in Excel
            time_col = None
            if 'time' in df.columns:
                time_col = 'time'
            elif 'tiempo' in df.columns:
                time_col = 'tiempo'
            elif 'Tiempo' in df.columns:
                time_col = 'Tiempo'
            elif 'Time' in df.columns:
                time_col = 'Time'
                
            if time_col:
                # Find all rows up to current time
                max_time = df[time_col].max()
                if time_val > max_time:
                    time_val = max_time
                
                # Find row corresponding to current time
                rows_up_to_now = df[df[time_col] <= time_val]
                
                if not rows_up_to_now.empty:
                    # Take the last row for current values
                    current_row = rows_up_to_now.iloc[-1]
                    
                    # Extract values if they exist
                    if 'MAP' in current_row:
                        st.session_state.map = int(current_row['MAP'])
                    if 'CO' in current_row:
                        st.session_state.co = float(current_row['CO'])
                    if 'SVV' in current_row:
                        st.session_state.svv = int(current_row['SVV'])
                    if 'PVV' in current_row:
                        st.session_state.pvv = int(current_row['PVV'])
                    
                    # Update trend data
                    # Clear existing data and reload all rows up to now
                    st.session_state.trend_data = {
                        'time': list(rows_up_to_now[time_col]),
                        'map': list(rows_up_to_now['MAP'] if 'MAP' in rows_up_to_now.columns else []),
                        'co': list(rows_up_to_now['CO'] if 'CO' in rows_up_to_now.columns else []),
                        'svv': list(rows_up_to_now['SVV'] if 'SVV' in rows_up_to_now.columns else []),
                        'pvv': list(rows_up_to_now['PVV'] if 'PVV' in rows_up_to_now.columns else []),
                        'risk': []
                    }
                    
                    # Calculate risk for each point
                    for i in range(len(st.session_state.trend_data['time'])):
                        map_val = st.session_state.trend_data['map'][i] if i < len(st.session_state.trend_data['map']) else 75
                        co_val = st.session_state.trend_data['co'][i] if i < len(st.session_state.trend_data['co']) else 5.0
                        svv_val = st.session_state.trend_data['svv'][i] if i < len(st.session_state.trend_data['svv']) else 12
                        pvv_val = st.session_state.trend_data['pvv'][i] if i < len(st.session_state.trend_data['pvv']) else 11
                        
                        risk = calculate_risk(map_val, co_val, svv_val, pvv_val)
                        st.session_state.trend_data['risk'].append(risk)
                    
                    # Update x_data for charts
                    st.session_state.x_data = list(st.session_state.trend_data['time'])
        except Exception as e:
            st.sidebar.error(f"Error updating data: {str(e)}")
    else:
        # Manual mode or no Excel data: add only the current point
        if len(st.session_state.trend_data['map']) >= 100:  # Keep up to 100 points to avoid overload
            for key in st.session_state.trend_data:
                if key != 'time' and st.session_state.trend_data[key]:
                    st.session_state.trend_data[key].pop(0)
        
        # Add current time
        if 'time' not in st.session_state.trend_data:
            st.session_state.trend_data['time'] = []
        
        st.session_state.trend_data['time'].append(st.session_state.simulation_time)
        
        # Add new values
        st.session_state.trend_data['map'].append(st.session_state.map)
        st.session_state.trend_data['co'].append(st.session_state.co)
        st.session_state.trend_data['svv'].append(st.session_state.svv)
        st.session_state.trend_data['pvv'].append(st.session_state.pvv)
        
        # Update x_data for charts
        st.session_state.x_data = list(range(len(st.session_state.trend_data['map'])))
    
    # Calculate risk based on current parameters
    risk_score = calculate_risk(st.session_state.map, st.session_state.co, st.session_state.svv, st.session_state.pvv)
    
    # Ensure that risk array is updated
    if len(st.session_state.trend_data['risk']) < len(st.session_state.x_data):
        st.session_state.trend_data['risk'].append(risk_score)
    
    return risk_score