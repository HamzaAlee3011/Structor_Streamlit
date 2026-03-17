import plotly.graph_objects as go


# Function for marking centroid line
def mark_centroidal_line(fig, x_bar, y_bar):

    # Creates a horizontal line at centroid y coordinate
    fig.add_hline(y=y_bar,
                  line_dash="dash",
                  line_width=1,
                  line_color="grey")

    # Creates a vertical line at centroid x coordinate
    fig.add_vline(x=x_bar,
                  line_dash="dash",
                  line_width=1,
                  line_color="grey")

    return fig

# Function for creating Rectangle shape based on inputs
def create_rectangle_shape(b, h):
    """
    Create a rectangular diagram based on user inputs for base and height.

    This function generates a Plotly figure with a rectangle defined by the given
    base (`b`) and height (`h`). The rectangle is displayed with x and y axes, including
    arrows to indicate the axes directions.

    Parameters
    ----------
    b : float
        The base length of the rectangle. This value determines the width of the rectangle
        along the x-axis.

    h : float
        The height of the rectangle. This value determines the height of the rectangle
        along the y-axis.

    Returns
    -------
    fig : plotly.graph_objs._figure.Figure
        A Plotly figure object displaying the rectangle with annotations for x and y axes.

    Notes
    -----
    - The function includes x and y axes with arrow annotations to clearly indicate
      the directions.
    - The rectangle's aspect ratio is maintained as 1:1 to ensure accurate representation
      of the shape.
    - The figure's x and y ranges are slightly extended beyond the rectangle dimensions
      to provide clear view of the axes.

    Examples
    --------
    >>> fig = create_rectangle_shape(b=10, h=5)
    >>> fig.show()
    """
    fig = go.Figure()

    # Axes lines with arrows
    # x-axis arrow
    fig.add_annotation(
        x=b + 7,  # Arrow head
        y=0,  # Arrow head
        ax=-2,  # Arrow tail
        ay=0,  # Arrow tail
        xref='x',
        yref='y',
        axref='x',
        ayref='y',
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowwidth=2,
        arrowcolor='grey'
    )

    # y-axis arrow
    fig.add_annotation(
        x=0,  # Arrow head
        y=h + 7,  # Arrow head
        ax=0,  # Arrow tail
        ay=-2,  # Arrow tail
        xref='x',
        yref='y',
        axref='x',
        ayref='y',
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowwidth=2,
        arrowcolor='grey'
    )

    fig.add_shape(type="rect",
                  x0=0, y0=0, x1=b, y1=h,
                  line=dict(
                      color="blue",
                      width=1,
                  ),
                  fillcolor="lightblue",
                  )
    fig.update_shapes(dict(xref='x', yref='y'))

    # Set aspect ratio to equal
    fig.update_layout(
        xaxis=dict(scaleanchor="y", scaleratio=1, constrain="domain"),  # aspectmode
        yaxis=dict(scaleanchor="x", scaleratio=1, constrain="domain"),
    )

    # Set axes properties
    fig.update_xaxes(range=[-2, b + 7], showgrid=False)
    fig.update_yaxes(range=[-2, h + 7], showgrid=False)



    mark_centroidal_line(fig=fig, x_bar=b/2, y_bar=h/2)

    return fig

# Function for creating I-shape symmetrical diagram based on inputs
def create_I_symmetrical_shape(flange_width, flange_thickness, web_thickness, web_height, x_bar, y_bar):
    """
    Create an I-shape symmetrical diagram based on user inputs.

    This function generates a Plotly figure with an I-shaped diagram, including
    top and bottom flanges, a web section, and x and y axes with arrows for clarity.

    Parameters
    ----------
    flange_width : float
        The width of the top and bottom flanges of the I-shape.

    flange_thickness : float
        The thickness of the top and bottom flanges of the I-shape.

    web_thickness : float
        The thickness of the web section connecting the top and bottom flanges.

    web_height : float
        The height of the web section between the top and bottom flanges.

    x_bar : float
        The centroid x of the I-shape.

    Returns
    -------
    fig : plotly.graph_objs._figure.Figure
        A Plotly figure object displaying the I-shape with axes annotations.

    Notes
    -----
    - The diagram includes x and y axes with arrows to clearly indicate directions.
    - The I-shape is constructed with three rectangles: the top flange, bottom flange,
      and web section, each filled with light blue color.
    - The figure's x and y ranges are slightly extended beyond the shape dimensions
      to provide a clear view of the axes.

    Examples
    --------
    >>> fig = create_I_symmetrical_shape(flange_width=20, flange_thickness=2,
                                         web_thickness=1, web_height=10, x_bar=10)
    >>> fig.show()
    """

    fig = go.Figure()

    # Axes lines with arrows
    # x-axis arrow
    fig.add_annotation(
        x=flange_width + 30,  # Arrow head
        y=0,  # Arrow head
        ax=-2,  # Arrow tail
        ay=0,  # Arrow tail
        xref='x',
        yref='y',
        axref='x',
        ayref='y',
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowwidth=2,
        arrowcolor='grey'
    )

    # y-axis arrow
    fig.add_annotation(
        x=0,  # Arrow head
        y=2*flange_thickness + web_height + 30,  # Arrow head
        ax=0,  # Arrow tail
        ay=-2,  # Arrow tail
        xref='x',
        yref='y',
        axref='x',
        ayref='y',
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowwidth=2,
        arrowcolor='grey'
    )

    # Bottom Flange rectangle
    fig.add_shape(type="rect",
                      x0=0, y0=0, x1=flange_width, y1=flange_thickness,
                      line=dict(
                          color="blue",
                          width=1,
                      ),
                      fillcolor="lightblue",
                      )

    # Web rectangle
    fig.add_shape(type="rect",
                  x0=x_bar - (web_thickness/2),
                  y0=flange_thickness,
                  x1=x_bar + (web_thickness/2),
                  y1=flange_thickness + web_height,
                  line=dict(
                      color="blue",
                      width=1,
                  ),
                  fillcolor="lightblue",
                  )

    # Top flange rectangle
    fig.add_shape(type="rect",
                  x0=0,
                  y0=flange_thickness+web_height,
                  x1=flange_width,
                  y1=2*flange_thickness+web_height,
                  line=dict(
                      color="blue",
                      width=1,
                  ),
                  fillcolor="lightblue",
                  )

    fig.update_shapes(dict(xref='x', yref='y'))

    # Set aspect ratio to equal
    fig.update_layout(
        xaxis=dict(scaleanchor="y", scaleratio=1, constrain="domain"),  # aspectmode
        yaxis=dict(scaleanchor="x", scaleratio=1, constrain="domain"),
    )

    mark_centroidal_line(fig=fig, x_bar=x_bar, y_bar=y_bar)

    # Set axes properties
    fig.update_xaxes(range=[-2, flange_width + 30], showgrid=False)
    fig.update_yaxes(range=[-2, 2*flange_thickness + web_height + 30], showgrid=False)

    return fig

# Function for creating I-shape unsymmetrical diagram based on inputs
def create_I_unsymmetrical_shape(top_flange_width, top_flange_thickness, web_thickness, web_height, bottom_flange_width, bottom_flange_thickness, x_bar, y_bar):
    """
    Create an I-shape unsymmetrical diagram based on user inputs.

    This function generates a Plotly figure with an unsymmetrical I-shaped diagram,
    including top and bottom flanges and a web section. The diagram includes x and y axes
    with arrows for better visualization.

    Parameters
    ----------
    top_flange_width : float
        The width of the top flange of the I-shape.

    top_flange_thickness : float
        The thickness of the top flange.

    web_thickness : float
        The thickness of the web section connecting the top and bottom flanges.

    web_height : float
        The height of the web section between the top and bottom flanges.

    bottom_flange_width : float
        The width of the bottom flange of the I-shape.

    bottom_flange_thickness : float
        The thickness of the bottom flange.

    x_bar : float
        The x-coordinate of the centroid along the x-axis, used to position the web and
        flanges appropriately.

    Returns
    -------
    fig : plotly.graph_objs._figure.Figure
        A Plotly figure object displaying the unsymmetrical I-shape with axes annotations.

    Notes
    -----
    - The unsymmetrical I-shape is constructed with three rectangles: the top flange,
      the web section, and the bottom flange, each filled with light blue color.
    - The figure includes arrows along the x and y axes for clear visualization of the
      diagram's orientation.
    - The figure's x and y ranges are extended beyond the I-shape dimensions to ensure
      the axes are clearly visible.

    Examples
    --------
    >>> fig = create_I_unsymmetrical_shape(top_flange_width=25, top_flange_thickness=3,
                                           web_thickness=2, web_height=12,
                                           bottom_flange_width=20, bottom_flange_thickness=4,
                                           x_bar=12)
    >>> fig.show()
    """

    main_width = None
    if top_flange_width > bottom_flange_width:
        main_width = top_flange_width
    else:
        main_width = bottom_flange_width

    fig = go.Figure()

    # Axes lines with arrows
    # x-axis arrow
    fig.add_annotation(
        x=main_width + 30,  # Arrow head
        y=0,  # Arrow head
        ax=-2,  # Arrow tail
        ay=0,  # Arrow tail
        xref='x',
        yref='y',
        axref='x',
        ayref='y',
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowwidth=2,
        arrowcolor='grey'
    )

    # y-axis arrow
    fig.add_annotation(
        x=0,  # Arrow head
        y=bottom_flange_thickness + web_height + top_flange_thickness + 30,  # Arrow head
        ax=0,  # Arrow tail
        ay=-2,  # Arrow tail
        xref='x',
        yref='y',
        axref='x',
        ayref='y',
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowwidth=2,
        arrowcolor='grey'
    )

    # Bottom Flange rectangle
    fig.add_shape(type="rect",
                  x0=x_bar-(bottom_flange_width/2),
                  y0=0,
                  x1=x_bar + (bottom_flange_width/2),
                  y1=bottom_flange_thickness,
                  line=dict(
                      color="blue",
                      width=1,
                  ),
                  fillcolor="lightblue",
                  )

    # Web rectangle
    fig.add_shape(type="rect",
                  x0=x_bar - (web_thickness / 2),
                  y0=bottom_flange_thickness,
                  x1=x_bar + (web_thickness / 2),
                  y1=bottom_flange_thickness + web_height,
                  line=dict(
                      color="blue",
                      width=1,
                  ),
                  fillcolor="lightblue",
                  )

    # Top flange rectangle
    fig.add_shape(type="rect",
                  x0=x_bar - (top_flange_width / 2),
                  y0=bottom_flange_thickness + web_height,
                  x1=x_bar + (top_flange_width / 2),
                  y1=bottom_flange_thickness + web_height + top_flange_thickness,
                  line=dict(
                      color="blue",
                      width=1,
                  ),
                  fillcolor="lightblue",
                  )

    fig.update_shapes(dict(xref='x', yref='y'))

    # Set aspect ratio to equal
    fig.update_layout(
        xaxis=dict(scaleanchor="y", scaleratio=1, constrain="domain"),  # aspectmode
        yaxis=dict(scaleanchor="x", scaleratio=1, constrain="domain"),
    )

    mark_centroidal_line(fig=fig, x_bar=x_bar, y_bar=y_bar)

    # Set axes properties
    fig.update_xaxes(range=[-2, main_width + 30], showgrid=False)
    fig.update_yaxes(range=[-2, bottom_flange_thickness + web_height + top_flange_thickness + 30], showgrid=False)

    return fig


# Function for creating T-shape diagram based on inputs
def create_T_shape(flange_width, flange_thickness, web_thickness, web_height, x_bar, y_bar):
    """
    Create a T-shape diagram based on user inputs.

    This function generates a Plotly figure with a T-shaped diagram, including
    a top flange and a web section, along with x and y axes with arrows to indicate directions.

    Parameters
    ----------
    flange_width : float
        The width of the top flange of the T-shape.

    flange_thickness : float
        The thickness of the top flange.

    web_thickness : float
        The thickness of the web section that supports the flange.

    web_height : float
        The height of the web section below the flange.

    x_bar : float
        The x-coordinate of the centroid along the x-axis, used to position the web symmetrically.

    Returns
    -------
    fig : plotly.graph_objs._figure.Figure
        A Plotly figure object displaying the T-shape with annotations for the axes.

    Notes
    -----
    - The T-shape is constructed with two rectangles: the top flange and the web section,
      each filled with light blue color for visual clarity.
    - The figure includes arrows along the x and y axes to help visualize the diagram's orientation.
    - The figure's x and y ranges are extended beyond the T-shape dimensions to clearly display the axes.

    Examples
    --------
    >>> fig = create_T_shape(flange_width=20, flange_thickness=2,
                             web_thickness=1, web_height=10, x_bar=10)
    >>> fig.show()
    """

    fig = go.Figure()

    # Axes lines with arrows
    # x-axis arrow
    fig.add_annotation(
        x=flange_width + 30,  # Arrow head
        y=0,  # Arrow head
        ax=-2,  # Arrow tail
        ay=0,  # Arrow tail
        xref='x',
        yref='y',
        axref='x',
        ayref='y',
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowwidth=2,
        arrowcolor='grey'
    )

    # y-axis arrow
    fig.add_annotation(
        x=0,  # Arrow head
        y=flange_thickness + web_height + 30,  # Arrow head
        ax=0,  # Arrow tail
        ay=-2,  # Arrow tail
        xref='x',
        yref='y',
        axref='x',
        ayref='y',
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowwidth=2,
        arrowcolor='grey'
    )

    # Web rectangle
    fig.add_shape(type="rect",
                  x0=x_bar - (web_thickness / 2),
                  y0=0,
                  x1=x_bar + (web_thickness / 2),
                  y1= web_height,
                  line=dict(
                      color="blue",
                      width=1,
                  ),
                  fillcolor="lightblue",
                  )

    # Top flange rectangle
    fig.add_shape(type="rect",
                  x0=0,
                  y0=web_height,
                  x1=flange_width,
                  y1=flange_thickness + web_height,
                  line=dict(
                      color="blue",
                      width=1,
                  ),
                  fillcolor="lightblue",
                  )

    fig.update_shapes(dict(xref='x', yref='y'))

    # Set aspect ratio to equal
    fig.update_layout(
        xaxis=dict(scaleanchor="y", scaleratio=1, constrain="domain"),  # aspectmode
        yaxis=dict(scaleanchor="x", scaleratio=1, constrain="domain"),
    )

    mark_centroidal_line(fig=fig, x_bar=x_bar, y_bar=y_bar)

    # Set axes properties
    fig.update_xaxes(range=[-2, flange_width + 30], showgrid=False)
    fig.update_yaxes(range=[-2, flange_thickness + web_height + 30], showgrid=False)

    return fig
