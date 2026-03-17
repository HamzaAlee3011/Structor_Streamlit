import streamlit as st
from polygon_math import polygon
import numpy as np
import plotly.graph_objects as go

# === Section 0 === Functions for creating figure with marked properties =========================================

# Circle Hollow Figure shape drawing function
def circle_hollow_fig(outer_radius: float, inner_radius: float, unit_system: str):
    fig = go.Figure()

    # Center coordinates
    cx, cy = outer_radius, outer_radius

    # Generate circle coordinates
    theta = np.linspace(0, 2 * np.pi, 300)

    # Outer and inner ring coordinates
    outer_x = cx + outer_radius * np.cos(theta)
    outer_y = cy + outer_radius * np.sin(theta)

    inner_x = (cx + inner_radius * np.cos(theta))[::-1]  # reverse for correct fill
    inner_y = (cy + inner_radius * np.sin(theta))[::-1]

    # Combine to form a closed loop (annulus)
    ring_x = np.concatenate([outer_x, inner_x])
    ring_y = np.concatenate([outer_y, inner_y])

    # Add filled ring
    fig.add_trace(go.Scatter(
        x=ring_x, y=ring_y,
        fill='toself',
        mode='lines',
        name='Thickness',
        line=dict(color='#008080', width=1.5),
        fillcolor='rgba(0, 128, 128, 0.2)',
    ))

    # Center point
    fig.add_trace(go.Scatter(
        x=[cx], y=[cy],
        mode='markers+text',
        name='Center',
        text=[f"Center ({cx:.2f}, {cy:.2f})"],
        textposition='top center',
        marker=dict(color='red', size=8),
        textfont=dict(color='red', size=10)
    ))

    # Add center axes (gray dashed)
    fig.add_vline(x=outer_radius, line=dict(color="gray", width=1, dash="dash"))
    fig.add_hline(y=outer_radius, line=dict(color="gray", width=1, dash="dash"))

    # Axes from origin
    fig.add_vline(x=0, line=dict(color="black", width=1.5))
    fig.add_hline(y=0, line=dict(color="black", width=1.5))

    # Layout
    fig.update_layout(
        title="Hollow Circle (Pipe Section)",
        xaxis_title=f"X ({unit_system})",
        yaxis_title=f"Y ({unit_system})",
        showlegend=True,
        width=700,
        height=700
    )
    fig.update_yaxes(scaleanchor="x", scaleratio=1)

    return fig

# Circle Shape Section figure drawing function
def circle_fig(radius: float, unit_system: str):
    """
    Creates a Plotly figure showing a circle centered at origin using built-in shape.

    Args:
        radius (float): Radius of the circle.
        unit_system (str): Unit for X and Y axes labels.

    Returns:
        fig (go.Figure): Plotly figure of the circle.
    """

    # Create figure
    fig = go.Figure()

    # Add circle shape centered at (radius, radius)
    fig.add_shape(
        type="circle",
        xref="x", yref="y",
        x0=0, y0=0,  # i.e. (0, 0)
        x1=radius + radius, y1=radius + radius,  # i.e. (2r, 2r)
        line=dict(color="#008080", width=2),
        fillcolor="rgba(0, 128, 128, 0.1)",
    )

    # Add centroid marker
    fig.add_trace(go.Scatter(
        x=[radius], y=[radius],
        mode="markers+text",
        name="Centroid",
        marker=dict(color="red", size=10),
        text=[f"Centroid ({radius}, {radius})"],
        textposition="top center",
        textfont=dict(color="red", size=10)
    ))

    # Add center axes (gray dashed)
    fig.add_vline(x=radius, line=dict(color="gray", width=1, dash="dash"))
    fig.add_hline(y=radius, line=dict(color="gray", width=1, dash="dash"))

    # Axes from origin
    fig.add_vline(x=0, line=dict(color="black", width=1.5))
    fig.add_hline(y=0, line=dict(color="black", width=1.5))

    # Layout
    fig.update_layout(
        title="Circle with Centroid",
        xaxis_title=f"X ({unit_system})",
        yaxis_title=f"Y ({unit_system})",
        showlegend=True,
        width=850,
        height=700,
    )

    # Maintain aspect ratio
    fig.update_yaxes(scaleanchor="x", scaleratio=1)

    return fig


# Hollow rectangle figure drawing function
def rectangle_hollow_fig(outer_polygon_coord: list, inner_polygon_coord: list, unit_system: str):
    """
    Draws a hollow rectangle (or any polygon with a cut-out) with centroid and labels using Plotly.

    Parameters:
        outer_polygon_coord (list): List of [x, y] coordinates for the outer polygon.
        inner_polygon_coord (list): List of [x, y] coordinates for the inner polygon (cutout).
        unit_system (str): Unit system to be displayed on the axes.

    Returns:
        go.Figure: Plotly figure representing the hollow rectangle.
    """
    # Combine both polygons for total area and centroid
    combined_poly = polygon(outer_polygon_coord)
    centroid_origin = combined_poly.CenterMass
    area = combined_poly.Area

    # Prepare values for outer polygon
    outer_x = [pt[0] for pt in outer_polygon_coord] + [outer_polygon_coord[0][0]]
    outer_y = [pt[1] for pt in outer_polygon_coord] + [outer_polygon_coord[0][1]]

    # Prepare values for inner polygon
    inner_x = [pt[0] for pt in inner_polygon_coord] + [inner_polygon_coord[0][0]]
    inner_y = [pt[1] for pt in inner_polygon_coord] + [inner_polygon_coord[0][1]]

    fig = go.Figure()

    # Outer polygon
    fig.add_trace(go.Scatter(
        x=outer_x,
        y=outer_y,
        mode='lines+markers',
        name='Outer Polygon',
        line=dict(color="#004466", width=2),
        marker=dict(color='deepskyblue', size=6)
    ))

    # Inner polygon
    fig.add_trace(go.Scatter(
        x=inner_x,
        y=inner_y,
        mode='lines+markers',
        name='Inner Polygon (Hole)',
        line=dict(color="#004466", width=2),
        marker=dict(color='deepskyblue', size=6)
    ))

    # Fill outer polygon with cut-out
    fig.add_trace(go.Scatter(
        x=outer_x + inner_x[::-1],  # Close path including hole
        y=outer_y + inner_y[::-1],
        fill='toself',
        mode='none',
        fillcolor='rgba(0, 128, 128, 0.1)',
        showlegend=False
    ))

    # Vertex Labels (Grouped)
    label_x = [pt[0] for pt in outer_polygon_coord + inner_polygon_coord]
    label_y = [pt[1] for pt in outer_polygon_coord + inner_polygon_coord]
    labels = [f"({x},{y})" for x, y in outer_polygon_coord + inner_polygon_coord]

    fig.add_trace(go.Scatter(
        x=label_x,
        y=label_y,
        mode='text',
        name='Vertex Labels',
        visible='legendonly',
        text=labels,
        textposition="top center",
        textfont=dict(color='red', size=11)
    ))

    # Centroid marker and label
    fig.add_trace(go.Scatter(
        x=[centroid_origin[0]],
        y=[centroid_origin[1]],
        mode='markers+text',
        name='Centroid',
        marker=dict(color='red', size=10),
        text=[f'Centroid ({centroid_origin[0]:.2f}, {centroid_origin[1]:.2f})'],
        textposition='top center',
        textfont=dict(color='red', size=10)
    ))

    # Vertical and horizontal lines at centroid
    fig.add_vline(x=centroid_origin[0], line=dict(color="gray", width=1, dash="dash"))
    fig.add_hline(y=centroid_origin[1], line=dict(color="gray", width=1, dash="dash"))

    # Axes from origin
    fig.add_vline(x=0, line=dict(color="black", width=1.5))
    fig.add_hline(y=0, line=dict(color="black", width=1.5))

    # Layout
    fig.update_layout(
        title="Hollow Rectangle with Centroid",
        xaxis_title=f"X ({unit_system})",
        yaxis_title=f"Y ({unit_system})",
        showlegend=True,
        width=850,
        height=700
    )

    fig.update_yaxes(scaleanchor="x", scaleratio=1)

    return fig

# Function to create figures for polygon
def generalized_polygon_fig(polygon_coordinates: list, unit_system: str):
    # Original polygon for area and centroid
    poly_origin = polygon(polygon_coordinates)
    area = poly_origin.Area
    centroid_origin = poly_origin.CenterMass

    # Shift vertices to centroidal reference
    new_polygon_coordinates = [[x - centroid_origin[0], y - centroid_origin[1]] for x, y in polygon_coordinates]
    poly_centroid = polygon(new_polygon_coordinates)

    # Extract plotting values
    x_vals = [pt[0] for pt in polygon_coordinates] + [polygon_coordinates[0][0]]
    y_vals = [pt[1] for pt in polygon_coordinates] + [polygon_coordinates[0][1]]

    # Create plot
    fig = go.Figure()

    # Polygon edges (Teal Blue style)
    fig.add_trace(go.Scatter(
        x=x_vals, y=y_vals,
        mode='lines+markers',
        name='Polygon',
        line=dict(color="#004466", width=2),
        marker=dict(color='deepskyblue', size=6)
    ))

    # Fill polygon with light teal
    fig.add_trace(go.Scatter(
        x=x_vals, y=y_vals,
        fill='toself',
        mode='none',
        fillcolor='rgba(0, 128, 128, 0.1)',
        showlegend=False
    ))

    # --- Grouped Vertex Labels (as one trace) ---
    label_x = [pt[0] for pt in polygon_coordinates]
    label_y = [pt[1] for pt in polygon_coordinates]
    labels = [f"({x},{y})" for x, y in polygon_coordinates]

    fig.add_trace(go.Scatter(
        x=label_x,
        y=label_y,
        mode='text',
        name='Vertex Labels',
        visible='legendonly',  # 👈 Hide by default
        text=labels,
        textposition="top center",
        textfont=dict(color='red', size=11)
    ))

    # Centroid marker and label
    fig.add_trace(go.Scatter(
        x=[centroid_origin[0]],
        y=[centroid_origin[1]],
        mode='markers+text',
        name='Centroid',
        marker=dict(color='red', size=10),
        text=[f'Centroid ({centroid_origin[0]:.2f}, {centroid_origin[1]:.2f})'],
        textposition='top center',
        textfont=dict(color='red', size=10)
    ))

    # Vertical and horizontal dashed lines for centroid
    fig.add_vline(x=centroid_origin[0], line=dict(color="gray", width=1, dash="dash"))
    fig.add_hline(y=centroid_origin[1], line=dict(color="gray", width=1, dash="dash"))

    # X and Y axes from origin
    fig.add_vline(x=0, line=dict(color="black", width=1.5))
    fig.add_hline(y=0, line=dict(color="black", width=1.5))

    # Layout
    fig.update_layout(
        title="Polygon with Centroid",
        xaxis_title=f"X ({unit_system})",
        yaxis_title=f"Y ({unit_system})",
        showlegend=True,
        width=850,
        height=700
    )

    fig.update_yaxes(scaleanchor="x", scaleratio=1)

    return fig

# A function for custom polygon figure
def custom_polygon_fig(x_vals, y_vals, unit_system):

    # Create plot
    fig = go.Figure()

    # Polygon edges (Teal Blue style)
    fig.add_trace(go.Scatter(
        x=x_vals, y=y_vals,
        mode='lines+markers',
        name='Polygon',
        line=dict(color="#004466", width=2),
        marker=dict(color='deepskyblue', size=6)
    ))

    # Layout
    fig.update_layout(
        title="Custom Polygon",
        xaxis_title=f"X ({unit_system})",
        yaxis_title=f"Y ({unit_system})",
        showlegend=True,
        width=850,
        # height=700
    )

    fig.update_yaxes(scaleanchor="x", scaleratio=1)

    return fig

# === Section 1 === Functions for calculation of different sections  =========================================
def rectangle_shape(unit_system):
    # with st.container(border=True):
    st.write('##### :blue-background[**Parameters**]')
    col1, col2 = st.columns(2, gap='small', border=True)

    with col1:
        col1a, col2a = st.columns(2, gap='small')

        with col1a:
            b = st.number_input('Width (w)',
                                value=None,
                                min_value=0.000,
                                placeholder=unit_system)
        with col2a:
            h = st.number_input('Height (h)',
                                value=None,
                                min_value=0.000,
                                placeholder=unit_system)

    if b is not None and h is not None:
        # Calculate centroid
        x_bar = b / 2
        y_bar = h / 2

        # Calculate Moment of inertia about x-axis
        ix = (b * h ** 3) / 12

        # Calculate Moment of inertia about y-axis
        iy = (h * b ** 3) / 12

        # Calculates Area
        Area = b * h

        # col1, col2 = st.columns([2, 0.5], gap='small', vertical_alignment='bottom')

        with col1:
            # Result Heading
            st.write('\n')
            st.write('##### :blue-background[**Result**]')

            # Area Heading
            st.write(f"###### :red-background[Area]")
            st.code(f"{Area} {unit_system}²")

            # Centroid Heading
            st.write(f"###### :red-background[Centroid]")
            st.code(f"({x_bar.__round__(2)}, {y_bar.__round__(2)})")

            # Display moment of inertia about x-axis
            st.write(f"###### :red-background[Moment of Inertia - Ix]")
            st.code(f"{round(ix, 3)} {unit_system}⁴")

            # Display moment of inertia about y-axis
            st.write(f"###### :red-background[Moment of Inertia - Iy]")
            st.code(f"{round(iy, 3)} {unit_system}⁴")

    with col2:
        # Display the image of shape w.r.t cross-section shape
        st.image(shape_img_dict[shape_select], caption='Reference Image of Shape')

        coordinates = [[0, 0],
                       [0, h],
                       [b, h],
                       [b, 0],
                       # [0, 0]
                       ]

    if b is not None and h is not None:
        # show the plotly figure
        st.plotly_chart(figure_or_data=generalized_polygon_fig(polygon_coordinates=coordinates,
                                                               unit_system=unit_system),
                        theme=None)


# Rectangle hollow section function

def rectangle_hollow_shape(unit_system):
    # with st.container(border=True):
    st.write('##### :blue-background[**Parameters**]')
    col1, col2 = st.columns(2, gap='small', border=True)

    with col1:
        col1a, col2a = st.columns(2, gap='small')

        with col1a:
            b = st.number_input('Width (w)',
                                value=None,
                                min_value=0.000,
                                placeholder=unit_system)
        with col2a:
            h = st.number_input('Height (h)',
                                value=None,
                                min_value=0.000,
                                placeholder=unit_system)

        col1a, col2a = st.columns(2, gap='small')

        with col1a:
            t = st.number_input('Thickness (t)',
                                value=None,
                                min_value=0.000,
                                placeholder=unit_system)

    if all(x is not None for x in [b, h, t]):
        # Calculate centroid
        x_bar = b / 2
        y_bar = h / 2

        # Calculate Moment of inertia about x-axis
        # Outer rectangle Ix
        ix_outer = (b * h ** 3) / 12

        # Inner rectangle Ix
        ix_inner = ((b - 2 * t) * (h - 2 * t) ** 3) / 12

        # Resultant Ix
        Ix = ix_outer - ix_inner

        # Calculate Moment of inertia about y-axis
        # Outer rectangle Iy
        iy_outer = (h * b ** 3) / 12

        # Inner rectangle Iy
        iy_inner = ((h - 2 * t) * (b - 2 * t) ** 3) / 12

        # Resultant Ix
        Iy = iy_outer - iy_inner

        # Calculates Area
        Area = (b * h) - ((b - 2 * t) * (h - 2 * t))

        # col1, col2 = st.columns([2, 0.5], gap='small', vertical_alignment='bottom')

        with col1:
            # Result Heading
            st.write('\n')
            st.write('##### :blue-background[**Result**]')

            # Area Heading
            st.write(f"###### :red-background[Area]")
            st.code(f"{Area} {unit_system}²")

            # Centroid Heading
            st.write(f"###### :red-background[Centroid]")
            st.code(f"({x_bar.__round__(2)}, {y_bar.__round__(2)})")

            # Display moment of inertia about x-axis
            st.write(f"###### :red-background[Moment of Inertia - Ix]")
            st.code(f"{round(Ix, 3)} {unit_system}⁴")

            # Display moment of inertia about y-axis
            st.write(f"###### :red-background[Moment of Inertia - Iy]")
            st.code(f"{round(Iy, 3)} {unit_system}⁴")

            # Outer coordinates of rectangle
            outer_coordinates = [[0, 0],
                                 [0, h],
                                 [b, h],
                                 [b, 0],
                                 # [0, 0]
                                 ]

            # Inner coordinates of rectangle
            inner_coordinates = [[t, t],
                                 [t, t + (h - 2 * t)],
                                 [t + (b - 2 * t), t + (h - 2 * t)],
                                 [t + (b - 2 * t), t],
                                 # [0, 0]
                                 ]

    with col2:
        # Display the image of shape w.r.t cross-section shape
        st.image(shape_img_dict[shape_select], caption='Reference Image of Shape')

    if all(x is not None for x in [b, h, t]):
        # show the plotly figure
        st.plotly_chart(figure_or_data=rectangle_hollow_fig(outer_polygon_coord=outer_coordinates,
                                                            inner_polygon_coord=inner_coordinates,
                                                            unit_system=unit_system),
                        theme=None)


# I-shape (symmetrical) section function

def I_shape_symmetrical(unit_system: str):
    st.write('##### :blue-background[**Parameters**]')
    col1, col2 = st.columns(2, gap='small', border=True)

    with col1:
        col1a, col2a = st.columns(2, gap='small')

        with col1a:
            f_w = st.number_input('Flange Width (F-w)',
                                  value=None,
                                  min_value=0.000,
                                  placeholder=unit_system)
        with col2a:
            f_t = st.number_input('Flange Thickness (F-t)',
                                  value=None,
                                  min_value=0.000,
                                  placeholder=unit_system)

        col1a, col2a = st.columns(2, gap='small')
        with col1a:
            w_t = st.number_input('Web Thickness (W-t)',
                                  value=None,
                                  min_value=0.000,
                                  placeholder=unit_system)
        with col2a:
            w_h = st.number_input('Web Height (W-h)',
                                  value=None,
                                  min_value=0.000,
                                  placeholder=unit_system)

    if all(x is not None for x in [f_w, w_h, w_t, f_t]):
        # Defines the coordinates for I-shape
        shape_coordinates = [[0, 0],
                             [0, f_t],
                             [(f_w / 2) - (w_t / 2), f_t],
                             [(f_w / 2) - (w_t / 2), f_t + w_h],
                             [0, f_t + w_h],
                             [0, 2 * f_t + w_h],
                             [f_w, 2 * f_t + w_h],
                             [f_w, f_t + w_h],
                             [(f_w / 2) + (w_t / 2), f_t + w_h],
                             [(f_w / 2) + (w_t / 2), f_t],
                             [f_w, f_t],
                             [f_w, 0]]

        # Original polygon for area and centroid
        poly_origin = polygon(shape_coordinates)
        Area = poly_origin.Area
        centroid_origin = poly_origin.CenterMass

        # Shift vertices to centroidal reference
        new_polygon_coordinates = [[x - centroid_origin[0], y - centroid_origin[1]] for x, y in shape_coordinates]
        poly_centroid = polygon(new_polygon_coordinates)

        # # Calculate centroidal moments of inertia
        Ixx, Iyy, Ixy = poly_centroid.SecondMomentArea

        # Centroid calculations
        x_bar = centroid_origin[0]
        y_bar = centroid_origin[1]

        with col1:
            st.write('\n')
            st.write('##### :blue-background[**Result**]')

            # Area Heading
            st.write(f"###### :red-background[Area]")
            st.code(f"{Area} {unit_system}²")

            # Centroid Heading
            st.write(f"###### :red-background[Centroid]")
            st.code(f"({x_bar.__round__(2)}, {y_bar.__round__(2)})")

            # Display moment of inertia about x-axis
            st.write(f"###### :red-background[Moment of Inertia - Ix]")
            st.code(f"{round(Ixx, 3)} {unit_system}⁴")

            # Display moment of inertia about y-axis
            st.write(f"###### :red-background[Moment of Inertia - Iy]")
            st.code(f"{round(Iyy, 3)} {unit_system}⁴")

    with col2:
        # Display the image of shape w.r.t cross-section shape
        st.image(shape_img_dict[shape_select], caption='Reference Image of Shape')

    if all(x is not None for x in [f_w, w_h, w_t, f_t]):
        # show the plotly figure
        st.plotly_chart(figure_or_data=generalized_polygon_fig(polygon_coordinates=shape_coordinates,
                                                               unit_system=unit_system, ),
                        theme=None,
                        width='stretch')


# T-shape section function

def T_shape(unit_system: str):
    st.write('##### :blue-background[**Parameters**]')
    col1, col2 = st.columns(2, gap='small', border=True)

    with col1:
        col1a, col2a = st.columns(2, gap='small')

        with col1a:
            f_w = st.number_input('Flange Width (F-w)',
                                  value=None,
                                  min_value=0.000,
                                  placeholder=unit_system)
        with col2a:
            f_t = st.number_input('Flange Thickness (F-t)',
                                  value=None,
                                  min_value=0.000,
                                  placeholder=unit_system)

        col1a, col2a = st.columns(2, gap='small')
        with col1a:
            w_t = st.number_input('Web Thickness (W-t)',
                                  value=None,
                                  min_value=0.000,
                                  placeholder=unit_system)
        with col2a:
            w_h = st.number_input('Web Height (W-h)',
                                  value=None,
                                  min_value=0.000,
                                  placeholder=unit_system)

    if all(x is not None for x in [f_w, w_h, w_t, f_t]):
        # Defines the coordinates for I-shape
        shape_coordinates = [[(f_w / 2) - (w_t / 2), 0],
                             [(f_w / 2) - (w_t / 2), w_h],
                             [0, w_h],
                             [0, w_h + f_t],
                             [f_w, w_h + f_t],
                             [f_w, w_h],
                             [(f_w / 2) + (w_t / 2), w_h],
                             [(f_w / 2) + (w_t / 2), 0]]

        # Original polygon for area and centroid
        poly_origin = polygon(shape_coordinates)
        Area = poly_origin.Area
        centroid_origin = poly_origin.CenterMass

        # Shift vertices to centroidal reference
        new_polygon_coordinates = [[x - centroid_origin[0], y - centroid_origin[1]] for x, y in shape_coordinates]
        poly_centroid = polygon(new_polygon_coordinates)

        # # Calculate centroidal moments of inertia
        Ixx, Iyy, Ixy = poly_centroid.SecondMomentArea

        # Centroid calculations
        x_bar = centroid_origin[0]
        y_bar = centroid_origin[1]

        with col1:
            st.write('\n')
            st.write('##### :blue-background[**Result**]')

            # Area Heading
            st.write(f"###### :red-background[Area]")
            st.code(f"{Area} {unit_system}²")

            # Centroid Heading
            st.write(f"###### :red-background[Centroid]")
            st.code(f"({x_bar.__round__(2)}, {y_bar.__round__(2)})")

            # Display moment of inertia about x-axis
            st.write(f"###### :red-background[Moment of Inertia - Ix]")
            st.code(f"{round(Ixx, 3)} {unit_system}⁴")

            # Display moment of inertia about y-axis
            st.write(f"###### :red-background[Moment of Inertia - Iy]")
            st.code(f"{round(Iyy, 3)} {unit_system}⁴")

    with col2:
        # Display the image of shape w.r.t cross-section shape
        st.image(shape_img_dict[shape_select], caption='Reference Image of Shape')

    if all(x is not None for x in [f_w, w_h, w_t, f_t]):
        # show the plotly figure
        st.plotly_chart(figure_or_data=generalized_polygon_fig(polygon_coordinates=shape_coordinates,
                                                               unit_system=unit_system),
                        theme=None,
                        width='stretch')


# L-shape section function
def L_shape(unit_system: str):
    st.write('##### :blue-background[**Parameters**]')
    col1, col2 = st.columns(2, gap='small', border=True)

    with col1:
        col1a, col2a = st.columns(2, gap='small')

        with col1a:
            w = st.number_input('Width (w)',
                                value=None,
                                min_value=0.000,
                                placeholder=unit_system)
        with col2a:
            h = st.number_input('Height (h)',
                                value=None,
                                min_value=0.000,
                                placeholder=unit_system)

        col1a, col2a = st.columns(2, gap='small')

        with col1a:
            t = st.number_input('Thickness (t)',
                                value=None,
                                min_value=0.000,
                                placeholder=unit_system)

    if all(x is not None for x in [w, h, t]):
        # Defines the coordinates for I-shape
        shape_coordinates = [[0, 0],
                             [0, h],
                             [t, h],
                             [t, t],
                             [w, t],
                             [w, 0]]

        # Original polygon for area and centroid
        poly_origin = polygon(shape_coordinates)
        Area = poly_origin.Area
        centroid_origin = poly_origin.CenterMass

        # Shift vertices to centroidal reference
        new_polygon_coordinates = [[x - centroid_origin[0], y - centroid_origin[1]] for x, y in shape_coordinates]
        poly_centroid = polygon(new_polygon_coordinates)

        # # Calculate centroidal moments of inertia
        Ixx, Iyy, Ixy = poly_centroid.SecondMomentArea

        # Centroid calculations
        x_bar = centroid_origin[0]
        y_bar = centroid_origin[1]

        with col1:
            st.write('\n')
            st.write('##### :blue-background[**Result**]')

            # Area Heading
            st.write(f"###### :red-background[Area]")
            st.code(f"{Area} {unit_system}²")

            # Centroid Heading
            st.write(f"###### :red-background[Centroid]")
            st.code(f"({x_bar.__round__(2)}, {y_bar.__round__(2)})")

            # Display moment of inertia about x-axis
            st.write(f"###### :red-background[Moment of Inertia - Ix]")
            st.code(f"{round(Ixx, 3)} {unit_system}⁴")

            # Display moment of inertia about y-axis
            st.write(f"###### :red-background[Moment of Inertia - Iy]")
            st.code(f"{round(Iyy, 3)} {unit_system}⁴")

            # Display product of inertia
            st.write(f"###### :red-background[Product of Inertia - Ixy]")
            st.code(f"{round(Ixy, 3)} {unit_system}⁴")

    with col2:
        # Display the image of shape w.r.t cross-section shape
        st.image(shape_img_dict[shape_select], caption='Reference Image of Shape')

    if all(x is not None for x in [w, h, t]):
        # show the plotly figure
        st.plotly_chart(figure_or_data=generalized_polygon_fig(polygon_coordinates=shape_coordinates,
                                                               unit_system=unit_system),
                        theme=None,
                        width='stretch')

# C-shape section function
def C_shape(unit_system: str):
    st.write('##### :blue-background[**Parameters**]')
    col1, col2 = st.columns(2, gap='small', border=True)

    with col1:
        col1a, col2a = st.columns(2, gap='small')

        with col1a:
            w = st.number_input('Width (w)',
                                value=None,
                                min_value=0.000,
                                placeholder=unit_system)
        with col2a:
            h = st.number_input('Height (h)',
                                value=None,
                                min_value=0.000,
                                placeholder=unit_system)

        col1a, col2a = st.columns(2, gap='small')

        with col1a:
            t = st.number_input('Thickness (t)',
                                value=None,
                                min_value=0.000,
                                placeholder=unit_system)

    if all(x is not None for x in [w, h, t]):
        # Defines the coordinates for I-shape
        shape_coordinates = [[0, 0],
                             [0, h],
                             [w, h],
                             [w, h-t],
                             [t, h-t],
                             [t, t],
                             [w, t],
                             [w, 0]]

        # Original polygon for area and centroid
        poly_origin = polygon(shape_coordinates)
        Area = poly_origin.Area
        centroid_origin = poly_origin.CenterMass

        # Shift vertices to centroidal reference
        new_polygon_coordinates = [[x - centroid_origin[0], y - centroid_origin[1]] for x, y in shape_coordinates]
        poly_centroid = polygon(new_polygon_coordinates)

        # # Calculate centroidal moments of inertia
        Ixx, Iyy, Ixy = poly_centroid.SecondMomentArea

        # Centroid calculations
        x_bar = centroid_origin[0]
        y_bar = centroid_origin[1]

        with col1:
            st.write('\n')
            st.write('##### :blue-background[**Result**]')

            # Area Heading
            st.write(f"###### :red-background[Area]")
            st.code(f"{Area} {unit_system}²")

            # Centroid Heading
            st.write(f"###### :red-background[Centroid]")
            st.code(f"({x_bar.__round__(2)}, {y_bar.__round__(2)})")

            # Display moment of inertia about x-axis
            st.write(f"###### :red-background[Moment of Inertia - Ix]")
            st.code(f"{round(Ixx, 3)} {unit_system}⁴")

            # Display moment of inertia about y-axis
            st.write(f"###### :red-background[Moment of Inertia - Iy]")
            st.code(f"{round(Iyy, 3)} {unit_system}⁴")


    with col2:
        # Display the image of shape w.r.t cross-section shape
        st.image(shape_img_dict[shape_select], caption='Reference Image of Shape')

    if all(x is not None for x in [w, h, t]):
        # show the plotly figure
        st.plotly_chart(figure_or_data=generalized_polygon_fig(polygon_coordinates=shape_coordinates,
                                                               unit_system=unit_system),
                        theme=None,
                        width='stretch')


# Circle-shape section function
def Circle_shape(unit_system: str):
    st.write('##### :blue-background[**Parameters**]')
    col1, col2 = st.columns(2, gap='small', border=True)

    with col1:
        col1a, col2a = st.columns(2, gap='small')

        with col1a:
            r = st.number_input('Radius (R)',
                                value=None,
                                min_value=0.000,
                                placeholder=unit_system)

    if r is not None:

        # Area Calculation
        Area = (3.14159265 * r ** 2)

        # Centroid calculations
        x_bar = r
        y_bar = r

        # Moment of Inertia about x-axis/y-axis
        I = (3.14159265/4)*r**4

        with col1:
            st.write('\n')
            st.write('##### :blue-background[**Result**]')

            # Area Heading
            st.write(f"###### :red-background[Area]")
            st.code(f"{Area.__round__(3)} {unit_system}²")

            # Centroid Heading
            st.write(f"###### :red-background[Centroid]")
            st.code(f"({x_bar.__round__(2)}, {y_bar.__round__(2)})")

            # Display moment of inertia about x-axis/y-axis
            st.write(f"###### :red-background[Moment of Inertia - Ix/Iy]")
            st.code(f"{round(I, 3)} {unit_system}⁴")

    with col2:
        # Display the image of shape w.r.t cross-section shape
        st.image(shape_img_dict[shape_select], caption='Reference Image of Shape')

    if r is not None:
        # show the plotly figure
        st.plotly_chart(figure_or_data=circle_fig(radius=r, unit_system=unit_system),
                        theme=None,
                        width='stretch')


# Circle Hollow shape section function
def Circle_hollow_shape(unit_system: str):
    st.write('##### :blue-background[**Parameters**]')
    col1, col2 = st.columns(2, gap='small', border=True)

    with col1:
        col1a, col2a = st.columns(2, gap='small')

        with col1a:
            r_o = st.number_input('Outer Radius (Ro)',
                                value=None,
                                min_value=0.000,
                                placeholder=unit_system)

        with col2a:
            r_i = st.number_input('Inner Radius (Ri)',
                                value=None,
                                min_value=0.000,
                                placeholder=unit_system)

    if all(x is not None for x in [r_o, r_i]):

        # Area Calculation
        Area = (3.14159265 * r_o ** 2) - (3.14159265 * r_i ** 2)

        # Centroid calculations
        x_bar = r_o
        y_bar = r_o

        # Moment of Inertia about x-axis/y-axis
        I = ((3.14159265/4)*r_o**4) - ((3.14159265/4)*r_i**4)

        with col1:
            st.write('\n')
            st.write('##### :blue-background[**Result**]')

            # Area Heading
            st.write(f"###### :red-background[Area]")
            st.code(f"{Area.__round__(3)} {unit_system}²")

            # Centroid Heading
            st.write(f"###### :red-background[Centroid]")
            st.code(f"({x_bar.__round__(2)}, {y_bar.__round__(2)})")

            # Display moment of inertia about x-axis/y-axis
            st.write(f"###### :red-background[Moment of Inertia - Ix/Iy]")
            st.code(f"{round(I, 3)} {unit_system}⁴")

    with col2:
        # Display the image of shape w.r.t cross-section shape
        st.image(shape_img_dict[shape_select], caption='Reference Image of Shape')

    if all(x is not None for x in [r_o, r_i]):

        # show the plotly figure
        st.plotly_chart(figure_or_data=circle_hollow_fig(outer_radius=r_o,
                                                         inner_radius=r_i,
                                                         unit_system=unit_system),
                        theme=None,
                        width='stretch')

def custom_polygon_shape(unit_system: str):

    st.write('##### :blue-background[**Parameters**]')
    col1, col2 = st.columns(2, gap='small', border=True)

    with col1:
        poly_points = st.data_editor(data={'x': [0], 'y': [0]},
                                     hide_index=True,
                                     width='stretch',
                                     num_rows='dynamic')

        x = poly_points['x']
        y = poly_points['y']
        shape_coordinates = [[x[i], y[i]] for i in range(len(x))]

        calculate_but = st.button('Calculate',
                                  type='primary')

    with col2:
        # show the plotly figure
        st.plotly_chart(figure_or_data=custom_polygon_fig(x_vals=x, y_vals=y, unit_system=unit_system),
                        theme=None,
                        width='stretch')

    col1, col2 = st.columns(2, gap='small', border=True)

    if calculate_but:
        if shape_coordinates[0] == shape_coordinates[-1]:

            try:
                # Original polygon for area and centroid
                poly_origin = polygon(shape_coordinates)
                Area = poly_origin.Area
                centroid_origin = poly_origin.CenterMass

                # Shift vertices to centroidal reference
                new_polygon_coordinates = [[x - centroid_origin[0], y - centroid_origin[1]] for x, y in shape_coordinates]
                poly_centroid = polygon(new_polygon_coordinates)

                # # Calculate centroidal moments of inertia
                Ixx, Iyy, Ixy = poly_centroid.SecondMomentArea

                # Centroid calculations
                x_bar = centroid_origin[0]
                y_bar = centroid_origin[1]

                with col1:

                    st.write('\n')
                    st.write('##### :blue-background[**Result**]')

                    # Area Heading
                    st.write(f"###### :red-background[Area]")
                    st.code(f"{Area} {unit_system}²")

                    # Centroid Heading
                    st.write(f"###### :red-background[Centroid]")
                    st.code(f"({x_bar.__round__(2)}, {y_bar.__round__(2)})")

                    # Display moment of inertia about x-axis
                    st.write(f"###### :red-background[Moment of Inertia - Ix]")
                    st.code(f"{round(Ixx, 3)} {unit_system}⁴")

                    # Display moment of inertia about y-axis
                    st.write(f"###### :red-background[Moment of Inertia - Iy]")
                    st.code(f"{round(Iyy, 3)} {unit_system}⁴")

                    # Display product of inertia
                    st.write(f"###### :red-background[Product of Inertia - Ixy]")
                    st.code(f"{round(Ixy, 3)} {unit_system}⁴")

                with col2:
                    # show the plotly figure
                    st.plotly_chart(figure_or_data=generalized_polygon_fig(polygon_coordinates=shape_coordinates,
                                                                           unit_system=unit_system),
                                    theme=None,
                                    width='stretch')

            except:
                st.error("""
                        Error in computing results!
                        Please review the following aspects:
                        - Check the coordinates of polygon.
                        - No blank coordinate must be present.
                        """)
        else:
            st.error('- Polygon coordinates must be in a close loop. (The 1st and last coordinates must be same)')

# === Section 2 === App Layout and widgets =================================================================

# Dictionary for shape images
shape_img_dict = {'Rectangular': "Applications/Structural_Analysis/Section_Properties_Calculator/assets/Rectangle.png",
                  'Rectangular (Hollow)': 'Applications/Structural_Analysis/Section_Properties_Calculator/assets/Rectangle_hollow.png',
                  'Circular': 'Applications/Structural_Analysis/Section_Properties_Calculator/assets/Circle.png',
                  'Circular (Hollow)': 'Applications/Structural_Analysis/Section_Properties_Calculator/assets/Circle_hollow.png',
                  'I-shape (symmetrical)': "Applications/Structural_Analysis/Section_Properties_Calculator/assets/I_shape_symmetrical.png",
                  'T-shape': "Applications/Structural_Analysis/Section_Properties_Calculator/assets/T_shape.png",
                  'L-shape': 'Applications/Structural_Analysis/Section_Properties_Calculator/assets/L_shape.png',
                  'C-shape': 'Applications/Structural_Analysis/Section_Properties_Calculator/assets/C_shape.png',
                  'Custom Section': ''
                  }

col1, col2 = st.columns(2,
                        border=True)

with col1:
    # Select the desired unit
    unit_select = st.segmented_control('Select Unit',
                                       options=['mm', 'in', 'm', 'ft'],
                                       selection_mode='single',
                                       default='mm')
with col2:
    # Select the desired default cross-section shape
    shape_select = st.selectbox('Section',
                                options=shape_img_dict.keys())

st.subheader(':blue-background[**Analysis**]', divider='rainbow')

st.write('\n')
if shape_select == 'Rectangular':
    rectangle_shape(unit_select)
elif shape_select == 'I-shape (symmetrical)':
    I_shape_symmetrical(unit_select)
elif shape_select == 'T-shape':
    T_shape(unit_select)
elif shape_select == 'Rectangle (Hollow)':
    rectangle_hollow_shape(unit_select)
elif shape_select == 'L-shape':
    L_shape(unit_select)
elif shape_select == 'C-shape':
    C_shape(unit_select)
elif shape_select == 'Circular':
    Circle_shape(unit_select)
elif shape_select == 'Circular (Hollow)':
    Circle_hollow_shape(unit_select)
elif shape_select == 'Custom Section':
    custom_polygon_shape(unit_select)