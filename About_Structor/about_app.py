import streamlit as st

st.title("About Application")
st.write('\n')

st.write("### :blue-background[**:material/code_blocks: Developer**]")
st.divider()
st.write("""

***Ameer Hamza Ali***  
***Batch 2022***  
***Department of Civil Engineering***  
***NED University of Engineering & Technology, Karachi, Pakistan***  

Check out my profile:  
https://about-hamza-ali.streamlit.app/  

Let's connect!:  
https://www.linkedin.com/in/hamza-ali-35449a2aa/
""")


# --- Update Dialogs ---
@st.dialog('Updates')
def version2_3_update():
    st.subheader("🚀 What's New in Version 2.3.0?")
    st.markdown("""
    - 🏗️ **Frame Analysis App** — Added new module for analyzing **2D frames**, including member forces, joint displacements, and support reactions  
    - 👌 **Reinforced Concrete Design** - Added new section for R.C.D and added two applications of design short and slender columns as per ACI 318-19
    - 📊 **Enhanced Structural Tools** — Expands beyond beams into more advanced structural systems  
    - 🔧 **Improved Flexibility** — Extended capabilities for engineers working on indeterminate structures  
    """)


@st.dialog('Updates')
def version2_2_update():
    st.subheader("🚀 What's New in Version 2.2.0?")
    st.markdown("""
    - 🎯 **Directional Force & Moment Buttons** — Intuitive controls for applying loads  
    - 📊 **Interactive Pyecharts Graphs** — Enhanced visual analysis for internal forces  
    - 🧮 **Custom Section Calculator** — Compute properties of **user-defined sections**  
    - 📐 **Expanded Shape Library** — Added more standard shapes in Section Properties Calculator  
    - 🎨 **Improved UI & Layout** — Clean, consistent look across the application  
    """)


@st.dialog('Updates')
def version2_1_update():
    st.subheader("✨ What's New in Version 2.1.0?")
    st.markdown("""
    - 🎨 **Revamped UI** — Better overall layout  
    - 💾 **Save Dynamic Figure** — One-click HTML export  
    - 📊 **Internal Forces at Intervals** — Custom sampling  
    - 📍 **Internal Forces at Location** — Point-specific data  
    """)


@st.dialog('Information')
def version1_update():
    st.subheader("🎉 Version 1.0.0 - Official Release")
    st.write("We're live! 🚀 Excited to launch Structor!")
    st.markdown("""
    - ✅ Core features launched  
    - 🛠️ Minor bug fixes and UI polish  
    """)


# --- Version Table Simulation ---
st.write("### :blue-background[**:material/update: Version History**]")
st.divider()

st.write("**:red-background[Current Version:]**  2.3.0")
# Data for each version
versions = [
    {
        "version": "2.3.0",
        "date": "17/03/2026",
        "button": "See the Updates",
        "callback": version2_3_update
    },
    {
        "version": "2.2.0",
        "date": "23/06/2025",
        "button": "See the Updates",
        "callback": version2_2_update
    },
    {
        "version": "2.1.0",
        "date": "08/03/2025",
        "button": "See the Updates",
        "callback": version2_1_update
    },
    {
        "version": "1.0.0",
        "date": "20/01/2025",
        "button": "Info",
        "callback": version1_update
    }
]

# Table Header
col1, col2, col3 = st.columns(3, gap='small')
col1.markdown("**Version**")
col2.markdown("**Release Date**")
col3.markdown("**Details**")

# Table Rows
for v in versions:
    col1, col2, col3 = st.columns(3, border=True, gap='small')
    col1.write(v["version"])
    col2.write(v["date"])
    col3.button(v["button"], key=v["version"], on_click=v["callback"])

st.write('\n')
st.write("### :blue-background[**:material/communities: Purpose**]")
st.divider()
st.write(
    "This application is designed to analyze beams, frames, calculate Shear Force Diagrams (S.F.D), Bending Moment Diagrams (B.M.D), and deflections. It also computes the moment of inertia and centroid of various beam cross-section shapes, providing comprehensive structural analysis tools for engineers.")

st.write('\n')
st.write("### :blue-background[**:material/list_alt: Modules Used**]")
st.divider()
st.write("""
- **:grey-background[Streamlit]:** For creating the interactive web application interface.  
  [Streamlit Documentation](https://docs.streamlit.io/)

- **:grey-background[Pyecharts]:** For rendering interactive and visually rich graphs for advanced structural analysis.  
  [Pyecharts Documentation](https://pyecharts.org/#/)

- **:grey-background[Pandas]:** For data manipulation and creating data tables for beam properties and results.  
  [Pandas Documentation](https://pandas.pydata.org/docs/)

- **:grey-background[Numpy]:** For numerical computations, matrix operations, and core calculations in structural analysis.  
  [NumPy Documentation](https://numpy.org/doc/)

- **:grey-background[IndeterminateBeam]:** For performing beam analysis, including support additions and internal force calculations.  
  [IndeterminateBeam Documentation](https://indeterminatebeam.readthedocs.io/en/main/index.html#)  
  Learn more from the original paper by [Jesse Bonanno](https://www.linkedin.com/in/jessebonanno/):  
  [IndeterminateBeam Paper](https://jose.theoj.org/papers/10.21105/jose.00111)
  
- **:grey-background[PyNiteFEA]:** For frame and structural analysis using the finite element method.  
  [PyNiteFEA Documentation](https://github.com/JWock82/PyNite)

- **:grey-background[Plotly]:** For generating visual diagrams such as Shear Force Diagrams (S.F.D) and Bending Moment Diagrams (B.M.D).  
  [Plotly Documentation](https://plotly.com/python/)

- **:grey-background[Polygon_Math]:** For computing properties like area, centroid, and moments of inertia of custom polygonal sections.  
  [Polygon_Math Documentation (PyPI)](https://pypi.org/project/polygon-math/)
""")

st.write('\n')
st.write("###  :blue-background[**:material/call: Contact**]")
st.divider()
st.write("""
For further assistance, feedback, or to report any bugs, please contact me at ameer.hamza.alee3011@gmail.com.
""")
