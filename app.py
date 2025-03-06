import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import time
import os
import tempfile
import threading
import datetime
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

# Create temp directory to store uploaded files
temp_dir = tempfile.mkdtemp()

# Function to delete file after 10 minutes
def delete_file_after_delay(file_path, delay_seconds=600):
    def delete_task():
        time.sleep(delay_seconds)
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            pass  # Silently fail if file can't be deleted
    
    # Start thread to delete file after delay
    threading.Thread(target=delete_task, daemon=True).start()

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
    
    /* Clickable card styling */
    .clickable-card {
        background-color: #0a1e3d;
        border-radius: 5px;
        padding: 15px;
        margin-bottom: 10px;
        text-align: center;
        cursor: pointer;
        transition: background-color 0.3s;
    }
    
    .clickable-card:hover {
        background-color: #1a2f4d;
    }
    
    .card-title {
        font-weight: bold;
        font-size: 18px;
        margin-bottom: 5px;
    }
    
    .card-subtitle {
        font-size: 14px;
        color: #cccccc;
    }
    
    /* Modal dialog styling */
    .modal-dialog {
        border: 1px solid #1a2f4d;
        border-radius: 8px;
        background-color: #0a1e30;
        padding: 15px;
        margin-top: 10px;
        margin-bottom: 20px;
    }
    
    .modal-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
        border-bottom: 1px solid #1a2f4d;
        padding-bottom: 10px;
    }
    
    .modal-title {
        font-size: 18px;
        font-weight: bold;
    }
    
    .modal-close {
        cursor: pointer;
        font-size: 20px;
    }
    
    .modal-body {
        margin-bottom: 10px;
    }
    
    .stat-box {
        background-color: #0a1e3d;
        border-radius: 5px;
        padding: 10px;
        margin-bottom: 8px;
        display: flex;
        justify-content: space-between;
    }
    
    .stat-label {
        font-size: 14px;
    }
    
    .stat-value {
        font-weight: bold;
        font-size: 16px;
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
    # Define colors for thresholds if not provided
    if colors is None:
        colors = ['#32CD32', '#FFD700', '#FF4500']  # Green, Yellow, Red
    
    fig = go.Figure()
    
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

def create_performance_metrics_card(metrics, container_width=300, container_height=220):
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
        height=container_height,  # Increased height to fit all metrics
        margin=dict(l=5, r=5, t=30, b=10),
        paper_bgcolor='rgba(10, 30, 61, 0.7)',
    )
    
    return fig

def create_main_risk_trend(risk_data, x_data, container_width=800, container_height=150):
    """
    Creates the main risk trend visualization with discretely colored points
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
    
    # Create separate traces for each color range of markers
    # This gives discrete colors by risk level
    
    # Points with risk 0-60 (Green)
    green_x = [x_data[i] for i in range(len(risk_data)) if risk_data[i] < 60]
    green_y = [risk_data[i] for i in range(len(risk_data)) if risk_data[i] < 60]
    if green_x:
        fig.add_trace(go.Scatter(
            x=green_x, 
            y=green_y,
            mode='markers',
            marker=dict(size=6, color=colors[0]),
            name="Low Risk (<60%)",
            hovertemplate='Time: %{x}<br>Risk: %{y:.2f}%<extra></extra>',
            showlegend=True
        ))
    
    # Points with risk 60-80 (Yellow)
    yellow_x = [x_data[i] for i in range(len(risk_data)) if 60 <= risk_data[i] < 80]
    yellow_y = [risk_data[i] for i in range(len(risk_data)) if 60 <= risk_data[i] < 80]
    if yellow_x:
        fig.add_trace(go.Scatter(
            x=yellow_x, 
            y=yellow_y,
            mode='markers',
            marker=dict(size=6, color=colors[1]),
            name="Moderate Risk (60-80%)",
            hovertemplate='Time: %{x}<br>Risk: %{y:.2f}%<extra></extra>',
            showlegend=True
        ))
    
    # Points with risk 80-90 (Orange)
    orange_x = [x_data[i] for i in range(len(risk_data)) if 80 <= risk_data[i] < 90]
    orange_y = [risk_data[i] for i in range(len(risk_data)) if 80 <= risk_data[i] < 90]
    if orange_x:
        fig.add_trace(go.Scatter(
            x=orange_x, 
            y=orange_y,
            mode='markers',
            marker=dict(size=6, color=colors[2]),
            name="High Risk (80-90%)",
            hovertemplate='Time: %{x}<br>Risk: %{y:.2f}%<extra></extra>',
            showlegend=True
        ))
    
    # Points with risk 90-100 (Red)
    red_x = [x_data[i] for i in range(len(risk_data)) if risk_data[i] >= 90]
    red_y = [risk_data[i] for i in range(len(risk_data)) if risk_data[i] >= 90]
    if red_x:
        fig.add_trace(go.Scatter(
            x=red_x, 
            y=red_y,
            mode='markers',
            marker=dict(size=6, color=colors[3]),
            name="Critical Risk (>90%)",
            hovertemplate='Time: %{x}<br>Risk: %{y:.2f}%<extra></extra>',
            showlegend=True
        ))
    
    # Add the trend line (without markers since we add colored markers separately)
    fig.add_trace(go.Scatter(
        x=x_data, 
        y=risk_data,
        mode='lines',
        line=dict(color='white', width=2),
        name="Risk Trend",
        hovertemplate='Time: %{x}<br>Risk: %{y:.2f}%<extra></extra>',
        showlegend=False
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
            title=dict(text="Time", font=dict(size=10)),
            tickfont=dict(size=8)
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.1)',
            zeroline=False,
            title=dict(text="Risk (%)", font=dict(size=10)),
            tickfont=dict(size=8),
            range=[0, 100]
        ),
        hoverlabel=dict(
            bgcolor='rgba(10, 30, 61, 0.9)',
            font_size=10,
            font_family="Arial"
        ),
        showlegend=False  # Set to True if you want to show the legend
    )
    
    return fig

# Function to calculate risk
def calculate_risk(map_val, co_val, svv_val, pvv_val):
    risk_score = 100 - min(100, max(0, (map_val - 60) + (co_val * 10) - 
                                   (svv_val * 0.5) - (pvv_val * 0.5)))
    return risk_score

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

# Function to calculate trend statistics
def calculate_trend_stats(risk_data, time_interval=0.1):
    """
    Calculate statistics for risk trend data
    """
    if not risk_data:
        return {
            "high_risk_time": 0,
            "critical_risk_time": 0,
            "average_risk": 0,
            "trend_direction": "No data",
            "max_risk": 0,
            "time_above_threshold": 0
        }
    
    # Calculate time (in minutes) where risk > 80% (high risk)
    high_risk_points = len([r for r in risk_data if r >= 80])
    high_risk_time = (high_risk_points * time_interval) / 60
    
    # Calculate time (in minutes) where risk > 90% (critical risk)
    critical_risk_points = len([r for r in risk_data if r >= 90])
    critical_risk_time = (critical_risk_points * time_interval) / 60
    
    # Calculate average risk
    average_risk = sum(risk_data) / len(risk_data) if risk_data else 0
    
    # Calculate trend direction (increasing or decreasing)
    if len(risk_data) > 5:
        # Compare average of first half vs second half
        half_point = len(risk_data) // 2
        first_half_avg = sum(risk_data[:half_point]) / half_point if half_point > 0 else 0
        second_half_avg = sum(risk_data[half_point:]) / (len(risk_data) - half_point) if (len(risk_data) - half_point) > 0 else 0
        
        diff = second_half_avg - first_half_avg
        if diff > 5:
            trend_direction = "Strongly Increasing"
        elif diff > 1:
            trend_direction = "Increasing"
        elif diff < -5:
            trend_direction = "Strongly Decreasing"
        elif diff < -1:
            trend_direction = "Decreasing"
        else:
            trend_direction = "Stable"
    else:
        trend_direction = "Insufficient data"
    
    # Maximum risk value
    max_risk = max(risk_data) if risk_data else 0
    
    # Calculate time above threshold of 65%
    threshold_points = len([r for r in risk_data if r >= 65])
    time_above_threshold = (threshold_points * time_interval) / 60
    
    return {
        "high_risk_time": high_risk_time,
        "critical_risk_time": critical_risk_time,
        "average_risk": average_risk,
        "trend_direction": trend_direction,
        "max_risk": max_risk,
        "time_above_threshold": time_above_threshold
    }

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
    st.session_state.show_metrics = False
    st.session_state.show_trend_summary = False

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
        
        # Add file uploader for database files
        st.markdown("<div style='margin-bottom: 3px; margin-top: 10px;'>Upload Patient Data</div>", unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Upload patient data file (Excel, CSV)",
            type=["xlsx", "xls", "csv"],
            label_visibility="collapsed"
        )
        
        if uploaded_file is not None:
            try:
                # Save the file to temp directory
                file_path = os.path.join(temp_dir, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Schedule file deletion after 10 minutes
                delete_file_after_delay(file_path)
                
                # Success message
                st.markdown(
                    f"<div style='background-color: #0a623d; color: white; padding: 5px; border-radius: 5px; margin-top: 5px;'>"
                    f"File loaded: {uploaded_file.name} (temporary)</div>",
                    unsafe_allow_html=True
                )
                
                # If Excel or CSV, load into the data
                if uploaded_file.name.endswith(('.xlsx', '.xls')):
                    df = pd.read_excel(file_path)
                    st.session_state.excel_data_full = df
                    st.session_state.simulation_time = 0
                    st.session_state.running = False
                    
                    # Reset trend data for the new dataset
                    st.session_state.trend_data = {
                        'time': [],
                        'map': [],
                        'co': [],
                        'svv': [],
                        'pvv': [],
                        'risk': []
                    }
                    st.session_state.x_data = []
                    
                    # Show preview
                    with st.expander("Preview uploaded data"):
                        st.write(df.head())
                    
                elif uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(file_path)
                    st.session_state.excel_data_full = df
                    st.session_state.simulation_time = 0
                    st.session_state.running = False
                    
                    # Reset trend data for the new dataset
                    st.session_state.trend_data = {
                        'time': [],
                        'map': [],
                        'co': [],
                        'svv': [],
                        'pvv': [],
                        'risk': []
                    }
                    st.session_state.x_data = []
                    
                    # Show preview
                    with st.expander("Preview uploaded data"):
                        st.write(df.head())
            
            except Exception as e:
                st.markdown(
                    f"<div style='background-color: #622a0a; color: white; padding: 5px; border-radius: 5px; margin-top: 5px;'>"
                    f"Error: {str(e)}</div>",
                    unsafe_allow_html=True
                )
        
        # If patient changed, reset simulation
        if st.session_state.current_patient != patient_id and not uploaded_file:
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

# Update simulation button in main area (only visible in automatic mode)
if st.session_state.mode == "AUTOMÁTICO":
    st.button("UPDATE SIMULATION", type="primary", use_container_width=True)

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
    # Clickable card for Algorithm Metrics
    st.markdown("""
    <div class="clickable-card" id="metrics-card">
        <div class="card-title">Algorithm Metrics</div>
        <div class="card-subtitle">Click to view detailed performance metrics</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Create button to toggle metrics display (hidden but functional for the card)
    metrics_btn = st.button("Show Metrics", key="show_metrics_btn", label_visibility="collapsed")
    if metrics_btn:
        st.session_state.show_metrics = not st.session_state.show_metrics
    
    # Display metrics dialog if button was clicked
    if st.session_state.show_metrics:
        st.markdown("""
        <div class="modal-dialog">
            <div class="modal-header">
                <div class="modal-title">LSTM Algorithm Performance</div>
                <div class="modal-close" id="close-metrics">✕</div>
            </div>
            <div class="modal-body">
        """, unsafe_allow_html=True)
        
        # Display metrics in the modal
        for metric, value in metrics.items():
            st.markdown(f"""
            <div class="stat-box">
                <div class="stat-label">{metric}</div>
                <div class="stat-value">{value}</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div></div>", unsafe_allow_html=True)
        
        # Button to close the modal
        if st.button("Close", key="close_metrics_btn"):
            st.session_state.show_metrics = False

with row3_col2:
    # Risk gauge title with clickable card
    st.markdown("""
    <div class="clickable-card" id="risk-card">
        <div class="card-title">Risk Prediction SatO2 <65% in 10min</div>
        <div class="card-subtitle">Current Risk Assessment</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Show risk gauge with probability
    risk_gauge = create_risk_gauge(risk_score)
    risk_chart_placeholder = st.empty()
    risk_chart_placeholder.plotly_chart(risk_gauge, use_container_width=True, config={'displayModeBar': False})

# Main risk trend chart section with clickable button for summary
if len(st.session_state.trend_data['risk']) > 0:
    # Container for main trend chart
    st.markdown("<div class='main-trend-container'>", unsafe_allow_html=True)
    
    # Create button to toggle trend summary
    trend_summary_col1, trend_summary_col2 = st.columns([5, 1])
    
    with trend_summary_col2:
        st.markdown("""
        <div class="clickable-card" id="trend-summary-card" style="margin-top: 0; padding: 8px 5px;">
            <div class="card-title" style="font-size: 14px; margin-bottom: 0">Trend Summary</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Hidden button for trend summary
        summary_btn = st.button("Show Summary", key="show_summary_btn", label_visibility="collapsed")
        if summary_btn:
            st.session_state.show_trend_summary = not st.session_state.show_trend_summary
    
    # Create and display main trend chart
    main_trend_chart = create_main_risk_trend(
        st.session_state.trend_data['risk'],
        st.session_state.x_data if st.session_state.x_data else list(range(len(st.session_state.trend_data['risk'])))
    )
    
    st.plotly_chart(main_trend_chart, use_container_width=True, config={'displayModeBar': False})
    
    # Display trend summary if button was clicked
    if st.session_state.show_trend_summary:
        # Calculate trend statistics
        trend_stats = calculate_trend_stats(st.session_state.trend_data['risk'])
        
        st.markdown("""
        <div class="modal-dialog">
            <div class="modal-header">
                <div class="modal-title">Risk Trend Summary</div>
                <div class="modal-close" id="close-summary">✕</div>
            </div>
            <div class="modal-body">
        """, unsafe_allow_html=True)
        
        # Display trend statistics
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-label">Time with Risk >80%</div>
            <div class="stat-value">{trend_stats['high_risk_time']:.2f} min</div>
        </div>
        
        <div class="stat-box">
            <div class="stat-label">Time with Risk >90%</div>
            <div class="stat-value">{trend_stats['critical_risk_time']:.2f} min</div>
        </div>
        
        <div class="stat-box">
            <div class="stat-label">Average Risk</div>
            <div class="stat-value">{trend_stats['average_risk']:.1f}%</div>
        </div>
        
        <div class="stat-box">
            <div class="stat-label">Maximum Risk</div>
            <div class="stat-value">{trend_stats['max_risk']:.1f}%</div>
        </div>
        
        <div class="stat-box">
            <div class="stat-label">Trend Direction</div>
            <div class="stat-value">{trend_stats['trend_direction']}</div>
        </div>
        
        <div class="stat-box">
            <div class="stat-label">Time with Risk >65%</div>
            <div class="stat-value">{trend_stats['time_above_threshold']:.2f} min</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("</div></div>", unsafe_allow_html=True)
        
        # Button to close the modal
        if st.button("Close", key="close_summary_btn"):
            st.session_state.show_trend_summary = False
    
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

# Add JavaScript for clickable cards
st.markdown("""
<script>
    // Add click handlers to clickable cards
    document.addEventListener('DOMContentLoaded', function() {
        // Algorithm Metrics card
        const metricsCard = document.getElementById('metrics-card');
        if (metricsCard) {
            metricsCard.addEventListener('click', function() {
                // Find and click the hidden button
                const metricsBtn = document.querySelector('button[data-testid="baseButton-secondary"]');
                if (metricsBtn) metricsBtn.click();
            });
        }
        
        // Risk card - can be linked to trend summary later if needed
        const riskCard = document.getElementById('risk-card');
        if (riskCard) {
            riskCard.addEventListener('click', function() {
                // Action for clicking risk card
            });
        }
        
        // Trend Summary card
        const trendSummaryCard = document.getElementById('trend-summary-card');
        if (trendSummaryCard) {
            trendSummaryCard.addEventListener('click', function() {
                // Find and click the hidden button
                const summaryBtn = document.querySelector('button[data-testid="baseButton-secondary"]');
                if (summaryBtn) summaryBtn.click();
            });
        }
        
        // Close buttons for modals
        const closeMetricsBtn = document.getElementById('close-metrics');
        if (closeMetricsBtn) {
            closeMetricsBtn.addEventListener('click', function() {
                const closeBtn = document.querySelector('button[key="close_metrics_btn"]');
                if (closeBtn) closeBtn.click();
            });
        }
        
        const closeSummaryBtn = document.getElementById('close-summary');
        if (closeSummaryBtn) {
            closeSummaryBtn.addEventListener('click', function() {
                const closeBtn = document.querySelector('button[key="close_summary_btn"]');
                if (closeBtn) closeBtn.click();
            });
        }
    });
</script>
""", unsafe_allow_html=True)

# Automatic simulation (only run in automatic mode and when running)
if st.session_state.mode == "AUTOMÁTICO" and st.session_state.running:
    # Increment simulation time
    st.session_state.simulation_time += 0.1
    
    # Short pause for more realistic simulation
    time.sleep(0.1)
    
    # Use st.rerun() to update the page
    st.rerun()