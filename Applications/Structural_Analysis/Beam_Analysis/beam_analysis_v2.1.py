import streamlit as st
from indeterminatebeam import *
import pandas as pd
from plotly.subplots import make_subplots
from Applications.Structural_Analysis.Section_Properties_Calculator.assets.cross_section_shape_diagrams import *


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
    st.session_state.E = ''

# Initialize state for beam Moment of inertia
if 'I' not in st.session_state:
    st.session_state.I = ''


# Function for handling the inputs of E and I
def adjusting_string(input_string):
    """
    Replaces 'x' with '*' and '^' with '**' in the inputted string.

    Parameters:
    input_string (str): The string to be adjusted.

    Returns:
    str: The adjusted string with replacements.
    """
    # Replace 'x' with '*' and '^' with '**'
    adjusted_string = input_string.replace('x', '*').replace('^', '**')
    return adjusted_string


# Function for creating intervals at which the values of SF and BM is to be find
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


# Function to create table of Internal forces values (deflection not included)
@st.fragment
def create_table_without_deflection():
    col1, col2 = st.columns(2, gap='small', vertical_alignment='center')

    with col1:
        with st.popover('### **Values at Specified Location**', use_container_width=True):
            location_value = st.number_input('Location', min_value=0.00, value=1.00, key='b13-1', max_value=length)

            # Display the values at specified location
            st.dataframe(data={f"Location ({units_dict[unit_systems]['length']})": [location_value],
                               f'Shear Force ({units_dict[unit_systems]['force']})': [
                                   beam.get_shear_force(location_value)],
                               f'Bending Moment ({units_dict[unit_systems]['moment']})': [
                                   beam.get_bending_moment(location_value)]},
                         use_container_width=True)

    with col2:
        with st.popover('### **Values at Specified Interval**', use_container_width=True):
            interval_value = st.number_input('Interval', min_value=0.00, value=1.00, key='b13-2', max_value=length)

            st.write('\n')

            # Create intervals with a step of specified interval
            intervals = create_intervals(length, interval=interval_value)

            # Check if intervals are generated correctly
            if not intervals:
                st.warning("No intervals generated. Check the beam length and interval values.")
            else:
                sf_values = []
                bm_values = []

                # Calculate shear force and bending moment at each interval point
                for point in intervals:
                    try:
                        sf_values.append(beam.get_shear_force(point))
                        bm_values.append(beam.get_bending_moment(point))
                    except TypeError as e:
                        st.warning(f"An error occurred while calculating values at {point}: {e}")

                # Ensure that shear force and bending moment values are the correct length
                if len(sf_values) != len(intervals) or len(bm_values) != len(intervals):
                    st.warning("The length of shear force or bending moment values does not match the intervals.")
                else:
                    # Create DataFrame with internal forces
                    internalforces_values_dataframe = pd.DataFrame({
                        f'Interval ({units_dict[unit_systems]['length']})': intervals,
                        f'Shear Force ({units_dict[unit_systems]['force']})': sf_values,
                        f'Bending Moment ({units_dict[unit_systems]['moment']})': bm_values,
                        # Add deflection or other values as needed
                    })

                    # Display the DataFrame
                    st.dataframe(internalforces_values_dataframe,
                                 hide_index=True,
                                 use_container_width=True,
                                 height=315)

                    st.write("\n")


# Function to create table of Internal forces values (deflection included)
@st.fragment
def create_table_with_deflection():
    # with st.container(key='Specified_Location_cont_2',
    #                   border=True):
    col1, col2 = st.columns(2, gap='small', vertical_alignment='center')

    with col1:
        with st.popover('### **Values at Specified Location**', use_container_width=True):
            location_value = st.number_input('Location', min_value=0.00, value=1.00, key='b13-3', max_value=length)

            # Display the values at specified location
            st.dataframe(data={f"Location ({units_dict[unit_systems]['length']})": [location_value],
                               f'Shear Force ({units_dict[unit_systems]['force']})': [
                                   beam.get_shear_force(location_value)],
                               f'Bending Moment ({units_dict[unit_systems]['moment']})': [
                                   beam.get_bending_moment(location_value)],
                               f'Deflection ({units_dict[unit_systems]['deflection']})': [
                                   beam.get_deflection(location_value)]},
                         use_container_width=True)

    with col2:
        with st.popover('### **Values at Specified Interval**', use_container_width=True):

            interval_value = st.number_input('Interval', min_value=0.00, value=1.00, key='b13-4', max_value=length)

            st.write('\n')

            # Create intervals with a step of specified interval
            intervals = create_intervals(length, interval=interval_value)

            # Check if intervals are generated correctly
            if not intervals:
                st.warning("No intervals generated. Check the beam length and interval values.")
            else:
                sf_values = []
                bm_values = []
                deflections_values = []

                # Calculate shear force and bending moment at each interval point
                for point in intervals:
                    try:
                        sf_values.append(beam.get_shear_force(point))
                        bm_values.append(beam.get_bending_moment(point))
                        deflections_values.append(beam.get_deflection(point))
                    except TypeError as e:
                        st.warning(f"An error occurred while calculating values at {point}: {e}")

                # Ensure that shear force and bending moment values are the correct length
                if len(sf_values) != len(intervals) or len(bm_values) != len(intervals):
                    st.warning("The length of shear force or bending moment values does not match the intervals.")
                else:
                    # Create DataFrame with internal forces
                    internalforces_values_dataframe = pd.DataFrame({
                        f'Interval ({units_dict[unit_systems]['length']})': intervals,
                        f'Shear Force ({units_dict[unit_systems]['force']})': sf_values,
                        f'Bending Moment ({units_dict[unit_systems]['moment']})': bm_values,
                        f'Deflection ({units_dict[unit_systems]['deflection']})': deflections_values
                        # Add deflection or other values as needed
                    })

                    # Display the DataFrame
                    st.dataframe(internalforces_values_dataframe,
                                 hide_index=True,
                                 use_container_width=True,
                                 height=315)
                    st.write("\n")


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
                                        xunits=f"{units_dict[unit_systems]['length']}",
                                        yunits=f"{units_dict[unit_systems]['force']}",
                                        fig=analysis_fig, row=3, col=1)

    # Plot bending moment diagram in the fourth row
    analysis_fig = beam.plot_analytical('bm', color="rgba(204, 204, 0, 1)", title="Bending Moment Diagram",
                                        xlabel="Length", ylabel="Bending Moment",
                                        xunits=f"{units_dict[unit_systems]['length']}",
                                        yunits=f"{units_dict[unit_systems]['moment']}",
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
                                        xunits=f"{units_dict[unit_systems]['length']}",
                                        yunits=f"{units_dict[unit_systems]['force']}",
                                        fig=analysis_fig, row=3, col=1)

    # Plot bending moment diagram in the fourth row
    analysis_fig = beam.plot_analytical('bm', color="rgba(204, 204, 0, 1)", title="Bending Moment Diagram",
                                        xlabel="Length", ylabel="Bending Moment",
                                        xunits=f"{units_dict[unit_systems]['length']}",
                                        yunits=f"{units_dict[unit_systems]['moment']}",
                                        fig=analysis_fig, row=4, col=1)

    # Plot deflection diagram in the fifth row
    analysis_fig = beam.plot_analytical('d', color="rgba(255, 0, 0, 0.5)", title="Deflection Diagram",
                                        xlabel="Length", ylabel="Deflection",
                                        xunits=f"{units_dict[unit_systems]['length']}",
                                        yunits=f"{units_dict[unit_systems]['deflection']}",
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


# Function to show results without deflection
def result_without_deflection():
    # RESULTS SECTION
    st.write('\n')
    st.subheader(':blue-background[**Results**]', divider='rainbow')
    st.write('\n')

    col1a, col1b, col1c = st.columns(3, gap='medium')

    with col1b:
        st.metric('### :red-background[Max. Bending Moment]',
                  value=f"{round(beam.get_bending_moment(return_max=True), 2)}  {units_dict[unit_systems]['moment']}")
        st.metric('### :red-background[Min. Bending Moment]',
                  value=f"{round(beam.get_bending_moment(return_min=True), 2)}  {units_dict[unit_systems]['moment']}")
        st.metric('### :red-background[Absolute Max. Bending Moment]',
                  value=f"{round(beam.get_bending_moment(return_absmax=True), 2)}  {units_dict[unit_systems]['moment']}")

    with col1a:
        st.metric('### :red-background[Max. Shear Force]',
                  value=f"{round(beam.get_shear_force(return_max=True), 2)}  {units_dict[unit_systems]['force']}")
        st.metric('### :red-background[Min. Shear Force]',
                  value=f"{round(beam.get_shear_force(return_min=True), 2)}  {units_dict[unit_systems]['force']}")
        st.metric('### :red-background[Absolute Max. Shear Force]',
                  value=f"{round(beam.get_shear_force(return_absmax=True), 2)}  {units_dict[unit_systems]['force']}")


# Function to show results with deflection
def result_with_deflection():
    # RESULTS SECTION
    st.write('\n')
    st.subheader(':blue-background[**Results**]', divider='rainbow')
    st.write('\n')

    col1a, col1b, col1c = st.columns(3, gap='medium')

    with col1b:
        st.metric('### :red-background[Max. Bending Moment]',
                  value=f"{round(beam.get_bending_moment(return_max=True), 2)}  {units_dict[unit_systems]['moment']}")
        st.metric('### :red-background[Min. Bending Moment]',
                  value=f"{round(beam.get_bending_moment(return_min=True), 2)}  {units_dict[unit_systems]['moment']}")
        st.metric('### :red-background[Absolute Max. Bending Moment]',
                  value=f"{round(beam.get_bending_moment(return_absmax=True), 2)}  {units_dict[unit_systems]['moment']}")

    with col1a:
        st.metric('### :red-background[Max. Shear Force]',
                  value=f"{round(beam.get_shear_force(return_max=True), 2)}  {units_dict[unit_systems]['force']}")
        st.metric('### :red-background[Min. Shear Force]',
                  value=f"{round(beam.get_shear_force(return_min=True), 2)}  {units_dict[unit_systems]['force']}")
        st.metric('### :red-background[Absolute Max. Shear Force]',
                  value=f"{round(beam.get_shear_force(return_absmax=True), 2)}  {units_dict[unit_systems]['force']}")

    with col1c:
        st.metric('### :red-background[Upwards Deflection]',
                  value=f"{round(beam.get_deflection(return_max=True), 3)}  {units_dict[unit_systems]['deflection']}")
        st.metric('### :red-background[Downwards Deflection]',
                  value=f"{round(beam.get_deflection(return_min=True), 3)}  {units_dict[unit_systems]['deflection']}")
        st.metric('### :red-background[Absolute Max. Deflection]',
                  value=f"{round(beam.get_deflection(return_absmax=True), 3)}  {units_dict[unit_systems]['deflection']}")


# Function for saving dynamic html plot with button
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
        use_container_width=True
    )


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


created_shape_list = []


# Function for calculation of Rectangular shape
# @st.fragment
def calc_for_rectangle_shape():
    with st.container(border=True):
        st.write('##### :blue-background[**Parameters**]')
        col1, col2 = st.columns(2, gap='small')

        with col1:
            b = st.number_input('Width (w)', value=None, placeholder=units_dict_placeholder[unit_systems]['deflection'])
        with col2:
            h = st.number_input('Height (h)', value=None,
                                placeholder=units_dict_placeholder[unit_systems]['deflection'])

        if b is not None and h is not None:
            iy = (b * h ** 3) / 12
            x_bar = b / 2
            y_bar = h / 2

            st.write('\n')
            st.write('##### :blue-background[**Result**]')

            st.write(f"""###### :red-background[Centroid]  
            ({x_bar.__round__(2)}, {y_bar.__round__(2)})""")

            col1, col2 = st.columns([2, 0.5], gap='small', vertical_alignment='bottom')
            with col1:
                st.write(f"""###### :red-background[Moment of Inertia]
                {round(iy, 3)}""")  # {units_dict_placeholder[unit_systems]['I']}""")
            with col2:
                st.write(f"$${units_dict_placeholder[unit_systems]['I']}$$")

            created_shape_list.append(create_rectangle_shape(b=b, h=h))


# Function for calculation of I-shape symmetrical
# @st.fragment
def calc_for_I_symmetrical_shape():
    with st.container(border=True):
        st.write('##### :blue-background[**Parameters**]')
        col1, col2 = st.columns(2, gap='small')

        with col1:
            f_w = st.number_input('Flange Width (F-w)', value=None,
                                  placeholder=units_dict_placeholder[unit_systems]['deflection'])
        with col2:
            f_t = st.number_input('Flange Thickness (F-t)', value=None,
                                  placeholder=units_dict_placeholder[unit_systems]['deflection'])

        col1, col2 = st.columns(2, gap='small')
        with col1:
            w_t = st.number_input('Web Thickness (W-t)', value=None,
                                  placeholder=units_dict_placeholder[unit_systems]['deflection'])
        with col2:
            w_h = st.number_input('Web Height (W-h)', value=None,
                                  placeholder=units_dict_placeholder[unit_systems]['deflection'])

        if all(x is not None for x in [f_w, w_h, w_t, f_t]):
            # Centroid calculations
            x_bar = f_w / 2
            y_bar = f_t + (w_h / 2)

            # Moment of Inertia calculation
            iy = ((f_w * f_t ** 3) / 6) + 2 * ((f_w * f_t) * ((f_t + w_h) / 2) ** 2) + ((w_t * w_h ** 3) / 12)

            st.write('\n')
            st.write('##### :blue-background[**Result**]')

            st.write(f"""###### :red-background[Centroid]  
            ({x_bar.__round__(2)}, {y_bar.__round__(2)})""")

            col1, col2 = st.columns([2, 0.5], gap='small', vertical_alignment='bottom')
            with col1:
                st.write(f"""###### :red-background[Moment of Inertia]
                {round(iy, 3)}""")  # {units_dict_placeholder[unit_systems]['I']}""")
            with col2:
                st.write(f"$${units_dict_placeholder[unit_systems]['I']}$$")

            created_shape_list.append(create_I_symmetrical_shape(flange_width=f_w,
                                                                 flange_thickness=f_t,
                                                                 web_thickness=w_t,
                                                                 web_height=w_h,
                                                                 x_bar=x_bar,
                                                                 y_bar=y_bar))


# Function for calculation of I-shape unsymmetrical
# @st.fragment
def calc_for_I_unsymmetrical_shape():
    with st.container(border=True):
        st.write('##### :blue-background[**Parameters**]')

        col1, col2 = st.columns(2, gap='small')
        with col1:
            tf_w = st.number_input('Top Flange Width (TF-w)', value=None,
                                   placeholder=units_dict_placeholder[unit_systems]['deflection'])
        with col2:
            tf_t = st.number_input('Flange Thickness (TF-t)', value=None,
                                   placeholder=units_dict_placeholder[unit_systems]['deflection'])

        col1, col2 = st.columns(2, gap='small')
        with col1:
            w_t = st.number_input('Web Thickness (W-t)', value=None,
                                  placeholder=units_dict_placeholder[unit_systems]['deflection'])
        with col2:
            w_h = st.number_input('Web Height (W-h)', value=None,
                                  placeholder=units_dict_placeholder[unit_systems]['deflection'])

        col1, col2 = st.columns(2, gap='small')
        with col1:
            bf_w = st.number_input('Bottom Flange Width (BF-w)', value=None,
                                   placeholder=units_dict_placeholder[unit_systems]['deflection'])
        with col2:
            bf_t = st.number_input('Bottom Flange Thickness (BF-t)', value=None,
                                   placeholder=units_dict_placeholder[unit_systems]['deflection'])

        if all(x is not None for x in [tf_w, w_t, bf_w, tf_t, w_h, bf_t]):

            # Centroid calculation
            if tf_w > bf_w:
                x_bar = tf_w / 2
            else:
                x_bar = bf_w / 2

            A1 = bf_w * bf_t
            y1 = bf_t / 2
            A2 = w_t * w_h
            y2 = bf_t + (w_h / 2)
            A3 = tf_w * tf_t
            y3 = bf_t + w_h + (tf_t / 2)

            y_bar = (A1 * y1 + A2 * y2 + A3 * y3) / (A1 + A2 + A3)

            # Moment of inertia calculation
            iy = ((bf_w * bf_t ** 3) / 12) + A1 * (abs(y_bar - y1)) ** 2 + ((w_t * w_h ** 3) / 12) + A2 * (
                abs(y_bar - y2)) ** 2 + ((tf_w * tf_t ** 3) / 12) + A3 * (abs(y_bar - y3)) ** 2

            st.write('\n')
            st.write('##### :blue-background[**Result**]')

            st.write(f"""###### :red-background[Centroid]  
            ({x_bar.__round__(2)}, {y_bar.__round__(2)})""")

            col1, col2 = st.columns([2, 0.5], gap='small', vertical_alignment='bottom')
            with col1:
                st.write(f"""###### :red-background[Moment of Inertia]
                {round(iy, 3)}""")  # {units_dict_placeholder[unit_systems]['I']}""")
            with col2:
                st.write(f"$${units_dict_placeholder[unit_systems]['I']}$$")

            created_shape_list.append(create_I_unsymmetrical_shape(top_flange_width=tf_w,
                                                                   top_flange_thickness=tf_t,
                                                                   web_thickness=w_t,
                                                                   web_height=w_h,
                                                                   bottom_flange_width=bf_w,
                                                                   bottom_flange_thickness=bf_t,
                                                                   x_bar=x_bar,
                                                                   y_bar=y_bar))


# Function for calculation of T-shape
# @st.fragment
def calc_for_T_shape():
    with st.container(border=True):
        st.write('##### :blue-background[**Parameters**]')
        col1, col2 = st.columns(2, gap='small')

        with col1:
            f_w = st.number_input('Flange Width (F-w)', value=None,
                                  placeholder=units_dict_placeholder[unit_systems]['deflection'])
        with col2:
            f_t = st.number_input('Flange Thickness (F-t)', value=None,
                                  placeholder=units_dict_placeholder[unit_systems]['deflection'])

        col1, col2 = st.columns(2, gap='small')
        with col1:
            w_t = st.number_input('Web Thickness (W-t)', value=None,
                                  placeholder=units_dict_placeholder[unit_systems]['deflection'])
        with col2:
            w_h = st.number_input('Web Height (W-h)', value=None,
                                  placeholder=units_dict_placeholder[unit_systems]['deflection'])

        if all(x is not None for x in [f_w, w_h, w_t, f_t]):
            # centroid calculation
            x_bar = f_w / 2
            A1 = w_t * w_h
            A2 = f_w * f_t
            y1 = w_h / 2
            y2 = w_h + (f_t / 2)
            y_bar = (A1 * y1 + A2 * y2) / (A1 + A2)

            # Moment of inertia calculation
            iy = (w_t * w_h ** 3) / 12 + A1 * (y_bar - (w_h / 2)) ** 2 + (f_w * f_t ** 3) / 12 + A2 * (
                    w_h + (f_t / 2) - y_bar) ** 2

            st.write('\n')
            st.write('##### :blue-background[**Result**]')

            st.write(f"""###### :red-background[Centroid]  
            ({x_bar.__round__(2)}, {y_bar.__round__(2)})""")

            col1, col2 = st.columns([2, 0.5], gap='small', vertical_alignment='bottom')
            with col1:
                st.write(f"""###### :red-background[Moment of Inertia]
                {round(iy, 3)}""")  # {units_dict_placeholder[unit_systems]['I']}""")
            with col2:
                st.write(f"$${units_dict_placeholder[unit_systems]['I']}$$")

            created_shape_list.append(create_T_shape(flange_width=f_w,
                                                     flange_thickness=f_t,
                                                     web_thickness=w_t,
                                                     web_height=w_h,
                                                     x_bar=x_bar,
                                                     y_bar=y_bar))


# Dict for supports
supports = {'Roller': (0, 1, 0),
            'Pin': (1, 1, 0),
            'Fixed': (1, 1, 1)}

# Metric Units placeholder Dictionary
metric_units_dict_placeholder = {
    'length': '(m)',
    'force': '(kN)',
    'moment': '(kN.m)',
    'distributed': '(kN/m)',
    'deflection': '(mm)',
    'E': '(MPa)',
    'I': '(mm⁴)'
}
# Imperial units placeholder dictionary
imperial_units_dict_placeholder = {
    'length': '(ft)',
    'force': '(kip)',
    'moment': '(kip.ft)',
    'distributed': '(kip/ft)',
    'deflection': '(in)',
    'E': '(ksi)',
    'I': '(in⁴)'
}
# Combined placeholder dictionary for units
units_dict_placeholder = {'Metric': metric_units_dict_placeholder,
                          'Imperial': imperial_units_dict_placeholder}

# Metric Units Dictionary
metric_units_dict = {
    'length': 'm',
    'force': 'kN',
    'moment': 'kN.m',
    'distributed': 'kN/m',
    'deflection': 'mm',
    'E': 'MPa',
    'I': 'mm4'
}

# Imperial units dictionary
imperial_units_dict = {
    'length': 'ft',
    'force': 'kip',
    'moment': 'kip.ft',
    'distributed': 'kip/ft',
    'deflection': 'in',
    'E': 'kip/in2',
    'I': 'in4'
}
# Combined dictionary for units
units_dict = {'Metric': metric_units_dict,
              'Imperial': imperial_units_dict}

# Tabs for Beam Profile and Cross-section Shapes
tab1, tab2 = st.tabs(['Beam Profile', 'Cross-section'])

with tab1:
    st.subheader(':blue-background[**Parameters**]', divider='rainbow')

    # Unit system radio
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
        col1a, col1b, col1c = st.columns(3, gap='small')
        with col1a:
            # Use the session state value for length
            length = st.number_input('Length',
                                     value=st.session_state.beam_length,  # Set the default value to session state
                                     # min_value=0.0,
                                     placeholder=units_dict_placeholder[unit_systems]['length'],
                                     key="beam_length")  # Key for session state

        with col1b:
            modulus_of_elasticity = st.text_input('Modulus of Elasticity (E)', value=st.session_state.E,
                                                  placeholder=units_dict_placeholder[unit_systems]['E'], key='E')

        with col1c:
            m_of_inertia = st.text_input('Moment of Inertia (I)', value=st.session_state.I,
                                         placeholder=units_dict_placeholder[unit_systems]['I'], key='I')

        # Save the beam parameters
        # col2a, col2b, col2c = st.columns(3, gap='small')
        # with col2b:
        #     save_beam_param = st.button('Save', use_container_width=True, type='primary')
        #
        # # Handle the form submission
        # if save_beam_param:
        #     if length is not None and length != 0:
        #         st.success('Beam parameters updated successfully!')
        #     else:
        #         st.warning("Beam must have atleast length!")

    st.write('\n')

    if modulus_of_elasticity != '' and m_of_inertia != '':

        # Creating beam element
        beam = Beam(span=length, E=eval(adjusting_string(modulus_of_elasticity)),
                    I=eval(adjusting_string(m_of_inertia)))
    else:
        # Creating beam element
        beam = Beam(span=length)

    # Updating units w.r.t value in selectbox
    for param, unit in units_dict[unit_systems].items():
        beam.update_units(param, unit)

    # INPUTS SECTION
    st.subheader(':blue-background[**Model**]', divider='rainbow')

    col3a, col3b = st.columns([1.1, 2.1], gap='small')

    with col3a:
        # Supports section
        with st.popover('Supports', use_container_width=True):

            col1a, col1b = st.columns([2, 1.5], vertical_alignment='top')

            with col1a:
                # Inputs
                support_type = st.selectbox('Type of Support', options=['Roller', 'Pin', 'Fixed'])
                support_location_input = st.number_input('Location', min_value=0.0, value=None,
                                                         placeholder=units_dict_placeholder[unit_systems]['length'],
                                                         key='s1')  # Avoid 0 if not allowed
                add_support_but = st.button('Add', type='primary', use_container_width=True, key='b1')
                remove_support_but = st.button('Undo', use_container_width=True, key='b2')
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
                        else:
                            st.warning("Please provide a valid location for the support before adding.")

            if remove_support_but:
                # Check if lists are not empty before removing
                if st.session_state.sup_locations_list and st.session_state.sup_type_display_list:
                    removing_support(loc=st.session_state.sup_locations_list[-1],
                                     type=st.session_state.sup_type_display_list[-1])
                else:
                    st.warning("No supports available to remove.")

            with col1b:
                # Display DataFrame with stored support data
                if st.session_state.sup_locations_list:
                    sup_dataframe = pd.DataFrame({
                        'Location': st.session_state.sup_locations_list,
                        'Type': st.session_state.sup_type_display_list
                    })
                    st.dataframe(sup_dataframe, hide_index=True, width=200)

        # Point Loads section
        with st.popover('Point Loads', use_container_width=True):

            col1a, col1b = st.columns([1, 1], vertical_alignment='top')

            with col1a:
                # Inputs
                pl_magnitude = st.number_input('Magnitude', value=None,
                                               placeholder=units_dict_placeholder[unit_systems]['force'],
                                               help='(+ve) is upwards & (-ve) is downwards', key='pl1')
                pl_location = st.number_input('Location', min_value=0.00, value=None,
                                              placeholder=units_dict_placeholder[unit_systems]['length'], key='pl2')
                add_pl_but = st.button('Add', type='primary', use_container_width=True, key='b3')
                remove_pl_but = st.button('Undo', use_container_width=True, key='b4')
            if add_pl_but:
                # Check for valid location input
                if pl_magnitude is not None and pl_location is not None:
                    if pl_location > length:
                        st.warning("Please provide a valid value of location within beam length.")
                    else:
                        storing_pointloads(loc=pl_location, mag=pl_magnitude)
                else:
                    st.warning("Please provide a valid values of loading and location.")

            if remove_pl_but:
                # Check if lists are not empty before removing
                if st.session_state.pl_locations_list and st.session_state.pl_mag_list:
                    removing_pointloads(loc=st.session_state.pl_locations_list[-1],
                                        mag=st.session_state.pl_mag_list[-1])
                else:
                    st.warning("No point loads available to remove.")

            with col1b:
                # Display DataFrame with stored pointloads data
                if st.session_state.pl_locations_list:
                    pl_dataframe = pd.DataFrame({
                        'Location': st.session_state.pl_locations_list,
                        'Magnitude': st.session_state.pl_mag_list
                    })
                    st.dataframe(pl_dataframe, hide_index=True, width=200)

        # Point Moments section
        with st.popover('Point Moments', use_container_width=True):

            col1a, col1b = st.columns([1, 1], vertical_alignment='top')

            with col1a:
                # Inputs
                pm_magnitude = st.number_input('Magnitude', value=None,
                                               placeholder=units_dict_placeholder[unit_systems]['moment'],
                                               help='(+ve) is Anti-clockwise & (-ve) is clockwise', key='pm1')
                pm_location = st.number_input('Location', min_value=0.00, value=None,
                                              placeholder=units_dict_placeholder[unit_systems]['length'], key='pm2')
                add_pm_but = st.button('Add', type='primary', use_container_width=True, key='b5')
                remove_pm_but = st.button('Undo', use_container_width=True, key='b6')

            if add_pm_but:
                # Check for valid location input
                if pm_magnitude is not None and pm_location is not None:
                    if pm_location > length:
                        st.warning("Please provide a valid value of location within beam length.")
                    else:
                        storing_pointmoments(loc=pm_location, mag=pm_magnitude)
                else:
                    st.warning("Please provide a valid values of moment and location.")

            if remove_pm_but:
                # Check if lists are not empty before removing
                if st.session_state.pm_locations_list and st.session_state.pm_mag_list:
                    removing_pointmoments(loc=st.session_state.pm_locations_list[-1],
                                          mag=st.session_state.pm_mag_list[-1])
                else:
                    st.warning("No point moments available to remove.")

            with col1b:
                # Display DataFrame with stored point moments data
                if st.session_state.pm_locations_list:
                    pm_dataframe = pd.DataFrame({
                        'Location': st.session_state.pm_locations_list,
                        'Magnitude': st.session_state.pm_mag_list
                    })
                    st.dataframe(pm_dataframe, hide_index=True, width=200)

        # Uniformly Distributed Loads (UDLs) section
        with st.popover('Uniformly Distributed Loads (UDLs)', use_container_width=True):

            col1a, col1b = st.columns([1, 1], vertical_alignment='top')

            with col1a:
                # Inputs
                udl_magnitude = st.number_input('Magnitude', value=None,
                                                placeholder=units_dict_placeholder[unit_systems]['force'],
                                                help='(+ve) is upwards & (-ve) is downwards', key='udls1')
                udl_x1_location = st.number_input('Starting Location', min_value=0.00, value=None,
                                                  placeholder=units_dict_placeholder[unit_systems]['length'],
                                                  key='udls2')
                udl_x2_location = st.number_input('Ending Location', min_value=0.00, value=None,
                                                  placeholder=units_dict_placeholder[unit_systems]['length'],
                                                  key='udls3')
                add_udls_but = st.button('Add', type='primary', use_container_width=True, key='b7')
                remove_udls_but = st.button('Undo', use_container_width=True, key='b8')

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
                        storing_udls(loc1=udl_x1_location, loc2=udl_x2_location, mag=udl_magnitude)
                else:
                    st.warning("Please provide valid values for loading and locations.")

            if remove_udls_but:
                # Check if lists are not empty before removing
                if st.session_state.udls_x1_locations_list and st.session_state.udls_x2_locations_list and st.session_state.udls_mag_list:
                    removing_udls(loc1=st.session_state.udls_x1_locations_list[-1],
                                  loc2=st.session_state.udls_x2_locations_list[-1],
                                  mag=st.session_state.udls_mag_list[-1])
                else:
                    st.warning("No Uniformly Distributed Loads (UDLs) available to remove.")

            with col1b:
                # Display DataFrame with Uniformly Distributed Loads (UDLs) stored  data
                if st.session_state.udls_x1_locations_list:
                    udls_dataframe = pd.DataFrame({
                        'Starting Location': st.session_state.udls_x1_locations_list,
                        'Ending Location': st.session_state.udls_x2_locations_list,
                        'Magnitude': st.session_state.udls_mag_list
                    })
                    st.dataframe(udls_dataframe, hide_index=True, width=200)

        # Variably Distributed Loads (UDLs) section
        with st.popover('Variably Distributed Loads (VDLs)', use_container_width=True):

            col1a, col1b = st.columns([1, 1], vertical_alignment='top')

            with col1a:
                # Inputs
                vdl_magnitude_1 = st.number_input('Starting Magnitude', value=None,
                                                  placeholder=units_dict_placeholder[unit_systems]['force'],
                                                  help='(+ve) is upwards & (-ve) is downwards', key='vdls1')
                vdl_magnitude_2 = st.number_input('Ending Magnitude', value=None,
                                                  placeholder=units_dict_placeholder[unit_systems]['force'],
                                                  help='(+ve) is upwards & (-ve) is downwards', key='vdls2')
                vdl_x1_location = st.number_input('Starting Location', min_value=0.00, value=None,
                                                  placeholder=units_dict_placeholder[unit_systems]['length'],
                                                  key='vdls3')
                vdl_x2_location = st.number_input('Ending Location', min_value=0.00, value=None,
                                                  placeholder=units_dict_placeholder[unit_systems]['length'],
                                                  key='vdls4')
                add_vdls_but = st.button('Add', type='primary', use_container_width=True, key='b9')
                remove_vdls_but = st.button('Undo', use_container_width=True, key='b10')

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
                        storing_vdls(loc1=vdl_x1_location, loc2=vdl_x2_location, mag1=vdl_magnitude_1,
                                     mag2=vdl_magnitude_2)
                else:
                    st.warning("Please provide valid values for loadings and locations.")

            if remove_vdls_but:
                # Check if lists are not empty before removing
                if st.session_state.vdls_x1_locations_list and st.session_state.vdls_x2_locations_list and st.session_state.vdls_mag1_list and st.session_state.vdls_mag2_list:
                    removing_vdls(loc1=st.session_state.vdls_x1_locations_list[-1],
                                  loc2=st.session_state.vdls_x2_locations_list[-1],
                                  mag1=st.session_state.vdls_mag1_list[-1], mag2=st.session_state.vdls_mag2_list[-1])
                else:
                    st.warning("No Variably Distributed Loads (VDLs) available to remove.")

            with col1b:
                # Display DataFrame with Variably Distributed Loads (VDLs) stored  data
                if st.session_state.vdls_x1_locations_list:
                    vdls_dataframe = pd.DataFrame({
                        'Start Loc.': st.session_state.vdls_x1_locations_list,
                        'End Loc.': st.session_state.vdls_x2_locations_list,
                        'Start Mag.': st.session_state.vdls_mag1_list,
                        'End Mag.': st.session_state.vdls_mag2_list
                    })
                    st.dataframe(vdls_dataframe, hide_index=True, width=200, use_container_width=True)

        # Clear everything button
        clear_button = st.button('Clear all', key='b11')
        if clear_button:
            clear_everything()

    with col3b:
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
        for loc1, loc2, mag in zip(st.session_state.udls_x1_locations_list, st.session_state.udls_x2_locations_list,
                                   st.session_state.udls_mag_list):
            load = UDLV(span=(loc1, loc2), force=mag)
            beam.add_loads(load)

        # Add all VDLs from the DataFrame to the beam
        for loc1, loc2, mag1, mag2 in zip(st.session_state.vdls_x1_locations_list,
                                          st.session_state.vdls_x2_locations_list,
                                          st.session_state.vdls_mag1_list, st.session_state.vdls_mag2_list):
            load = TrapezoidalLoadV(span=(loc1, loc2), force=(mag1, mag2))
            beam.add_loads(load)

        # st.write('\n')
        # st.write('\n')
        # # st.write('\n')
        # st.write('\n')

        # Beam schematic section
        fig = beam.plot_beam_diagram()
        st.plotly_chart(fig, theme=None, use_container_width=True)

    # ANALYSIS SECTION
    st.subheader(':blue-background[**Analysis**]', divider='rainbow')

    col1a, col1b = st.columns(2, gap='small', vertical_alignment='center')
    with col1a:

        with st.container(key='Analysis_cont', border=True):
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
        # st.write('### Additional Options')
        analysis_but = st.button('Analyze', type='primary')

    if analysis_but:
        try:
            # Solve the beam
            beam.analyse()

            if analysis_options == 'S.F.D & B.M.D':
                st.plotly_chart(figure_or_data=sfd_bmd_plot(),
                                theme=None)
                save_html_plot_with_button(figure=sfd_bmd_plot())
                result_without_deflection()
                create_table_without_deflection()
                st.toast('Analysis Successful!', icon=":material/check_circle:")

            else:
                if modulus_of_elasticity != '' and m_of_inertia != '':
                    st.plotly_chart(figure_or_data=sfd_bmd_deflection_plot(),
                                    theme=None,
                                    use_container_width=True)
                    save_html_plot_with_button(figure=sfd_bmd_deflection_plot())
                    result_with_deflection()
                    create_table_with_deflection()
                    st.toast('Analysis Successful!', icon=":material/check_circle:")
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

# ------------------------------CROSS SECTION TAB------------------------------
with tab2:
    # Dictionary for shape images
    shape_img_dict = {'Rectangular': "./assets/Rectangle.png",
                      'I-shape (symmetrical)': "./assets/I_shape_symmetrical.png",
                      'I-shape (unsymmetrical)': "./assets/I_shape_unsymmetrical.png",
                      'T-shape': "./assets/T_shape.png"}

    shape_select = st.selectbox('Shape',
                                options=['Rectangular', 'I-shape (symmetrical)', 'I-shape (unsymmetrical)', 'T-shape'])

    col1, col2 = st.columns(2, gap='small', vertical_alignment='top')

    # Display the calculation widgets w.r.t cross section shape
    with col1:
        st.write('\n')
        if shape_select == 'Rectangular':
            calc_for_rectangle_shape()
        elif shape_select == 'I-shape (symmetrical)':
            calc_for_I_symmetrical_shape()
        elif shape_select == 'I-shape (unsymmetrical)':
            calc_for_I_unsymmetrical_shape()
        elif shape_select == 'T-shape':
            calc_for_T_shape()

    with col2:
        switch_shape_img = st.toggle('Switch Figure',
                                     help='Changes the figure from reference image to created figure based on user inputs')
        if not switch_shape_img:
            # Display the image of shape w.r.t cross-section shape
            st.image(shape_img_dict[shape_select], caption='Reference Image of Shape')
        else:
            # Display created cross-section shape
            if created_shape_list:
                st.plotly_chart(figure_or_data=created_shape_list[0], use_container_width=True)
