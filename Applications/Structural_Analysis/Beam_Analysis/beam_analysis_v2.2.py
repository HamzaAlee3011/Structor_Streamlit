import streamlit as st
from indeterminatebeam import *
import pandas as pd
from plotly.subplots import make_subplots
import pyecharts.options as opts
from streamlit_echarts import st_echarts
from pyecharts.charts import Line

# === SECTION 1 === Session States Initialization ========================================

# Initialize state for supports lists
if 'sup_locations_list' not in st.session_state:
    st.session_state.sup_locations_list = []
if 'sup_type_display_list' not in st.session_state:
    st.session_state.sup_type_display_list = []
if 'sup_type_list' not in st.session_state:
    st.session_state.sup_type_list = []

# Initialize state for point loads lists
if 'pl_locations_list' not in st.session_state:
    st.session_state.pl_locations_list = []
if 'pl_mag_list' not in st.session_state:
    st.session_state.pl_mag_list = []

# Initialize state for point moments lists
if 'pm_locations_list' not in st.session_state:
    st.session_state.pm_locations_list = []
if 'pm_mag_list' not in st.session_state:
    st.session_state.pm_mag_list = []

# Initialize state for Uniformly Distributed Loads (UDLs) lists
if 'udls_x1_locations_list' not in st.session_state:
    st.session_state.udls_x1_locations_list = []
if 'udls_x2_locations_list' not in st.session_state:
    st.session_state.udls_x2_locations_list = []
if 'udls_mag_list' not in st.session_state:
    st.session_state.udls_mag_list = []

# Initialize state for Variably Distributed Loads (VDLs) lists
if 'vdls_x1_locations_list' not in st.session_state:
    st.session_state.vdls_x1_locations_list = []
if 'vdls_x2_locations_list' not in st.session_state:
    st.session_state.vdls_x2_locations_list = []
if 'vdls_mag1_list' not in st.session_state:
    st.session_state.vdls_mag1_list = []
if 'vdls_mag2_list' not in st.session_state:
    st.session_state.vdls_mag2_list = []

# Initialize state for beam length
if 'beam_length' not in st.session_state:
    st.session_state.beam_length = 0.0  # Initial value for the length

# Initialize state for beam Modulus of Elasticity
if 'E' not in st.session_state:
    st.session_state.E = None

# Initialize state for beam Moment of inertia
if 'I' not in st.session_state:
    st.session_state.I = None

# === SECTION 2 === Generalized Settings for overall Beam Analysis application ========================================

# Dict for supports
supports = {'Roller': (0, 1, 0),
            'Pin': (1, 1, 0),
            'Fixed': (1, 1, 1)}

# Metric Units Dictionary
metric_units_dict = {
    'System': {
        'length': 'm',
        'force': 'kN',
        'moment': 'kN.m',
        'distributed': 'kN/m',
        'deflection': 'mm',
        'E': 'MPa',
        'I': 'mm4'},

    'Placeholder': {
        'length': '(m)',
        'force': '(kN)',
        'moment': '(kN.m)',
        'distributed': '(kN/m)',
        'deflection': '(mm)',
        'E': '(MPa)',
        'I': '(mm⁴)'
    }
}

# Imperial units dictionary
imperial_units_dict = {
    'System': {
        'length': 'ft',
        'force': 'kip',
        'moment': 'kip.ft',
        'distributed': 'kip/ft',
        'deflection': 'in',
        'E': 'kip/in2',
        'I': 'in4'
    },
    "Placeholder": {
        'length': '(ft)',
        'force': '(kip)',
        'moment': '(kip.ft)',
        'distributed': '(kip/ft)',
        'deflection': '(in)',
        'E': '(ksi)',
        'I': '(in⁴)'
    }
}

# Combined dictionary for units
units_dict = {'Metric': metric_units_dict,
              'Imperial': imperial_units_dict}

# Sign Convention dictionary for loads directions
sign_conv = {'↑': 1,
             '↓': -1,
             '↻': -1,
             '↺': 1}


# === SECTION 3 === Functions =====================================================================

# --- SECTION 3.0: Miscellaneous functions------------------------------------

# Function for saving dynamic html plot of indeterminatebeampy with button
@st.fragment
def save_html_plot_with_button(figure):
    # Generate the dynamic plot as an HTML string
    html_content = figure.to_html()

    # Create a download button for the HTML file
    st.download_button(
        label="Save Dynamic Figure",
        data=html_content,
        file_name="beam_plot.html",
        mime="text/html",
        width='stretch'
    )


# Function for creating intervals at which the values of SF and BM is to be found
def create_intervals(beam_length, interval):
    """
    Creates a list of specified intervals along the beam length.

    Parameters:
    beam_length (float): The total length of the beam.
    interval (float): The interval value at which to create points.

    Returns:
    list: A list of interval points along the beam length.
    """
    # Input validation with warnings
    if interval <= 0:
        st.warning("Interval must be a positive number.")
        return []
    if beam_length <= 0:
        st.warning("Beam length must be a positive number.")
        return []

    # Initialize the list and starting point
    intervals = []
    current_point = 0.0

    # Generate intervals using a loop
    while current_point <= beam_length:
        intervals.append(round(current_point, 2))
        current_point += interval

    # Ensure the last point is exactly the beam length if not already included
    if intervals[-1] != beam_length:
        intervals.append(round(beam_length, 2))

    return intervals


# --- SECTION 3.1: Adding and Removing loads/supports functions------------------------------------

# Function to store support data in session state
def storing_support(loc, type):
    st.session_state.sup_locations_list.append(loc)
    st.session_state.sup_type_display_list.append(type)
    st.session_state.sup_type_list.append(supports[type])


# Function to remove support data in session state
def removing_support(loc, type):
    try:
        st.session_state.sup_locations_list.remove(loc)
        st.session_state.sup_type_display_list.remove(type)
        st.session_state.sup_type_list.remove(supports[type])
    except ValueError:
        st.warning("Support not found or already removed.")
    except IndexError:
        st.warning("No supports available to remove.")


# Function to store point load data in session state
def storing_pointloads(loc, mag):
    st.session_state.pl_locations_list.append(loc)
    st.session_state.pl_mag_list.append(mag)


# Function to remove point load data in session state
def removing_pointloads(loc, mag):
    st.session_state.pl_locations_list.remove(loc)
    st.session_state.pl_mag_list.remove(mag)


# Function to store point moments data in session state
def storing_pointmoments(loc, mag):
    st.session_state.pm_locations_list.append(loc)
    st.session_state.pm_mag_list.append(mag)


# Function to remove point load data in session state
def removing_pointmoments(loc, mag):
    st.session_state.pm_locations_list.remove(loc)
    st.session_state.pm_mag_list.remove(mag)


# Function to store Uniformly Distributed Loads (UDLs)data in session state
def storing_udls(loc1, loc2, mag):
    st.session_state.udls_x1_locations_list.append(loc1)
    st.session_state.udls_x2_locations_list.append(loc2)
    st.session_state.udls_mag_list.append(mag)


# Function to remove Uniformly Distributed Loads (UDLs)data in session state
def removing_udls(loc1, loc2, mag):
    st.session_state.udls_x1_locations_list.remove(loc1)
    st.session_state.udls_x2_locations_list.remove(loc2)
    st.session_state.udls_mag_list.remove(mag)


# Function to store Variably Distributed Loads (UDLs)data in session state
def storing_vdls(loc1, loc2, mag1, mag2):
    st.session_state.vdls_x1_locations_list.append(loc1)
    st.session_state.vdls_x2_locations_list.append(loc2)
    st.session_state.vdls_mag1_list.append(mag1)
    st.session_state.vdls_mag2_list.append(mag2)


# Function to remove Variably Distributed Loads (UDLs)data in session state
def removing_vdls(loc1, loc2, mag1, mag2):
    st.session_state.vdls_x1_locations_list.remove(loc1)
    st.session_state.vdls_x2_locations_list.remove(loc2)
    st.session_state.vdls_mag1_list.remove(mag1)
    st.session_state.vdls_mag2_list.remove(mag2)


# Function for clearing everything once at all
@st.dialog('Erase Data')
def clear_everything():
    st.write('Are you sure you want to clear all the entries?')
    delete_data = st.button('Confirm')
    if delete_data:
        st.session_state.sup_locations_list.clear()
        st.session_state.sup_type_display_list.clear()
        st.session_state.sup_type_list.clear()
        st.session_state.pl_locations_list.clear()
        st.session_state.pl_mag_list.clear()
        st.session_state.pm_locations_list.clear()
        st.session_state.pm_mag_list.clear()
        st.session_state.udls_x1_locations_list.clear()
        st.session_state.udls_x2_locations_list.clear()
        st.session_state.udls_mag_list.clear()
        st.session_state.vdls_x1_locations_list.clear()
        st.session_state.vdls_x2_locations_list.clear()
        st.session_state.vdls_mag1_list.clear()
        st.session_state.vdls_mag2_list.clear()
        st.rerun()


# --- SECTION 3.2: Diagram Generating functions -> Indeterminatebeam default------------------------------------

# Function to create SFD and BMD Diagrams
def sfd_bmd_plot():
    # Create a subplot figure
    analysis_fig = make_subplots(rows=4, cols=1, shared_xaxes=False, vertical_spacing=0.05,
                                 subplot_titles=(
                                     "Beam Schematic", 'Reaction Forces', "Shear Force Diagram",
                                     "Bending Moment Diagram"))

    # Plot Beam schematic diagram in the first row
    analysis_fig = beam.plot_beam_diagram(fig=analysis_fig, row=1, col=1)

    # Plot Beam reaction force diagram in the second row
    analysis_fig = beam.plot_reaction_force(fig=analysis_fig, row=2, col=1)

    # Plot shear force diagram in the third row
    analysis_fig = beam.plot_analytical('sf', color="rgba(144, 238, 144, 1)", title="Shear Force Diagram",
                                        xlabel="Length", ylabel="Shear Force",
                                        xunits=f"{units_dict[unit_systems]['System']['length']}",
                                        yunits=f"{units_dict[unit_systems]['System']['force']}",
                                        fig=analysis_fig, row=3, col=1)

    # Plot bending moment diagram in the fourth row
    analysis_fig = beam.plot_analytical('bm', color="rgba(204, 204, 0, 1)", title="Bending Moment Diagram",
                                        xlabel="Length", ylabel="Bending Moment",
                                        xunits=f"{units_dict[unit_systems]['System']['length']}",
                                        yunits=f"{units_dict[unit_systems]['System']['moment']}",
                                        fig=analysis_fig, row=4, col=1)

    # Update layout for the entire figure
    analysis_fig.update_layout(
        height=1600,
        # width=1200,
        # plot_bgcolor='#E9EFF9',
        showlegend=False,
        title_text="Beam Analysis Results",
    )

    # Show the figure
    return analysis_fig


# Function to create SFD, BMD and Deflection diagrams
def sfd_bmd_deflection_plot():
    # Create a subplot figure
    analysis_fig = make_subplots(rows=5, cols=1, shared_xaxes=False, vertical_spacing=0.05,
                                 subplot_titles=(
                                     "Beam Schematic", 'Reaction Forces', "Shear Force Diagram",
                                     "Bending Moment Diagram",
                                     "Deflection Diagram"))

    # Plot Beam schematic diagram in the first row
    analysis_fig = beam.plot_beam_diagram(fig=analysis_fig, row=1, col=1)

    # Plot Beam reaction force diagram in the second row
    analysis_fig = beam.plot_reaction_force(fig=analysis_fig, row=2, col=1)

    # Plot shear force diagram in the third row
    analysis_fig = beam.plot_analytical('sf', color="rgba(144, 238, 144, 1)", title="Shear Force Diagram",
                                        xlabel="Length", ylabel="Shear Force",
                                        xunits=f"{units_dict[unit_systems]['System']['length']}",
                                        yunits=f"{units_dict[unit_systems]['System']['force']}",
                                        fig=analysis_fig, row=3, col=1)

    # Plot bending moment diagram in the fourth row
    analysis_fig = beam.plot_analytical('bm', color="rgba(204, 204, 0, 1)", title="Bending Moment Diagram",
                                        xlabel="Length", ylabel="Bending Moment",
                                        xunits=f"{units_dict[unit_systems]['System']['length']}",
                                        yunits=f"{units_dict[unit_systems]['System']['moment']}",
                                        fig=analysis_fig, row=4, col=1)

    # Plot deflection diagram in the fifth row
    analysis_fig = beam.plot_analytical('d', color="rgba(255, 0, 0, 0.5)", title="Deflection Diagram",
                                        xlabel="Length", ylabel="Deflection",
                                        xunits=f"{units_dict[unit_systems]['System']['length']}",
                                        yunits=f"{units_dict[unit_systems]['System']['deflection']}",
                                        fig=analysis_fig, row=5, col=1)

    # Update layout for the entire figure
    analysis_fig.update_layout(
        height=1600,
        # width=1500,
        showlegend=False,
        # plot_bgcolor='#E9EFF9',
        title_text="Beam Analysis Results",
    )
    # Show the figure
    return analysis_fig


# --- SECTION 3.4: Analysis Results functions-------------------------------------------------------------

# Function to show results without deflection
def result_without_deflection():
    # RESULTS SECTION
    st.write('\n')
    st.subheader(':blue-background[**Detailed Results Overview**]', divider='rainbow')
    st.write('\n')

    col1a, col1b, col1c = st.columns(3, gap='medium')

    with col1b:
        st.metric('### :red-background[Max. Bending Moment]',
                  value=f"{round(beam.get_bending_moment(return_max=True), 2)}  {units_dict[unit_systems]['Placeholder']['moment']}")
        st.metric('### :red-background[Min. Bending Moment]',
                  value=f"{round(beam.get_bending_moment(return_min=True), 2)}  {units_dict[unit_systems]['Placeholder']['moment']}")
        st.metric('### :red-background[Absolute Max. Bending Moment]',
                  value=f"{round(beam.get_bending_moment(return_absmax=True), 2)}  {units_dict[unit_systems]['Placeholder']['moment']}")

    with col1a:
        st.metric('### :red-background[Max. Shear Force]',
                  value=f"{round(beam.get_shear_force(return_max=True), 2)}  {units_dict[unit_systems]['Placeholder']['force']}")
        st.metric('### :red-background[Min. Shear Force]',
                  value=f"{round(beam.get_shear_force(return_min=True), 2)}  {units_dict[unit_systems]['Placeholder']['force']}")
        st.metric('### :red-background[Absolute Max. Shear Force]',
                  value=f"{round(beam.get_shear_force(return_absmax=True), 2)}  {units_dict[unit_systems]['Placeholder']['force']}")


# Function to show results with deflection
def result_with_deflection():
    # RESULTS SECTION
    st.write('\n')
    st.subheader(':blue-background[**Detailed Results Overview**]', divider='rainbow')
    st.write('\n')

    col1a, col1b, col1c = st.columns(3, gap='medium')

    with col1b:
        st.metric('### :red-background[Max. Bending Moment]',
                  value=f"{round(beam.get_bending_moment(return_max=True), 2)}  {units_dict[unit_systems]['Placeholder']['moment']}")
        st.metric('### :red-background[Min. Bending Moment]',
                  value=f"{round(beam.get_bending_moment(return_min=True), 2)}  {units_dict[unit_systems]['Placeholder']['moment']}")
        st.metric('### :red-background[Absolute Max. Bending Moment]',
                  value=f"{round(beam.get_bending_moment(return_absmax=True), 2)}  {units_dict[unit_systems]['Placeholder']['moment']}")

    with col1a:
        st.metric('### :red-background[Max. Shear Force]',
                  value=f"{round(beam.get_shear_force(return_max=True), 2)}  {units_dict[unit_systems]['Placeholder']['force']}")
        st.metric('### :red-background[Min. Shear Force]',
                  value=f"{round(beam.get_shear_force(return_min=True), 2)}  {units_dict[unit_systems]['Placeholder']['force']}")
        st.metric('### :red-background[Absolute Max. Shear Force]',
                  value=f"{round(beam.get_shear_force(return_absmax=True), 2)}  {units_dict[unit_systems]['Placeholder']['force']}")

    with col1c:
        st.metric('### :red-background[Upwards Deflection]',
                  value=f"{round(beam.get_deflection(return_max=True), 3)}  {units_dict[unit_systems]['Placeholder']['deflection']}")
        st.metric('### :red-background[Downwards Deflection]',
                  value=f"{round(beam.get_deflection(return_min=True), 3)}  {units_dict[unit_systems]['Placeholder']['deflection']}")
        st.metric('### :red-background[Absolute Max. Deflection]',
                  value=f"{round(beam.get_deflection(return_absmax=True), 3)}  {units_dict[unit_systems]['Placeholder']['deflection']}")


# --- SECTION 3.5: Pyecharts Function for generating detail diagrams-------------------------------------

# This function is created mainly with the help of ChatGPT. Since Pyechart is a graphing library, so it has various
# commands and learning the library syntax was not the main purpose so this function is mainly written by ChatGPT
# with reference of Pyecharts gallery
# Reference Link: https://gallery.pyecharts.org/#/

@st.fragment
def PyechartPlot_and_Table(force_type: str, np: int = 150) -> None:
    """
    Display a Streamlit table and interactive Pyecharts plot of internal force values along a beam.

    This function visualizes Shear Force, Bending Moment, or Deflection across the beam's length
    by generating both a numerical data table and a smooth area line chart with highlight markers.

    Parameters
    ----------
    force_type : str
        Type of internal force to compute and display.
        Acceptable values:
        - 'sf'  → Shear Force
        - 'bm'  → Bending Moment
        - 'def' → Deflection

    np : int, optional
        Number of points used for generating a smooth plot curve, by default 150.

    Returns
    -------
    None
        This function renders Streamlit UI elements including:
        - A dataframe of force values at user-defined intervals
        - A Pyecharts plot with:
            - Smooth area chart of computed force values
            - Scatter points for discrete user-selected interval values
            - Max and Min markers on the graph
            - Interactive zoom and restore tools
            - English tooltips and axes

    Notes
    -----
    - The x-axis range is auto-adjusted to beam length.
    - The y-axis min and max are calculated based on force values.
    - The plot is visually styled with light gridlines and clean formatting.
    - Image export is disabled; zoom and restore are enabled.
    - Titles, tooltips, and labels are shown in English.
    """

    # A dictionary to use the title and units with respect to the type of internal force/deflection
    force_type_dict = {'sf': ['Shear Force', f'{units_dict[unit_systems]["Placeholder"]["force"]}'],
                       'bm': ['Bending Moment', f'{units_dict[unit_systems]["Placeholder"]["moment"]}'],
                       'def': ['Deflections', f'{units_dict[unit_systems]["Placeholder"]["deflection"]}']}

    col1, col2 = st.columns([0.3, 1], gap='small', vertical_alignment='center')

    with col1:

        col1a, col2a = st.columns(2, gap='small', vertical_alignment='bottom')

        # A toggle button to whether show the graph or not (it was necessary due to st.fragment problem)
        with col1a:
            show_graph = st.toggle('Graph',
                                   value=False,
                                   key=f'c-{force_type_dict[force_type]}')

        # A toggle button to whether show the labels of specified moments or not
        with col2a:
            show_label_opt = st.toggle('Labels',
                                       value=False,
                                       key=f'd-{force_type_dict[force_type]}')

        # Interval value number input
        interval_value = st.number_input('Interval',
                                         min_value=0.00,
                                         value=1.00,
                                         key=f'b-{force_type_dict[force_type]}',
                                         max_value=length,
                                         )

        intervals = create_intervals(length, interval=interval_value)

        if not intervals:
            st.warning("No intervals generated. Check the beam length and interval values.")
        else:
            values = []

            # Generate and stores the respective value to the list in specified interval
            for point in intervals:
                try:
                    if force_type == 'sf':
                        values.append(round(beam.get_shear_force(round(point, 3)), 3))
                    elif force_type == 'bm':
                        values.append(round(beam.get_bending_moment(round(point, 3)), 3))
                    elif force_type == 'def':
                        values.append(round(beam.get_deflection(round(point, 3)), 3))

                except TypeError as e:
                    st.warning(f"Error at {point}: {e}")

            if len(values) != len(intervals):
                st.warning("Mismatch between intervals and values.")
            else:

                # Create and show the dataframe table of values
                df = pd.DataFrame({
                    f'Interval {units_dict[unit_systems]["Placeholder"]["length"]}': intervals,
                    f'{force_type_dict[force_type][0]} {force_type_dict[force_type][1]}': values,
                })

                st.dataframe(df, hide_index=True, width='stretch', height=315)

    with col2:

        # Create x and y values of respective force to make the copy of diagram
        span = length
        no_of_pts = np
        spacing = span / (no_of_pts - 1)
        x = create_intervals(length, interval=spacing)
        x_roundedoff = map(lambda x: round(x, 3), x)

        y = []

        if force_type == 'sf':
            y = [round(beam.get_shear_force(pt), 3) for pt in x_roundedoff]
            minval = round(beam.get_shear_force(return_min=True), 3)
            maxval = round(beam.get_shear_force(return_max=True), 3)
        elif force_type == 'bm':
            y = [round(beam.get_bending_moment(pt), 3) for pt in x_roundedoff]
            minval = round(beam.get_bending_moment(return_min=True), 3)
            maxval = round(beam.get_bending_moment(return_max=True), 3)
        elif force_type == 'def':
            y = [round(beam.get_deflection(pt), 3) for pt in x_roundedoff]
            minval = round(beam.get_deflection(return_min=True), 3)
            maxval = round(beam.get_deflection(return_max=True), 3)

        if show_graph:
            # A complete code snippet which creates the Pyechart Figure

            color_schemes = [
                {
                    "name": "Teal Blue",
                    "line_color": "#008080",
                    "fill_color": "rgba(0, 128, 128, 0.2)"
                },
                {
                    "name": "Steel Blue",
                    "line_color": "#4682B4",
                    "fill_color": "rgba(70, 130, 180, 0.2)"
                },
                {
                    "name": "Slate Gray",
                    "line_color": "#708090",
                    "fill_color": "rgba(112, 128, 144, 0.2)"
                },
                {
                    "name": "Royal Purple",
                    "line_color": "#7851A9",
                    "fill_color": "rgba(120, 81, 169, 0.2)"
                },
                {
                    "name": "Ocean Green",
                    "line_color": "#3CB371",
                    "fill_color": "rgba(60, 179, 113, 0.2)"
                },
                {
                    "name": "Neon Green",
                    "line_color": "#39FF14",  # Bright green
                    "fill_color": "rgba(57, 255, 20, 0.2)"
                },
                {
                    "name": "Neon Blue",
                    "line_color": "#00FFFF",  # Cyan/Aqua
                    "fill_color": "rgba(0, 255, 255, 0.2)"
                },
                {
                    "name": "Neon Purple",
                    "line_color": "#B026FF",  # Bright purple
                    "fill_color": "rgba(176, 38, 255, 0.2)"
                },
                {
                    "name": "Neon Pink",
                    "line_color": "#FF1493",  # Deep pink
                    "fill_color": "rgba(255, 20, 147, 0.2)"
                },
                {
                    "name": "Neon Yellow",
                    "line_color": "#FFFF33",  # Bright yellow
                    "fill_color": "rgba(255, 255, 51, 0.2)"
                },
                {
                    "name": "Electric Orange",
                    "line_color": "#FF5E00",
                    "fill_color": "rgba(255, 94, 0, 0.2)"
                },
            ]

            # Pick a color scheme by index
            index = 0  # Change from 0 to 10 to try others
            line_color = color_schemes[index]["line_color"]
            fill_color = color_schemes[index]["fill_color"]

            chart = (
                Line()

                # First Plot the Original Interpolated points
                .add_xaxis(x)
                .add_yaxis(
                    series_name=f'{force_type_dict[force_type][0]} {force_type_dict[force_type][1]}',
                    y_axis=y,
                    is_symbol_show=False,
                    is_smooth=True,
                    areastyle_opts=opts.AreaStyleOpts(opacity=0.3, color=fill_color),
                    linestyle_opts=opts.LineStyleOpts(width=2, color=line_color),
                    itemstyle_opts=opts.ItemStyleOpts(color=line_color),
                    label_opts=opts.LabelOpts(is_show=False),
                    markpoint_opts=opts.MarkPointOpts(
                        data=[
                            opts.MarkPointItem(type_="max", name="Max"),
                            opts.MarkPointItem(type_="min", name="Min")
                        ],
                        symbol="circle",
                        symbol_size=10,
                        label_opts=opts.LabelOpts(color="red")
                    ),
                )

                # Secondly plot the users interval points
                .add_xaxis(intervals)  # <- this is the key fix!
                .add_yaxis(
                    series_name=f'{force_type_dict[force_type][0]} {force_type_dict[force_type][1]} (Specified)',
                    y_axis=values,
                    xaxis_index=0,
                    symbol="circle",
                    symbol_size=7,
                    is_symbol_show=True,
                    is_smooth=False,
                    linestyle_opts=opts.LineStyleOpts(width=0, color="orange"),
                    itemstyle_opts=opts.ItemStyleOpts(color="orange"),
                    label_opts=opts.LabelOpts(is_show=show_label_opt,
                                              font_size=10,
                                              font_weight=1,
                                              is_value_animation=True)  # no lines
                )
                .set_global_opts(
                    title_opts=opts.TitleOpts(
                        title=f"{force_type_dict[force_type][0]} Diagram",
                        pos_left="center",

                    ),
                    xaxis_opts=opts.AxisOpts(
                        type_="value",  # Ensures smooth line instead of step
                        name=f"Location {units_dict[unit_systems]['Placeholder']['length']}",
                        name_location="middle",
                        name_gap=30,
                        position="bottom",
                        offset=3,
                        min_=0,
                        max_=length,
                        splitline_opts=opts.SplitLineOpts(
                            is_show=True,
                            linestyle_opts=opts.LineStyleOpts(opacity=0.2)
                        )
                    ),
                    yaxis_opts=opts.AxisOpts(
                        type_='value',
                        is_show=True,
                        name="",  # Hides Y-axis name
                        min_=minval,
                        max_=maxval,
                        splitline_opts=opts.SplitLineOpts(
                            is_show=True,
                            linestyle_opts=opts.LineStyleOpts(opacity=0.2)
                        )
                    ),
                    tooltip_opts=opts.TooltipOpts(trigger="axis"),
                    legend_opts=opts.LegendOpts(
                        pos_bottom="0%",  # Put legend below x-axis
                        pos_left="center",  # Centered horizontally
                        orient="horizontal"  # Keep the items in a row
                    ),
                    toolbox_opts=opts.ToolboxOpts(
                        is_show=True,
                        feature={
                            "dataZoom": {
                                "show": True,
                                "title": {
                                    "zoom": "Zoom",
                                    "back": "Reset Zoom"
                                }
                            },
                            "restore": {
                                "show": True,
                                "title": "Restore"
                            },
                            "dataView": {
                                "show": True,
                                "title": "Data View",
                                "readOnly": True
                            },
                            "magicType": {
                                "show": True,
                                "title": {
                                    "line": "Line Chart",
                                    "bar": "Bar Chart",
                                    "stack": "Stack",
                                    "tiled": "Tiled"
                                },
                                "type": ["line", "bar"]
                            },
                            # "saveAsImage" is intentionally omitted
                        }
                    )

                )

            )

            # Display the Pyechart figure in Streamlit
            import json

            st_echarts(
                options=json.loads(chart.dump_options()),
                height="500px",
                key=f"{force_type}-chart"
            )

            # st.write(chart.get_options())

# === SECTION 4 === App Layout ====================================================================
st.header('Beam Analysis', divider='orange')
st.subheader(':blue-background[**Parameters**]', divider='rainbow')

# Unit system radio widget
unit_systems = st.radio(
    'Unit system',
    options=["Metric", "Imperial"],
    captions=[
        "length (m), force (kN), moment (kN.m), distributed load (kN/m), deflection (mm), E (MPa), I (mm⁴)",
        "length (ft), force (kip), moment (kip.ft), distributed load (kip/ft), deflection (in), E (kip/in²), I (in⁴)"
    ]
)

# Inputs for beam parameters
with st.container(border=True):
    col1, col2, col3 = st.columns(3, gap='small')
    with col1:
        # Use the session state value for length
        length = st.number_input('Length',
                                 value=st.session_state.beam_length,  # Set the default value to session state
                                 min_value=0.0,
                                 placeholder=units_dict[unit_systems]['Placeholder']['length'],
                                 key="beam_length")  # Key for session state

    with col2:
        # Use the session state value for E
        modulus_of_elasticity = st.number_input('Modulus of Elasticity (E)',
                                                value=st.session_state.E,
                                                placeholder=units_dict[unit_systems]['Placeholder']['E'],
                                                key='E')

    with col3:
        # Use the session state value for I
        moment_of_inertia = st.number_input('Moment of Inertia (I)',
                                            value=st.session_state.I,
                                            placeholder=units_dict[unit_systems]['Placeholder']['I'],
                                            key='I')

st.write('\n')

if modulus_of_elasticity is not None and moment_of_inertia is not None:

    # Creating beam element
    beam = Beam(span=length,
                E=modulus_of_elasticity,
                I=moment_of_inertia)

else:
    # Creating beam element
    beam = Beam(span=length)

# Updating units w.r.t value in selectbox widget
for param, unit in units_dict[unit_systems]['System'].items():
    beam.update_units(param, unit)

# --- SECTION 4.1: Inputs ----------------------------------------------------------------------

st.subheader(':blue-background[**Model**]', divider='rainbow')

# Columns for input widgets and figure display
col1, col2 = st.columns([1.1, 2.1], gap='small')

# Supports---------------------------------------------------------------------------------------

with col1:
    # Supports section
    with st.popover('Supports', width='stretch'):

        col1a, col2a = st.columns([2, 1.5], vertical_alignment='top')

        with col1a:
            support_location_input = st.number_input('Location', min_value=0.0, value=None,
                                                     placeholder=units_dict[unit_systems]['Placeholder']['length'],
                                                     key='s1')  # Avoid 0 if not allowed

        with col2a:
            support_type = st.selectbox('Type of Support', options=['Roller', 'Pin', 'Fixed'])

        st.divider()

        col1a, col2a = st.columns([2, 1.5], vertical_alignment='bottom')

        with col2a:
            add_support_but = st.button('Add', type='primary', width='stretch', key='b1')

        with col1a:
            row_select = st.selectbox(label='Select row',
                                      options=[x for x in range(len(st.session_state.sup_locations_list))],
                                      key='r1')

        with col2a:
            remove_support_but = st.button('Delete', width='stretch', key='b2')

        # Logic to add supports to beam model
        if add_support_but:
            # check if user is adding support within the beam length
            if support_location_input is not None and support_location_input > length:
                st.warning("Please enter location of supports within the beam length")

            else:
                if support_location_input in st.session_state.sup_locations_list:
                    st.warning("The location entered has already support associated with it.")
                else:
                    # Check for valid location input
                    if support_location_input is not None:
                        storing_support(loc=support_location_input, type=support_type)
                        st.rerun()
                    else:
                        st.warning("Please provide a valid location for the support before adding.")

        # Logic to remove supports from beam model
        if remove_support_but:
            # Check if lists are not empty before removing
            if st.session_state.sup_locations_list and st.session_state.sup_type_display_list:
                removing_support(loc=st.session_state.sup_locations_list[row_select],
                                 type=st.session_state.sup_type_display_list[row_select])

                st.rerun()
            else:
                st.warning("No supports available to remove.")

        # Display DataFrame with stored support data
        if st.session_state.sup_locations_list:
            sup_dataframe = pd.DataFrame({
                'Location': st.session_state.sup_locations_list,
                'Type': st.session_state.sup_type_display_list
            })
            st.dataframe(data=sup_dataframe,
                         width='stretch',
                         key='supp_table')

    # Point Loads---------------------------------------------------------------------------------------

    with st.popover('Point Loads', width='stretch'):

        pl_location = st.number_input('Location',
                                      min_value=0.000,
                                      format="%0.3f",
                                      value=None,
                                      placeholder=units_dict[unit_systems]['Placeholder']['length'],
                                      key='pl1')

        col1a, col2a = st.columns([0.5, 1], vertical_alignment='top')

        with col1a:
            direction = st.pills("Direction",
                                 options=["↑", "↓"],
                                 default="↓",
                                 selection_mode="single",
                                 key='pl2')

        with col2a:
            pl_magnitude = st.number_input('Magnitude',
                                           min_value=0.000,
                                           format="%0.3f",
                                           value=None,
                                           placeholder=units_dict[unit_systems]['Placeholder']['force'],
                                           key='pl3')

        st.divider()

        col1a, col2a = st.columns([2, 1.5], vertical_alignment='bottom')

        with col2a:
            add_pl_but = st.button('Add', type='primary', width='stretch', key='b3')

        with col1a:
            row_select = st.selectbox(label='Select row',
                                      options=[x for x in range(len(st.session_state.pl_locations_list))],
                                      key='r2')

        with col2a:
            remove_pl_but = st.button('Delete', width='stretch', key='b4')

        if add_pl_but:
            # Check for valid location input
            if pl_magnitude is not None and pl_location is not None:
                if pl_location > length:
                    st.warning("Please provide a valid value of location within beam length.")
                else:
                    storing_pointloads(loc=pl_location, mag=pl_magnitude * sign_conv[direction])
                    st.rerun()
            else:
                st.warning("Please provide a valid values of loading and location.")

        if remove_pl_but:
            # Check if lists are not empty before removing
            if st.session_state.pl_locations_list and st.session_state.pl_mag_list:
                removing_pointloads(loc=st.session_state.pl_locations_list[row_select],
                                    mag=st.session_state.pl_mag_list[row_select])
                st.rerun()
            else:
                st.warning("No point loads available to remove.")

        # Display DataFrame with stored pointloads data
        if st.session_state.pl_locations_list:
            pl_dataframe = pd.DataFrame({
                'Location': st.session_state.pl_locations_list,
                'Magnitude': st.session_state.pl_mag_list
            })
            st.dataframe(pl_dataframe,
                         width='stretch')

    # Point Moments---------------------------------------------------------------------------------------

    with st.popover('Point Moments', width='stretch'):

        pm_location = st.number_input('Location',
                                      min_value=0.000,
                                      value=None,
                                      format='%0.3f',
                                      placeholder=units_dict[unit_systems]['Placeholder']['length'],
                                      key='pm1')

        col1a, col2a = st.columns([0.5, 1], vertical_alignment='top')

        with col1a:
            direction = st.pills("Direction",
                                 options=["↻", "↺"],
                                 default="↻",
                                 selection_mode="single",
                                 key='pm2')

        with col2a:
            # Inputs
            pm_magnitude = st.number_input('Magnitude',
                                           value=None,
                                           min_value=0.000,
                                           format='%0.3f',
                                           placeholder=units_dict[unit_systems]['Placeholder']['moment'],
                                           key='pm3')

        st.divider()

        col1a, col2a = st.columns([2, 1.5], vertical_alignment='bottom')

        with col2a:
            add_pm_but = st.button('Add', type='primary', width='stretch', key='b5')

        with col1a:
            row_select = st.selectbox(label='Select row',
                                      options=[x for x in range(len(st.session_state.pm_locations_list))],
                                      key='r3')

        with col2a:
            remove_pm_but = st.button('Delete', width='stretch', key='b6')

        if add_pm_but:
            # Check for valid location input
            if pm_magnitude is not None and pm_location is not None:
                if pm_location > length:
                    st.warning("Please provide a valid value of location within beam length.")
                else:
                    storing_pointmoments(loc=pm_location, mag=pm_magnitude * sign_conv[direction])
                    st.rerun()
            else:
                st.warning("Please provide a valid values of moment and location.")

        if remove_pm_but:
            # Check if lists are not empty before removing
            if st.session_state.pm_locations_list and st.session_state.pm_mag_list:
                removing_pointmoments(loc=st.session_state.pm_locations_list[row_select],
                                      mag=st.session_state.pm_mag_list[row_select])
                st.rerun()
            else:
                st.warning("No point moments available to remove.")

        # Display DataFrame with stored point moments data
        if st.session_state.pm_locations_list:
            pm_dataframe = pd.DataFrame({
                'Location': st.session_state.pm_locations_list,
                'Magnitude': st.session_state.pm_mag_list
            })
            st.dataframe(pm_dataframe,
                         width='stretch')

    # Uniformly Distributed Loads (UDL)-------------------------------------------------------------------

    with st.popover('Uniformly Distributed Loads (UDLs)', width='stretch'):

        col1a, col2a = st.columns(2, vertical_alignment='top')

        with col1a:
            udl_x1_location = st.number_input('Starting Location',
                                              min_value=0.000,
                                              format='%0.3f',
                                              value=None,
                                              placeholder=units_dict[unit_systems]['Placeholder']['length'],
                                              key='udls1')
        with col2a:
            udl_x2_location = st.number_input('Ending Location',
                                              min_value=0.000,
                                              value=None,
                                              format='%0.3f',
                                              placeholder=units_dict[unit_systems]['Placeholder']['length'],
                                              key='udls2')

        col1a, col2a = st.columns(2, vertical_alignment='top')

        with col1a:
            direction = st.pills("Direction",
                                 options=["↑", "↓"],
                                 default="↓",
                                 selection_mode="single",
                                 key='udl3')

        with col2a:
            # Inputs
            udl_magnitude = st.number_input('Magnitude',
                                            value=None,
                                            min_value=0.000,
                                            format='%0.3f',
                                            placeholder=units_dict[unit_systems]['Placeholder']['force'],
                                            key='udls4')

        st.divider()

        col1a, col2a = st.columns(2, vertical_alignment='bottom')

        with col2a:
            add_udls_but = st.button('Add', type='primary', width='stretch', key='b7')

        with col1a:
            row_select = st.selectbox(label='Select row',
                                      options=[x for x in range(len(st.session_state.udls_mag_list))],
                                      key='r4')

        with col2a:
            remove_udls_but = st.button('Delete', width='stretch', key='b8')

        if add_udls_but:
            # Check for valid location input
            if udl_magnitude is not None and udl_x1_location is not None and udl_x2_location is not None:
                if udl_x1_location > length:
                    st.warning("Please provide a valid value of starting location within beam length.")
                elif udl_x2_location > length:
                    st.warning("Please provide a valid value of ending location within beam length.")
                elif udl_x1_location >= udl_x2_location:
                    st.warning("Starting location must be less than the ending location.")
                else:
                    storing_udls(loc1=udl_x1_location, loc2=udl_x2_location, mag=udl_magnitude * sign_conv[direction])
                    st.rerun()
            else:
                st.warning("Please provide valid values for loading and locations.")

        if remove_udls_but:
            # Check if lists are not empty before removing
            if st.session_state.udls_x1_locations_list and st.session_state.udls_x2_locations_list and st.session_state.udls_mag_list:
                removing_udls(loc1=st.session_state.udls_x1_locations_list[-1],
                              loc2=st.session_state.udls_x2_locations_list[-1],
                              mag=st.session_state.udls_mag_list[-1])
                st.rerun()
            else:
                st.warning("No Uniformly Distributed Loads (UDLs) available to remove.")

        # Display DataFrame with Uniformly Distributed Loads (UDLs) stored  data
        if st.session_state.udls_x1_locations_list:
            udls_dataframe = pd.DataFrame({
                'Starting Location': st.session_state.udls_x1_locations_list,
                'Ending Location': st.session_state.udls_x2_locations_list,
                'Magnitude': st.session_state.udls_mag_list
            })
            st.dataframe(udls_dataframe,
                         width='stretch')

    # Variably Distributed Loads (VDL)--------------------------------------------------------------------
    with st.popover('Variably Distributed Loads (VDLs)', width='stretch'):

        col1a, col2a, col3a = st.columns([1, 0.5, 1], vertical_alignment='top', gap='small')

        with col1a:
            vdl_x1_location = st.number_input('Starting Location',
                                              min_value=0.000,
                                              value=None,
                                              placeholder=units_dict[unit_systems]['Placeholder']['length'],
                                              key='vdls1')
        with col2a:
            direction_1 = st.pills("Direction",
                                 options=["↑", "↓"],
                                 default="↓",
                                 selection_mode="single",
                                 key='vdl2')

        with col3a:
            # Inputs
            vdl_magnitude_1 = st.number_input('Starting Magnitude',
                                              value=None,
                                              min_value=0.000,
                                              placeholder=units_dict[unit_systems]['Placeholder']['force'],
                                              key='vdls3')

        col1a, col2a, col3a = st.columns([1, 0.5, 1], vertical_alignment='top', gap='small')
        with col1a:
            vdl_x2_location = st.number_input('Ending Location',
                                              min_value=0.000,
                                              value=None,
                                              placeholder=units_dict[unit_systems]['Placeholder']['length'],
                                              key='vdls4')

        with col2a:
            direction_2 = st.pills("Direction",
                                 options=["↑", "↓"],
                                 default="↓",
                                 selection_mode="single",
                                 key='vdl5')

        with col3a:
            vdl_magnitude_2 = st.number_input('Ending Magnitude',
                                              value=None,
                                              min_value=0.000,
                                              placeholder=units_dict[unit_systems]['Placeholder']['force'],
                                              key='vdls6')

        st.divider()

        col1a, col2a = st.columns(2, vertical_alignment='bottom')

        with col2a:
            add_vdls_but = st.button('Add', type='primary', width='stretch', key='b9')

        with col1a:
            row_select = st.selectbox(label='Select row',
                                      options=[x for x in range(len(st.session_state.vdls_x1_locations_list))],
                                      key='r5')

        with col2a:
            remove_vdls_but = st.button('Delete', width='stretch', key='b10')

        if add_vdls_but:
            # Check for valid location input
            if vdl_magnitude_1 is not None and vdl_magnitude_2 is not None and vdl_x1_location is not None and vdl_x2_location is not None:
                if vdl_x1_location > length:
                    st.warning("Please provide a valid value of starting location within beam length.")
                elif vdl_x2_location > length:
                    st.warning("Please provide a valid value of ending location within beam length.")
                elif vdl_x1_location >= vdl_x2_location:
                    st.warning("Starting location must be less than the ending location.")
                else:
                    storing_vdls(loc1=vdl_x1_location,
                                 loc2=vdl_x2_location,
                                 mag1=vdl_magnitude_1 * sign_conv[direction_1],
                                 mag2=vdl_magnitude_2 * sign_conv[direction_2])

                    st.rerun()
            else:
                st.warning("Please provide valid values for loadings and locations.")

        if remove_vdls_but:
            # Check if lists are not empty before removing
            if st.session_state.vdls_x1_locations_list and st.session_state.vdls_x2_locations_list and st.session_state.vdls_mag1_list and st.session_state.vdls_mag2_list:
                removing_vdls(loc1=st.session_state.vdls_x1_locations_list[row_select],
                              loc2=st.session_state.vdls_x2_locations_list[row_select],
                              mag1=st.session_state.vdls_mag1_list[row_select],
                              mag2=st.session_state.vdls_mag2_list[row_select])

                st.rerun()
            else:
                st.warning("No Variably Distributed Loads (VDLs) available to remove.")

        # Display DataFrame with Variably Distributed Loads (VDLs) stored  data
        if st.session_state.vdls_x1_locations_list:
            vdls_dataframe = pd.DataFrame({
                'Start Loc.': st.session_state.vdls_x1_locations_list,
                'End Loc.': st.session_state.vdls_x2_locations_list,
                'Start Mag.': st.session_state.vdls_mag1_list,
                'End Mag.': st.session_state.vdls_mag2_list
            })
            st.dataframe(vdls_dataframe, width='stretch')

    # Clear everything button
    clear_button = st.button('Clear all', key='b11')
    if clear_button:
        clear_everything()

# Adding All the load/support values to beam model and displaying the figure

with col2:
    # Add all supports from the DataFrame to the beam
    for loc, typ in zip(st.session_state.sup_locations_list, st.session_state.sup_type_list):
        supp = Support(coord=loc, fixed=typ)
        beam.add_supports(supp)

    # Add all pointloads from the DataFrame to the beam
    for loc, mag in zip(st.session_state.pl_locations_list, st.session_state.pl_mag_list):
        load = PointLoadV(coord=loc, force=mag)
        beam.add_loads(load)

    # Add all point moments from the DataFrame to the beam
    for loc, mag in zip(st.session_state.pm_locations_list, st.session_state.pm_mag_list):
        load = PointTorque(coord=loc, force=mag)
        beam.add_loads(load)

    # Add all UDLs from the DataFrame to the beam
    for loc1, loc2, mag in zip(st.session_state.udls_x1_locations_list,
                               st.session_state.udls_x2_locations_list,
                               st.session_state.udls_mag_list):
        load = UDLV(span=(loc1, loc2), force=mag)
        beam.add_loads(load)

    # Add all VDLs from the DataFrame to the beam
    for loc1, loc2, mag1, mag2 in zip(st.session_state.vdls_x1_locations_list,
                                      st.session_state.vdls_x2_locations_list,
                                      st.session_state.vdls_mag1_list,
                                      st.session_state.vdls_mag2_list):
        load = TrapezoidalLoadV(span=(loc1, loc2), force=(mag1, mag2))
        beam.add_loads(load)

    # Beam schematic section
    fig = beam.plot_beam_diagram()
    st.plotly_chart(fig, theme=None, width='stretch')

# === SECTION 5 === Analysis ====================================================================
st.subheader(':blue-background[**Analysis**]', divider='rainbow')

col1a, col1b = st.columns(2, gap='small', vertical_alignment='center')
with col1a:
    with st.container(key='Analysis_cont', border=True):

        # An option widget to specify the type of analysis
        analysis_options = st.radio('Type of Analysis',
                                    options=['S.F.D & B.M.D', 'S.F.D, B.M.D & Deflection diagram'],
                                    horizontal=True)

        st.divider()

        # Option to get from user about adding query points
        query_points_option = st.toggle('Query Points', value=False, help='Highlights all the critical points on '
                                                                          'beam where the values changes')

    if query_points_option == True:

        # Merge all lists of critical points
        query_point_list = list(set(st.session_state.sup_locations_list
                                    + st.session_state.pl_locations_list
                                    + st.session_state.pm_locations_list
                                    + st.session_state.udls_x1_locations_list
                                    + st.session_state.udls_x2_locations_list
                                    + st.session_state.vdls_x1_locations_list
                                    + st.session_state.vdls_x2_locations_list))

        query_point_list.sort()

        # Add all query points to beam
        for points in query_point_list:
            beam.add_query_points(points)

with col1b:
    # Analysis button which will run the analysis
    analysis_but = st.button('Analyze', type='primary')

# Layout Option 1
# Display the Analysis Results
# if analysis_but:
#     # try:
#     # Solve the beam
#     beam.analyse()
#
#     if analysis_options == 'S.F.D & B.M.D':
#         st.plotly_chart(figure_or_data=sfd_bmd_plot(),
#                         theme=None)
#
#         st.subheader(':blue-background[**Analysis**]', divider='rainbow')
#
#         save_html_plot_with_button(figure=sfd_bmd_plot())
#
#         result_without_deflection()
#
#         with st.container(key='plot1', border=True):
#             PyechartPlot_and_Table(force_type='sf', np=300)
#
#         with st.container(key='plot2', border=True):
#             PyechartPlot_and_Table(force_type='bm', np=300)
#
#         st.toast('Analysis Successful!', icon=":material/check_circle:")
#
#     else:
#         if modulus_of_elasticity is not None and moment_of_inertia is not None:
#             st.plotly_chart(figure_or_data=sfd_bmd_deflection_plot(),
#                             theme=None,
#                             width='stretch')
#
#             save_html_plot_with_button(figure=sfd_bmd_deflection_plot())
#
#             result_with_deflection()
#
#             with st.container(key='plot3', border=True):
#                 PyechartPlot_and_Table(force_type='sf', np=300)
#
#             with st.container(key='plot4', border=True):
#                 PyechartPlot_and_Table(force_type='bm', np=300)
#
#             with st.container(key='plot5', border=True):
#                 PyechartPlot_and_Table(force_type='def', np=300)
#
#             st.toast('Analysis Successful!', icon=":material/check_circle:")
#         else:
#             st.warning(
#                 'Modulus of elasticity (E) and Moment of inertia (I) are required for **Deflection Diagram**')
# except:
#     st.error("""
#     The beam model is incomplete or incorrect.
#     Please review the following aspects:
#     - Reactions
#     - Supports
#     - Loads
#     """)


# Layout Option 2

# Display the Analysis Results
if analysis_but:
    try:
        # Solve the beam
        beam.analyse()

        if analysis_options == 'S.F.D & B.M.D':

            # Creates two tabs as specified
            tab1, tab2 = st.tabs(['General Analysis', 'Detail Overview'])

            with tab1:
                # Displays the indeterminatebeampy plot
                st.plotly_chart(figure_or_data=sfd_bmd_plot(),
                                theme=None)

                # Displays the button to save indeterminatebeampy plot as HTML file
                save_html_plot_with_button(figure=sfd_bmd_plot())

                st.toast('Analysis Successful!', icon=":material/check_circle:")

            with tab2:

                # Shows the main results like max, min, abs max/min values
                result_without_deflection()

                # Displays the pyechart graph wth table for shear force
                with st.container(key='plot1', border=True):
                    PyechartPlot_and_Table(force_type='sf', np=300)

                # Displays the pyechart graph wth table for bending moment
                with st.container(key='plot2', border=True):
                    PyechartPlot_and_Table(force_type='bm', np=300)

        else:
            if modulus_of_elasticity is not None and moment_of_inertia is not None:

                # Creates two tabs as specified
                tab1, tab2 = st.tabs(['General Analysis', 'Detail Overview'])

                with tab1:
                    # Displays the indeterminatebeampy plot
                    st.plotly_chart(figure_or_data=sfd_bmd_deflection_plot(),
                                    theme=None)

                    # Displays the button to save indeterminatebeampy plot as HTML file
                    save_html_plot_with_button(figure=sfd_bmd_deflection_plot())

                    st.toast('Analysis Successful!', icon=":material/check_circle:")

                with tab2:
                    result_with_deflection()

                    # Displays the pyechart graph wth table for shear force
                    with st.container(key='plot3', border=True):
                        PyechartPlot_and_Table(force_type='sf', np=300)

                    # Displays the pyechart graph wth table for bending moment
                    with st.container(key='plot4', border=True):
                        PyechartPlot_and_Table(force_type='bm', np=300)

                    # Displays the pyechart graph wth table for deflection
                    with st.container(key='plot5', border=True):
                        PyechartPlot_and_Table(force_type='def', np=300)

            else:
                st.warning(
                    'Modulus of elasticity (E) and Moment of inertia (I) are required for **Deflection Diagram**')
    except:
        st.error("""
        The beam model is incomplete or incorrect.
        Please review the following aspects:
        - Reactions
        - Supports
        - Loads
        """)
