import streamlit as st
import numpy as np
import plotly.graph_objects as go


def add_nodes(base_figure, x_values: list, y_values: list):
    # """
    #     Adds nodes as scatter points and lines to the figure.
    # """

    # Check if both lists are the same length and not empty
    if len(x_values) == len(y_values) and len(x_values) > 0:
        # Add scatter trace with orange markers
        base_figure.add_trace(
            go.Scatter(
                x=x_values,
                y=y_values,
                mode='markers+text',
                name='User Data',
                marker=dict(color='orange', size=10),
                # line=dict(color='deepskyblue'),
                text=[str(i + 1) for i in range(len(x_values))],  # Labels: 1, 2, 3, ...
                textfont=dict(color='black'),
                textposition='middle center'
            )
        )

        return base_figure


def add_member(base_figure,
               x_values: list,
               y_values: list,
               name,
               member_line_color: float | int):
    # """
    #     Adds members as scatter points as lines to the figure.
    # """

    # Check if both lists are the same length and not empty
    if len(x_values) == len(y_values) and len(x_values) > 0:
        # Add scatter trace with orange markers
        base_figure.add_trace(
            go.Scatter(
                x=x_values,
                y=y_values,
                mode='lines',
                name=f"Member {name}",
                # marker=dict(color='orange', size=11),
                line=dict(color=member_line_color),
                # text=[str(i+1) for i in range(len(x_values))], # Labels: 1, 2, 3, ...
                # text=member_labels,  # Labels: 1, 2, 3, ...
                # textfont=dict(color='black', size=10),
                # textposition='middle center'
            )
        )


def rotate_point(x, y, theta_deg):
    theta = np.radians(theta_deg)
    x_rot = x * np.cos(theta) - y * np.sin(theta)
    y_rot = x * np.sin(theta) + y * np.cos(theta)
    return x_rot, y_rot


import plotly.graph_objects as go


def add_arrow(fig, arrow_tip: list, arrow_end: list, width=1.5, color='rgb(255,51,0)', head=3):
    """
    Adds a single arrow to a Plotly figure.

    Parameters:
    - fig: Plotly figure object
    - arrow_tip: [x0, y0] where the arrow points to
    - arrow_end: [x1, y1] where the arrow starts
    - length: arrow width (default 1.5)
    - color: arrow color (default red-orange)
    - head: arrowhead style (default 3)
    """
    arrow = go.layout.Annotation(
        x=arrow_tip[0],
        y=arrow_tip[1],
        xref="x",
        yref="y",
        text="",
        showarrow=True,
        axref="x",
        ayref="y",
        ax=arrow_end[0],
        ay=arrow_end[1],
        arrowhead=head,
        arrowwidth=width,
        arrowcolor=color
    )

    fig.update_layout(annotations=[arrow])


# Function for creating arrows on nodes
def add_nodal_arrow(fig,
                    arrow_tip_or_node: list,
                    direction: str,
                    magnitude: float = None,
                    arrow_length=1.00,
                    width=1.5,
                    color='rgb(255,51,0)',
                    head=3):

    arrow_tip = np.array(arrow_tip_or_node)

    # Determine arrow end based on direction and magnitude text position
    if direction == '↑':
        length = np.array([0, arrow_length])
        arrow_end = arrow_tip - length
        mag_text_pos = arrow_tip - length - length / 4
    elif direction == "↓":
        length = np.array([0, arrow_length])
        arrow_end = arrow_tip + length
        mag_text_pos = arrow_tip + length + length / 4
    elif direction == "←":
        length = np.array([arrow_length, 0])
        arrow_end = arrow_tip + length
        mag_text_pos = arrow_tip + length + length
    elif direction == "→":
        length = np.array([arrow_length, 0])
        arrow_end = arrow_tip - length
        mag_text_pos = arrow_tip - length - length
    else:
        raise ValueError("Invalid direction. Use '↑', '↓', '←', or '→'.")

    # Arrow annotation
    arrow = go.layout.Annotation(
        x=arrow_tip[0],
        y=arrow_tip[1],
        xref="x",
        yref="y",
        text="",
        showarrow=True,
        axref="x",
        ayref="y",
        ax=arrow_end[0],
        ay=arrow_end[1],
        arrowhead=head,
        arrowwidth=width,
        arrowcolor=color
    )

    # Add arrow to figure annotations
    if fig.layout.annotations:
        fig.layout.annotations += (arrow,)
    else:
        fig.layout.annotations = (arrow,)

    # Magnitude text at arrow end
    if magnitude is not None:
        magnitude_annot = go.layout.Annotation(
            x=mag_text_pos[0],
            y=mag_text_pos[1],
            xref="x",
            yref="y",
            text=f"{magnitude}",
            showarrow=False,
            font=dict(color=color, size=10)
        )

        if fig.layout.annotations:
            fig.layout.annotations += (magnitude_annot,)
        else:
            fig.layout.annotations = (magnitude_annot,)

# Add the moments symbol with respect to node coordinates
def add_nodal_moments(fig, node: list,
                      direction: str,
                      magnitude: float = None,
                      size=14,
                      color='rgb(255,51,0)',
                      magnitude_offset=0.2):
    """
    Adds a nodal moment symbol (↻ or ↺) with optional magnitude displayed above the symbol.

    Parameters:
    - fig: Plotly figure object
    - node: [x, y] coordinates where moment is applied
    - direction: "↻" or "↺"
    - magnitude: numeric value displayed above the symbol
    - size: font size of the symbol
    - color: color of the symbol
    - magnitude_offset: vertical offset for magnitude label
    """
    if direction not in ["↻", "↺"]:
        raise ValueError("Direction must be either '↻' (clockwise) or '↺' (counter-clockwise)")

    # Moment symbol annotation
    symbol_annot = go.layout.Annotation(
        x=node[0],
        y=node[1],
        xref="x",
        yref="y",
        text=direction,
        showarrow=False,
        font=dict(size=size, color=color)
    )

    annotations = [symbol_annot]

    # Magnitude annotation positioned above
    if magnitude is not None:
        magnitude_annot = go.layout.Annotation(
            x=node[0],
            y=node[1] + magnitude_offset,
            xref="x",
            yref="y",
            text=f"{magnitude}",
            showarrow=False,
            font=dict(size=size * 0.8, color=color)
        )
        annotations.append(magnitude_annot)

    # Add annotations
    if fig.layout.annotations:
        fig.layout.annotations += tuple(annotations)
    else:
        fig.layout.annotations = tuple(annotations)

def draw_support_triangle(fig, x_sup, orientation="up", row=None, col=None):
    """Draw an anchored triangle on a plotly figure.

    Parameters
    ----------
    fig : plotly figure         to append arrow shape to.
    x_sup : int
        The x position for the arrow to be anchored to.
    orientation : 'up' or 'right, optional
        direction that the arrow faces, by default "up"
    row : int or None,
        Row of subplot to draw line on. If None specified assumes a full plot,
        by default None.
    col : int or None,
        Column of subplot to draw line on. If None specified assumes a full
        plot, by default None.


    Returns
    -------
    plotly figure
        Returns the plotly figure passed into function with the triangle
        appended to it.
    """

    if orientation in ['up', 'right']:

        # Define the triangle as a point using the scatter marker.
        trace = go.Scatter(
            x=[x_sup],
            y=[0],
            fill="toself",
            showlegend=False,
            mode="markers",
            name='Support',
            marker=dict(
                symbol="arrow-" + orientation,
                size=10,
                color='blue'),
            hovertemplate=None,
            hoverinfo="skip")

        # Append trace to plot or subplot
        if row and col:
            fig.add_trace(trace, row=row, col=col)
        else:
            fig.add_trace(trace)

    return fig


st.title("🔄 Line Rotation Visualizer")
st.set_page_config(layout='wide')

st.write("Define the line endpoints:")

col1, col2 = st.columns([0.2, 0.8])

with col1:
    x0 = st.number_input("X0", value=0.0)
    y0 = st.number_input("Y0", value=0.0)
    x1 = st.number_input("X1", value=3.0)
    y1 = st.number_input("Y1", value=3.0)

    angle = st.number_input("Rotation Angle (degrees)", min_value=-360, max_value=360, value=0, step=1)

# Rotate endpoints
A_rot = x0, y0
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
    showlegend=True,
    xaxis=dict(
        title=f'X',
        showgrid=True
    ),
    yaxis=dict(
        title=f'Y',
        showgrid=True,
        scaleanchor="x"  # Equal scaling
    )
)

add_nodal_arrow(fig=fig,
                arrow_tip_or_node=[4, 4],
                direction="↓",
                arrow_length=0.2,
                magnitude=3)

add_nodal_moments(fig=fig,
                  node=[3, 3],
                  direction="↻",
                  magnitude='20',
                  size=30)



fig.update_yaxes(scaleanchor="x", scaleratio=1)

with col2:
    st.plotly_chart(fig, use_container_width=True)

