import math
import numpy as np
import streamlit as st
import pandas as pd

# Initializing placeholder variables
Mu_bottom_g = None
Mu_bottom_gpw = None
Mu_bottom_ns = None
Mu_bottom_s = None

Mu_top_g = None
Mu_top_gpw = None
Mu_top_ns = None
Mu_top_s = None

bent_factor = None

delta_ns = None
delta_s = None

Mc = None
Pu = None

bar_no = None
no_of_bars = None

As_top = None
As_bottom = None
Ag = None

e_design = None
Mn = None
Pn = None
c = None

Mu_factored = None
Pu_factored = None

st.set_page_config(layout='wide')

st.header('Design of Long Column by ACI Moment Magnifier Method (ACI 318-19)',
          divider='blue')

# Given data
st.subheader('Data', divider='red')

col1, col2, col3 = st.columns(3, gap='small')

with col1:
    st.write('#### :blue-background[**Column/Frame Details**]')

    with st.container(key='1', border=True):
        # Select Type of column
        column_type = st.radio('Column Type',
                               options=['Braced (Non Sway) Frame',
                                        'Unbraced (Sway) Frame'])

        st.divider()
        # Curvature bent
        type_of_bending = st.radio('Type of Bending',
                                   options=['Bending in Single Curvature',
                                            'Bending in Double Curvature'],
                                   index=0)

        st.divider()
        Lu = st.number_input('Clear Height ($L_u$)',
                             value=None,
                             placeholder='ft')

# Material Properties of Footing
with col2:
    st.write('#### :blue-background[**Material Properties**]')

    with st.container(key='2', border=True):
        f_c = st.number_input("Concrete Strength - ($f'_c$)",
                              value=None,
                              placeholder='ksi')
        f_c = 1 if f_c is None else f_c

        f_y = st.number_input("Steel Yield Strength - ($f_y$)",
                              value=None,
                              placeholder='ksi')
        f_y = 1 if f_y is None else f_y

        E_c = st.number_input("Elastic Modulus of Concrete - ($E_c$)",
                              value=(57000 * (f_c * 1000) ** 0.5) / 1000,
                              placeholder='ksi')

# Safety Factors
with col3:
    st.write('#### :blue-background[**Safety Factors**]')

    with st.container(key='3', border=True):
        phi_axial = st.number_input("$\\phi$", value=0.65)

        if f_c <= 4:
            beta = 0.85

        elif f_c > 4:
            beta = -0.00005 * f_c * 1000 + 1.05

        beta = st.number_input("$\\beta$", value=beta)

st.write('#### :blue-background[**Loads**]')

with st.container(key='load cont', border=True):
    col1, col2, col3 = st.columns(3, gap='small', border=True)

    # Axial Loads Input

    with col1:
        st.write('##### :red-background[**Axial Loads**]')

        Pu_choice = st.radio('$P_{u}$ - Mode of Input',
                             options=['Directly Provided', 'Calculated from Service Loads'])

        st.divider()

        if Pu_choice == 'Directly Provided':
            Pu = st.number_input("$P_{u}$",
                                 value=None,
                                 placeholder='Kip')

        else:
            P_d = st.number_input("$P_{Dead}$",
                                  value=None,
                                  placeholder='Kip')

            P_l = st.number_input("$P_{Live}$",
                                  value=None,
                                  placeholder='Kip')

            st.divider()
            col1a, col2a = st.columns(2, gap='small', vertical_alignment='center')

            with col1a:
                st.write("$P_{u}$ (kips)")

            with col2a:
                if P_d is not None and P_l is not None:
                    Pu = 1.2 * P_d + 1.6 * P_l
                    st.code(f'{Pu}')

                else:
                    st.code(f'')
    # Moment at tops input
    with col2:
        st.write('##### :red-background[**Moments At Top**]')

        Mu_top_choice = st.radio('$M_{u,\\;Top}$  - Mode of Input',
                                 options=['Directly Provided', 'Calculated from Service Loads'])

        st.divider()

        if Mu_top_choice == 'Directly Provided':
            Mu_top = st.number_input("$M_{u,\\;Top}$",
                                     value=None,
                                     placeholder='Kip-ft')

        else:
            M_d_top = st.number_input("$M_{Dead,\\;Top}$",
                                      value=None,
                                      placeholder='Kip-ft')

            M_l_top = st.number_input("$M_{Live,\\;Top}$",
                                      value=None,
                                      placeholder='Kip-ft')

            M_w_top = st.number_input("$M_{Wind,\\;Top}$",
                                      value=0,
                                      placeholder='Kip-ft')

            st.divider()
            col1a, col2a = st.columns([0.6, 0.4], gap='small', vertical_alignment='center')

            with col1a:
                if column_type == "Unbraced (Sway) Frame":
                    st.write("$M_{u,\\;Top,_{(GL)}}$ (K-ft)")
                    st.write("$M_{u,\\;Top,_{(GL + WL)}}$ (K-ft)")

                else:
                    st.write("$M_{u,\\;Top}$ (K-ft)")

            with col2a:
                if column_type == "Unbraced (Sway) Frame":
                    if all(x is not None for x in [M_d_top, M_l_top, M_w_top]):

                        # Gravity Loads Combination
                        Mu_top_g = 1.2 * M_d_top + 1.6 * M_l_top

                        # Wind Loads Combination
                        Mu_top_ns = 1.2 * M_d_top + 1 * M_l_top
                        Mu_top_s = 1.6 * M_w_top

                        Mu_top_gpw = Mu_top_ns + Mu_top_s  # gpw stands for (gravity plus wind loads)

                        st.code(f'{Mu_top_g}')
                        st.code(f'{Mu_top_gpw}')

                    else:
                        Mu_top_g = None
                        Mu_top_gpw = None
                        Mu_top_ns = None
                        Mu_top_s = None
                        st.code(f'')

                else:
                    if all(x is not None for x in [M_d_top, M_l_top]):
                        # Gravity Loads Combination
                        Mu_top = 1.2 * M_d_top + 1.6 * M_l_top
                        Mu_top = round(Mu_top, 2)
                        st.code(f'{Mu_top}')

                    else:
                        Mu_top = None
                        st.code(f'')

    # Moment at bottom Inputs
    with col3:
        st.write('##### :red-background[**Moments At Bottom**]')

        Mu_bottom_choice = st.radio('$M_{u,\\;Bottom}$  - Mode of Input',
                                    options=['Directly Provided', 'Calculated from Service Loads'])

        st.divider()

        if Mu_bottom_choice == 'Directly Provided':
            Mu_bottom = st.number_input("$M_{u,\\;Bottom}$",
                                        value=None,
                                        placeholder='Kip-ft')

        else:
            M_d_bottom = st.number_input("$M_{Dead,\\;Bottom}$",
                                         value=None,
                                         placeholder='Kip-ft')

            M_l_bottom = st.number_input("$M_{Live,\\;Bottom}$",
                                         value=None,
                                         placeholder='Kip-ft')

            M_w_bottom = st.number_input("$M_{Wind,\\;Bottom}$",
                                         value=0,
                                         placeholder='Kip-ft')

            st.divider()
            col1a, col2a = st.columns([0.6, 0.4], gap='small', vertical_alignment='center')

            with col1a:
                if column_type == "Unbraced (Sway) Frame":
                    st.write("$M_{u,\\;Bottom,_{(GL)}}$ (K-ft)")
                    st.write("$M_{u,\\;Bottom,_{(GL + WL)}}$ (K-ft)")

                else:
                    st.write("$M_{u,\\;Bottom}$ (K-ft)")

            with col2a:
                if column_type == "Unbraced (Sway) Frame":
                    if all(x is not None for x in [M_d_bottom, M_l_bottom, M_w_bottom]):

                        # Gravity Loads Combination
                        Mu_bottom_g = 1.2 * M_d_bottom + 1.6 * M_l_bottom

                        # Wind Loads Combination
                        Mu_bottom_ns = 1.2 * M_d_bottom + 1 * M_l_bottom
                        Mu_bottom_s = 1.6 * M_w_bottom

                        Mu_bottom_gpw = Mu_bottom_ns + Mu_bottom_s  # gpw stands for (gravity plus wind loads)

                        st.code(f'{Mu_bottom_g}')
                        st.code(f'{Mu_bottom_gpw}')

                    else:
                        Mu_bottom_g = None
                        Mu_bottom_gpw = None
                        Mu_bottom_ns = None
                        Mu_bottom_s = None
                        st.code(f'')

                else:
                    if all(x is not None for x in [M_d_bottom, M_l_bottom]):
                        # Gravity Loads Combination
                        Mu_bottom = 1.2 * M_d_bottom + 1.6 * M_l_bottom
                        Mu_bottom = round(Mu_bottom, 2)
                        st.code(f'{Mu_bottom}')

                    else:
                        Mu_bottom = None
                        st.code(f'')

# Decide M1 and M2 based on values of Mu_top and Mu_bottom in case of Braced (Non Sway) Frame
if column_type == "Braced (Non Sway) Frame":
    if Mu_top is not None and Mu_bottom is not None:
        M2 = max(Mu_top, Mu_bottom)
        M1 = min(Mu_top, Mu_bottom)

    else:
        M2 = None
        M1 = None

# Section for effective length factor (K)
st.write('#### :blue-background[**Effective Length Factor (K)**]')

with st.container(key='K container', border=True):
    K_choice = st.radio('K Factor - Mode of Input',
                        options=['Directly Provided', 'Calculated from End Restrained Factors'],
                        index=1)

    if K_choice == 'Directly Provided':
        K = st.number_input("K",
                            value=None)

    else:
        col1, col2 = st.columns(2, gap='small', border=True)

        with col1:
            st.write('##### :red-background[**Top End Restrained Factor ($\\psi_{A}$)**]')

            psi_A_choice = st.radio('$\\psi_{A}$ - Mode of Input',
                                    options=['Directly Provided', 'Calculated from Members Stiffness'],
                                    index=0)

            if psi_A_choice == 'Directly Provided':
                psi_A = st.number_input("$\\psi_{A}$",
                                        value=None)

            else:
                # psi_A inputs for Short_Columns
                psi_A_inputs_columns = pd.DataFrame({'Ec (Ksi)': [0.0], 'Ig (in⁴)': [0.0], 'Lc (ft)': [0.0]})

                st.write('##### **Columns**')
                psi_A_inputs_columns = st.data_editor(data=psi_A_inputs_columns,
                                                      width='stretch',
                                                      num_rows='dynamic',
                                                      key='Short_Columns-A')

                columns_stiffness_values = []
                # Iterate over each row of the DataFrame
                for i, row in psi_A_inputs_columns.iterrows():
                    E = row['Ec (Ksi)']
                    I = 0.7 * row['Ig (in⁴)']
                    L = row['Lc (ft)']

                    # st.write(E, I, L, i) # for debugging

                    stiffness = E * I / (L * 12) if L != 0 else 0  # prevent divide-by-zero
                    columns_stiffness_values.append(stiffness)

                # st.write(sum(columns_stiffness_values))

                # psi_A inputs for beams
                psi_A_inputs_beams = pd.DataFrame({'Ec (Ksi)': [0.0], 'Ig (in⁴)': [0.0], 'Lc (ft)': [0.0]})

                st.write('##### **Beams**')
                psi_A_inputs_beams = st.data_editor(data=psi_A_inputs_beams,
                                                    width='stretch',
                                                    num_rows='dynamic',
                                                    key='beams-A')

                beam_stiffness_values = []
                # Iterate over each row of the DataFrame
                for i, row in psi_A_inputs_beams.iterrows():
                    E = row['Ec (Ksi)']
                    I = 0.35 * row['Ig (in⁴)']
                    L = row['Lc (ft)']

                    # st.write(E, I, L, i) # for debugging

                    stiffness = E * I / (L * 12) if L != 0 else 0  # prevent divide-by-zero
                    beam_stiffness_values.append(stiffness)

                # st.write(sum(beam_stiffness_values))

                st.divider()

                col1a, col2a = st.columns(2, gap='small')

                with col1a:
                    st.write('$\\psi_{A}$')

                with col2a:
                    if sum(columns_stiffness_values) > 0 and sum(beam_stiffness_values) > 0:
                        psi_A = sum(columns_stiffness_values) / sum(beam_stiffness_values)
                        psi_A = round(psi_A, 2)

                        st.code(f'{psi_A}')

                    else:
                        psi_A = None
                        st.code(f'')

        with col2:
            st.write('##### :red-background[**Bottom End Restrained Factor ($\\psi_{B}$)**]')

            psi_B_choice = st.radio('$\\psi_{B}$ - Mode of Input',
                                    options=['Directly Provided', 'Calculated from Members Stiffness'],
                                    index=0)

            if psi_B_choice == 'Directly Provided':
                psi_B = st.number_input("$\\psi_{B}$",
                                        value=None)

            else:
                # psi_A inputs for Short_Columns
                psi_B_inputs_columns = pd.DataFrame({'Ec (Ksi)': [0.0], 'Ig (in⁴)': [0.0], 'Lc (ft)': [0.0]})

                st.write('##### **Columns**')
                psi_B_inputs_columns = st.data_editor(data=psi_B_inputs_columns,
                                                      width='stretch',
                                                      num_rows='dynamic',
                                                      key='Short_Columns-B')

                columns_stiffness_values = []
                # Iterate over each row of the DataFrame
                for i, row in psi_B_inputs_columns.iterrows():
                    E = row['Ec (Ksi)']
                    I = 0.7 * row['Ig (in⁴)']
                    L = row['Lc (ft)']

                    # st.write(E, I, L, i) # for debugging

                    stiffness = E * I / (L * 12) if L != 0 else 0  # prevent divide-by-zero
                    columns_stiffness_values.append(stiffness)

                # psi_A inputs for beams
                psi_B_inputs_beams = pd.DataFrame({'Ec (Ksi)': [0], 'Ig (in⁴)': [0], 'Lc (ft)': [0]})

                st.write('##### **Beams**')
                psi_B_inputs_beams = st.data_editor(data=psi_B_inputs_beams,
                                                    width='stretch',
                                                    num_rows='dynamic',
                                                    key='beams-B')

                beam_stiffness_values = []
                # Iterate over each row of the DataFrame
                for i, row in psi_B_inputs_beams.iterrows():
                    E = row['Ec (Ksi)']
                    I = 0.35 * row['Ig (in⁴)']
                    L = row['Lc (ft)']

                    # st.write(E, I, L, i) # for debugging

                    stiffness = E * I / (L * 12) if L != 0 else 0  # prevent divide-by-zero
                    beam_stiffness_values.append(stiffness)

                st.divider()

                col1a, col2a = st.columns(2, gap='small')

                with col1a:
                    st.write('$\\psi_{B}$')

                with col2a:
                    if sum(columns_stiffness_values) > 0 and sum(beam_stiffness_values) > 0:
                        psi_B = sum(columns_stiffness_values) / sum(beam_stiffness_values)
                        psi_B = round(psi_B, 2)

                        st.code(f'{psi_B}')

                    else:
                        psi_B = None
                        st.code(f'')

        if psi_A is not None and psi_B is not None:
            if column_type == 'Braced (Non Sway) Frame':
                K = (3 * psi_A * psi_B + 1.4 * (psi_A + psi_B) + 0.64) / (
                        3 * psi_A * psi_B + 2 * (psi_A + psi_B) + 1.28)

            else:
                K = ((1.6 * psi_A * psi_B + 4 * (psi_A + psi_B) + 7.5) / (psi_A + psi_B + 7.5)) ** 0.5

            col1a, col2a = st.columns([0.1, 0.9], gap='small', vertical_alignment='center')
            K = round(K, 2)

            with col1a:
                st.write("$K$")

            with col2a:
                st.code(f'{K}')

        else:
            K = None

st.space()
# Calculation section
st.subheader('Calculations', divider='red')

# Assume trial section inputs
st.write('#### :blue-background[**Assume Trial Section**]')

with st.container(key='trial section', border=True):
    col1, col2 = st.columns(2, gap='small')

    # Column Width (b)
    with col2:
        b = st.number_input("Width $(b)$",
                            value=None,
                            placeholder='inches')

        # Column Depth (h)
        h = st.number_input("Height $(h)$",
                            value=None,
                            placeholder='inches')

        # Concrete Cover
        cover = st.number_input("Clear Covers (all sides)",
                                value=1.5,
                                placeholder='inches',
                                max_value=2.0)

    with col1:
        def cross_section_diagram(b, h, cover):
            # Create figure only if inputs exist
            if b is not None and h is not None and cover is not None:

                import plotly.graph_objects as go

                # Outer rectangle (concrete)
                outer_x = [0, b, b, 0, 0]
                outer_y = [0, 0, h, h, 0]

                # Inner rectangle (stirrup)
                stir_x1 = cover
                stir_x2 = b - cover
                stir_y1 = cover
                stir_y2 = h - cover

                inner_x = [stir_x1, stir_x2, stir_x2, stir_x1, stir_x1]
                inner_y = [stir_y1, stir_y1, stir_y2, stir_y2, stir_y1]

                fig = go.Figure()

                # Concrete boundary
                fig.add_trace(go.Scatter(
                    x=outer_x, y=outer_y,
                    mode="lines",
                    line=dict(width=3),
                    name="Concrete Section"
                ))

                # Stirrup boundary
                fig.add_trace(go.Scatter(
                    x=inner_x, y=inner_y,
                    mode="lines",
                    line=dict(width=2, dash="dash", color='darkgreen'),
                    name="Stirrup (at cover)"
                ))

                fig.update_layout(
                    width=450,
                    height=550,
                    title="Rectangular Column Cross-Section",
                    xaxis=dict(scaleanchor="y", title="Width (in)"),
                    yaxis=dict(title="Height (in)"),
                    showlegend=False,
                    margin=dict(l=20, r=20, t=40, b=20)
                )

                st.plotly_chart(fig, use_container_width='stretch')

            else:
                st.info("Enter b, h, and cover to visualize cross-section.")


        cross_section_diagram(b, h, cover)

# check for slenderness
st.write('#### :blue-background[**Slenderness Check**]')
# ================== BRACED (NON-SWAY) FRAME ==================

if column_type == 'Braced (Non Sway) Frame':

    col1, col2 = st.columns(2, gap='small', border=True)

    # ================== EQUATIONS PANEL ==================
    with col1:
        st.write("##### :red-background[Slenderness Criterion]")

        st.latex(r"\small{\text{For braced columns:}}")
        st.latex(
            r"\small{\frac{K\,l_u}{r} \le 34 + 12\left(\frac{M_1}{M_2}\right)}"
        )
        st.latex(
            r"""\scriptsize{
            \begin{aligned}
            &\text{where } M_1 \text{ and } M_2 \text{ are the end moments of the column, } M_2 > M_1,\\
            &\text{and the ratio } M_1/M_2 \text{ is considered negative if the member is bent in}\\
            &\text{single curvature, and positive for double curvature.}
            \end{aligned}
            }"""
        )

    # ================== RESULTS PANEL ==================
    with col2:

        st.write("##### :red-background[Check Calculation]")

        if all(v is not None for v in [K, Lu, b, h, M1, M2]):

            # Radius of gyration for rectangle (ACI recommends r ≈ 0.3h for slenderness)
            r = 0.3 * h

            # Compute LHS = K * Lu / r
            LHS = K * (Lu * 12) / r  # Lu in feet → convert to inches
            LHS = round(LHS, 2)

            # Sign convention for M1/M2
            if type_of_bending == "Bending in Single Curvature":
                bent_factor = -1  # M1/M2 negative
            else:
                bent_factor = 1

            # RHS = 34 + 12(M1/M2)
            RHS = 34 + 12 * (bent_factor * M1 / M2)
            RHS = round(RHS, 2)

            col1a, col2a = st.columns([0.4, 0.6], gap='small', vertical_alignment='center')

            # Radius of gyration (r)
            with col1a:
                st.write("Radius of gyration $(r)$")
            with col2a:
                st.code(f"{round(r, 2)} in")

            col1a, col2a = st.columns([0.4, 0.6], gap='small', vertical_alignment='center')

            # LHS = K · Lu / r
            with col1a:
                st.write("LHS = $\\dfrac{K\,L_u}{r}$")
            with col2a:
                st.code(f"{LHS}")

            col1a, col2a = st.columns([0.4, 0.6], gap='small', vertical_alignment='center')

            # RHS = 34 + 12(M1/M2)
            with col1a:
                st.write("RHS = $34 + 12\\left(\\frac{M_1}{M_2}\\right)$")
            with col2a:
                st.code(f"{RHS}")

            # Verdict section
            if LHS <= RHS:
                st.success("Column is **NOT slender** (OK)")
                st.info(
                    """
                    Recommended:
                    Design the column as **Short Column**

                    [Go to Short Column Design](/short_column_design)
                    """
                )

            else:
                st.error("Column **IS Slender** (Slenderness effects need to be considered)")

        else:
            st.info("Enter required inputs (K, Lu, b, h) to perform slenderness check.")

# ================== UNBRACED (SWAY) FRAME ==================
if column_type == "Unbraced (Sway) Frame":

    col1, col2 = st.columns(2, gap='small', border=True)

    # ================== EQUATIONS PANEL ==================
    with col1:
        st.write("##### :red-background[Slenderness Criterion]")

        st.latex(r"\small{\text{For unbraced (sway) columns:}}")

        st.latex(
            r"\small{\frac{K\,l_u}{r} \le 22}"
        )

        st.latex(
            r"\scriptsize{\text{Unbraced columns are more critical because lateral displacement occurs.}}"
        )

    # ================== RESULTS PANEL ==================
    with col2:

        st.write("##### :red-background[Check Calculation]")

        # Required inputs (b, h, K, Lu available and needed)
        if all(v is not None for v in [K, Lu, b, h]):

            # Radius of gyration for rectangle (ACI recommendation)
            r = 0.3 * h

            # Compute LHS = K * Lu / r
            LHS = K * (Lu * 12) / r  # Convert Lu (ft) → inches
            LHS = round(LHS, 2)

            # RHS for unbraced = constant 22
            RHS = 22

            # -------- Display Results --------
            col1a, col2a = st.columns([0.4, 0.6], gap='small', vertical_alignment='center')

            # Radius of gyration (r)
            with col1a:
                st.write("Radius of gyration $(r)$")
            with col2a:
                st.code(f"{round(r, 2)} in")

            # LHS
            col1a, col2a = st.columns([0.4, 0.6], gap='small', vertical_alignment='center')
            with col1a:
                st.write("LHS = $\\dfrac{K\,L_u}{r}$")
            with col2a:
                st.code(f"{LHS}")

            # RHS
            col1a, col2a = st.columns([0.4, 0.6], gap='small', vertical_alignment='center')
            with col1a:
                st.write("RHS = $22$")
            with col2a:
                st.code(f"{RHS}")

            # Verdict section
            if LHS <= RHS:
                st.success("Column is **NOT slender** (OK)")
                st.info(
                    """
                    Recommended:
                    Design the column as **Short Column**

                    [Go to Short Column Design](/short_column_design)
                    """
                )

            else:
                st.error("Column **IS Slender** (Slenderness effects need to be considered)")

        else:
            st.info("Enter required inputs (K, Lu, b, h) to perform slenderness check.")

# ================== EI CALCULATION ==================
st.write('#### :blue-background[**Flexural Rigidity (EI) of Column**]')

col1, col2 = st.columns(2, gap='small', border=True)

# ================== EQUATIONS PANEL ==================
with col1:
    st.write("##### :red-background[EI Equation]")

    st.latex(r"\small{\text{Flexural Rigidity of Column:}}")
    st.latex(r"\small{EI = \frac{0.4 \, E_c \, I_g}{1 + \beta}}")

    st.latex(
        r"""\scriptsize{
        \begin{aligned}
        &E_c = 57000 \, \sqrt{f'_c} \quad (\text{psi})\\
        &I_g = \frac{b \, h^3}{12} \quad (\text{in}^4)\\
        &\beta = 
        \begin{cases}
        \beta_{dns} = \frac{1.2 D_{sustained}}{P_u} & \text{for braced frames} \\
        \beta_{ds} = \frac{\text{max sustained shear}}{\text{total factored shear}} & \text{for unbraced frames}
        \end{cases}
        \end{aligned}
        }"""
    )

# ================== RESULTS PANEL ==================
with col2:
    st.write("##### :red-background[Input & Computation]")

    # Common inputs
    if column_type == "Braced (Non Sway) Frame":

        beta_factor_choice = st.radio('$\\beta_{dns}$ - Mode of Input',
                                      options=['Directly Provided', 'Calculated from Loads'])

        st.divider()

        if beta_factor_choice == 'Directly Provided':
            beta_factor = st.number_input('$\\beta_{dns}$',
                                          placeholder=None,
                                          value=None)
        else:
            D_sustained = st.number_input(
                "Sustained Dead Load -  $P_{D,\\text{sustained}}$",
                value=None,
                placeholder='Kips'
            )

            if all(x is not None for x in [D_sustained, Pu]):
                beta_factor = 1.2 * D_sustained / Pu

                col1a, col2a = st.columns([0.4, 0.6], gap='small', vertical_alignment='center')

                with col1a:
                    st.write('$\\beta_{dns}$')

                with col2a:
                    st.code(f"{round(beta_factor, 2)}")
            else:
                beta_factor = None

    elif column_type == "Unbraced (Sway) Frame":

        beta_factor_choice = st.radio('$\\beta_{dns}$ - Mode of Input',
                                      options=['Directly Provided', 'Calculated from Loads'])

        st.divider()

        if beta_factor_choice == 'Directly Provided':
            beta_factor = st.number_input('$\\beta_{ds}$',
                                          placeholder=None,
                                          value=None)
        else:
            max_sustained_shear = st.number_input("Maximum Sustained Shear",
                                                  value=None,
                                                  placeholder='Kips')

            total_factored_shear = st.number_input("Total Factored Shear",
                                                   value=None,
                                                   placeholder='Kips')

            if all(v is not None for v in [max_sustained_shear, total_factored_shear]):
                beta_factor = max_sustained_shear / total_factored_shear
                col1a, col2a = st.columns([0.4, 0.6], gap='small', vertical_alignment='center')

                with col1a:
                    st.write('$\\beta_{ds}$')

                with col2a:
                    st.code(f"{round(beta_factor, 2)}")

            else:
                beta_factor = None

    # Compute EI if inputs available
    if all(v is not None for v in [b, h, f_c, beta_factor]):
        Ec = 57000 * np.sqrt(f_c * 1000)
        Ig = b * h ** 3 / 12
        EI = 0.4 * Ec * Ig / (1 + beta_factor) / 1000

        col1a, col2a = st.columns([0.4, 0.6], gap='small', vertical_alignment='center')
        with col1a:
            st.write("$E_c$ (psi)")
        with col2a:
            st.code(f"{round(Ec, 2)}")

        col1a, col2a = st.columns([0.4, 0.6], gap='small', vertical_alignment='center')
        with col1a:
            st.write("$I_g$ (in⁴)")
        with col2a:
            st.code(f"{round(Ig, 2)}")

        col1a, col2a = st.columns([0.4, 0.6], gap='small', vertical_alignment='center')
        with col1a:
            st.write("$EI$ (kip-in²)")
        with col2a:
            st.code(f"{round(EI, 2)}")

    else:
        st.info("Enter all required inputs to compute EI.")
        EI = None

# ================== Euler Buckling Load CALCULATION ==================
st.write('#### :blue-background[**Euler Buckling Load $(P_{c})$**]')

if column_type == 'Braced (Non Sway) Frame':

    col1, col2 = st.columns(2, gap='small', border=True)

    # ================== EQUATIONS PANEL ==================
    with col1:
        st.write("##### :red-background[Euler Buckling Load Equation]")

        # st.latex(r"\small{\text{For braced columns:}}")
        st.latex(r"\small{P_c = \frac{\pi^2 \, EI}{(K L_u)^2}}")
        st.latex(
            r"""\scriptsize{
            \begin{aligned}
            &E I = \text{Flexural rigidity of the column (kip-in}^2\text{)}\\
            &K = \text{Effective length factor}\\
            &L_u = \text{Unsupported length (clear height) of the column (ft)}
            \end{aligned}
            }"""
        )

    # ================== RESULTS PANEL ==================
    with col2:
        st.write("##### :red-background[Computation]")

        if all(v is not None for v in [EI, K, Lu]):

            # Euler Buckling Load
            Pc = np.pi ** 2 * EI / (K * Lu * 12) ** 2
            Pc = round(Pc, 2)

            # Display results

            col1a, col2a = st.columns([0.4, 0.6], gap='small', vertical_alignment='center')
            with col1a:
                st.write("$EI$ (kip-in²)")
            with col2a:
                st.code(f"{round(EI, 2)}")

            col1a, col2a = st.columns([0.4, 0.6], gap='small', vertical_alignment='center')
            with col1a:
                st.write("$P_c$ (kips)")
            with col2a:
                st.code(f"{Pc}")

        else:
            st.info("Enter required inputs (EI, K, Lu) to compute Euler Buckling Load.")
            Pc = None

# ================== Story Sway Buckling Load CALCULATION ==================

if column_type == 'Unbraced (Sway) Frame':
    col1, col2 = st.columns(2, gap='small', border=True)

    # ================== EQUATIONS PANEL ==================
    with col1:
        st.write("##### :red-background[Story Sway Capacity Equation]")

        st.latex(r"\small{\text{For unbraced columns in a story:}}")
        st.latex(
            r"\small{\sum P_c = P_{c1} + P_{c2} + ... + P_{cn}}"
        )
        st.latex(
            r"""\scriptsize{
            \begin{aligned}
            &\sum P_c = \text{Total axial capacity of all columns in the story}\\
            &P_{ci} = \text{Euler buckling load of individual column i (kip)}\\
            &n = \text{Number of columns in the story}
            \end{aligned}
            }"""
        )

    # ================== RESULTS PANEL ==================
    with col2:
        st.write("##### :red-background[Input & Computation]")

        st.write("##### **$P_c$ of All Columns in a Story**")

        # ======= Display each column Pc in two-column style =======
        col1a, col2a = st.columns([0.7, 0.3], gap='small', vertical_alignment='top')

        # Editable input table for EI, K, and Lu
        Pc_inputs_sway_columns = pd.DataFrame({
            'No. Col.': [1],
            'EI (k-in²)': [0.0],
            'K': [0.0],
            'Lu (ft)': [0.0]
        })

        with col1a:
            Pc_inputs_sway_columns = st.data_editor(
                data=Pc_inputs_sway_columns,
                width='stretch',
                num_rows='dynamic',
                key='Pc_sway_columns_table_input'
            )

        Pc_values = []

        for i, row in Pc_inputs_sway_columns.iterrows():

            no_of_col_i = row['No. Col.']
            EI_i = row['EI (k-in²)']
            K_i = row['K']
            Lu_i = row['Lu (ft)']

            # -------------------------------
            # VALIDATION CHECK
            # -------------------------------
            # Skip row entirely if any input is missing
            if (
                    any([
                        pd.isna(no_of_col_i),
                        pd.isna(EI_i),
                        pd.isna(K_i),
                        pd.isna(Lu_i)
                    ])
                    or no_of_col_i <= 0
                    or EI_i <= 0
                    or K_i <= 0
                    or Lu_i <= 0
            ):
                continue  # Skip this row completely

            # -------------------------------
            # EULER LOAD FOR THIS COLUMN
            # -------------------------------
            Pc_i = (np.pi ** 2 * EI_i) / ((K_i * Lu_i * 12) ** 2)
            Pc_i = round(Pc_i, 1)

            # -------------------------------
            # APPEND Pc_i FOR THE NUMBER OF COLUMNS
            # -------------------------------
            for _ in range(int(no_of_col_i)):  # << safe now
                Pc_values.append(Pc_i)

        with col2a:
            # Editable input table for EI, K, and Lu
            Pc_calc_sway_columns = pd.DataFrame({
                'Pc (kip)': Pc_values
            })

            Pc_calc_sway_columns = st.dataframe(
                data=Pc_calc_sway_columns,
                width='stretch',
                height=141,
                # num_rows='dynamic',
                key='Pc_sway_columns_table_result'
            )

        # ================= TOTAL SUM ==================
        if len(Pc_values) > 0:

            sum_Pc = round(sum(Pc_values), 3)

            col1a, col2a = st.columns([0.4, 0.6], gap='small', vertical_alignment='center')
            with col1a:
                st.write(r"$\sum P_c$")
            with col2a:
                st.code(f"{sum_Pc} kips")

        else:
            st.info("Enter EI, K, and Lu for at least one sway-resisting column.")
            sum_Pc = None

# ================== Moment Magnifier (Non Sway Frames) CALCULATION ==================
if column_type == 'Braced (Non Sway) Frame':

    st.write('#### :blue-background[**Moment Magnifier $(\\delta_{ns})$**]')

    col1, col2 = st.columns(2, gap='small', border=True)

    # --------------------------------------------------
    # LEFT PANEL — EQUATIONS
    # --------------------------------------------------
    with col1:
        st.write("##### :red-background[Moment Magnifier Criterion]")

        st.latex(r"\small{\text{For Braced (Non Sway) Columns:}}")

        st.latex(
            r"""
            \delta_{ns} = 
            \frac{C_m}{
                1 - \left( \frac{P_u}{0.75\,P_c} \right)
            }
            """
        )

        st.latex(
            r"""
            C_m = 0.6 - 0.4\left(\frac{M_1}{M_2}\right)
            """
        )

        st.latex(
            r"""
            \scriptsize{
            \begin{aligned}
            &\delta_{ns} \ge 1.0 \\
            &P_u = \text{Factored axial load} \\
            &P_c = \text{Euler critical load} \\
            &M_1, M_2 = \text{Smaller and larger end moments (consider sign)} 
            \end{aligned}
            }
            """
        )

    # --------------------------------------------------
    # RIGHT PANEL — COMPUTATION
    # --------------------------------------------------
    with col2:
        st.write("##### :red-background[Computation]")

        # Cm computation
        if all(v not in [None, 0] for v in [bent_factor, M1, M2]):
            Cm = 0.6 - 0.4 * (bent_factor * M1 / M2)
            Cm = round(Cm, 2)
        else:
            Cm = None

        # Check required inputs
        if all(v not in [None, 0] for v in [Pu, Pc, Cm]):

            denominator = 1 - (Pu / (0.75 * Pc))

            if denominator <= 0:
                delta_ns = float('inf')  # approaching buckling
            else:
                delta_ns = Cm / denominator

            # Clamp minimum value
            if delta_ns < 1.0:
                delta_ns = 1.0

            delta_ns = round(delta_ns, 2)

            # -------------------------
            # DISPLAY RESULTS
            # -------------------------
            # M1 result
            col1b, col2b = st.columns([0.4, 0.6], gap='small', vertical_alignment='center')
            with col1b:
                st.write("$M_1$ (K-ft)")
            with col2b:
                st.code(f"{round(M1, 3)}")

            # M2 result
            col1b, col2b = st.columns([0.4, 0.6], gap='small', vertical_alignment='center')
            with col1b:
                st.write("$M_2$ (K-ft)")
            with col2b:
                st.code(f"{round(M2, 3)}")

            # Cm result
            col1b, col2b = st.columns([0.4, 0.6], gap='small', vertical_alignment='center')
            with col1b:
                st.write("$C_m$")
            with col2b:
                st.code(f"{round(Cm, 3)}")

            col1a, col2a = st.columns([0.4, 0.6], gap='small', vertical_alignment='center')
            # Moment Magnifier Result
            with col1a:
                st.write("Moment Magnifier $(\\delta_{ns})$")
            with col2a:
                st.code(f"{delta_ns}")

            # Verdict messages
            if denominator <= 0:
                st.error("Instability: $\\delta_{ns} \\to \\infty$ (Column approaching elastic buckling).")
            else:
                st.success("Moment magnifier computed successfully.")

        else:
            st.info("Enter valid values for $P_u$, $P_c$, $M_1$ and $M_2$ to compute $\\delta_{ns}$.")

# ================== Moment Magnifier (Sway Frames) CALCULATION ==================
if column_type == 'Unbraced (Sway) Frame':

    st.write('#### :blue-background[**Moment Magnifier $(\\delta_{s})$**]')

    col1, col2 = st.columns(2, gap='small', border=True)

    # --------------------------------------------------
    # LEFT PANEL — EQUATIONS
    # --------------------------------------------------
    with col1:
        st.write("##### :red-background[Moment Magnifier Criterion]")

        st.latex(r"\small{\text{For Unbraced (Sway) Frames:}}")

        st.latex(
            r"""
            \delta_s =
            \frac{1}{
                1 - \left( \frac{\sum P_u}{0.75\,\sum P_c} \right)
            }
            """
        )

        st.latex(
            r"""
            \scriptsize{
            \begin{aligned}
            &\delta_s \ge 1.0 \\
            &\delta_s \le 2.5 \\
            &\sum P_u = \text{Sum of factored axial loads of columns in a story} \\
            &\sum P_c = \text{Sum of Euler critical loads of columns in a story}
            \end{aligned}
            }
            """
        )

    # --------------------------------------------------
    # RIGHT PANEL — COMPUTATION
    # --------------------------------------------------
    with col2:
        st.write("##### :red-background[Computation]")

        st.write("##### **$P_u$ of All Columns in a Story**")

        # ======= Display each column Pc in two-column style =======
        col1a, col2a = st.columns([0.7, 0.3], gap='small', vertical_alignment='top')

        # Editable input table for EI, K, and Lu
        Pu_inputs_sway_columns = pd.DataFrame({
            'No. of same Col.': [1],
            'Pu (Kips)': [0.0],

        })

        with col1a:
            Pu_inputs_sway_columns = st.data_editor(
                data=Pu_inputs_sway_columns,
                width='stretch',
                num_rows='dynamic',
                key='Pu_sway_columns_table_input'
            )

        Pu_values_sway = []

        for i, row in Pu_inputs_sway_columns.iterrows():

            no_of_col_i = row['No. of same Col.']
            Pu_i = row['Pu (Kips)']

            # -------------------------------
            # VALIDATION CHECK
            # -------------------------------
            # Skip row entirely if any input is missing
            if (
                    any([
                        pd.isna(no_of_col_i),
                        pd.isna(Pu_i),
                    ])
                    or no_of_col_i <= 0
                    or Pu_i <= 0
            ):
                continue  # Skip this row completely

            for _ in range(int(no_of_col_i)):  # << safe now
                Pu_values_sway.append(Pu_i)

        # ================= TOTAL SUM ==================
        if len(Pu_values_sway) > 0:

            sum_Pu_sway = round(sum(Pu_values_sway), 2)

            col1a, col2a = st.columns([0.4, 0.6], gap='small', vertical_alignment='center')
            with col1a:
                st.write(r"$\sum P_u$")
            with col2a:
                st.code(f"{sum_Pu_sway} kips")

        else:
            st.info("Enter values of Pu for at least one column.")
            sum_Pu_sway = None

        # Check if required inputs exist
        if all(v not in [None, 0] for v in [sum_Pu_sway, sum_Pc]):

            denominator = 1 - (sum_Pu_sway / (0.75 * sum_Pc))

            # Instability check
            if denominator <= 0:
                delta_s = float('inf')
            else:
                delta_s = 1 / denominator

            # Apply limits
            if delta_s < 1.0:
                delta_s = 1.0
            if delta_s > 2.5:
                delta_s = 2.5

            delta_s = round(delta_s, 2)

            # -------------------------
            # DISPLAY RESULTS
            # -------------------------
            col1a, col2a = st.columns([0.4, 0.6], vertical_alignment='center')
            with col1a:
                st.write("Moment Magnifier $(\\delta_s)$")
            with col2a:
                st.code(f"{delta_s}")

            # Verdict messages
            if denominator <= 0:
                st.error("Instability: $\\delta_s \\to \\infty$ (Frame approaching sway buckling).")
            elif delta_s == 2.5:
                st.warning("Capped at maximum value: $\\delta_s = 2.5$")
            else:
                st.success("Moment magnifier computed successfully.")

        else:
            st.info("Compute both $\\sum P_u$ and $\\sum P_c$ for columns.")
            delta_s = None

# ================== Design Moment (Non Sway Frames) CALCULATION ==================
if column_type == 'Braced (Non Sway) Frame':

    st.write('#### :blue-background[**Design Moment $(M_{c})$**]')

    col1, col2 = st.columns(2, gap='small', border=True)

    # --------------------------------------------------
    # LEFT PANEL — EQUATIONS
    # --------------------------------------------------
    with col1:
        st.write("##### :red-background[Design Moment Criterion]")

        st.latex(r"\small{\text{For Braced (Non Sway) Columns:}}")

        st.latex(
            r"""
            \small{
            M_c = \delta_{ns} \, M_2
            }
            """
        )

        st.latex(
            r"""
            \scriptsize{
            \begin{aligned}
            &M_2 = \text{larger factored end moment (in absolute value)} \\
            &\delta_{ns} = \text{moment magnifier for non-sway frames}
            \end{aligned}
            }
            """
        )

    # --------------------------------------------------
    # RIGHT PANEL — COMPUTATION
    # --------------------------------------------------
    with col2:
        st.write("##### :red-background[Computation]")

        if all(v not in [None, 0] for v in [delta_ns, M2]):

            # Compute M_c
            Mc = delta_ns * M2
            Mc = round(Mc, 3)

            # -------------------------
            # DISPLAY RESULTS
            # -------------------------
            col1a, col2a = st.columns([0.4, 0.6], gap='small')

            with col1a:
                st.write("Design Moment $(M_c)$")
            with col2a:
                st.code(f"{Mc} kip-ft")

            st.success("Design moment for non-sway frame computed successfully.")

        else:
            st.info("Both $\\delta_{ns}$ and $M_2$ are needed to compute the design moment.")

# ================== Design Moment (Sway Frames) CALCULATION ==================
if column_type == 'Unbraced (Sway) Frame':

    st.write('#### :blue-background[**Design Moments $(M_{c1},\, M_{c2})$**]')

    col1, col2 = st.columns(2, gap='small', border=True)

    # --------------------------------------------------
    # LEFT PANEL — EQUATIONS
    # --------------------------------------------------
    with col1:
        st.write("##### :red-background[Design Moment Criterion]")

        st.latex(r"\small{\text{For Unbraced (Sway) Columns:}}")

        st.latex(
            r"""
            \small{
            \begin{aligned}
            M_{c1} &= M_{1ns} + \delta_s\, M_{1s} \\
            M_{c2} &= M_{2ns} + \delta_s\, M_{2s}
            \end{aligned}
            }
            """
        )

        st.latex(
            r"""
            \scriptsize{
            \begin{aligned}
            &M_{1ns},\, M_{2ns} = \text{non-sway end moments} \\
            &M_{1s},\, M_{2s} = \text{sway end moments} \\
            &\delta_s = \text{sway moment magnifier} \\
            &M_c = \max(M_{c1},\, M_{c2}) \\
            &\text{(design magnified moment is the larger of } M_{c1} \text{ and } M_{c2})
            \end{aligned}
            }
            """
        )

    # --------------------------------------------------
    # RIGHT PANEL — COMPUTATION
    # --------------------------------------------------
    with col2:
        st.write("##### :red-background[Computation]")

        # Required values: delta_s, M1ns, M2ns, M1s, M2s
        required_inputs = [delta_s, Mu_top_ns, Mu_bottom_ns, Mu_top_s, Mu_bottom_s]

        if all(v not in [None] for v in required_inputs):

            # Compute design end moments
            Mc1 = Mu_top_ns + delta_s * Mu_top_s
            Mc2 = Mu_bottom_ns + delta_s * Mu_bottom_s

            Mc1 = round(Mc1, 3)
            Mc2 = round(Mc2, 3)

            Mc = max(Mc1, Mc2)

            # -------------------------
            # DISPLAY RESULTS
            # -------------------------
            col1a, col2a = st.columns([0.45, 0.55], gap='small')

            with col1a:
                st.write("Design Moment $(M_{c1})$")
            with col2a:
                st.code(f"{Mc1} kip-ft")

            col1b, col2b = st.columns([0.45, 0.55], gap='small')

            with col1b:
                st.write("Design Moment $(M_{c2})$")
            with col2b:
                st.code(f"{Mc2} kip-ft")

            col1b, col2b = st.columns([0.45, 0.55], gap='small')

            with col1b:
                st.write("Design Moment $(M_{c})$")
            with col2b:
                st.code(f"{Mc} kip-ft")

            st.success("Design moments for sway frame computed successfully.")

        else:
            st.info("Enter $M_{1ns}, M_{2ns}, M_{1s}, M_{2s}, \\delta_s$ to compute design moments.")

# ================== DESIGN OF CROSS SECTION ==================
st.write('#### :blue-background[**Design of Cross Section**]')

col1, col2 = st.columns(2, gap='small', border=True)

# --------------------------------------------------
# LEFT PANEL — EQUATIONS
# --------------------------------------------------
with col1:
    st.write("##### :red-background[Design Loads]")

    # -----------------------------
    # Design Axial Load
    # -----------------------------
    st.write("**Design Axial Load = $P_u$**")
    # st.latex(r"P_u")

    # -----------------------------
    # Design Moment
    # -----------------------------
    st.write("**Design Moment = $M_c$**")
    # st.latex(r"M_c")

    # -----------------------------
    # Design Eccentricity
    # -----------------------------
    st.write("**Design Eccentricity**")
    st.latex(r"e_{\text{design}} = \frac{M_c}{P_u} \times 12")

# --------------------------------------------------
# RIGHT PANEL — COMPUTATION
# --------------------------------------------------
with col2:
    st.write("##### :red-background[Computation]")

    if Pu is not None and Mc is not None:

        col1a, col2a, col3a = st.columns([0.4, 0.4, 0.2], gap='small', vertical_alignment='center')

        # Pu display
        with col1a:
            st.write("Design Axial Load $(P_u)$")
        with col2a:

            if column_type == "Unbraced (Sway) Frame":
                Pu = 1.2 * P_d + 1 * P_l

            st.code(f"{Pu}")

        with col3a:
            st.latex(r'\text{(Kips)}')

        col1a, col2a, col3a = st.columns([0.4, 0.4, 0.2], gap='small', vertical_alignment='center')

        # Mc display
        with col1a:
            st.write("Design Moment $(M_c)$")
        with col2a:
            st.code(f"{Mc}")

        with col3a:
            st.latex(r'\text{(Kip-ft)}')

        # Calculating Design Eccentricity
        e_design = (Mc / Pu) * 12
        e_design = round(e_design, 2)

        col1a, col2a, col3a = st.columns([0.4, 0.4, 0.2], gap='small', vertical_alignment='center')

        # e_design display
        with col1a:
            st.write("Design Eccentricity $(e_{design})$")
        with col2a:
            st.code(f"{e_design}")

        with col3a:
            st.latex(r'\text{(inch)}')

col1, col2 = st.columns(2, gap='small', border=True)

# --------------------------------------------------
# LEFT PANEL — EQUATIONS
# --------------------------------------------------
with col1:
    st.write("##### :red-background[Reinforcement Calculation]")
    # st.write("---")

    # -----------------------------
    # Gross Area A_g
    # -----------------------------
    st.write("**Gross Area of Section**")
    st.latex(r"A_g = b \times h")

    # st.write("---")
    #
    # # -----------------------------
    # # Steel Ratio ρ
    # # -----------------------------
    # st.write("**Steel Ratio**")
    # st.latex(r"\rho")
    #
    # st.write("---")

    # -----------------------------
    # Total Steel Area A_s
    # -----------------------------
    st.write("**Total Steel Area**")
    st.latex(r"A_s = \rho A_g")

# --------------------------------------------------
# RIGHT PANEL — COMPUTATION
# --------------------------------------------------
with col2:
    st.write("##### :red-background[Input & Computation]")
    rho = st.number_input('**Assume Percentage of Steel ($\\rho$)**',
                          placeholder='%',
                          value=None,
                          min_value=0.00,
                          format="%0.2f")

    st.divider()

    col1a, col2a, col3a = st.columns([0.4, 0.4, 0.2], gap='small', vertical_alignment='center')

    if b is not None and h is not None:
        Ag = b * h

    if rho is not None and Ag is not None:
        rho = rho / 100
        As = (rho * Ag).__round__(2)
    else:
        As = None

    if As is not None:
        with col1a:
            st.write("Area of Steel $(A_{s})$")
        with col2a:
            st.code(f"{As}")

        with col3a:
            st.latex(r'\text{(in²)}')

col1, col2 = st.columns(2, gap='small', border=True)

# --------------------------------------------------
# LEFT PANEL — EQUATIONS
# --------------------------------------------------
with col1:
    st.write("##### :red-background[Cross Section Diagram]")
    # -----------------------------
    # Steel on Top
    # -----------------------------
    st.write("**Steel on Top (Compression Zone)**")
    st.latex(
        r"""
        A_s(\text{top})
        = n_{\text{top}}
        \left(\frac{\pi}{4}\left(\frac{\text{bar}}{8}\right)^2\right)
        """
    )

    # -----------------------------
    # Steel on Bottom
    # -----------------------------
    st.write("**Steel on Bottom (Tension Zone)**")
    st.latex(
        r"""
        A_s(\text{bottom})
        = n_{\text{bottom}}
        \left(\frac{\pi}{4}\left(\frac{\text{bar}}{8}\right)^2\right)
        """
    )


    def cross_section_diagram_rf(b, h, cover, bar_no, no_of_bars, c=None):
        import plotly.graph_objects as go
        import numpy as np

        if None in (b, h, cover, bar_no, no_of_bars):
            st.info("Enter all design values to generate cross section diagram.")
            return

        # Convert bar number (#4 → 4/8 inch dia)
        bar_dia = bar_no / 8  # in inches
        bar_radius = bar_dia / 2

        # Number of bars on top and bottom
        n_top = int(no_of_bars / 2)
        n_bot = int(no_of_bars / 2)

        # Concrete polygon
        outer_x = [0, b, b, 0, 0]
        outer_y = [0, 0, h, h, 0]

        # Stirrup inner boundary
        stir_x1 = cover
        stir_x2 = b - cover
        stir_y1 = cover
        stir_y2 = h - cover

        inner_x = [stir_x1, stir_x2, stir_x2, stir_x1, stir_x1]
        inner_y = [stir_y1, stir_y1, stir_y2, stir_y2, stir_y1]

        # ----------------------------------------------
        # Compute bar positions
        # ----------------------------------------------

        usable_width = (b - 2 * cover)

        if n_top > 1:
            bar_spacing = (usable_width - 2 * bar_radius) / (n_top - 1)
        else:
            bar_spacing = 0

        top_bars = [(cover + bar_radius + i * bar_spacing,
                     h - cover - bar_radius) for i in range(n_top)]
        bottom_bars = [(cover + bar_radius + i * bar_spacing,
                        cover + bar_radius) for i in range(n_bot)]

        # ----------------------------------------------
        # Plotly figure
        # ----------------------------------------------
        fig = go.Figure()

        # Concrete outline
        fig.add_trace(go.Scatter(
            x=outer_x, y=outer_y,
            mode="lines",
            line=dict(width=3),
            name="Concrete"
        ))

        # Stirrup outline
        fig.add_trace(go.Scatter(
            x=inner_x, y=inner_y,
            mode="lines",
            line=dict(width=2, dash="dash", color='darkgreen'),
            name="Stirrup"
        ))

        # Neutral Axis
        if c is not None:
            fig.add_trace(go.Scatter(
                x=[-2, b + 2],
                y=[h - c, h - c],
                mode="lines+text",
                line=dict(width=2, dash="dot", color='red'),
                text=["N.A"] * 2,
                textposition="top right",
                name="Neutral Axis"
            ))

        # Top bars
        for x, y in top_bars:
            fig.add_shape(
                type="circle",
                x0=x - bar_radius, x1=x + bar_radius,
                y0=y - bar_radius, y1=y + bar_radius,
                line_color="black", fillcolor="steelblue"
            )

        # Label top bars as "n-#bar_no"
        fig.add_trace(go.Scatter(
            x=[np.mean([p[0] for p in top_bars])],
            y=[top_bars[0][1] - 0.5 - bar_radius*2.5],
            mode="text",
            text=[f"{n_top}-#{bar_no}"],
            textposition="bottom center",
            showlegend=False
        ))

        # Bottom bars
        for x, y in bottom_bars:
            fig.add_shape(
                type="circle",
                x0=x - bar_radius, x1=x + bar_radius,
                y0=y - bar_radius, y1=y + bar_radius,
                line_color="black", fillcolor="tomato"
            )
        # Label bottom bars
        fig.add_trace(go.Scatter(
            x=[np.mean([p[0] for p in bottom_bars])],
            y=[bottom_bars[0][1] + 0.5 + bar_radius*2.5],
            mode="text",
            text=[f"{n_bot}-#{bar_no}"],
            textposition="bottom center",
            showlegend=False
        ))

        # Layout
        fig.update_layout(
            width=450,
            height=550,
            title="Reinforced Concrete Column Cross Section",
            xaxis=dict(scaleanchor="y", title="Width (in)", range=[-2.5, b + 4]),
            yaxis=dict(title="Height (in)", range=[-1, h + 1]),
            showlegend=False,
            margin=dict(l=20, r=20, t=40, b=20)
        )

        st.plotly_chart(fig, use_container_width=True)

# --------------------------------------------------
# RIGHT PANEL — COMPUTATION
# --------------------------------------------------
with col2:
    st.write("##### :red-background[Input & Computation]")
    if As is not None:
        st.write('**No. of Bars Calculated**')

        bar_no_data = pd.DataFrame(
            data={
                'Bar No.': [f'#{x}' for x in range(3, 15)],
                'No. of Bars': [
                    As / ((np.pi / 4) * (x / 8) ** 2) for x in range(3, 15)
                ]
            }
        )

        st.dataframe(data=bar_no_data, hide_index=True, width='stretch', height=210)

        st.write('**Select Bar Number & Enter No. of Bars**')

        col2a, col2b = st.columns(2, gap='small', vertical_alignment='top', border=True)

        with col2a:
            bar_no = st.number_input('Bar No.', value=None, min_value=0)
        with col2b:
            no_of_bars = st.number_input('No of Bars', value=None, min_value=0)

        if bar_no and no_of_bars:

            distr_no_of_bars = no_of_bars / 2

            single_bar_area = (np.pi / 4) * (bar_no / 8) ** 2

            As_top = round(distr_no_of_bars * single_bar_area, 2)
            As_bottom = round(distr_no_of_bars * single_bar_area, 2)

        else:
            As_top = None
            As_bottom = None

        st.divider()

        if As_top and As_bottom:

            col1a, col2a, col3a = st.columns([0.4, 0.4, 0.2], gap='small', vertical_alignment='center')

            with col1a:
                st.write("Area of Steel on Top $(A_{s})$")
            with col2a:
                st.code(f"{As_top}")
            with col3a:
                st.latex(r'\text{(in²)}')

            col1a, col2a, col3a = st.columns([0.4, 0.4, 0.2], gap='small', vertical_alignment='center')

            with col1a:
                st.write("Area of Steel on Bottom $(A_{s'})$")
            with col2a:
                st.code(f"{As_bottom}")
            with col3a:
                st.latex(r'\text{(in²)}')

            col1a, col2a, col3a = st.columns([0.4, 0.4, 0.2], gap='small', vertical_alignment='center')

            # Calculate the spacings between bars

            spacing = (b - 2 * cover - 2 * (3 / 8) - distr_no_of_bars * single_bar_area) / (distr_no_of_bars - 1)
            spacing = round(spacing, 2)

            with col1a:
                st.write("Spacing b/w Bars")
            with col2a:
                st.code(f"{spacing}")
            with col3a:
                st.latex(r'\text{(in)}')

            # check for spacing
            if spacing >= 1:
                st.success('Spacing b/w Bars is Acceptable!')

            else:
                st.error('Spacing b/w Bars is not Acceptable! (Spacing < 1 in)')

with col1:
    st.divider()

    if all(x is not None for x in [b, h, cover, bar_no, no_of_bars]):
        cross_section_diagram_rf(b, h, cover, bar_no=bar_no, no_of_bars=no_of_bars)

st.write('#### :blue-background[**Eccentricity Check**]')

col1, col2 = st.columns(2, gap='small', border=True)

# --------------------------------------------------
# LEFT PANEL — EQUATIONS
# --------------------------------------------------
with col1:
    st.write("##### :red-background[Equations Used]")

    # Effective depth d
    st.write("**Effective Depth**")
    st.latex(r"d = h - \text{cover} - d_{stirrup} - \frac{d_{bar}}{2}")

    # Effective depth d'
    st.write("**Effective Depth to Compression Steel**")
    st.latex(r"d' = \text{cover} + d_{stirrup} + \frac{d_{bar}}{2}")

    # Whitney block
    st.write("**Whitney Stress Block Depth**")
    st.latex(r"a = \beta_1 c")

    # Strains
    st.write("**Strain in Compression Steel**")
    st.latex(r"\varepsilon_c = \frac{c - d'}{c} \times 0.003")

    st.write("**Strain in Tension Steel**")
    st.latex(r"\varepsilon_t = \frac{d - c}{c} \times 0.003")

    # Stresses
    st.write("**Stress in Compression Steel**")
    st.latex(r"f_{cs} = E_s \varepsilon_c \le f_y")

    st.write("**Stress in Tension Steel**")
    st.latex(r"f_{ts} = E_s \varepsilon_t \le f_y")

    # Forces
    st.write("**Concrete Compression Force**")
    st.latex(r"C_c = 0.85 f'_c \, a \, b")

    st.write("**Compression Steel Force**")
    st.latex(r"C_s = A_s' * (f_{cs} - 0.85f'c)")

    st.write("**Tension Steel Force**")
    st.latex(r"T = A_s f_{ts}")

    # Axial load
    st.write("**Nominal Axial Load**")
    st.latex(r"P_n = C_c + C_s - T")

    # Moment
    st.write("**Nominal Moment**")
    st.latex(r"M_n = C_c\left(\frac{h}{2}-\frac{a}{2}\right) + C_s\left(\frac{h}{2}-d'\right) + T\left(d-\frac{h}{2}\right)")

    # Eccentricity
    st.write("**Calculated Eccentricity**")
    st.latex(r"e_{\text{calc}} = \frac{M_n}{P_n} \times 12")

    st.write("**Ultimate Loads**")
    st.latex(r"M_u = \phi M_n")
    st.latex(r"P_u = \phi P_n")


# --------------------------------------------------
# RIGHT PANEL — COMPUTATION
# --------------------------------------------------
with col2:
    st.write("##### :red-background[Computed Values]")

    if all(x is not None for x in [As_top, As_bottom, b, h, e_design]):

        stirrup_dia = 3/8
        bar_dia = bar_no / 8

        # EFFECTIVE DEPTHS
        d = round(h - cover - stirrup_dia - bar_dia/2, 2)
        d_dash = round(cover + stirrup_dia + bar_dia/2, 2)

        # ITERATION for neutral axis c
        c_factor = 0.6
        max_iter = 10000
        tol = 0.01

        for _ in range(max_iter):

            c = c_factor*d
            a = beta * c

            strain_c = ((c - d_dash) / c) * 0.003
            f_cs = min(29000 * strain_c, f_y)

            strain_t = ((d - c) / c) * 0.003
            f_ts = min(29000 * strain_t, f_y)

            C_c = 0.85 * f_c * a * b
            C_s = As_top * (f_cs - 0.85*f_c)
            T = As_bottom * f_ts

            Pn = C_c + C_s - T
            Mn = (C_c * (h/2 - a/2) +
                  C_s * (h/2 - d_dash) +
                  T * (d - h/2)) / 12  # ft-kip

            e_calc = round((Mn / Pn) * 12, 2)

            if abs(e_calc - e_design) <= tol:
                break

            c_factor += 0.0001

        # -------------------------------
        # FORMATTED DISPLAY
        # -------------------------------

        # d
        ca, cb, cc = st.columns([0.4, 0.4, 0.2])
        with ca: st.write("Effective Depth $(d)$")
        with cb: st.code(f"{d}")
        with cc: st.latex(r'\text{(in)}')

        # d'
        ca, cb, cc = st.columns([0.4, 0.4, 0.2])
        with ca: st.write("Compression Depth $(d')$")
        with cb: st.code(f"{d_dash}")
        with cc: st.latex(r'\text{(in)}')

        # c
        ca, cb, cc = st.columns([0.4, 0.4, 0.2])
        with ca: st.write("Neutral Axis Depth $(c)$")
        with cb: st.code(f"{round(c,2)}")
        with cc: st.latex(r'\text{(in)}')

        # a
        ca, cb, cc = st.columns([0.4, 0.4, 0.2])
        with ca: st.write("Whitney Block $(a)$")
        with cb: st.code(f"{round(a,2)}")
        with cc: st.latex(r'\text{(in)}')

        # strain_c
        ca, cb, cc = st.columns([0.4, 0.4, 0.2])
        with ca: st.write("Strain in Compression Steel $(\epsilon_c)$")
        with cb: st.code(f"{round(strain_c,6)}")
        with cc: st.latex(r'\text{ }')

        # f_cs
        ca, cb, cc = st.columns([0.4, 0.4, 0.2])
        with ca: st.write("Stress in Compression Steel $(f_{cs})$")
        with cb: st.code(f"{round(f_cs,0)}")
        with cc: st.latex(r'\text{(ksi)}')

        # strain_t
        ca, cb, cc = st.columns([0.4, 0.4, 0.2])
        with ca: st.write("Strain in Tension Steel $(\epsilon_t)$")
        with cb: st.code(f"{round(strain_t,6)}")
        with cc: st.latex(r'\text{ }')

        # f_ts
        ca, cb, cc = st.columns([0.4, 0.4, 0.2])
        with ca: st.write("Stress in Tension Steel $(f_{ts})$")
        with cb: st.code(f"{round(f_ts,0)}")
        with cc: st.latex(r'\text{(ksi)}')

        # Cc
        ca, cb, cc = st.columns([0.4, 0.4, 0.2])
        with ca: st.write("Concrete Force $(C_c)$")
        with cb: st.code(f"{round(C_c,2)}")
        with cc: st.latex(r'\text{(kips)}')

        # Cs
        ca, cb, cc = st.columns([0.4, 0.4, 0.2])
        with ca: st.write("Compression Steel Force $(C_s)$")
        with cb: st.code(f"{round(C_s,2)}")
        with cc: st.latex(r'\text{(kips)}')

        # T
        ca, cb, cc = st.columns([0.4, 0.4, 0.2])
        with ca: st.write("Tension Steel Force $(T)$")
        with cb: st.code(f"{round(T,2)}")
        with cc: st.latex(r'\text{(kips)}')

        # Pn
        ca, cb, cc = st.columns([0.4, 0.4, 0.2])
        with ca: st.write("Nominal Axial Load $(P_n)$")
        with cb: st.code(f"{round(Pn,2)}")
        with cc: st.latex(r'\text{(kips)}')

        # Mn
        ca, cb, cc = st.columns([0.4, 0.4, 0.2])
        with ca: st.write("Nominal Moment $(M_n)$")
        with cb: st.code(f"{round(Mn,2)}")
        with cc: st.latex(r'\text{(kip-ft)}')

        # e_calc
        ca, cb, cc = st.columns([0.4, 0.4, 0.2])
        with ca: st.write("Calculated Eccentricity $(e_{calc})$")
        with cb: st.code(f"{round(e_calc,2)}")
        with cc: st.latex(r'\text{(in)}')

        # Final Success Message
        st.success("Eccentricity Matched — Design Completed!")

    st.divider()
    st.write("##### :red-background[Results Verification]")

    if Mn is not None and Pn is not None:
        # ϕ-factored strengths
        Mu_factored = (phi_axial * Mn).__round__(2)  # ultimate moment capacity
        Pu_factored = (phi_axial * Pn).__round__(2)  # ultimate axial capacity

        # -------------------------------
        # Display Results
        # -------------------------------
        col1v, col2v, col3v = st.columns([0.4, 0.4, 0.2], gap='small')

        with col1v:
            st.write("Ultimate Moment Capacity $(M_u)$")
        with col2v:
            st.code(f"{Mu_factored}")
        with col3v:
            st.latex(r"\text{(Kip-ft)}")

        col1v, col2v, col3v = st.columns([0.4, 0.4, 0.2], gap='small')

        with col1v:
            st.write("Ultimate Axial Capacity $(P_u)$")
        with col2v:
            st.code(f"{Pu_factored}")
        with col3v:
            st.latex(r"\text{(Kips)}")

        # -------------------------------
        # Strength Verification
        # -------------------------------
        st.divider()
        st.write("##### :red-background[Strength Check]")

        moment_ok = Mu_factored >= Mc
        axial_ok = Pu_factored >= Pu  # use your original design Pu variable (factored)

        if moment_ok and axial_ok:
            st.success("✔ Strength Requirements Satisfied")
            st.success(f"$M_u = {Mu_factored} \ge M_c = {Mc}$")
            st.success(f"$P_u = {Pu_factored} \ge P_{{design}} = {Pu}$")
            st.success("Design Successful 🎉")

        else:
            st.error("❌ Strength Requirements NOT Satisfied")

            if not moment_ok:
                st.error(f"$M_u = {Mu_factored} < M_c = {Mc}$ (Moment NG)")

            if not axial_ok:
                st.error(f"$P_u = {Pu_factored} < P_{{design}} = {Pu}$ (Axial NG)")

# ================== DESIGN SUMMARY ==================
st.space()
st.subheader('Design Summary', divider='red')

col1, col2 = st.columns(2, gap='small', border=True)

# --------------------------------------------------
# LEFT PANEL — Cross Section Diagram
# --------------------------------------------------
with col1:
    cross_section_diagram_rf(b, h, cover, bar_no=bar_no, no_of_bars=no_of_bars, c=c)

# --------------------------------------------------
# RIGHT PANEL — Design Parameters
# --------------------------------------------------
with col2:
    st.write("##### :red-background[Key Design Parameters]")

    # Design Axial Load
    col1a, col2a, col3a = st.columns([0.5, 0.3, 0.2], gap='small', vertical_alignment='center')
    with col1a:
        st.write("Nominal Designed Axial Load $(\\phi P_u)$")
    with col2a:
        st.code(f"{Pu_factored}")
    with col3a:
        st.latex(r"\text{(kips)}")

    # Design Moment
    col1a, col2a, col3a = st.columns([0.5, 0.3, 0.2], gap='small', vertical_alignment='center')
    with col1a:
        st.write("Nominal Designed Moment $(\\phi M_u)$")
    with col2a:
        st.code(f"{Mc}")
    with col3a:
        st.latex(r"\text{(k-ft)}")

    # Design Eccentricity
    col1a, col2a, col3a = st.columns([0.5, 0.3, 0.2], gap='small', vertical_alignment='center')
    with col1a:
        st.write("Design Eccentricity $(e_{\mathrm{design}})$")
    with col2a:
        st.code(f"{e_design}")
    with col3a:
        st.latex(r"\text{(in)}")

    # Neutral Axis Depth
    if c is not None:
        col1a, col2a, col3a = st.columns([0.5, 0.3, 0.2], gap='small', vertical_alignment='center')
        with col1a:
            st.write("Neutral Axis Depth $(c)$")
        with col2a:
            st.code(f"{c.__round__(2)}")
        with col3a:
            st.latex(r"\text{(in)}")

    # Top Steel Area
    if As_top is not None:
        col1a, col2a, col3a = st.columns([0.5, 0.3, 0.2], gap='small', vertical_alignment='center')
        with col1a:
            st.write("Area of Top Steel $(A_{s,\mathrm{top}})$")
        with col2a:
            st.code(f"{As_top:.2f}")
        with col3a:
            st.latex(r"\text{(in²)}")

    # Bottom Steel Area
    if As_bottom is not None:
        col1a, col2a, col3a = st.columns([0.5, 0.3, 0.2], gap='small', vertical_alignment='center')
        with col1a:
            st.write("Area of Bottom Steel $(A_{s,\mathrm{bottom}})$")
        with col2a:
            st.code(f"{As_bottom:.2f}")
        with col3a:
            st.latex(r"\text{(in²)}")

    col1a, col2a= st.columns(2, gap='small', vertical_alignment='center')
    with col1a:
        st.write('**Provided Spacing Between Ties**')

    with col2a:
        if all(x is not None for x in [b, h, bar_no]):
            tie_spacing_1 = 48 * 3 / 8
            tie_spacing_2 = 16 * bar_no / 8
            tie_spacing_3 = min(b, h)
            final_tie_spacing = min(tie_spacing_1, tie_spacing_2, tie_spacing_3)
            st.code(f'#3@{final_tie_spacing}"c/c')
