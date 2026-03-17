import streamlit as st
import numpy as np
import plotly.graph_objects as go

def rotate_point(x, y, theta_deg):
    theta = np.radians(theta_deg)
    x_rot = x * np.cos(theta) - y * np.sin(theta)
    y_rot = x * np.sin(theta) + y * np.cos(theta)
    return x_rot, y_rot

st.title("🔄 Line Rotation Visualizer")

st.write("Define the line endpoints:")

col1, col2 = st.columns(2)

with col1:
    x0 = st.number_input("X0", value=0.0)
    y0 = st.number_input("Y0", value=0.0)
    x1 = st.number_input("X1", value=3.0)
    y1 = st.number_input("Y1", value=3.0)

    angle = st.slider("Rotation Angle (degrees)", min_value=-360, max_value=360, value=0, step=1)

# Rotate endpoints
A_rot = rotate_point(x0, y0, angle)
B_rot = rotate_point(x1, y1, angle)

# Plot
fig = go.Figure()

# Original line
fig.add_trace(go.Scatter(
    x=[x0, x1],
    y=[y0, y1],
    mode='lines+markers',
    line=dict(color='lightgray', dash='dash'),
    marker=dict(color='gray', size=6),
    name="Original Line"
))

# Rotated line
fig.add_trace(go.Scatter(
    x=[A_rot[0], B_rot[0]],
    y=[A_rot[1], B_rot[1]],
    mode='lines+markers',
    line=dict(color='blue'),
    marker=dict(color='red', size=8),
    name=f"Rotated Line ({angle}°)"
))

fig.update_layout(
    title="Rotated Line Visualization",
    xaxis_title="X",
    yaxis_title="Y",
    width=700,
    height=600,
    showlegend=True
)
fig.update_yaxes(scaleanchor="x", scaleratio=1)

with col2:
    st.plotly_chart(fig, use_container_width=True)
