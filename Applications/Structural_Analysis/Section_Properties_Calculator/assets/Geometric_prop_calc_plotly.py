from polygon_math import polygon
import plotly.graph_objects as go

# Define polygon vertices
# points = [[0, 0],
#           [0, 200],
#           [400, 200],
#           [400, 0],
#           [380, 0],
#           [380, 180],
#           [20, 180],
#           [20, 0]]

points = [
    [5, 0],
    [5, 8],
    [0, 8],
    [0, 10],
    [12, 10],
    [12, 8],
    [7, 8],
    [7, 0],
    # [7, 10]
]

def show_properties_marked_figure_plotly():
    # Original polygon for area and centroid
    poly_origin = polygon(points)
    area = poly_origin.Area
    centroid_origin = poly_origin.CenterMass

    # Shift vertices to centroidal reference
    new_points = [[x - centroid_origin[0], y - centroid_origin[1]] for x, y in points]
    poly_centroid = polygon(new_points)

    # Calculate centroidal moments of inertia
    Ixx, Iyy, Ixy = poly_centroid.SecondMomentArea

    # Extract plotting values
    x_vals = [pt[0] for pt in points] + [points[0][0]]
    y_vals = [pt[1] for pt in points] + [points[0][1]]

    # Create plot
    fig = go.Figure()

    # Polygon edges
    fig.add_trace(go.Scatter(
        x=x_vals, y=y_vals,
        mode='lines+markers',
        name='Polygon',
        line=dict(color='blue'),
        marker=dict(color='blue')
    ))

    # Label vertices
    for i, (x, y) in enumerate(points):
        fig.add_trace(go.Scatter(
            x=[x], y=[y],
            mode='text',
            text=[f'P{i+1} ({x},{y})'],
            textposition="top center",
            showlegend=False,
            textfont=dict(color='green', size=10)
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

    # Inertia annotation box (P.C.A)
    text_str = (
        f"Ixx (P.C.A): {Ixx:.2f} units⁴<br>"
        f"Iyy (P.C.A): {Iyy:.2f} units⁴<br>"
        f"Ixy (P.C.A): {Ixy:.2f} units⁴"
    )

    fig.add_annotation(
        xref='paper', yref='paper',
        x=1.05, y=0.95,
        text=text_str,
        showarrow=False,
        align='left',
        bordercolor='gray',
        borderwidth=1,
        borderpad=10,
        bgcolor='white',
        opacity=0.9
    )

    # Layout adjustments
    fig.update_layout(
        title="Polygon with Vertices and Centroid (Centroidal Moments)",
        xaxis_title="X",
        yaxis_title="Y",
        showlegend=True,
        width=850,
        height=550
    )
    fig.update_yaxes(scaleanchor="x", scaleratio=1)

    return fig
