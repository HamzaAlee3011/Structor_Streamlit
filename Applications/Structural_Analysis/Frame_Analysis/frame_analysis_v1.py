import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from Pynite.FEModel3D import FEModel3D
import math

# Unknown error
# Initialize Member Point Loads (MPL) member list if not present
if 'mpl_members_list' not in st.session_state:
    st.session_state.mpl_members_list = []

# Initialize Member Point Moments (MPM) member list if not present
if 'mpm_members_list' not in st.session_state:
    st.session_state.mpm_members_list = []

if 'mdl_members_list' not in st.session_state:
    st.session_state.mdl_members_list = []


# === SECTION 1 === Plotly Drawing Aid Functions =====================================================
# def draw_fixed_support(fig, node: list, size=0.2, color="rgba(0, 0, 255, 0.7)", line_width=2):
#     """
#     Draws a fixed support symbol as a filled square centered at the contact_point.
#
#     Parameters:
#     - fig: Plotly figure to draw on
#     - contact_point: [x, y] coordinate at center of square
#     - size: side length of the square
#     - color: color of the square
#     - line_width: border width of the square
#     """
#
#     x_center = node[0]
#     y_center = node[1]
#
#     # Calculate square bounds
#     x0 = x_center - size / 2
#     x1 = x_center + size / 2
#     y0 = y_center - size / 2
#     y1 = y_center + size / 2
#
#     fig.add_shape(
#         type="rect",
#         xref="x", yref="y",
#         x0=x0, y0=y0,
#         x1=x1, y1=y1,
#         line=dict(color=color, width=line_width),
#         fillcolor=color
#     )
#
#     return fig

def draw_fixed_support(fig, node: list, size=12, color="rgba(0, 0, 255, 0.7)", row=None, col=None):
    """
    Draws a fixed support symbol as a square marker at the node position.

    Parameters:
    - fig: Plotly figure to draw on
    - node: [x, y] coordinate
    - size: marker size (not axis-scaled)
    - color: marker fill color (supports alpha)
    - row, col: For subplots (optional)
    """
    trace = go.Scatter(
        x=[node[0]],
        y=[node[1]],
        mode="markers",
        marker=dict(
            symbol="square",
            size=size,
            color=color
        ),
        name="Fixed Support",
        showlegend=False,
        hoverinfo="skip"
    )

    if row and col:
        fig.add_trace(trace, row=row, col=col)
    else:
        fig.add_trace(trace)

    return fig


def draw_roller_support(fig, node: list, color='blue', size=18, position='Roller (horizontal-bottom)'):
    """
    Draws a roller support using the Unicode symbol ⁍ at a given node position,
    with rotation based on support orientation.

    Parameters:
    - fig: Plotly figure object
    - node: [x, y] coordinate of the support
    - color: color of the symbol
    - size: font size
    - position: one of ['Roller (horizontal-bottom)', 'Roller (horizontal-top)',
                        'Roller (vertical-left)', 'Roller (vertical-right)']
    """

    x, y = node
    text_angle = 0
    x_offset = 0
    y_offset = 0

    # Determine rotation and offset based on orientation
    if position == 'Roller (horizontal-bottom)':
        text_angle = -90
        y_offset = 0
    elif position == 'Roller (horizontal-top)':
        text_angle = 90
        y_offset = 0
    elif position == 'Roller (vertical-left)':
        text_angle = 0
        x_offset = 0
    elif position == 'Roller (vertical-right)':
        text_angle = 180
        x_offset = 0
    else:
        raise ValueError(f"Unknown roller position: {position}")

    fig.add_annotation(
        x=x + x_offset,
        y=y + y_offset,
        text='Þ',
        showarrow=False,
        font=dict(size=size, color=color),
        textangle=text_angle,
        xanchor='center',
        yanchor='middle'
    )

    return fig


def draw_support_triangle(fig, node, size=12, orientation="up", row=None, col=None, color="rgba(0, 0, 255, 0.7)"):
    """Draw an anchored triangle on a plotly figure.

    Parameters
    ----------
    fig : plotly figure         to append arrow shape to.
    node : list
        The node position for the arrow to be anchored to.
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
        :param color:
    """

    if orientation in ['up', 'right']:

        # Define the triangle as a point using the scatter marker.
        trace = go.Scatter(
            x=[node[0]],
            y=[node[1]],
            fill="toself",
            showlegend=False,
            mode="markers",
            name='Support',
            marker=dict(
                symbol="arrow-" + orientation,
                size=size,
                color=color),
            hovertemplate=None,
            hoverinfo="skip")

        # Append trace to plot or subplot
        if row and col:
            fig.add_trace(trace, row=row, col=col)
        else:
            fig.add_trace(trace)

    return fig


# Add nodes to graph
def add_nodes(base_figure,
              x_values: list,
              y_values: list,
              node_labels: list,
              node_label_color: float | int,
              node_label_size: float | int,
              node_marker_size: float | int,
              node_marker_color: float | int,
              show_in_legend=True
              ):
    # """
    #     Adds nodes as scatter points to the figure.
    # """

    # Check if both lists are the same length and not empty
    if len(x_values) == len(y_values) and len(x_values) > 0:
        # Add scatter trace with orange markers
        base_figure.add_trace(
            go.Scatter(
                x=x_values,
                y=y_values,
                mode='markers+text',
                name='Nodes',
                marker=dict(color=node_marker_color, size=node_marker_size),
                # line=dict(color='deepskyblue'),
                # text=[str(i+1) for i in range(len(x_values))], # Labels: 1, 2, 3, ...
                text=[f"<b>{label}</b>" for label in node_labels],  # Labels: 1, 2, 3, ...
                textfont=dict(color=node_label_color, size=node_label_size),
                textposition='middle center',
                showlegend=show_in_legend
            )
        )


def add_support_settlement_symbol(fig, node: list, direction='X', label='', size=18, color='skyblue'):
    """
    Add a support movement/settlement symbol to a Plotly figure.

    Parameters:
    - fig: Plotly Figure object to add the symbol to
    - node [x, y]: Coordinates of the node
    - direction: 'X', 'Y', or 'Rotation'
    - label: Text to show on right side of symbol (e.g., 'X', 'Y', 'θ')
    - size: Font size of the symbol
    - color: Color of symbol and label
    """

    x = node[0]
    y = node[1]

    offset = 0.45  # Horizontal offset from node
    spacing = 0.15  # Gap between symbol and label

    if direction == 'X':
        symbol = '↔'
        text_angle = 0
        symbol_x = x + offset
        symbol_y = y
        label_x = symbol_x + spacing
        label_y = symbol_y

    elif direction == 'Y':
        symbol = '↔'
        text_angle = 90
        symbol_x = x + offset
        symbol_y = y
        label_x = symbol_x + spacing
        label_y = symbol_y

    elif direction == 'Rotation':
        symbol = '𝚹'
        text_angle = 0
        symbol_x = x + offset
        symbol_y = y
        label_x = symbol_x + spacing
        label_y = symbol_y

    else:
        raise ValueError("Direction must be 'X', 'Y', or 'Rotation'")

    # Plot the symbol
    fig.add_annotation(
        x=symbol_x,
        y=symbol_y,
        text=f'    {symbol}',
        showarrow=False,
        font=dict(size=size, color=color),
        textangle=text_angle,
        xanchor='center',
        yanchor='middle'
    )

    # Plot the label on the right of symbol
    if label:
        fig.add_annotation(
            x=label_x,
            y=label_y,
            text=f'      {label}',
            showarrow=False,
            font=dict(size=size - 8, color=color),
            textangle=text_angle,
            xanchor='left',
            yanchor='middle'
        )


# Adds lines as members to graph
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


# Function to add moment arrows to in between members
def add_member_point_moments_symbol(fig, member: str,
                                    load_position: float,
                                    direction: str,
                                    magnitude=None,
                                    mag_offset=0.2,
                                    marker_color='rgb(255,51,0)',
                                    label_color='rgb(255,51,0)',
                                    label_size=10):
    """
    Adds a moment symbol (↺ or ↻) to a member for point moment representation.
    Magnitude text is rotated along the perpendicular direction.
    """

    # Get the member coordinates from Streamlit session state
    x1 = st.session_state.members_data[f'{member}']['Start Node Value'][0]
    y1 = st.session_state.members_data[f'{member}']['Start Node Value'][1]
    x2 = st.session_state.members_data[f'{member}']['End Node Value'][0]
    y2 = st.session_state.members_data[f'{member}']['End Node Value'][1]

    start = np.array([x1, y1], dtype=float)
    end = np.array([x2, y2], dtype=float)

    # Member vector
    member_vec = end - start
    member_length = np.linalg.norm(member_vec)
    if member_length == 0:
        raise ValueError("Member length is zero, cannot draw symbol.")

    # Unit vector along member
    member_dir = member_vec / member_length

    # Perpendicular vector (rotate by +90° CCW)
    perp_dir = np.array([-member_dir[1], member_dir[0]])

    # Flip perpendicular vector for CW rotation
    if direction == '↻':
        perp_dir = -perp_dir
    elif direction != '↺':
        raise ValueError("Invalid direction. Use '↺' or '↻'.")

    # Symbol position
    symbol_pos = start + member_vec * load_position

    # Rotation angle for magnitude text
    text_angle = math.degrees(math.atan2(perp_dir[1], perp_dir[0]))

    # Add the moment symbol itself
    fig.add_annotation(
        x=symbol_pos[0],
        y=symbol_pos[1],
        text=direction,
        showarrow=False,
        font=dict(color=marker_color, size=label_size)  # slightly larger
    )

    # Add magnitude text if provided
    if magnitude is not None:
        mag_pos = symbol_pos + perp_dir * mag_offset
        fig.add_annotation(
            x=mag_pos[0],
            y=mag_pos[1],
            text=f"{magnitude} {units_dict[unit_systems]['Placeholder']['M']}",
            showarrow=False,
            textangle=0,
            font=dict(color=label_color, size=label_size - 15),
            xanchor='left',
            yanchor='top'
        )


# Functon to add Point arrows to in between members
def add_member_point_load_arrow(fig, member: str,
                                load_position: float,
                                direction: str,
                                arrow_length=1.0,
                                magnitude=None,
                                width=1.5,
                                marker_color='rgb(255,51,0)',
                                label_color='rgb(255,51,0)',
                                label_size=10,
                                head=3):
    """
    Adds a perpendicular arrow to a member for point load representation.
    Magnitude text is rotated along the arrow direction.
    """

    # Gets the member coordinates from Streamlit session state
    x1 = st.session_state.members_data[f'{member}']['Start Node Value'][0]
    y1 = st.session_state.members_data[f'{member}']['Start Node Value'][1]
    x2 = st.session_state.members_data[f'{member}']['End Node Value'][0]
    y2 = st.session_state.members_data[f'{member}']['End Node Value'][1]

    start_point = [x1, y1]
    end_point = [x2, y2]

    # Convert to NumPy arrays
    start = np.array(start_point, dtype=float)
    end = np.array(end_point, dtype=float)

    # Member vector
    member_vec = end - start
    member_length = np.linalg.norm(member_vec)

    if member_length == 0:
        raise ValueError("Member length is zero, cannot draw arrow.")

    # Unit vector along member
    member_dir = member_vec / member_length

    # Perpendicular vector (rotate by +90° CCW)
    perp_dir = np.array([-member_dir[1], member_dir[0]])

    text_angle_rot = None

    # Flip if direction is '↑'
    if direction == '↑':
        perp_dir = -perp_dir
    elif direction != '↓':
        raise ValueError("Invalid direction. Use '↑' or '↓'.")

    # Load application point
    load_point = start + member_vec * load_position

    # Arrow tip and end
    arrow_tip = load_point
    arrow_end = load_point + perp_dir * arrow_length

    # Text position a bit beyond arrow end
    mag_text_pos = arrow_end + perp_dir * (arrow_length * 0.25)

    # Compute rotation angle for text in degrees
    text_angle = math.degrees(math.atan2(perp_dir[1], perp_dir[0]))

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
        arrowcolor=marker_color
    )

    if fig.layout.annotations:
        fig.layout.annotations += (arrow,)
    else:
        fig.layout.annotations = (arrow,)

    # Magnitude label
    if magnitude is not None:
        magnitude_annot = go.layout.Annotation(
            x=mag_text_pos[0],
            y=mag_text_pos[1],
            xref="x",
            yref="y",
            text=f"{magnitude} {units_dict[unit_systems]['Placeholder']['F']}",
            textangle=text_angle - 90,
            showarrow=False,
            font=dict(color=label_color, size=label_size)
        )

        fig.layout.annotations += (magnitude_annot,)

        # Example usage:
        # fig = go.Figure()
        # add_member_point_load_arrow(fig, [0, 0], [5, 3], load_position=0.5, direction='up', arrow_length=0.5, magnitude='10 kN')
        # fig.show()


# Function for creating arrows on nodes
def add_nodal_arrow(fig, arrow_tip_or_node: list,
                    direction: str,
                    magnitude: float = None,
                    arrow_length=1.00,
                    width=1.5,
                    marker_color='rgb(255,51,0)',
                    label_color='rgb(255,51,0)',
                    label_size=10,
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
        arrowcolor=marker_color
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
            font=dict(color=label_color, size=label_size)
        )

        if fig.layout.annotations:
            fig.layout.annotations += (magnitude_annot,)
        else:
            fig.layout.annotations = (magnitude_annot,)


# Add the moments symbol with respect to node coordinates
def add_nodal_moments(fig, node: list,
                      direction: str,
                      magnitude: float = None,
                      marker_color='rgb(255,51,0)',
                      marker_size=30,
                      label_color='rgb(255,51,0)',
                      label_size=10,
                      magnitude_offset=0.75):
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
        font=dict(size=marker_size, color=marker_color)
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
            font=dict(size=label_size, color=label_color)
        )
        annotations.append(magnitude_annot)

    # Add annotations
    if fig.layout.annotations:
        fig.layout.annotations += tuple(annotations)
    else:
        fig.layout.annotations = tuple(annotations)


def add_reaction_moments(fig, node: list,
                         direction: str,
                         magnitude: float = None,
                         marker_color='rgb(255,51,0)',
                         marker_size=30,
                         label_color='rgb(255,51,0)',
                         label_size=10,
                         magnitude_offset=0.75):
    """
    Adds a rotated moment reaction symbol (↶ or ↷) to indicate a reaction moment,
    with optional magnitude label below.

    Parameters:
    - fig: Plotly figure object
    - node: [x, y] coordinates of the reaction
    - direction: "↶" or "↷"
    - magnitude: optional float, shown below the symbol
    - marker_color: color of the moment symbol
    - marker_size: size of the symbol
    - label_color: color of magnitude label
    - label_size: size of magnitude label
    - magnitude_offset: vertical distance below the symbol
    """
    if direction not in ["↶", "↷"]:
        raise ValueError("Direction must be either '↶' (anticlockwise) or '↷' (clockwise)")

    symbol_annot = go.layout.Annotation(
        x=node[0],
        y=node[1],
        xref="x",
        yref="y",
        text=direction,
        showarrow=False,
        textangle=180,  # Rotate to appear bottom-oriented
        font=dict(size=marker_size, color=marker_color)
    )

    annotations = [symbol_annot]

    if magnitude is not None:
        magnitude_annot = go.layout.Annotation(
            x=node[0],
            y=node[1] - magnitude_offset,
            xref="x",
            yref="y",
            text=f"{magnitude}",
            showarrow=False,
            font=dict(size=label_size, color=label_color)
        )
        annotations.append(magnitude_annot)

    if fig.layout.annotations:
        fig.layout.annotations += tuple(annotations)
    else:
        fig.layout.annotations = tuple(annotations)


def add_member_distributed_load_global_axis(fig,
                                            member,
                                            x1: float, x2: float,
                                            mag1: float, mag2: float,
                                            direction: str,
                                            arrow_length=1.0,
                                            color='rgba(255,51,0,0.5)',
                                            line_color='rgb(255,51,0)',
                                            width=1.5,
                                            head=3,
                                            label_color='rgb(255,51,0)',
                                            label_size=10):
    """
    Adds a distributed load (trapezoidal/rectangular) on a member in global axis directions.
    """

    # Gets the member coordinates
    x1_point = st.session_state.members_data[f'{member}']['Start Node Value'][0]
    y1_point = st.session_state.members_data[f'{member}']['Start Node Value'][1]
    x2_point = st.session_state.members_data[f'{member}']['End Node Value'][0]
    y2_point = st.session_state.members_data[f'{member}']['End Node Value'][1]

    node_start = [x1_point, y1_point]
    node_end = [x2_point, y2_point]

    start = np.array(node_start)
    end = np.array(node_end)
    member_vec = end - start
    member_len = np.linalg.norm(member_vec)
    member_unit = member_vec / member_len

    # Global direction vectors
    if direction == '↑':
        dir_vec = np.array([0, -1])
    elif direction == '↓':
        dir_vec = np.array([0, 1])
    elif direction == '→':
        dir_vec = np.array([-1, 0])
    elif direction == '←':
        dir_vec = np.array([1, 0])
    else:
        raise ValueError("Invalid direction. Use '↑', '↓', '←', or '→'.")

    if all(x is not None for x in [x1, x2, mag1, mag2]):

        # Points on the member at x1, x2
        p1 = start + member_unit * x1
        p2 = start + member_unit * x2

        # Arrow tips
        tip1 = p1
        tip2 = p2

        if mag1 > mag2:
            mag1_length = 2
            mag2_length = 1
        elif mag1 < mag2:
            mag1_length = 1
            mag2_length = 2
        else:
            mag1_length = mag2_length = 1.5  # equal case

        # reference visual height is e.g. 10% of max member length
        target_ratio = 0.25
        ref_height = target_ratio * calculate_member_length(member)
        scale = ref_height / abs(x1 - x2)

        # Arrow ends (in load direction)
        end1 = tip1 + dir_vec * mag1_length * arrow_length * round(scale, 4)
        end2 = tip2 + dir_vec * mag2_length * arrow_length * round(scale, 4)

        # Draw arrows (using Plotly annotation like nodal arrows)
        for tip, end in [(tip1, end1), (tip2, end2)]:
            arrow = go.layout.Annotation(
                x=tip[0], y=tip[1],
                xref="x", yref="y",
                text="", showarrow=True,
                ax=end[0], ay=end[1],
                axref="x", ayref="y",
                arrowhead=head, arrowwidth=width,
                arrowcolor=line_color
            )
            if fig.layout.annotations:
                fig.layout.annotations += (arrow,)
            else:
                fig.layout.annotations = (arrow,)

        # Add magnitude labels
        for end, mag in [(end1, mag1), (end2, mag2)]:
            label = go.layout.Annotation(
                x=end[0], y=end[1],
                xref="x", yref="y",
                text=f"{mag} {units_dict[unit_systems]['Placeholder']['F']}",
                showarrow=False,
                font=dict(color=label_color, size=label_size)
            )
            if fig.layout.annotations:
                fig.layout.annotations += (label,)
            else:
                fig.layout.annotations = (label,)

        # Polygon (trapezoid)
        x_poly = [tip1[0], tip2[0], end2[0], end1[0], tip1[0]]
        y_poly = [tip1[1], tip2[1], end2[1], end1[1], tip1[1]]

        fig.add_trace(go.Scatter(
            x=x_poly, y=y_poly,
            mode="lines",
            fill="toself",
            # fillcolor=color,
            line=dict(color=line_color, width=1),
            showlegend=False
        ))

        return fig


def add_member_distributed_load_local_axis(fig,
                                           member,
                                           x1: float, x2: float,
                                           mag1: float, mag2: float,
                                           direction: str,
                                           arrow_length=1.0,
                                           color='rgba(255,51,0,0.5)',
                                           line_color='rgb(255,51,0)',
                                           width=1.5,
                                           head=3,
                                           label_color='rgb(255,51,0)',
                                           label_size=10):
    """
    Adds a distributed load (trapezoidal/rectangular) on a member
    in local axis directions (perpendicular to member axis).

    Parameters
    ----------
    fig : go.Figure
        Plotly figure to update.
    member : str
        Member key from session_state.
    x1, x2 : float
        Distances along the member length (0=start, L=end).
    mag1, mag2 : float
        Magnitudes of distributed load at x1 and x2.
    direction : str
        Local load direction ["↑", "↓"].
    arrow_length : float
        Base arrow scaling.
    """

    # Get member coordinates
    x1_point = st.session_state.members_data[f'{member}']['Start Node Value'][0]
    y1_point = st.session_state.members_data[f'{member}']['Start Node Value'][1]
    x2_point = st.session_state.members_data[f'{member}']['End Node Value'][0]
    y2_point = st.session_state.members_data[f'{member}']['End Node Value'][1]

    start = np.array([x1_point, y1_point], dtype=float)
    end = np.array([x2_point, y2_point], dtype=float)

    member_vec = end - start
    member_len = np.linalg.norm(member_vec)

    if member_len == 0:
        raise ValueError("Member length is zero, cannot draw load.")

    # Unit vectors
    member_unit = member_vec / member_len
    perp_dir = np.array([-member_unit[1], member_unit[0]])  # local axis ⟂

    # Flip for "↑"
    if direction == '↑':
        perp_dir = -perp_dir
    elif direction != '↓':
        raise ValueError("Invalid direction. Use '↑' or '↓'.")

    # Points on the member at x1, x2
    p1 = start + member_unit * x1
    p2 = start + member_unit * x2

    # Arrow tips
    tip1, tip2 = p1, p2

    # Scale magnitudes relative
    mag1_len = (mag1 / max(mag1, mag2)) * arrow_length
    mag2_len = (mag2 / max(mag1, mag2)) * arrow_length

    # Arrow ends
    end1 = tip1 + perp_dir * mag1_len
    end2 = tip2 + perp_dir * mag2_len

    # Draw arrows
    for tip, end in [(tip1, end1), (tip2, end2)]:
        arrow = go.layout.Annotation(
            x=tip[0], y=tip[1],
            xref="x", yref="y",
            text="", showarrow=True,
            ax=end[0], ay=end[1],
            axref="x", ayref="y",
            arrowhead=head, arrowwidth=width,
            arrowcolor=line_color
        )
        fig.layout.annotations += (arrow,)

    # Polygon (trapezoid)
    x_poly = [tip1[0], tip2[0], end2[0], end1[0], tip1[0]]
    y_poly = [tip1[1], tip2[1], end2[1], end1[1], tip1[1]]

    fig.add_trace(go.Scatter(
        x=x_poly, y=y_poly,
        mode="lines",
        fill="toself",
        # fillcolor=color,
        line=dict(color=line_color, width=1),
        showlegend=False
    ))

    # Add magnitude labels
    for end, mag in [(end1, mag1), (end2, mag2)]:
        text_angle = math.degrees(math.atan2(perp_dir[1], perp_dir[0])) - 90
        mag_label = go.layout.Annotation(
            x=end[0], y=end[1],
            xref="x", yref="y",
            text=f"{mag} {units_dict[unit_systems]['Placeholder']['F']}",
            textangle=text_angle,
            showarrow=False,
            font=dict(color=label_color, size=label_size)
        )
        fig.layout.annotations += (mag_label,)

    return fig


# Calculates the member length
def calculate_member_length(member=str):
    # Gets the member coordinates
    x1 = st.session_state.members_data[f'{member}']['Start Node Value'][0]
    y1 = st.session_state.members_data[f'{member}']['Start Node Value'][1]
    x2 = st.session_state.members_data[f'{member}']['End Node Value'][0]
    y2 = st.session_state.members_data[f'{member}']['End Node Value'][1]

    member_length = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    return float(member_length)


# === SECTION 1 === Functions ===============================================================================
# Displays the Complete Model Figure (includes everything)
def Plot_Model(title='Diagram',
               show_nodes=True,
               show_members=True,
               show_member_labels=False,
               show_Nodal_Point_Loads=True,
               show_Nodal_Point_Moments=True,
               show_Member_Point_Loads=True,
               show_Member_Moments=True,
               show_Member_Distributed_Loads=True,
               show_supports=True,
               show_reactions=False,
               show_settlements=True):
    fig = go.Figure()

    if show_members == True:
        for member in range(len(st.session_state.members_data)):
            x1 = st.session_state.members_data[f'{member}']['Start Node Value'][0]
            y1 = st.session_state.members_data[f'{member}']['Start Node Value'][1]
            x2 = st.session_state.members_data[f'{member}']['End Node Value'][0]
            y2 = st.session_state.members_data[f'{member}']['End Node Value'][1]

            add_member(base_figure=fig,
                       x_values=[x1, x2],
                       y_values=[y1, y2],
                       name=member,
                       member_line_color=member_line_color)

            if show_member_labels == True:
                # Midpoint
                mid_point_x = (x1 + x2) / 2
                mid_point_y = (y1 + y2) / 2

                # Direction vector
                dx = x2 - x1
                dy = y2 - y1
                length = (dx ** 2 + dy ** 2) ** 0.5
                if length == 0:
                    continue

                dx /= length
                dy /= length

                # Offset along the member direction
                offset = 0.15
                label_x = mid_point_x + offset * dx
                label_y = mid_point_y + offset * dy

                # Calculate angle in degrees for text rotation
                angle_rad = math.atan2(dy, dx)
                angle_deg = math.degrees(angle_rad)

                # Keep text upright (rotate only between -90 and 90 degrees)
                if angle_deg > 90:
                    angle_deg -= 180
                elif angle_deg < -90:
                    angle_deg += 180

                # Add annotation
                fig.add_annotation(
                    x=label_x,
                    y=label_y,
                    text=f"M{member}",
                    showarrow=False,
                    font=dict(color='green', size=12),
                    textangle=angle_deg - 90,
                    xanchor="center",
                    yanchor="top",
                )

    if show_nodes == True:
        # Add Nodes to Display Model
        add_nodes(base_figure=fig,
                  x_values=node_x,
                  y_values=node_y,
                  node_labels=node_index_values,
                  node_label_color=node_label_color,
                  node_label_size=node_label_size,
                  node_marker_size=node_marker_size,
                  node_marker_color=node_marker_color)

    if show_Nodal_Point_Loads == True:
        # Add Nodal Point Load arrows to Model
        for arrows in range(len(st.session_state.npl_node_list)):
            # Gets the index of one by one from the Nodal Point Loads respective lists
            selected_node = st.session_state.npl_node_list[arrows]
            direction = st.session_state.npl_direction_list[arrows]
            mag = st.session_state.npl_mag_list[arrows]

            # st.write(arrows)
            add_nodal_arrow(fig=fig,
                            arrow_tip_or_node=st.session_state.nodes_data[selected_node],
                            # Gets the Node coordinates
                            magnitude=f"{mag} {units_dict[unit_systems]['Placeholder']['F']}",
                            # from the nodes data dictionary
                            direction=direction,
                            arrow_length=1 * loads_marker_size,
                            marker_color=load_marker_color,
                            label_color=loads_label_color,
                            label_size=loads_label_size)

    if show_Nodal_Point_Moments == True:
        # Add Nodal Point Moments to Model
        for moment in range(len(st.session_state.npm_node_list)):
            # Gets the index of one by one from the Nodal Point Loads respective lists
            selected_node = st.session_state.npm_node_list[moment]
            direction = st.session_state.npm_direction_list[moment]
            mag = st.session_state.npm_mag_list[moment]

            # st.write(arrows)
            add_nodal_moments(fig=fig,
                              node=st.session_state.nodes_data[selected_node],  # Gets the Node coordinates
                              magnitude=f"{mag} {units_dict[unit_systems]['Placeholder']['M']}",
                              # from the nodes data dictionary
                              direction=direction,
                              marker_size=30 * loads_marker_size,
                              marker_color=load_marker_color,
                              label_size=loads_label_size,
                              label_color=loads_label_color)

    if show_Member_Point_Loads == True:
        # Add Member Point Load arrows to Model
        for i in range(len(st.session_state.mpl_members_list)):
            # Gets the index of one by one from the Member Point Load respective lists
            member_id = st.session_state.mpl_members_list[i]
            location = st.session_state.mpl_location_list[i]
            direction = st.session_state.mpl_direction_list[i]
            mag = st.session_state.mpl_mag_list[i]

            add_member_point_load_arrow(fig,
                                        member=member_id,
                                        load_position=location / calculate_member_length(member_id),
                                        direction=str(direction),
                                        arrow_length=loads_marker_size,
                                        magnitude=mag,
                                        marker_color=load_marker_color,
                                        label_color=load_marker_color)

    if show_Member_Moments == True:
        # Add Member Point Load arrows to Model
        for i in range(len(st.session_state.mpm_members_list)):
            # Gets the index of one by one from the Member Point Load respective lists
            member_id = st.session_state.mpm_members_list[i]
            location = st.session_state.mpm_location_list[i]
            direction = st.session_state.mpm_direction_list[i]
            mag = st.session_state.mpm_mag_list[i]

            add_member_point_moments_symbol(fig,
                                            member=member_id,
                                            load_position=location / calculate_member_length(member_id),
                                            direction=str(direction),
                                            label_size=25 * loads_marker_size,
                                            magnitude=mag,
                                            marker_color=load_marker_color,
                                            label_color=load_marker_color)

    # Plots the distributed loads on model
    if show_Member_Distributed_Loads == True:

        for i in range(len(st.session_state.mdl_members_list)):
            member_name = str(st.session_state.mdl_members_list[i])
            x1 = st.session_state.mdl_x1_list[i]
            x2 = st.session_state.mdl_x2_list[i]
            mag_1 = st.session_state.mdl_mag1_list[i]
            mag_2 = st.session_state.mdl_mag2_list[i]
            direction = str(st.session_state.mdl_direction_list[i])
            axis_system = str(st.session_state.mdl_member_axis_list[i])

            if axis_system == 'Local':
                add_member_distributed_load_local_axis(fig,
                                                       member=member_name,
                                                       x1=x1,
                                                       x2=x2,
                                                       mag1=mag_1,
                                                       mag2=mag_2,
                                                       direction=direction,
                                                       color=load_marker_color,
                                                       line_color=load_marker_color,
                                                       label_color=loads_label_color)

            elif axis_system == 'Global':
                add_member_distributed_load_global_axis(fig,
                                                        member=member_name,
                                                        x1=x1,
                                                        x2=x2,
                                                        mag1=mag_1,
                                                        mag2=mag_2,
                                                        direction=direction,
                                                        arrow_length=loads_marker_size,
                                                        color=load_marker_color,
                                                        line_color=load_marker_color,
                                                        label_color=loads_label_color)

    # Add the supports to the graph
    if show_supports == True:

        # Extract the data from the respective lists
        for i in range(len(st.session_state.supports_node_list)):
            selected_node = st.session_state.supports_node_list[i]
            selected_support_type = st.session_state.supports_type_list[i]

            # Checks and adds roller supports
            if selected_support_type in ['Roller (horizontal-bottom)', 'Roller (horizontal-top)',
                                         'Roller (vertical-left)', 'Roller (vertical-right)']:
                draw_roller_support(fig,
                                    node=st.session_state.nodes_data[selected_node],  # Gets the Node coordinates,
                                    size=node_marker_size + 25,
                                    position=selected_support_type)

            # Checks and add fixed supports
            elif selected_support_type == "Fixed":
                draw_fixed_support(fig,
                                   node=st.session_state.nodes_data[selected_node],
                                   size=node_marker_size + 4)

            # Checks and add pinned supports
            elif selected_support_type == 'Pinned':
                draw_support_triangle(fig,
                                      node=st.session_state.nodes_data[selected_node],
                                      size=node_marker_size + 4)

    # After Analysis show the reactions
    if show_reactions == True:
        # st.session_state.support_reactions_data.update({i: {'FX': FX,
        #                                                     'FY': FY,
        #                                                     'MZ': MZ}})
        for i in st.session_state.support_reactions_data:
            node_coordinates = st.session_state.nodes_data[i]
            reaction_FX = st.session_state.support_reactions_data[i]['FX']
            reaction_FX = round(reaction_FX, 3)
            reaction_FY = st.session_state.support_reactions_data[i]['FY']
            reaction_FY = round(reaction_FY, 3)
            reaction_MZ = st.session_state.support_reactions_data[i]['MZ']
            reaction_MZ = round(reaction_MZ, 3)

            if reaction_FX < 0:
                add_nodal_arrow(fig,
                                arrow_tip_or_node=node_coordinates,
                                direction="←",
                                magnitude=f"{abs(reaction_FX)} {units_dict[unit_systems]['Placeholder']['F']}",
                                )
            elif reaction_FX > 0:
                add_nodal_arrow(fig,
                                arrow_tip_or_node=node_coordinates,
                                direction="→",
                                magnitude=f"{abs(reaction_FX)} {units_dict[unit_systems]['Placeholder']['F']}",
                                )

            if reaction_FY < 0:
                add_nodal_arrow(fig,
                                arrow_tip_or_node=node_coordinates,
                                direction="↓",
                                magnitude=f"{abs(reaction_FY)} {units_dict[unit_systems]['Placeholder']['F']}",
                                )
            elif reaction_FY > 0:
                add_nodal_arrow(fig,
                                arrow_tip_or_node=node_coordinates,
                                direction="↑",
                                magnitude=f"{abs(reaction_FY)} {units_dict[unit_systems]['Placeholder']['F']}",
                                )

            if reaction_MZ < 0:
                add_reaction_moments(fig=fig,
                                     node=node_coordinates,  # Gets the Node coordinates
                                     magnitude=f"{abs(reaction_MZ)} {units_dict[unit_systems]['Placeholder']['M']}",
                                     # from the nodes data dictionary
                                     direction="↷",
                                     marker_size=35 * loads_marker_size,
                                     marker_color='orange',
                                     label_size=loads_label_size,
                                     label_color='orange')

            elif reaction_MZ > 0:
                add_reaction_moments(fig=fig,
                                     node=node_coordinates,  # Gets the Node coordinates
                                     magnitude=f"{abs(reaction_MZ)} {units_dict[unit_systems]['Placeholder']['M']}",
                                     # from the nodes data dictionary
                                     direction="↶",
                                     marker_size=35 * loads_marker_size,
                                     marker_color='orange',
                                     label_size=loads_label_size,
                                     label_color='orange')

    # Plot the settlement symbol
    if show_settlements == True:
        for i in range(len(st.session_state.settlement_node_list)):
            node_id = st.session_state.settlement_node_list[i]
            node_coordinates = st.session_state.nodes_data[node_id]
            settlement_direction = st.session_state.settlement_direction_list[i]
            mag_label = st.session_state.settlement_mag_list[i]

            if settlement_direction == 'Rotation':
                add_support_settlement_symbol(fig,
                                              node=node_coordinates,
                                              direction=settlement_direction,
                                              label=f'{mag_label} {units_dict[unit_systems]["Placeholder"]["Settlement"]["rot"]}',
                                              size=node_marker_size + 5)
            else:
                add_support_settlement_symbol(fig,
                                              node=node_coordinates,
                                              direction=settlement_direction,
                                              label=f'{mag_label} {units_dict[unit_systems]["Placeholder"]["Settlement"]["axial"]}',
                                              size=node_marker_size + 7)

    # Update layout
    fig.update_layout(
        title=dict(
            text=title,
            x=0.5,  # Center the title horizontally
            xanchor='center'
        ),
        xaxis=dict(
            title=f'X {units_dict[unit_systems]["Placeholder"]["L"]}',
            showgrid=True
        ),
        yaxis=dict(
            title=f'Y {units_dict[unit_systems]["Placeholder"]["L"]}',
            showgrid=True,
            scaleanchor="x"  # Equal scaling
        )
    )

    return fig


# Generalized function to plot scatter values
def plot_scatter(fig, x, y, title="Scatter Plot", x_label="X", y_label="Y"):
    # fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode='markers+lines', marker=dict(size=6), name='Data'))
    fig.update_layout(
        title=title,
        xaxis_title=x_label,
        yaxis_title=y_label,
        template='plotly_white'
    )
    return fig


# Plots the values of internal forces along the member length and direction
def plot_along_local_axis(fig, start, end, values, scale=1, name='Moment',
                          color='yellow', fill='toself', line_type='solid'):
    # Convert to numpy arrays
    start = np.array(start)
    end = np.array(end)
    direction = end - start
    length = np.linalg.norm(direction)
    unit_vector = direction / length

    # Local x positions
    x_local = np.linspace(0, length, len(values))

    # Global axis projection
    points_global = [start + x * unit_vector for x in x_local]

    # Perpendicular vector in XY plane
    perp_vector = np.array([-unit_vector[1], unit_vector[0], 0])

    # Displaced (offset) points
    displaced_points = [p + scale * v * perp_vector for p, v in zip(points_global, values)]

    # Extract XY coords for plotting
    x_plot = [p[0] for p in displaced_points]
    y_plot = [p[1] for p in displaced_points]

    # Close the polygon back to the original member line
    x_polygon = [start[0]] + x_plot + [end[0]]
    y_polygon = [start[1]] + y_plot + [end[1]]

    fig.add_trace(go.Scatter(
        x=x_polygon,
        y=y_polygon,
        fill=fill,
        mode='lines',
        name=name,
        line=dict(color=color, width=2, dash=line_type),
        opacity=0.6,
        showlegend=False
    ))

    # Add start and end value markers with text
    for idx in [0, -1]:
        fig.add_trace(go.Scatter(
            x=[x_plot[idx]],
            y=[y_plot[idx]],
            mode='markers+text',
            marker=dict(color=color, size=5),
            text=[f'{values[idx]:.3f}'],
            textposition='top center',
            showlegend=False
        ))


# Extracts the shear force value
def extract_shear_force(member, direction='Fy', n_points=20, combo_name='Combo 1'):
    length = model.members[member].L()
    interval = length / (n_points - 1)
    x_vals, shear_forces = [], []
    for i in range(n_points):
        x = i * interval
        val = model.members[member].shear(direction, x, combo_name=combo_name)
        # st.write(val)
        # if val is None:
        #     st.write(f"Warning: Shear force is None at x = {x} for direction {direction}")
        x_vals.append(x)
        shear_forces.append(float(val) if val is not None else 0.0)
    return x_vals, shear_forces


# Extracts the normal forces
def extract_normal_force(member, n_points=20, combo_name='Combo 1'):
    length = model.members[member].L()
    interval = length / (n_points - 1)
    x_vals, axial_forces = [], []

    for i in range(n_points):
        x = i * interval
        val = model.members[member].axial(x, combo_name=combo_name)
        x_vals.append(x)
        axial_forces.append(float(val) if val is not None else 0.0)

    return x_vals, axial_forces


# Extract the Bending Moment Diagram values
def extract_bending_moment(member, direction='Mz', n_points=200, combo_name='Combo 1'):
    length = model.members[member].L()
    interval = length / (n_points - 1)
    x_vals, moment_vals = [], []
    for i in range(n_points):
        x = i * interval
        val = model.members[member].moment(direction, x, combo_name=combo_name)
        x_vals.append(x)

        if moment_convention == True:
            moment_vals.append(float(val * 1) if val is not None else 0.0)  # Moment on Tension Side

        else:
            moment_vals.append(float(val * -1) if val is not None else 0.0)  # Moment on Compression Side

    return x_vals, moment_vals


def auto_scale_factor_forces(model, force_type='shear', direction='Fy', combo_name='Combo 1', target_ratio=0.1):
    """
    Automatically calculates scale factor for internal force diagrams.

    Parameters:
    - model: FE model
    - force_type: 'shear', 'moment', or 'axial'
    - direction: 'Fy', 'Mz', or 'Fx'
    - combo_name: Load combination
    - target_ratio: How much height (as ratio of member length) diagram should occupy

    Returns:
    - scale factor (float)
    """

    max_force = 0.0
    max_length = 0.0

    for member_id, member in model.members.items():
        length = member.L()
        max_length = max(max_length, length)

        # Get max/min depending on force type
        if force_type == 'shear':
            f = abs(member.max_shear(direction, combo_name))
        elif force_type == 'moment':
            f = max(abs(member.max_moment(direction, combo_name)), abs(member.min_moment(direction, combo_name)))
        elif force_type == 'axial':
            f = max(abs(member.max_axial(combo_name)), abs(member.min_axial(combo_name)))
        else:
            raise ValueError("Invalid force_type")

        max_force = max(max_force, f)

    if max_force == 0:
        return 0.05  # fallback scale

    # reference visual height is e.g. 10% of max member length
    ref_height = target_ratio * max_length
    scale = ref_height / max_force
    return round(scale, 4)


def auto_scale_factor_deflections(model, nodes_data, combo_name='Combo 1', target_ratio=0.1):
    """
    Automatically calculates ONE scale factor for nodal deflections (DX & DY).

    Parameters:
    - model: FE model
    - nodes_data: dict {node_id: (x, y)}
    - combo_name: Load combination
    - target_ratio: Visual size of deflection relative to model

    Returns:
    - scale factor (float)
    """

    max_deflection = 0.0

    # Loop through all nodes
    for node_id in nodes_data.keys():
        dx = Get_Model_Reactions(model, support_node=node_id, reaction_type='DX') or 0.0
        dy = Get_Model_Reactions(model, support_node=node_id, reaction_type='DY') or 0.0

        # Resultant deflection
        d = (dx ** 2 + dy ** 2) ** 0.5
        max_deflection = max(max_deflection, abs(d))

    if max_deflection == 0:
        return 0.05  # fallback

    # Get model size for reference
    xs = [v[0] for v in nodes_data.values()]
    ys = [v[1] for v in nodes_data.values()]

    model_size = max(max(xs) - min(xs), max(ys) - min(ys))

    # Scale so max deflection ≈ target_ratio * model size
    scale = (target_ratio * model_size) / max_deflection

    return round(scale, 4)


def Plot_axial_force_diagram_truss(title='Diagram',
                                   show_nodes=True,
                                   show_members=True,
                                   show_member_labels=True,
                                   combo_name='Combo 1',
                                   label_size=12):
    member_name = []
    axial_force_val = []

    for member in st.session_state.members_data.keys():
        val = model.members[member].axial(1, combo_name=combo_name)
        member_name.append(member)
        axial_force_val.append(round(val, 3) if val is not None else 0.0)

    # st.write(axial_force_val)

    # Creates a figure/graph object
    fig = go.Figure()

    # Add members to graph
    if show_members == True:
        for member in range(len(st.session_state.members_data)):
            x1 = st.session_state.members_data[f'{member}']['Start Node Value'][0]
            y1 = st.session_state.members_data[f'{member}']['Start Node Value'][1]
            x2 = st.session_state.members_data[f'{member}']['End Node Value'][0]
            y2 = st.session_state.members_data[f'{member}']['End Node Value'][1]

            member_color = str()

            if axial_force_val[member] > 0:
                member_color = '#FF6347'

            elif axial_force_val[member] < 0:
                member_color = '#1E90FF'
            else:
                member_color = 'grey'

            add_member(base_figure=fig,
                       x_values=[x1, x2],
                       y_values=[y1, y2],
                       name=member,
                       member_line_color=member_color)

            if show_member_labels:
                # Midpoint
                mid_x = (x1 + x2) / 2
                mid_y = (y1 + y2) / 2

                # Direction unit vector
                dx = x2 - x1
                dy = y2 - y1
                length = (dx ** 2 + dy ** 2) ** 0.5
                if length == 0:
                    continue
                dx /= length
                dy /= length

                # Rotation angle
                angle_rad = math.atan2(dy, dx)
                angle_deg = math.degrees(angle_rad)
                if angle_deg > 90:
                    angle_deg -= 180
                elif angle_deg < -90:
                    angle_deg += 180

                # Offsets
                offset_name = 0.15
                offset_value = -0.15  # below the member

                # Colors
                force = axial_force_val[member]
                force_type = str()
                if force > 0:
                    label_color = '#FF6347'  # Red (Compression)
                    force_type = '(C)'
                elif force < 0:
                    label_color = '#1E90FF'  # Red (Tension)
                    force_type = '(T)'
                else:
                    label_color = 'grey'

                # Member name (above)
                fig.add_annotation(
                    x=mid_x + offset_name * dx,
                    y=mid_y + offset_name * dy,
                    text=f"M{member}",
                    showarrow=False,
                    font=dict(color=label_color, size=label_size),
                    textangle=angle_deg - 90,
                    xanchor="center",
                    yanchor="bottom"
                )

                # Force value (below)
                fig.add_annotation(
                    x=mid_x + offset_value * dx,
                    y=mid_y + offset_value * dy,
                    text=f"{force:.2f} {force_type}",
                    showarrow=False,
                    font=dict(color=label_color, size=label_size - 1),
                    textangle=angle_deg - 90,
                    xanchor="center",
                    yanchor="top"
                )

    # Add Nodes to Graph
    if show_nodes == True:
        add_nodes(base_figure=fig,
                  x_values=node_x,
                  y_values=node_y,
                  node_labels=node_index_values,
                  node_label_color=node_label_color,
                  node_label_size=node_label_size,
                  node_marker_size=node_marker_size,
                  node_marker_color=node_marker_color)

    # Update layout
    fig.update_layout(
        title=dict(
            text=title,
            x=0.5,  # Center the title horizontally
            xanchor='center'
        ),
        xaxis=dict(
            title=f'X {units_dict[unit_systems]["Placeholder"]["L"]}',
            showgrid=True
        ),
        yaxis=dict(
            title=f'Y {units_dict[unit_systems]["Placeholder"]["L"]}',
            showgrid=True,
            scaleanchor="x"  # Equal scaling
        )
    )

    return fig


# Plots the Internal force for single member
def Plot_Member_Distributed_Load_Preview(member=str,
                                         color='orange',
                                         axis_system='Local',
                                         x1=float | int,
                                         x2=float | int,
                                         mag1=float | int,
                                         mag2=float | int,
                                         direction=str):
    """
    Plots distributed load preview diagrams
    along the local and global of a structural member.
    """

    member_length = calculate_member_length(member)
    start_node = st.session_state.members_data[f'{member}']['Start Node']
    end_node = st.session_state.members_data[f'{member}']['End Node']

    fig = go.Figure()

    if axis_system == 'Local':

        # Define node 1
        node_1 = [x1, 0]

        # Define node 2
        node_2 = [x2, 0]

        arrow_length_1 = 1 if mag1 < mag2 else 2
        arrow_length_2 = 1 if mag2 < mag1 else 2

        add_nodal_arrow(fig=fig,
                        arrow_tip_or_node=node_1,
                        # Gets the Node coordinates
                        magnitude=f"{mag1} {units_dict[unit_systems]['Placeholder']['F']}",
                        # from the nodes data dictionary
                        direction=direction,
                        arrow_length=arrow_length_1,
                        marker_color=load_marker_color,
                        label_color=loads_label_color,
                        label_size=loads_label_size)

        add_nodal_arrow(fig=fig,
                        arrow_tip_or_node=node_2,
                        # Gets the Node coordinates
                        magnitude=f"{mag2} {units_dict[unit_systems]['Placeholder']['F']}",
                        # from the nodes data dictionary
                        direction=direction,
                        arrow_length=arrow_length_2,
                        marker_color=load_marker_color,
                        label_color=loads_label_color,
                        label_size=loads_label_size)

        fig.add_trace(go.Scatter(
            x=[x1, x1, x2, x2],
            y=[0, -arrow_length_1 * sign_conv[direction], -arrow_length_2 * sign_conv[direction], 0],
            mode='lines+text',
            name='Distributed Load',
            fill='toself',
            line=dict(color=load_marker_color, width=2)
        ))

        # Plot the frame element
        fig.add_trace(go.Scatter(
            x=[0, member_length],
            y=[0, 0],
            mode='lines',
            name='Member Axis',
            line=dict(color=member_line_color, width=2.5)
        ))

        # Plot the Nodes
        add_nodes(base_figure=fig,
                  x_values=[0, member_length],
                  y_values=[0, 0],
                  node_labels=[start_node, end_node],
                  node_label_color=node_label_color,
                  node_label_size=node_label_size,
                  node_marker_size=node_marker_size,
                  node_marker_color=node_marker_color)

        # Layout settings
        fig.update_layout(
            title=f"Diagram for Member {member}",
            xaxis_title=f"Length {units_dict[unit_systems]['Placeholder']['L']}",
            yaxis_title=f"Load {units_dict[unit_systems]['Placeholder']['F']}",
            showlegend=False,
            height=250)

    elif axis_system == 'Global':

        add_member_distributed_load_global_axis(fig,
                                                member=member,
                                                x1=x1,
                                                x2=x2,
                                                mag1=mag1,
                                                mag2=mag2,
                                                direction=direction,
                                                color=load_marker_color,
                                                line_color=load_marker_color,
                                                label_color=loads_label_color)

        # add_member_distributed_load_local_axis(fig,
        #                                         member=member,
        #                                         x1=x1,
        #                                         x2=x2,
        #                                         mag1=mag1,
        #                                         mag2=mag2,
        #                                         direction=direction,
        #                                         color=load_marker_color,
        #                                         line_color=load_marker_color,
        #                                         label_color=loads_label_color)

        # Extract the member coordinates
        x1_point = st.session_state.members_data[f'{member}']['Start Node Value'][0]
        y1_point = st.session_state.members_data[f'{member}']['Start Node Value'][1]
        x2_point = st.session_state.members_data[f'{member}']['End Node Value'][0]
        y2_point = st.session_state.members_data[f'{member}']['End Node Value'][1]

        # Plot the frame element
        add_member(base_figure=fig,
                   x_values=[x1_point, x2_point],
                   y_values=[y1_point, y2_point],
                   name=member,
                   member_line_color=member_line_color)

        # Plot the Nodes
        add_nodes(base_figure=fig,
                  x_values=[x1_point, x2_point],
                  y_values=[y1_point, y2_point],
                  node_labels=[start_node, end_node],
                  node_label_color=node_label_color,
                  node_label_size=node_label_size,
                  node_marker_size=node_marker_size,
                  node_marker_color=node_marker_color)

        # Layout settings
        fig.update_layout(
            title=f"Diagram for Member {member}",
            xaxis_title=f"Length {units_dict[unit_systems]['Placeholder']['L']}",
            yaxis_title=f"Load {units_dict[unit_systems]['Placeholder']['F']}",
            showlegend=False,
            xaxis=dict(scaleanchor="y", scaleratio=1),
            yaxis=dict(scaleratio=1)
        )

    return fig


# Plots the Internal force for single member
def Plot_Member_Point_Load_Preview(member=str,
                                   color='orange',
                                   location=float | int,
                                   direction=str,
                                   magnitude=float | int):
    """
    Plots load preview diagrams
    along the horizontal axis of a structural member.
    """

    member_length = calculate_member_length(member)
    start_node = st.session_state.members_data[f'{member}']['Start Node']
    end_node = st.session_state.members_data[f'{member}']['End Node']

    fig = go.Figure()

    # ["↑", "↓"]
    direction_text = str()
    unit_text = str()

    if direction == "↑":
        y_offset = 'top'
        direction_text = "⬆"
        mag_text_offset = -0.1
        unit_text = 'F'

    if direction == "↓":
        y_offset = 'bottom'
        direction_text = "⬇"
        mag_text_offset = 0.1
        unit_text = 'F'

    if direction == '↺':
        y_offset = 'middle'
        direction_text = "↺"
        mag_text_offset = 0.1
        unit_text = 'M'

    if direction == '↻':
        y_offset = 'middle'
        direction_text = "↻"
        mag_text_offset = 0.1
        unit_text = 'M'

    fig.add_annotation(
        x=location,
        y=0,
        text=direction_text,
        showarrow=False,
        font=dict(size=28, color=color),
        textangle=0,
        xanchor='center',
        yanchor=y_offset
    )

    # Plot the magnitude
    fig.add_annotation(
        x=location,
        y=mag_text_offset,
        text=f"{magnitude} {units_dict[unit_systems]['Placeholder'][unit_text]}",
        showarrow=False,
        font=dict(size=12, color=color),
        textangle=0,
        xanchor='center',
        yanchor=y_offset
    )

    # Plot the frame element
    fig.add_trace(go.Scatter(
        x=[0, member_length],
        y=[0, 0],
        mode='lines',
        name='Member Axis',
        line=dict(color=member_line_color, width=2.5)
    ))

    # Plot the Nodes
    add_nodes(base_figure=fig,
              x_values=[0, member_length],
              y_values=[0, 0],
              node_labels=[start_node, end_node],
              node_label_color=node_label_color,
              node_label_size=node_label_size,
              node_marker_size=node_marker_size,
              node_marker_color=node_marker_color)

    # Layout settings
    fig.update_layout(
        title=f"Diagram for Member {member}",
        xaxis_title=f"Length {units_dict[unit_systems]['Placeholder']['L']}",
        yaxis_title=f"Load {units_dict[unit_systems]['Placeholder']['F']}",
        showlegend=False,
        height=250
    )

    return fig


# Plots the Internal force for single member
def Plot_Member_Internal_Forces(member: str,
                                plot_shear_force=False,
                                plot_bending_moment=False,
                                combo_name='Combo 1',
                                color='red'):
    """
    Plots internal force diagrams (shear force and bending moment)
    along the horizontal axis of a structural member.
    """

    fig = go.Figure()

    member_length = model.members[member].L()
    start_node = st.session_state.members_data[f'{member}']['Start Node']
    end_node = st.session_state.members_data[f'{member}']['End Node']

    y_axis_name = str()
    title = str()

    # Plot Shear Force
    if plot_shear_force:
        title = 'Shear Force'
        y_axis_name = f'Shear Force {units_dict[unit_systems]["Placeholder"]["F"]}'
        x_shear, shear_vals = extract_shear_force(member, direction='Fy', n_points=200, combo_name=combo_name)

        fig.add_trace(go.Scatter(
            x=x_shear + x_shear[::-1],
            y=shear_vals + [0] * len(shear_vals),
            mode='lines+text',
            name='Shear Force',
            fill='toself',
            line=dict(color=color, width=2)
        ))

    # Plot Bending Moment
    if plot_bending_moment:
        title = 'Bending Moment'
        y_axis_name = f'Bending Moment {units_dict[unit_systems]["Placeholder"]["M"]}'
        x_moment, moment_vals = extract_bending_moment(member, direction='Mz', n_points=200, combo_name=combo_name)

        fig.add_trace(go.Scatter(
            x=x_moment + x_moment[::-1],
            y=moment_vals + [0] * len(moment_vals),
            mode='lines+text',
            name='Bending Moment',
            fill='toself',
            line=dict(color=color, width=2)
        ))

    # Plot the frame element
    fig.add_trace(go.Scatter(
        x=[0, member_length],
        y=[0, 0],
        mode='lines',
        name='Member Axis',
        line=dict(color=member_line_color, width=2.5)
    ))

    # Plot the Nodes
    add_nodes(base_figure=fig,
              x_values=[0, member_length],
              y_values=[0, 0],
              node_labels=[start_node, end_node],
              node_label_color=node_label_color,
              node_label_size=node_label_size,
              node_marker_size=node_marker_size,
              node_marker_color=node_marker_color)

    # Layout settings
    fig.update_layout(
        title=f"{title} Diagram for Member {member}",
        xaxis_title=f"Length {units_dict[unit_systems]['Placeholder']['L']}",
        yaxis_title=y_axis_name,
        showlegend=False,
        height=250,
        # hovermode='y',  # enables vertical hover interaction
        xaxis=dict(
            showspikes=True,
            spikemode='across',
            spikesnap='cursor',
            showline=True,
            spikedash='solid',
            spikethickness=0.2,
            spikecolor="grey"
        ),
    )

    return fig


# Plots the internal forces of complete frame structure
def Plot_Internal_Forces(title='Diagram',
                         show_nodes=False,
                         show_displaced_nodes=True,
                         show_members=True,
                         show_member_labels=False,
                         show_supports=True,
                         plot_normal_force=False,
                         plot_shear_force=False,
                         plot_bending_moment=False,
                         plot_deflection=False,
                         scale=0.05):
    # Creates a figure/graph object
    fig = go.Figure()

    # Add members to graph
    if show_members == True:
        for member in range(len(st.session_state.members_data)):
            x1 = st.session_state.members_data[f'{member}']['Start Node Value'][0]
            y1 = st.session_state.members_data[f'{member}']['Start Node Value'][1]
            x2 = st.session_state.members_data[f'{member}']['End Node Value'][0]
            y2 = st.session_state.members_data[f'{member}']['End Node Value'][1]

            add_member(base_figure=fig,
                       x_values=[x1, x2],
                       y_values=[y1, y2],
                       name=member,
                       member_line_color=member_line_color)

            if show_member_labels == True:
                # Midpoint
                mid_point_x = (x1 + x2) / 2
                mid_point_y = (y1 + y2) / 2

                # Direction vector
                dx = x2 - x1
                dy = y2 - y1
                length = (dx ** 2 + dy ** 2) ** 0.5
                if length == 0:
                    continue

                dx /= length
                dy /= length

                # Offset along the member direction
                offset = 0.15
                label_x = mid_point_x + offset * dx
                label_y = mid_point_y + offset * dy

                # Calculate angle in degrees for text rotation
                angle_rad = math.atan2(dy, dx)
                angle_deg = math.degrees(angle_rad)

                # Keep text upright (rotate only between -90 and 90 degrees)
                if angle_deg > 90:
                    angle_deg -= 180
                elif angle_deg < -90:
                    angle_deg += 180

                # Add annotation
                fig.add_annotation(
                    x=label_x,
                    y=label_y,
                    text=f"M{member}",
                    showarrow=False,
                    font=dict(color='green', size=12),
                    textangle=angle_deg - 90,
                    xanchor="center",
                    yanchor="top",
                )

    # Add Nodes to Graph
    if show_nodes == True:
        add_nodes(base_figure=fig,
                  x_values=node_x,
                  y_values=node_y,
                  node_labels=node_index_values,
                  node_label_color=node_label_color,
                  node_label_size=node_label_size,
                  node_marker_size=node_marker_size,
                  node_marker_color=node_marker_color)

    # Add the supports to the graph
    if show_supports == True:

        # Extract the data from the respective lists
        for i in range(len(st.session_state.supports_node_list)):
            selected_node = st.session_state.supports_node_list[i]
            selected_support_type = st.session_state.supports_type_list[i]

            # Checks and adds roller supports
            if selected_support_type in ['Roller (horizontal-bottom)', 'Roller (horizontal-top)',
                                         'Roller (vertical-left)', 'Roller (vertical-right)']:
                draw_roller_support(fig,
                                    node=st.session_state.nodes_data[selected_node],  # Gets the Node coordinates,
                                    size=node_marker_size + 20,
                                    position=selected_support_type)

            # Checks and add fixed supports
            elif selected_support_type == "Fixed":
                draw_fixed_support(fig,
                                   node=st.session_state.nodes_data[selected_node],
                                   size=node_marker_size + 4)

            # Checks and add pinned supports
            elif selected_support_type == 'Pinned':
                draw_support_triangle(fig,
                                      node=st.session_state.nodes_data[selected_node],
                                      size=node_marker_size + 4)

    for member_id in st.session_state.members_data:
        member = model.members[member_id]
        i_node = member.i_node
        j_node = member.j_node
        start = np.array([i_node.X, i_node.Y, i_node.Z])
        end = np.array([j_node.X, j_node.Y, j_node.Z])

        if plot_shear_force:
            _, shear_vals = extract_shear_force(member=member_id, direction='Fy', n_points=200)
            plot_along_local_axis(fig, start, end, shear_vals, scale=scale, color=shear_force_diagram_color,
                                  name="Shear")

        if plot_normal_force:
            _, axial_vals = extract_normal_force(member=member_id, n_points=200)
            plot_along_local_axis(fig, start, end, axial_vals, scale=scale, color=axial_force_diagram_color,
                                  name='Axial')

        if plot_bending_moment:
            _, moment_vals = extract_bending_moment(member=member_id, direction='Mz', n_points=200)
            plot_along_local_axis(fig, start, end, moment_vals, scale=scale, color=bending_moment_diagram_color)

        if plot_deflection == True:

            def extract_2d_member_deflection(model, member_id, num_points=50, scale=1.0, combo='Combo 1'):
                member = model.members[member_id]
                length = member.L()
                x_local = np.linspace(0, length, num_points)

                defl_x, defl_y = [], []

                for x in x_local:
                    ux = member.deflection('dx', x, combo_name=combo)
                    uy = member.deflection('dy', x, combo_name=combo)
                    defl_x.append(ux if ux is not None else 0)
                    defl_y.append(uy if uy is not None else 0)

                # Original global coordinates
                i_node, j_node = member.i_node, member.j_node
                x_orig = np.linspace(i_node.X, j_node.X, num_points)
                y_orig = np.linspace(i_node.Y, j_node.Y, num_points)

                # Member angle
                theta = np.arctan2(j_node.Y - i_node.Y, j_node.X - i_node.X)

                # Convert local deflections to global system
                dx = np.cos(theta) * np.array(defl_x) - np.sin(theta) * np.array(defl_y)
                dy = np.sin(theta) * np.array(defl_x) + np.cos(theta) * np.array(defl_y)

                x_deflected = x_orig + dx * scale * units_dict[unit_systems]["conv_fact"]["def"]
                y_deflected = y_orig + dy * scale * units_dict[unit_systems]["conv_fact"]["def"]

                return x_deflected, y_deflected, i_node.X, j_node.X, i_node.Y, j_node.Y

            # Plot the displacements along the member local axes
            for member_id in model.members:
                try:
                    x_def, y_def, x_i, x_j, y_i, y_j = extract_2d_member_deflection(
                        model, member_id, num_points=50, scale=scale, combo='Combo 1')

                    # Deflected shape (red dashed line)
                    fig.add_trace(go.Scatter(
                        x=x_def,
                        y=y_def,
                        mode='lines',
                        line=dict(color=deflection_diagram_color,
                                  dash='dash',
                                  width=1),
                        name='Deflected Shape',
                        showlegend=False
                    ))

                except Exception as e:
                    st.warning(f"Failed to extract deflection for member {member_id}: {e}")

            if show_displaced_nodes == True:
                # Lists for storing displaced node values
                displaced_node_x_values = []
                displaced_node_y_values = []
                displaced_annotations = []

                for node_id in st.session_state.nodes_data.keys():
                    original_x = st.session_state.nodes_data[node_id][0]
                    original_y = st.session_state.nodes_data[node_id][1]

                    # Extract the individual displacements
                    dx = Get_Model_Reactions(model, support_node=node_id, reaction_type='DX') or 0.0
                    dy = Get_Model_Reactions(model, support_node=node_id, reaction_type='DY') or 0.0

                    # Scale them
                    factor = units_dict[unit_systems]["conv_fact"]["def"]
                    scaled_dx = dx * factor * scale
                    scaled_dy = dy * factor * scale

                    # Compute displaced coordinates
                    x_disp = original_x + scaled_dx
                    y_disp = original_y + scaled_dy

                    # Store for plotting
                    displaced_node_x_values.append(x_disp)
                    displaced_node_y_values.append(y_disp)

                    # # Prepare annotation label (you can customize decimal places)
                    # label = f"({dx*factor:.2f}, {dy*factor:.2f})"
                    # displaced_annotations.append(dict(
                    #     x=x_disp,
                    #     y=y_disp,
                    #     text=label,
                    #     showarrow=False,
                    #     arrowhead=1,
                    #     ax=0,
                    #     ay=-20,
                    #     font=dict(color=deflection_diagram_color, size=node_label_size)
                    # ))

                # Plot displaced nodes
                add_nodes(base_figure=fig,
                          x_values=displaced_node_x_values,
                          y_values=displaced_node_y_values,
                          node_labels=node_index_values,
                          node_label_color=node_label_color,
                          node_label_size=node_label_size,
                          node_marker_size=node_marker_size,
                          node_marker_color=deflection_diagram_color,
                          show_in_legend=False)

                # Add annotations to the figure
                if "layout" in fig:
                    fig["layout"].annotations += tuple(displaced_annotations)
                else:
                    fig.update_layout(annotations=displaced_annotations)

    # Update layout
    fig.update_layout(
        title=dict(
            text=title,
            x=0.5,  # Center the title horizontally
            xanchor='center'
        ),
        xaxis=dict(
            title=f'X {units_dict[unit_systems]["Placeholder"]["L"]}',
            showgrid=True
        ),
        yaxis=dict(
            title=f'Y {units_dict[unit_systems]["Placeholder"]["L"]}',
            showgrid=True,
            scaleanchor="x"  # Equal scaling
        )
    )

    return fig


@st.fragment
def Display_Normal_Force_Section():
    member_names = []
    axial_force_val = []
    force_type = []

    for member in st.session_state.members_data.keys():
        val = model.members[member].axial(1, combo_name='Combo 1')
        member_names.append(member)
        axial_force_val.append(round(val, 3) if val is not None else 0.0)

        if val > 0:
            force_type.append('Compression')

        elif val < 0:
            force_type.append('Tension')

        else:
            force_type.append('-')

    # Create dataframe
    nf_table_data = {
        f"Member ": member_names,
        f"Axial Force {units_dict[unit_systems]['Placeholder']['F']}": axial_force_val,
        'Force Type': force_type
    }

    # Columns for input widgets and figure display
    col1, col2 = st.columns([0.4, 0.6], gap='small')

    if structure_type == 'Frame':

        with col1:
            with st.container(border=True,
                              key='nf_container'):
                nf_scale_factor_but = st.number_input('Diagram Scale',
                                                      help='Scales the Normal Force diagram',
                                                      value=auto_scale_factor_forces(model, force_type='axial'),
                                                      format="%0.3f"
                                                      )

            # Show table
            st.dataframe(nf_table_data, width='stretch')

        # Show the normal force diagram
        with col2:
            st.plotly_chart(Plot_Internal_Forces(title='Normal Force Diagram',
                                                 show_member_labels=True,
                                                 plot_normal_force=True,
                                                 scale=nf_scale_factor_but,
                                                 show_supports=False),
                            key='Normal_Force-Plot')

    else:
        with col1:
            with st.container(border=True,
                              key='nf_container'):
                nf_scale_factor_but = st.number_input('Diagram Scale',
                                                      help='Scales the Normal Force diagram',
                                                      value=12)

            # Show table
            st.dataframe(nf_table_data, width='stretch')

        # Show the normal force diagram for Truss
        with col2:
            st.plotly_chart(Plot_axial_force_diagram_truss(title='Axial Force Diagram',
                                                           label_size=nf_scale_factor_but))


@st.fragment
def Display_Shear_Force_Section():
    # Columns for input widgets and figure display
    col1, col2 = st.columns([0.4, 0.6], gap='small')

    with col1:
        with st.container(border=True,
                          key='sf_container'):
            col1a, col2a = st.columns(2, gap='small')
            with col1a:
                select_member = st.selectbox('Select Member',
                                             options=st.session_state.members_data.keys(),
                                             key='SF_Selection_member',
                                             help="Select specific member to compute it's value at intervals")

            with col2a:
                sf_scale_factor_but = st.number_input('Diagram Scale',
                                                      help='Scales the Shear Force diagram',
                                                      value=auto_scale_factor_forces(model, force_type='shear',
                                                                                     direction='Fy'),
                                                      format="%0.3f"
                                                      )

        # # Prepare the SF data for table
        #
        # # Get member length
        # member_length = model.members[select_member].L()
        #
        # # Compute number of points
        # n_points = int(member_length / interval) + 1
        # x_values = []
        # shear_values = []
        #
        # for i in range(n_points):
        #     x = round(i * interval, 3)
        #     shear = model.members[select_member].shear('Fy', x, combo_name='Combo 1')
        #     x_values.append(x)
        #     shear_values.append(round(float(shear), 3) if shear is not None else 0.0)
        #
        # # Create dataframe
        # sf_table_data = {
        #     f"Distance {units_dict[unit_systems]['Placeholder']['L']}": x_values,
        #     f"Shear Force {units_dict[unit_systems]['Placeholder']['F']}": shear_values
        # }
        #
        # # Show table
        # st.dataframe(sf_table_data, width='stretch')

        with st.expander(label='Individual Member Diagram'):
            st.plotly_chart(Plot_Member_Internal_Forces(member=select_member,
                                                        plot_shear_force=True,
                                                        color=shear_force_diagram_color))

            value = round(model.members[select_member].max_shear('Fy', combo_tags='Combo 1'), 3)
            st.metric('**Max Shear Force**',
                      value=f"{value} {units_dict[unit_systems]['Placeholder']['F']}")

            value = round(model.members[select_member].min_shear('Fy', combo_tags='Combo 1'), 3)
            st.metric('**Min Shear Force**',
                      value=f"{value} {units_dict[unit_systems]['Placeholder']['F']}")

    # Show the shear force diagram
    with col2:
        st.plotly_chart(Plot_Internal_Forces(title='Shear Force Diagram',
                                             plot_shear_force=True,
                                             scale=sf_scale_factor_but,
                                             show_supports=False),
                        key='Shear_Force-Plot')


@st.fragment
def Display_Bending_Moment_Section():
    # Columns for input widgets and figure display
    col1, col2 = st.columns([0.4, 0.6], gap='small')

    with col1:
        with st.container(border=True, key='bm_container'):
            col1a, col2a = st.columns(2, gap='small')
            with col1a:
                select_member = st.selectbox('Select Member',
                                             options=st.session_state.members_data.keys(),
                                             key='BM_Selection_member',
                                             help="Select specific member to compute its value at intervals")

            with col2a:
                bm_scale_factor_but = st.number_input('Diagram Scale',
                                                      help='Scales the Bending Moment diagram',
                                                      value=auto_scale_factor_forces(model, force_type='moment',
                                                                                     direction='Mz'),
                                                      format="%0.3f"
                                                      )

        # Prepare the BM data for table

        # # Get member length
        # member_length = model.members[select_member].L()
        #
        # # Compute number of points
        # n_points = int(member_length / interval) + 1
        # x_values = []
        # moment_values = []
        #
        # for i in range(n_points):
        #     x = round(i * interval, 3)
        #     moment = model.members[select_member].moment('Mz', x, combo_name='Combo 1')
        #     x_values.append(x)
        #     moment_values.append(round(float(moment), 3) if moment is not None else 0.0)
        #
        # # Create dataframe
        # bm_table_data = {
        #     f"Distance {units_dict[unit_systems]['Placeholder']['L']}": x_values,
        #     f"Bending Moment {units_dict[unit_systems]['Placeholder']['M']}": moment_values
        # }
        #
        # # Show table
        # st.dataframe(bm_table_data, width='stretch')

        with st.expander(label='Individual Member Diagram'):
            st.plotly_chart(Plot_Member_Internal_Forces(member=select_member,
                                                        plot_bending_moment=True,
                                                        color=bending_moment_diagram_color))

            value = round(model.members[select_member].max_moment('Mz', combo_tags='Combo 1'), 3)
            st.metric('**Max Bending Moment**',
                      value=f'{value} {units_dict[unit_systems]["Placeholder"]["M"]}')

            value = round(model.members[select_member].min_moment('Mz', combo_tags='Combo 1'), 3)
            st.metric('**Min Bending Moment**',
                      value=f'{value} {units_dict[unit_systems]["Placeholder"]["M"]}')

    # Show the bending moment diagram
    with col2:
        st.plotly_chart(Plot_Internal_Forces(title='Bending Moment Diagram',
                                             plot_bending_moment=True,
                                             scale=bm_scale_factor_but,
                                             show_supports=False),
                        key='Bending_Moment-Plot')


@st.fragment
def Plot_Deflection_Diagram_with_Table():
    # Columns for input widgets and figure display
    col1, col2 = st.columns([0.4, 0.6], gap='small')

    with col1:
        with st.container(border=True, key='deflection_container'):
            # col1a, col2a, col3a = st.columns(3, gap='small')

            df_scale_factor = st.number_input('Diagram Scale',
                                              help='Scales the deflection diagram for visualization',
                                              value=auto_scale_factor_deflections(
                                                  model,
                                                  st.session_state.nodes_data,
                                                  combo_name='Combo 1',
                                                  target_ratio=0.001
                                              ),
                                              format="%0.5f"
                                              )

        # Get node coordinates (optional)
        # nodes = [i_node.name, j_node.name]
        dx_values = []
        dy_values = []
        rot_values = []

        for node in st.session_state.nodes_data.keys():
            dx = Get_Model_Reactions(model, support_node=node, reaction_type='DX')
            dy = Get_Model_Reactions(model, support_node=node, reaction_type='DY')
            rot = Get_Model_Reactions(model, support_node=node, reaction_type='RZ')

            dx_values.append(
                round(float(dx * units_dict[unit_systems]["conv_fact"]["def"]), 3) if dx is not None else 0.0)
            dy_values.append(
                round(float(dy * units_dict[unit_systems]["conv_fact"]["def"]), 3) if dy is not None else 0.0)

            # dx_values.append(
            #     round(float(dx), 3) if dx is not None else 0.0)
            # dy_values.append(
            #     round(float(dy), 3) if dy is not None else 0.0)

            rot_values.append(float(rot).__round__(3))

        # Create table
        df_table_data = {
            "Node": st.session_state.nodes_data.keys(),
            f"Deflection X {units_dict[unit_systems]['Placeholder']['def']}": dx_values,
            f"Deflection Y {units_dict[unit_systems]['Placeholder']['def']}": dy_values,
            f"Rotation (rad)": rot_values
        }

        # Show table
        st.dataframe(df_table_data, width='stretch', hide_index=True)

    # Plot the deflection diagram
    with col2:
        st.plotly_chart(Plot_Internal_Forces(title='Deflection Diagram',
                                             show_nodes=True,
                                             plot_deflection=True,
                                             scale=df_scale_factor),
                        key='Deflection-Plot')


def Get_Model_Reactions(model, support_node, reaction_type):
    node = str(support_node)

    # Available Types
    # [FX, FY, MZ, DX, DY,RZ]
    if reaction_type == 'FX':
        return model.nodes[node].RxnFX['Combo 1']

    elif reaction_type == 'FY':
        return model.nodes[node].RxnFY['Combo 1']

    elif reaction_type == 'MZ':
        return model.nodes[node].RxnMZ['Combo 1']

    elif reaction_type == 'DX':
        return model.nodes[node].DX['Combo 1']

    elif reaction_type == 'DY':
        return model.nodes[node].DY['Combo 1']

    elif reaction_type == 'RZ':
        return model.nodes[node].RZ['Combo 1']


# === SECTION 2 === Generalized Settings for overall Frame Analysis application ========================================

# Units Dictionary
units_dict = {
    'Metric': {
        'conv_fact': {
            'L': 1,
            'F': 1,
            'M': 1,
            'DistL': 1,
            'def': 1000,  # m to mm
            'E': 1000,  # MPa to KN/m²
            'I': 10 ** (-12),  # mm⁴ to m
            'A': 10 ** (-6),  # mm² to m²
            'Settlement': {'axial': 1 / 1000,  # mm to m
                           'rot': 1}
        },

        'Placeholder': {
            'L': '(m)',
            'F': '(kN)',
            'M': '(kN.m)',
            'DistL': '(kN/m)',
            'def': '(mm)',
            'E': '(MPa)',
            'I': '(mm⁴)',
            'A': '(mm²)',
            'Settlement': {'axial': '(mm)',
                           'rot': '(radians)'}

        },

        'Default_Section': {
            'E': 200000,
            'I': 1,
            'A': 1
        }
    },

    'Imperial': {
        'conv_fact': {
            'L': 1,
            'F': 1,
            'M': 1,
            'DistL': 1,
            'def': 12,  # ft to in
            'E': 144,  # Ksi to Ksf
            'I': 12 ** (-4),  # in⁴ to ft⁴
            'A': 12 ** (-2),  # in² to ft²
            'Settlement': {'axial': 1 / 12,  # mm to m
                           'rot': 1}
        },
        "Placeholder": {
            'L': '(ft)',
            'F': '(kip)',
            'M': '(kip.ft)',
            'DistL': '(kip/ft)',
            'def': '(in)',
            'E': '(ksi)',
            'I': '(in⁴)',
            'A': '(in²)',
            'Settlement': {'axial': '(in)',
                           'rot': '(radians)'}
        },

        'Default_Section': {
            'E': 29000,
            'I': 1,
            'A': 1,
        }

    }

}

# Sign Convention dictionary for loads directions
sign_conv = {'↑': 1,
             '↓': -1,
             "←": -1,
             "→": 1,
             '↻': -1,
             '↺': 1}

# === SECTION 4 === App Layout ====================================================================
st.header('Frame/Truss Analysis', divider='orange')

st.subheader(':blue-background[**Settings**]', divider='rainbow')

# Columns for Graph settings
col1, col2 = st.columns(2, gap='medium')

with col1:
    # Unit system radio widget
    unit_systems = st.radio(
        label='Unit system',
        options=["Metric", "Imperial"],
        captions=[
            "length (m), force (kN), moment (kN.m), distributed load (kN/m), deflection (mm), E (MPa), I (mm⁴)",
            "length (ft), force (kip), moment (kip.ft), distributed load (kip/ft), deflection (in), E (kip/in²), I (in⁴)"
        ]
    )

with col2:
    with st.popover('Model Display Settings', width='stretch'):
        col1a, col2a = st.columns(2, gap='small')

        with col1a:
            # Size of node label
            node_label_size = st.number_input('Node Label Size',
                                              min_value=0,
                                              value=10)

        with col2a:
            # Color of node label
            node_label_color = st.color_picker('Node Label Color',
                                               value='#0D0D0D')

        col1a, col2a = st.columns(2, gap='small')
        with col1a:
            # Size of node Marker
            node_marker_size = st.number_input('Node Marker Size',
                                               min_value=0,
                                               value=11)
        with col2a:
            # Color of marker
            node_marker_color = st.color_picker('Node Marker Color',
                                                value='#FFB705')

        col1a, col2a = st.columns(2, gap='small')
        with col1a:
            member_label = st.checkbox('Member Labels',
                                       value=True)

        with col2a:
            # Color of member line
            member_line_color = st.color_picker('Member Color',
                                                value='#87CEEB')

        col1a, col2a = st.columns(2, gap='small')
        with col1a:
            # Size of load marker/symbols
            loads_marker_size = st.slider('Load Marker Size',
                                          min_value=1.0,
                                          max_value=2.0,
                                          value=1.0)

        with col2a:
            # Color of load symbols
            load_marker_color = st.color_picker('Loads Marker Color',
                                                value='#EA4488')

        col1a, col2a = st.columns(2, gap='small')
        with col1a:
            # Size of load marker/symbols
            loads_label_size = st.slider('Load Label Size',
                                         min_value=1,
                                         max_value=20,
                                         value=10)

        with col2a:
            # Color of load symbols
            loads_label_color = st.color_picker('Loads Label Color',
                                                value='#EA4488')
with col2:
    with st.popover('Output Display Settings', width='stretch'):
        # Color of axial force diagram
        axial_force_diagram_color = st.color_picker('Axial Force Diagram Color',
                                                    value='#D8B4F8')

        # Color of shear force diagram
        shear_force_diagram_color = st.color_picker('Shear Force Diagram Color',
                                                    value='#FFD700')

        # Color of bending moment diagram
        bending_moment_diagram_color = st.color_picker('Bending Moment Diagram Color',
                                                       value='#39FF14')

        # Color of bending moment diagram
        deflection_diagram_color = st.color_picker('Deflected Shape Diagram Color',
                                                   value='#FF073A')

with col2:
    moment_convention = st.toggle('Moment Diagram on Tension Side',
                                  value=True)
# with col3:
#     with st.popover('Results Display', width='stretch'):
#         st.write('working')

st.write('')
st.subheader(':blue-background[**Model**]', divider='rainbow')

# Tabs for Section And Model
tab1, tab2, tab3, tab4 = st.tabs(['Section', 'Frame', 'Loads', 'Analysis & Results'])

# Sections Tabs and Layout===================================================================================
with tab1:
    # Dataframe for Sections Data (Stores the data of all sections)

    if 'section_data' not in st.session_state:
        st.session_state.section_data = {}

    st.session_state.section_data.update({'Default': {
        'E': (units_dict[unit_systems]['Default_Section']['E']),
        'I': (units_dict[unit_systems]['Default_Section']['I']),
        'A': (units_dict[unit_systems]['Default_Section']['A']),
    }
    })

    # ----------------------------------------------------------------------------------------

    col1, col2 = st.columns([0.4, 0.6], gap='small', border=True)

    with col1:
        sec_name = st.text_input('Section Name',
                                 value=None,
                                 placeholder='Sec-1',
                                 key='S-name')

        modulus_of_elasticity = st.number_input('Modulus of Elasticity (E)',
                                                value=None,
                                                placeholder=units_dict[unit_systems]['Placeholder']['E'],
                                                key='E')

        moment_of_inertia = st.number_input('Moment of Inertia (I)',
                                            value=None,
                                            placeholder=units_dict[unit_systems]['Placeholder']['I'],
                                            key='I')

        area = st.number_input('Cross-section Area (A)',
                               value=None,
                               placeholder=units_dict[unit_systems]['Placeholder']['A'],
                               key='A')

        st.divider()

        col1a, col2a = st.columns(2, gap='small', vertical_alignment='bottom')

        with col2a:
            add_section_but = st.button('Add', type='primary', width='stretch', key='1')

        with col1a:
            row_select = st.selectbox(label='Select Section',
                                      options=st.session_state.section_data.keys(),
                                      key='r1')

        with col2a:
            remove_section_but = st.button('Delete', width='stretch', key='2')

    # Logic for adding section to dataframe
    if add_section_but:
        if all(x is not None for x in [sec_name, modulus_of_elasticity, moment_of_inertia, area]):
            st.session_state.section_data.update({sec_name: {'E': modulus_of_elasticity,
                                                             'I': moment_of_inertia,
                                                             'A': area}})
            st.rerun()

    # Logic for deleting the selected section
    if remove_section_but:
        del st.session_state.section_data[row_select]
        st.rerun()

    # For Debugging only
    # st.write(st.session_state.section_data)

    with col2:

        # Extract data from section_data dataframe for display
        E_values = []
        I_values = []
        A_values = []

        for section in st.session_state.section_data:
            E_values.append(st.session_state.section_data[section]['E'])
            I_values.append(st.session_state.section_data[section]['I'])
            A_values.append(st.session_state.section_data[section]['A'])

        # Prepare the data fro display
        data_for_table = {
            'Section Name': st.session_state.section_data.keys(),
            f"E {units_dict[unit_systems]['Placeholder']['E']}": E_values,
            f"I {units_dict[unit_systems]['Placeholder']['I']}": I_values,
            f"A {units_dict[unit_systems]['Placeholder']['A']}": A_values,

        }

        # Display the recorded sections
        sections_table = st.dataframe(data=data_for_table,
                                      width='stretch',
                                      hide_index=True)

# Frame Modelling Tab & Layout===========================================================================
with tab2:
    # Columns for input widgets and figure display
    col1, col2 = st.columns([0.4, 0.6], gap='small')

    # Nodes---------------------------------------------------------------------------------------

    if 'nodes_data' not in st.session_state:
        st.session_state.nodes_data = {}

    with col1:
        # Nodes section
        with st.popover('Nodes', width='stretch'):
            st.write('**Add Nodes**')
            # Nodes Input
            nodes = st.data_editor(
                data={'x': [0.0], 'y': [0.0]},
                hide_index=True,
                width='stretch',
                num_rows='dynamic',
                column_config={
                    "x": st.column_config.NumberColumn(
                        "X",
                        format="%.2f",
                        step=0.01
                    ),
                    "y": st.column_config.NumberColumn(
                        "Y",
                        format="%.2f",
                        step=0.01
                    )
                }
            )

            # Extract x and y values from the dataframe
            node_x = nodes['x']  # x coordinate of node
            node_y = nodes['y']  # y coordinate of node

            # Convert to DataFrame (for getting index values)
            nodes_df = pd.DataFrame(nodes)

            # getting the index values
            node_index_values = nodes_df.index.tolist()

        for value in node_index_values:
            st.session_state.nodes_data.update({value: [node_x[value], node_y[value]]})

        # Verification of nodal data (only for debugging)
        # st.write(st.session_state.nodes_data)

    # Members---------------------------------------------------------------------------------------

    # Initialize members data if not present
    if 'members_data' not in st.session_state:
        st.session_state.members_data = {}


    # Renumbering function
    def renumber_members_data():
        values = list(st.session_state.members_data.values())
        st.session_state.members_data = {str(i): v for i, v in enumerate(values)}


    with col1:
        with st.popover('Members', width='stretch'):
            col1a, col2a = st.columns(2, vertical_alignment='top')

            with col1a:
                start_node = st.selectbox('First Node', options=node_index_values)

            with col2a:
                end_node = st.selectbox('Second Node', options=node_index_values)

            section_type = st.selectbox('Select Section', options=st.session_state.section_data.keys())

            st.divider()

            col1a, col2a = st.columns([2, 1.5], vertical_alignment='bottom')

            with col2a:
                add_member_but = st.button('Add', type='primary', width='stretch', key='3')

            with col1a:
                row_select = st.selectbox(
                    label='Select row',
                    options=list(st.session_state.members_data.keys()),
                    key='r2'
                )

            with col2a:
                remove_member_but = st.button('Delete', width='stretch', key='4')

            # Prepare the member data for table
            member_name_values_list = []
            start_node_values_list = []
            end_node_values_list = []
            section_type_list = []

            # Extract the member data
            for member in st.session_state.members_data:
                member_name_values_list.append(member)
                start_node_values_list.append(st.session_state.members_data[member]['Start Node'])
                end_node_values_list.append(st.session_state.members_data[member]['End Node'])
                section_type_list.append(st.session_state.members_data[member]['Section Type'])

            # Display the members data
            data_for_members_table = {'Member ID': member_name_values_list,
                                      'Start Node': start_node_values_list,
                                      'End Node': end_node_values_list,
                                      'Section': section_type_list}

            members_table = st.dataframe(data_for_members_table,
                                         width='stretch',
                                         hide_index=True)

    # Add member logic
    if add_member_but:

        sorted_nodes = sorted([
            st.session_state.nodes_data[start_node],
            st.session_state.nodes_data[end_node]
        ])

        start_node_value = sorted_nodes[0]
        end_node_value = sorted_nodes[1]

        # Find the respective Start node ID w.r.t to it's value
        # Suppose you want to find the key with value [5, 0]
        target_value = start_node_value

        start_node = None
        for key, value in st.session_state.nodes_data.items():
            if value == target_value:
                start_node = key
                break

        # Find the respective End node ID w.r.t to it's value
        # Suppose you want to find the key with value [5, 0]
        target_value = end_node_value

        end_node = None
        for key, value in st.session_state.nodes_data.items():
            if value == target_value:
                end_node = key
                break

        if all(x is not None for x in [start_node, end_node]):
            st.session_state.members_data[str(len(st.session_state.members_data))] = {
                'Start Node Value': st.session_state.nodes_data[start_node],
                'End Node Value': st.session_state.nodes_data[end_node],
                'Start Node': start_node,
                'End Node': end_node,
                'Section Type': section_type
            }
            renumber_members_data()
            st.rerun()

    # Remove member logic
    if remove_member_but:
        if row_select in st.session_state.members_data:
            del st.session_state.members_data[row_select]
            renumber_members_data()
            st.rerun()

    # Display the members data for verification (only for debugging)
    # st.write(st.session_state.members_data)

    # Supports----------------------------------------------------------------------------------------------
    if 'supports_node_list' not in st.session_state:
        st.session_state.supports_node_list = []

    if 'supports_type_list' not in st.session_state:
        st.session_state.supports_type_list = []

    with col1:
        with st.popover('Supports', width='stretch'):
            col1a, col2a = st.columns([0.4, 0.6], vertical_alignment='top')

            with col1a:
                support_node = st.selectbox('Select Node', options=node_index_values)

            with col2a:
                support_type = st.selectbox('Select Support Type', options=['Fixed',
                                                                            'Pinned',
                                                                            'Roller (horizontal-bottom)',
                                                                            'Roller (horizontal-top)',
                                                                            'Roller (vertical-left)',
                                                                            'Roller (vertical-right)'])

            st.divider()

            col1a, col2a = st.columns([2, 1.5], vertical_alignment='bottom')

            with col2a:
                add_support_but = st.button('Add', type='primary', width='stretch', key='5')

            with col1a:
                row_select = st.selectbox(
                    label='Select row',
                    options=[x for x in range(len(st.session_state.supports_node_list))],
                    key='r3'
                )

            with col2a:
                remove_support_but = st.button('Delete', width='stretch', key='6')

            # Display the support data store in the memory

            support_data_for_table = {'Node': st.session_state.supports_node_list,
                                      'Support Type': st.session_state.supports_type_list}

            # Check the data (For Debugging only)
            # st.write(support_data_for_table)

            # Display the editable table that will be later used to extract values to be used
            support_table = st.dataframe(support_data_for_table,
                                         width='stretch',
                                         hide_index=False)

            # Add the data to the respective lists on the press of Add button
            if add_support_but:
                if all(x is not None for x in [support_type, support_node]):
                    st.session_state.supports_node_list.append(support_node)
                    st.session_state.supports_type_list.append(support_type)
                    st.rerun()

            # Remove the data form the list on the basis of row selection
            if remove_support_but:
                if type(row_select) != type(None):
                    st.session_state.supports_node_list.pop(int(row_select))
                    st.session_state.supports_type_list.pop(int(row_select))
                    st.rerun()

    # Support Displacements/Settlements--------------------------------------------------------------------

    if 'settlement_node_list' not in st.session_state:
        st.session_state.settlement_node_list = []

    if 'settlement_direction_list' not in st.session_state:
        st.session_state.settlement_direction_list = []

    if 'settlement_mag_list' not in st.session_state:
        st.session_state.settlement_mag_list = []

    with col1:
        with st.popover('Support Settlements', width='stretch'):
            col1a, col2a = st.columns([0.4, 0.6], vertical_alignment='top')

            # Node at which displacement is to be modeled
            with col1a:
                displaced_node = st.selectbox('Select Node', options=st.session_state.supports_node_list,
                                              key='displaced_node')

            # Direction of settlement
            with col2a:
                displacement_type = st.selectbox('Select Displacement Direction',
                                                 options=['X', 'Y', 'Rotation'],
                                                 key='displacement_type')

            # Magnitude of settlement
            displacement_mag = st.number_input('Magnitude',
                                               format="%0.3f",
                                               value=None,
                                               placeholder=units_dict[unit_systems]['Placeholder']['Settlement'][
                                                   'rot'] if displacement_type == 'Rotation' else
                                               units_dict[unit_systems]['Placeholder']['Settlement']['axial'],
                                               key='settlement_mag')

            st.divider()

            col1a, col2a = st.columns([2, 1.5], vertical_alignment='bottom')

            with col2a:
                add_nodal_settle_but = st.button('Add', type='primary', width='stretch', key='7')

            with col1a:
                row_select = st.selectbox(
                    label='Select row',
                    options=[x for x in range(len(st.session_state.settlement_node_list))],
                    key='r4'
                )

            with col2a:
                remove_nodal_settle_but = st.button('Delete', width='stretch', key='8')

            # Display the settlement data store in the memory

            nodal_settle_data_for_table = {'Node': st.session_state.settlement_node_list,
                                           'Displacement Type': st.session_state.settlement_direction_list,
                                           f'Magnitude': st.session_state.settlement_mag_list}

            # Check the data (For Debugging only)
            # st.write(nodal_settle_data_for_table)

            # Display the editable table that will be later used to extract values to be used
            nodal_settlement_table = st.dataframe(nodal_settle_data_for_table,
                                                  width='stretch',
                                                  hide_index=False)

            # Add the data to the respective lists on the press of Add button
            if add_nodal_settle_but:
                if all(x is not None for x in [displaced_node, displacement_type, displacement_mag]):
                    st.session_state.settlement_node_list.append(displaced_node)
                    st.session_state.settlement_direction_list.append(displacement_type)
                    st.session_state.settlement_mag_list.append(float(displacement_mag))
                    st.rerun()

            # Remove the data form the list on the basis of row selection
            if remove_nodal_settle_but:
                if type(row_select) != type(None):
                    st.session_state.settlement_node_list.pop(int(row_select))
                    st.session_state.settlement_direction_list.pop(int(row_select))
                    st.session_state.settlement_mag_list.pop(int(row_select))
                    st.rerun()

    with col2:
        model_figure = st.plotly_chart(figure_or_data=Plot_Model(title='Model',
                                                                 show_Nodal_Point_Loads=False,
                                                                 show_Nodal_Point_Moments=False,
                                                                 show_Member_Point_Loads=False,
                                                                 show_Member_Moments=False,
                                                                 show_Member_Distributed_Loads=False,
                                                                 show_member_labels=member_label),
                                       width='stretch',
                                       key='plot1')

# Loads Section Tab========================================================================================
with tab3:
    # Columns for input widgets and figure display
    col1, col2 = st.columns([0.4, 0.6], gap='small')

    # Nodal Point Loads (NPL)---------------------------------------------------------------------------------------

    # Initialize Nodal Point Load (NPL) node list if not present
    if 'npl_node_list' not in st.session_state:
        st.session_state.npl_node_list = []

    # Initialize Nodal Point Load (NPL) direction list if not present
    if 'npl_direction_list' not in st.session_state:
        st.session_state.npl_direction_list = []

    # Initialize Nodal Point Load (NPL) magnitude list if not present
    if 'npl_mag_list' not in st.session_state:
        st.session_state.npl_mag_list = []

    with col1:
        with st.popover(':red-background[**Nodal**] - Point Loads', width='stretch'):

            ### Layout --------------------------------------------------
            # Node at which point load is to be applied
            npl_node = st.selectbox('Select Node',
                                    options=node_index_values,
                                    key='npl_node')

            # magnitude of nodal point load
            npl_mag = st.number_input('Magnitude',
                                      min_value=0.000,
                                      format="%0.3f",
                                      value=None,
                                      placeholder=units_dict[unit_systems]['Placeholder']['F'],
                                      key='npl_mag')

            npl_direction = st.pills("Direction",
                                     options=["↑", "↓", "←", "→"],
                                     default="↑",
                                     selection_mode="single",
                                     key='pl2')

            st.divider()

            col1a, col2a = st.columns([2, 1.5], vertical_alignment='bottom')

            with col2a:
                add_npl_but = st.button('Add', type='primary', width='stretch', key='npl_1')

            with col1a:
                row_select = st.selectbox(
                    label='Select row',
                    options=[x for x in range(len(st.session_state.npl_node_list))],
                    key='npl_2'
                )

            with col2a:
                remove_npl_but = st.button('Delete', width='stretch', key='npl_3')

            # Display the Nodal Point Load data store in the memory

            npl_data_for_table = {'Node': st.session_state.npl_node_list,
                                  f"Magnitude {units_dict[unit_systems]['Placeholder']['F']}": st.session_state.npl_mag_list,
                                  'Direction': st.session_state.npl_direction_list}

            # Check the data (For Debugging only)
            # st.write(npl_data_for_table)

            # Display the editable table that will be later used to extract values to be used
            npl_table = st.dataframe(npl_data_for_table,
                                     width='stretch',
                                     hide_index=False)

            # Store all the data to the respective lists on the press of add button
            if add_npl_but:
                if all(x is not None for x in [npl_node, npl_mag, npl_direction]):
                    st.session_state.npl_node_list.append(npl_node)
                    st.session_state.npl_direction_list.append(npl_direction)
                    st.session_state.npl_mag_list.append(npl_mag)
                    st.rerun()

            # Remove the data form the list on the basis of row selection
            if remove_npl_but:
                if type(row_select) != type(None):
                    st.session_state.npl_node_list.pop(int(row_select))
                    st.session_state.npl_direction_list.pop(int(row_select))
                    st.session_state.npl_mag_list.pop(int(row_select))
                    st.rerun()

    # Nodal Point Moments (NPM)---------------------------------------------------------------------------------------

    # Initialize Nodal Point Moments (NPM) node list if not present
    if 'npm_node_list' not in st.session_state:
        st.session_state.npm_node_list = []

    # Initialize Nodal Point Moments (NPM) direction list if not present
    if 'npm_direction_list' not in st.session_state:
        st.session_state.npm_direction_list = []

    # Initialize Nodal Point Moments (NPM) magnitude list if not present
    if 'npm_mag_list' not in st.session_state:
        st.session_state.npm_mag_list = []

    with col1:
        with st.popover(':red-background[**Nodal**] - Point Moments', width='stretch'):
            ### Layout --------------------------------------------------
            # Node at which point load is to be applied
            npm_node = st.selectbox('Select Node',
                                    options=node_index_values,
                                    key='npm_node')

            # magnitude of nodal point load
            npm_mag = st.number_input('Magnitude',
                                      min_value=0.000,
                                      format="%0.3f",
                                      value=None,
                                      placeholder=units_dict[unit_systems]['Placeholder']['M'],
                                      key='npm_mag')

            npm_direction = st.pills("Direction",
                                     options=["↻", "↺"],
                                     default="↻",
                                     selection_mode="single",
                                     key='npm_dir')

            st.divider()

            col1a, col2a = st.columns([2, 1.5], vertical_alignment='bottom')

            with col2a:
                add_npm_but = st.button('Add', type='primary', width='stretch', key='npm_1')

            with col1a:
                row_select = st.selectbox(
                    label='Select row',
                    options=[x for x in range(len(st.session_state.npm_node_list))],
                    key='npm_2'
                )

            with col2a:
                remove_npm_but = st.button('Delete', width='stretch', key='npm_3')

            # Display the Nodal Point Load data store in the memory

            npm_data_for_table = {'Node': st.session_state.npm_node_list,
                                  f"Magnitude {units_dict[unit_systems]['Placeholder']['M']}": st.session_state.npm_mag_list,
                                  'Direction': st.session_state.npm_direction_list}

            # st.write(npl_data_for_table)

            st.dataframe(npm_data_for_table,
                         width='stretch',
                         hide_index=False)

            # Store all the data to the respective lists on the press of add button
            if add_npm_but:
                if all(x is not None for x in [npm_node, npm_mag, npm_direction]):
                    st.session_state.npm_node_list.append(npm_node)
                    st.session_state.npm_direction_list.append(npm_direction)
                    st.session_state.npm_mag_list.append(npm_mag)
                    st.rerun()

            # Remove the data form the list on the basis of row selection
            if remove_npm_but:
                if type(row_select) != type(None):
                    st.session_state.npm_node_list.pop(int(row_select))
                    st.session_state.npm_direction_list.pop(int(row_select))
                    st.session_state.npm_mag_list.pop(int(row_select))
                    st.rerun()

    # Member Point Load (MPL)---------------------------------------------------------------------------------------

    # Initialize Member Point Loads (MPL) direction list if not present
    if 'mpl_direction_list' not in st.session_state:
        st.session_state.mpl_direction_list = []

    # Placed on start of code
    # Initialize Member Point Loads (MPL) member list if not present
    # if 'mpl_members_list' not in st.session_state:
    #     st.session_state.mpl_members_list = []

    # Initialize Member Point Loads (MPL) location of load list if not present
    if 'mpl_location_list' not in st.session_state:
        st.session_state.mpl_location_list = []

    # Initialize Member Point Loads (MPL) magnitude list if not present
    if 'mpl_mag_list' not in st.session_state:
        st.session_state.mpl_mag_list = []

    with col1:
        with st.popover(':red-background[**Member**] - Point Loads', width='stretch'):
            ### Layout --------------------------------------------------

            if st.session_state.members_data.keys():
                # Member at which point load is to be applied
                mpl_member = st.selectbox('Select Member',
                                          options=st.session_state.members_data.keys(),
                                          key='mpl_member')

                col1a, col2a = st.columns(2, vertical_alignment='bottom')

                with col1a:
                    # distance of point load from start node
                    mpl_x = st.number_input('Distance (x)',
                                            min_value=0.000,
                                            format="%0.3f",
                                            value=None,
                                            max_value=calculate_member_length(mpl_member),
                                            placeholder=units_dict[unit_systems]['Placeholder']['L'],
                                            key='mpl_x')

                with col2a:
                    # magnitude of nodal point load
                    mpl_mag = st.number_input('Magnitude',
                                              min_value=0.000,
                                              format="%0.3f",
                                              value=None,
                                              placeholder=units_dict[unit_systems]['Placeholder']['F'],
                                              key='mpl_mag')

                mpl_direction = st.pills("Direction",
                                         options=["↑", "↓"],
                                         default="↓",
                                         selection_mode="single",
                                         key='mpl_load')

                with st.expander('Load Preview'):
                    st.plotly_chart(Plot_Member_Point_Load_Preview(member=mpl_member,
                                                                   location=mpl_x,
                                                                   direction=mpl_direction,
                                                                   magnitude=mpl_mag),
                                    key='mpl_load_preview')

                st.divider()

                col1a, col2a = st.columns([2, 1.5], vertical_alignment='bottom')

                with col2a:
                    add_mpl_but = st.button('Add', type='primary', width='stretch', key='mpl_1')

                with col1a:
                    row_select = st.selectbox(
                        label='Select row',
                        options=[x for x in range(len(st.session_state.mpl_members_list))],
                        key='mpl_2'
                    )

                with col2a:
                    remove_mpl_but = st.button('Delete', width='stretch', key='mpl_3')

                # Display the Member Point Load data store in the memory

                mpl_data_for_table = {'Member': st.session_state.mpl_members_list,
                                      f"Location {units_dict[unit_systems]['Placeholder']['L']}": st.session_state.mpl_location_list,
                                      f"Magnitude {units_dict[unit_systems]['Placeholder']['F']}": st.session_state.mpl_mag_list,
                                      'Direction': st.session_state.mpl_direction_list}

                # st.write(npl_data_for_table)

                st.dataframe(mpl_data_for_table,
                             width='stretch',
                             hide_index=False)

                # Store all the data to the respective lists on the press of add button
                if add_mpl_but:
                    if all(x is not None for x in [mpl_member, mpl_x, mpl_mag, mpl_direction]):
                        st.session_state.mpl_members_list.append(mpl_member)
                        st.session_state.mpl_location_list.append(mpl_x)
                        st.session_state.mpl_direction_list.append(mpl_direction)
                        st.session_state.mpl_mag_list.append(mpl_mag)
                        st.rerun()

                # Remove the data form the list on the basis of row selection
                if remove_mpl_but:
                    if type(row_select) != type(None):
                        st.session_state.mpl_members_list.pop(int(row_select))
                        st.session_state.mpl_location_list.pop(int(row_select))
                        st.session_state.mpl_direction_list.pop(int(row_select))
                        st.session_state.mpl_mag_list.pop(int(row_select))
                        st.rerun()

    # Member Point Moments (MPM)---------------------------------------------------------------------------------------

    # Initialize Member Point Moments (MPM) direction list if not present
    if 'mpm_direction_list' not in st.session_state:
        st.session_state.mpm_direction_list = []

    # Placed on start of code
    # # Initialize Member Point Moments (MPM) member list if not present
    # if 'mpm_members_list' not in st.session_state:
    #     st.session_state.mpm_members_list = []

    # Initialize Member Point Moments (MPM) location of load list if not present
    if 'mpm_location_list' not in st.session_state:
        st.session_state.mpm_location_list = []

    # Initialize Member Point Moments (MPM) magnitude list if not present
    if 'mpm_mag_list' not in st.session_state:
        st.session_state.mpm_mag_list = []

    with col1:
        with st.popover(':red-background[**Member**] - Point Moments', width='stretch'):
            ### Layout --------------------------------------------------

            if st.session_state.members_data.keys():
                # Member at which point load is to be applied
                mpm_member = st.selectbox('Select Member',
                                          options=st.session_state.members_data.keys(),
                                          key='mpm_member')

                col1a, col2a = st.columns(2, vertical_alignment='bottom')

                with col1a:
                    # distance of point load from start node
                    mpm_x = st.number_input('Distance (x)',
                                            min_value=0.000,
                                            format="%0.3f",
                                            value=None,
                                            max_value=calculate_member_length(mpl_member),
                                            placeholder=units_dict[unit_systems]['Placeholder']['L'],
                                            key='mpm_x')

                with col2a:
                    # magnitude of member point moment
                    mpm_mag = st.number_input('Magnitude',
                                              min_value=0.000,
                                              format="%0.3f",
                                              value=None,
                                              placeholder=units_dict[unit_systems]['Placeholder']['M'],
                                              key='mpm_mag')

                mpm_direction = st.pills("Direction",
                                         options=["↻", "↺"],
                                         default="↻",
                                         selection_mode="single",
                                         key='mpm_load')

                with st.expander('Load Preview'):
                    st.plotly_chart(Plot_Member_Point_Load_Preview(member=mpm_member,
                                                                   location=mpm_x,
                                                                   direction=mpm_direction,
                                                                   magnitude=mpm_mag),
                                    key='mpm_load_preview')

                st.divider()

                col1a, col2a = st.columns([2, 1.5], vertical_alignment='bottom')

                with col2a:
                    add_mpm_but = st.button('Add', type='primary', width='stretch', key='mpm_1')

                with col1a:
                    row_select = st.selectbox(
                        label='Select row',
                        options=[x for x in range(len(st.session_state.mpm_members_list))],
                        key='mpm_2'
                    )

                with col2a:
                    remove_mpm_but = st.button('Delete', width='stretch', key='mpm_3')

                # Display the Member Point Load data store in the memorym
                mpm_data_for_table = {'Member': st.session_state.mpm_members_list,
                                      f"Location {units_dict[unit_systems]['Placeholder']['L']}": st.session_state.mpm_location_list,
                                      f"Magnitude {units_dict[unit_systems]['Placeholder']['F']}": st.session_state.mpm_mag_list,
                                      'Direction': st.session_state.mpm_direction_list}

                # st.write(npl_data_for_table)

                st.dataframe(mpm_data_for_table,
                             width='stretch',
                             hide_index=False)

                # Store all the data to the respective lists on the press of add button
                if add_mpm_but:
                    if all(x is not None for x in [mpm_member, mpm_x, mpm_mag, mpm_direction]):
                        st.session_state.mpm_members_list.append(mpm_member)
                        st.session_state.mpm_location_list.append(mpm_x)
                        st.session_state.mpm_direction_list.append(mpm_direction)
                        st.session_state.mpm_mag_list.append(mpm_mag)
                        st.rerun()

                # Remove the data form the list on the basis of row selection
                if remove_mpm_but:
                    if type(row_select) != type(None):
                        st.session_state.mpm_members_list.pop(int(row_select))
                        st.session_state.mpm_location_list.pop(int(row_select))
                        st.session_state.mpm_direction_list.pop(int(row_select))
                        st.session_state.mpm_mag_list.pop(int(row_select))
                        st.rerun()

    # Member Distributed Loads (MDL)---------------------------------------------------------------------------------------

    # Initialize Member Distributed Loads (MDL) direction list if not present
    if 'mdl_member_axis_list' not in st.session_state:
        st.session_state.mdl_member_axis_list = []
    #
    # # Placed on start of code
    # Initialize Member Distributed Loads (MDL) member list if not present
    # if 'mdl_members_list' not in st.session_state:
    #     st.session_state.mdl_members_list = []
    #
    # Initialize Member Distributed Loads (MDL) location (x1) of load 1 list if not present
    if 'mdl_x1_list' not in st.session_state:
        st.session_state.mdl_x1_list = []

    # Initialize Member Distributed Loads (MDL) location (x1) of load 1 list if not present
    if 'mdl_x2_list' not in st.session_state:
        st.session_state.mdl_x2_list = []

    # Initialize Member Distributed Loads (MDL) load 1 list if not present
    if 'mdl_mag1_list' not in st.session_state:
        st.session_state.mdl_mag1_list = []

    # Initialize Member Distributed Loads (MDL) load 1 list if not present
    if 'mdl_mag2_list' not in st.session_state:
        st.session_state.mdl_mag2_list = []

    # Initialize Member Distributed Loads (MDL) direction list if not present
    if 'mdl_direction_list' not in st.session_state:
        st.session_state.mdl_direction_list = []

    with col1:
        with st.popover(':red-background[**Member**] - Distributed Loads', width='stretch'):
            ### Layout --------------------------------------------------

            if st.session_state.members_data.keys():

                # Select axis (Global or Local) along which the load is to be applied
                mdl_member_axis = st.radio(label='Select Axis System',
                                           options=["Local", "Global"],
                                           captions=[
                                               "The distributed loads will be applied perpendicular to the Local Axis of selected member",
                                               "The distributed loads will be applied w.r.t the Global Axis of structure"
                                           ]
                                           )

                # Member at which point load is to be applied
                mdl_member = st.selectbox('Select Member',
                                          options=st.session_state.members_data.keys(),
                                          key='mdl_member')

                col1a, col2a = st.columns(2, vertical_alignment='bottom')

                with col1a:
                    # distance of point load from start node
                    mdl_x1 = st.number_input('Distance (x₁)',
                                             min_value=0.000,
                                             format="%0.3f",
                                             value=0.0,
                                             max_value=calculate_member_length(mdl_member),
                                             placeholder=units_dict[unit_systems]['Placeholder']['L'],
                                             key='mdl_x1')

                with col2a:
                    # distance of point load from start node
                    mdl_x2 = st.number_input('Distance (x₂)',
                                             min_value=0.000,
                                             format="%0.3f",
                                             value=calculate_member_length(mdl_member),
                                             max_value=calculate_member_length(mdl_member),
                                             placeholder=units_dict[unit_systems]['Placeholder']['L'],
                                             key='mdl_x2')

                with col1a:
                    # magnitude of member distributed load
                    mdl_mag1 = st.number_input('Start Magnitude',
                                               min_value=0.000,
                                               format="%0.3f",
                                               value=None,
                                               placeholder=units_dict[unit_systems]['Placeholder']['F'],
                                               key='mdl_mag1')
                with col2a:
                    # magnitude of member distributed load
                    mdl_mag2 = st.number_input('End Magnitude',
                                               min_value=0.000,
                                               format="%0.3f",
                                               value=None,
                                               placeholder=units_dict[unit_systems]['Placeholder']['F'],
                                               key='mdl_mag2')

                if mdl_member_axis == 'Local':
                    mdl_direction = st.pills("Direction",
                                             options=["↑", "↓"],
                                             default="↓",
                                             selection_mode="single",
                                             key='mdl_direction')

                else:
                    mdl_direction = st.pills("Direction",
                                             options=["↑", "↓", "←", "→"],
                                             default="↑",
                                             selection_mode="single",
                                             key='mdl_direction')

                with st.expander('Load Preview'):
                    if all(x is not None for x in [mdl_x1, mdl_x2, mdl_mag1, mdl_mag2]):
                        st.plotly_chart(Plot_Member_Distributed_Load_Preview(member=mdl_member,
                                                                             axis_system=mdl_member_axis,
                                                                             x1=mdl_x1,
                                                                             x2=mdl_x2,
                                                                             mag1=mdl_mag1,
                                                                             mag2=mdl_mag2,
                                                                             direction=mdl_direction),
                                        key='mdl_load_preview')

                st.divider()

                col1a, col2a = st.columns([2, 1.5], vertical_alignment='bottom')

                with col2a:
                    add_mdl_but = st.button('Add', type='primary', width='stretch', key='mdl_1')

                with col1a:
                    row_select = st.selectbox(
                        label='Select row',
                        options=[x for x in range(len(st.session_state.mdl_members_list))],
                        key='mdl_2'
                    )

                with col2a:
                    remove_mdl_but = st.button('Delete', width='stretch', key='mdl_3')

                # Display the Member Point Load data store in the memory
                mdl_data_for_table = {'Member': st.session_state.mdl_members_list,
                                      'Axis System': st.session_state.mdl_member_axis_list,
                                      f"Distance (x₁) {units_dict[unit_systems]['Placeholder']['L']}": st.session_state.mdl_x1_list,
                                      f"Distance (x₂) {units_dict[unit_systems]['Placeholder']['L']}": st.session_state.mdl_x2_list,
                                      f"Mag-1 {units_dict[unit_systems]['Placeholder']['F']}": st.session_state.mdl_mag1_list,
                                      f"Mag-2 {units_dict[unit_systems]['Placeholder']['F']}": st.session_state.mdl_mag2_list,
                                      'Direction': st.session_state.mdl_direction_list}

                # st.write(mdl_data_for_table)

                st.dataframe(mdl_data_for_table,
                             width='stretch',
                             hide_index=False)

                # Store all the data to the respective lists on the press of add button
                if add_mdl_but:
                    if all(x is not None for x in
                           [mdl_member, mdl_member_axis, mdl_x1, mdl_x2, mdl_mag1, mdl_mag2, mdl_direction]):
                        st.session_state.mdl_members_list.append(mdl_member)
                        st.session_state.mdl_member_axis_list.append(mdl_member_axis)
                        st.session_state.mdl_x1_list.append(mdl_x1)
                        st.session_state.mdl_x2_list.append(mdl_x2)
                        st.session_state.mdl_mag1_list.append(mdl_mag1)
                        st.session_state.mdl_mag2_list.append(mdl_mag2)
                        st.session_state.mdl_direction_list.append(mdl_direction)
                        st.rerun()

                # Remove the data form the list on the basis of row selection
                if remove_mdl_but:
                    if type(row_select) != type(None):
                        st.session_state.mdl_members_list.pop(int(row_select))
                        st.session_state.mdl_member_axis_list.pop(int(row_select))
                        st.session_state.mdl_x1_list.pop(int(row_select))
                        st.session_state.mdl_x2_list.pop(int(row_select))
                        st.session_state.mdl_mag1_list.pop(int(row_select))
                        st.session_state.mdl_mag2_list.pop(int(row_select))
                        st.session_state.mdl_direction_list.pop(int(row_select))
                        st.rerun()

    with col2:
        load_model_figure = st.plotly_chart(figure_or_data=Plot_Model(title='Model with Loads',
                                                                      show_member_labels=True),
                                            width='stretch',
                                            key='plot2')

    with tab4:

        # Columns for input widgets and figure display
        col1, col2 = st.columns([0.4, 0.6], gap='small')

        with col1:
            with st.container(border=True,
                              key='analysis_cont'):
                structure_type = st.radio('Structure Type',
                                          options=['Frame', 'Truss'])

            # Analysis button
            analyze_but = st.button('Analyze',
                                    width='content',
                                    key='analyze_but')

        with col2:
            final_model_figure = st.plotly_chart(figure_or_data=Plot_Model(title='Final Model',
                                                                           show_member_labels=member_label),
                                                 width='stretch',
                                                 key='plot3')

        if analyze_but:
            # Initialize Pynite model
            model = FEModel3D()

            # Adding nodes to model-------------------------------
            for i in st.session_state.nodes_data.keys():
                model.add_node(name=f'{i}',
                               X=st.session_state.nodes_data[i][0],
                               Y=st.session_state.nodes_data[i][1],
                               Z=0)

            # Define and add materials and add sections using sections_data as a reference

            for i in st.session_state.section_data.keys():
                # Example Format
                # st.session_state.section_data.update({'Default': {
                #     'E': (units_dict[unit_systems]['Default_Section']['E']),
                #     'I': (units_dict[unit_systems]['Default_Section']['I']),
                #     'A': (units_dict[unit_systems]['Default_Section']['A']),
                # }
                # })
                section_name = i  # Name of section
                material_name = f'{section_name} Material'  # Name of material
                E = st.session_state.section_data[i]['E']  # Modulus of Elasticity
                Iz = st.session_state.section_data[i]['I']  # Moment of Inertia
                A = st.session_state.section_data[i]['A']  # Area of Section
                Iy = Iz
                J = 1
                nu = 1  # Poisson's ratio
                G = 1  # Shear modulus of elasticity
                rho = 1  # Density

                # Add a material with the following properties
                model.add_material(material_name,
                                   E * units_dict[unit_systems]['conv_fact']['E'],
                                   G, nu, rho)  # Useless in current scenario

                # Add a section with the following properties:
                model.add_section(section_name,
                                  A=A * units_dict[unit_systems]['conv_fact']['A'],
                                  Iz=Iz * units_dict[unit_systems]['conv_fact']['I'],
                                  Iy=Iy, J=J)  # Useless in current scenario

            # Add all members to the Model with respect to the members_data dictionary
            for i in st.session_state.members_data.keys():
                member_name = str(i)  # Gets the member name
                i_node = str(st.session_state.members_data[i]['Start Node'])
                j_node = str(st.session_state.members_data[i]['End Node'])
                section_name = str(st.session_state.members_data[i]['Section Type'])

                model.add_member(member_name,
                                 i_node=i_node,
                                 j_node=j_node,
                                 section_name=section_name,
                                 material_name=f'{section_name} Material')


            # ----------------------------
            # Define Supports (2D frame assumptions inside 3D model)
            # ----------------------------
            # Add all the supports to Model with respect to supports_data
            for i in range(len(st.session_state.supports_node_list)):
                node_name = str(st.session_state.supports_node_list[i])
                support_type = st.session_state.supports_type_list[i]

                # Always lock out-of-plane DOF for 2D model
                base = dict(
                    support_DZ=True,
                    support_RX=True,
                    support_RY=True
                )

                if support_type == "Fixed":
                    model.def_support(
                        node_name=node_name,
                        support_DX=True,
                        support_DY=True,
                        support_RZ=True,
                        **base
                    )

                elif support_type == "Pinned":
                    model.def_support(
                        node_name=node_name,
                        support_DX=True,
                        support_DY=True,
                        support_RZ=False,
                        **base
                    )

                elif support_type in ["Roller (horizontal-bottom)", "Roller (horizontal-top)"]:
                    model.def_support(
                        node_name=node_name,
                        support_DX=False,
                        support_DY=True,
                        support_RZ=False,
                        **base
                    )

                elif support_type in ["Roller (vertical-left)", "Roller (vertical-right)"]:
                    model.def_support(
                        node_name=node_name,
                        support_DX=True,
                        support_DY=False,
                        support_RZ=False,
                        **base
                    )

            # Add all the nodal settlements/displacements to the model
            for i in range(len(st.session_state.settlement_node_list)):
                node_name = str(st.session_state.settlement_node_list[i])
                displacement_direction = str(st.session_state.settlement_direction_list[i])
                displacement_magnitude = st.session_state.settlement_mag_list[i]

                if displacement_direction == 'X':
                    model.def_node_disp(node_name=node_name,
                                        direction='DX',
                                        magnitude=displacement_magnitude *
                                                  units_dict[unit_systems]['conv_fact']['Settlement']['axial'])

                if displacement_direction == 'Y':
                    model.def_node_disp(node_name=node_name,
                                        direction='DY',
                                        magnitude=displacement_magnitude *
                                                  units_dict[unit_systems]['conv_fact']['Settlement']['axial'])

                if displacement_direction == 'Rotation':
                    model.def_node_disp(node_name=node_name,
                                        direction='RZ',
                                        magnitude=displacement_magnitude *
                                                  units_dict[unit_systems]['conv_fact']['Settlement']['rot'])

            # Add all the Nodal Point Loads (npl) to the Model with respect to npl_lists
            for i in range(len(st.session_state.npl_node_list)):
                node_name = str(st.session_state.npl_node_list[i])
                direction = str(st.session_state.npl_direction_list[i])
                mag = st.session_state.npl_mag_list[i]

                if direction in ['↓', '↑']:
                    # Add a point load
                    model.add_node_load(node_name=node_name,
                                        direction='FY',
                                        P=mag * sign_conv[direction])

                if direction in ["←", "→"]:
                    # Add a point load
                    model.add_node_load(node_name=node_name,
                                        direction='FX',
                                        P=mag * sign_conv[direction])

            # Add all the Nodal Point Moments (npm) to the Model with respect to npm_lists
            for i in range(len(st.session_state.npm_node_list)):
                node_name = str(st.session_state.npm_node_list[i])
                direction = str(st.session_state.npm_direction_list[i])
                mag = st.session_state.npm_mag_list[i]

                if direction in ['↻', '↺']:
                    # Add a point load
                    model.add_node_load(node_name=node_name,
                                        direction='MZ',
                                        P=mag * sign_conv[direction])

            # Add all the Member Point Loads (mpl) to the Model with respect to mpl_lists
            for i in range(len(st.session_state.mpl_members_list)):
                member_name = str(st.session_state.mpl_members_list[i])
                location = st.session_state.mpl_location_list[i]
                direction = str(st.session_state.mpl_direction_list[i])
                mag = st.session_state.mpl_mag_list[i]

                if direction in ["↑", '↓']:
                    # Add a point load
                    model.add_member_pt_load(member_name=member_name,
                                             direction='Fy',
                                             x=location,
                                             P=mag * sign_conv[direction])

            # Add all the Member Point Moments (mpm) to the Model with respect to mpm_lists
            for i in range(len(st.session_state.mpm_members_list)):
                member_name = str(st.session_state.mpm_members_list[i])
                location = st.session_state.mpm_location_list[i]
                direction = str(st.session_state.mpm_direction_list[i])
                mag = st.session_state.mpm_mag_list[i]

                if direction in ["↻", "↺"]:
                    # Add a point load
                    model.add_member_pt_load(member_name=member_name,
                                             direction='Mz',
                                             x=location,
                                             P=mag * sign_conv[direction])

            # Add all the Member Distributed Loads (mdl) to the Model with respect to mdl_lists
            for i in range(len(st.session_state.mdl_members_list)):
                member_name = str(st.session_state.mdl_members_list[i])
                x1 = st.session_state.mdl_x1_list[i]
                x2 = st.session_state.mdl_x2_list[i]
                mag_1 = st.session_state.mdl_mag1_list[i]
                mag_2 = st.session_state.mdl_mag2_list[i]
                direction = str(st.session_state.mdl_direction_list[i])
                axis_system = str(st.session_state.mdl_member_axis_list[i])

                if axis_system == 'Local':
                    model.add_member_dist_load(member_name=member_name,
                                               direction='Fy',
                                               # Adds load perpendicular to member's local axis (up or down) only
                                               x1=x1,
                                               x2=x2,
                                               w1=mag_1 * sign_conv[direction],
                                               w2=mag_2 * sign_conv[direction])

                if axis_system == 'Global':

                    if direction in ['↓', '↑']:
                        model.add_member_dist_load(member_name=member_name,
                                                   direction='FY',
                                                   x1=x1,
                                                   x2=x2,
                                                   w1=mag_1 * sign_conv[direction],
                                                   w2=mag_2 * sign_conv[direction])

                    if direction in ["←", "→"]:
                        model.add_member_dist_load(member_name=member_name,
                                                   direction='FX',
                                                   x1=x1,
                                                   x2=x2,
                                                   w1=mag_1 * sign_conv[direction],
                                                   w2=mag_2 * sign_conv[direction])

            # Analyze the frame
            model.analyze()

            # Show the notification
            st.toast('Analysis Successful!')

            # Extract all the Reactions
            if 'support_reactions_data' not in st.session_state:
                st.session_state.support_reactions_data = {}

            for i in st.session_state.supports_node_list:
                # Reaction in Global X Direction
                FX = Get_Model_Reactions(model=model,
                                         support_node=i,
                                         reaction_type='FX')

                # Reaction in Global Y Direction
                FY = Get_Model_Reactions(model=model,
                                         support_node=i,
                                         reaction_type='FY')

                # Moment Reaction along Global Z Direction
                MZ = Get_Model_Reactions(model=model,
                                         support_node=i,
                                         reaction_type='MZ')

                st.session_state.support_reactions_data.update({i: {'FX': FX,
                                                                    'FY': FY,
                                                                    'MZ': MZ}})

            # for debugging only
            # st.write(st.session_state.supports_node_list)
            # st.write(st.session_state.support_reactions_data)

            st.subheader('Reactions',
                         divider='rainbow')

            # Columns for input widgets and figure display
            col1, col2 = st.columns([0.4, 0.6], gap='small')

            with col1:
                FX_list = []  # Gets and stores all the horizontal reactions
                FY_list = []  # Gets and stores all the vertical reactions
                MZ_list = []  # Gets and stores all the moment reactions

                for i in st.session_state.support_reactions_data:
                    FX_list.append(st.session_state.support_reactions_data[i]['FX'])
                    FY_list.append(st.session_state.support_reactions_data[i]['FY'])
                    MZ_list.append(st.session_state.support_reactions_data[i]['MZ'])
                    # nodes.append(i)

                # Prepare the reactions data for table
                reaction_data_for_table = {'Node': st.session_state.support_reactions_data.keys(),
                                           f"Fx {units_dict[unit_systems]['Placeholder']['F']}": FX_list,
                                           f"Fy {units_dict[unit_systems]['Placeholder']['F']}": FY_list,
                                           f"Mz {units_dict[unit_systems]['Placeholder']['M']}": MZ_list
                                           }

                # Display the reactions data table
                st.dataframe(reaction_data_for_table,
                             width='stretch',
                             hide_index=False)

            # PLot the reactions diagram
            with col2:
                st.plotly_chart(Plot_Model(title='Reactions',
                                           show_reactions=True,
                                           show_settlements=False))

            # Deflected Shape diagram section
            st.subheader('Deflected Shape Diagram',
                         divider='rainbow')

            # Show the complete Deflected Shape diagram section
            Plot_Deflection_Diagram_with_Table()
            st.write('')

            # Axial forces section
            st.subheader('Axial Forces',
                         divider='rainbow')

            Display_Normal_Force_Section()
            st.write('')

            if structure_type == 'Frame':
                # Shear forces section
                st.subheader('Shear Forces',
                             divider='rainbow')

                # Show the complete shear force section
                Display_Shear_Force_Section()
                st.write('')

                # Bending Moment diagram section
                st.subheader('Bending Moments',
                             divider='rainbow')

                # Show the complete Bending Moment section
                Display_Bending_Moment_Section()
                st.write('')