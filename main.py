# بِسْمِ ٱللَّٰهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ
# In The Name of Allah, The most Beneficent and Most Merciful
# Alhamdulillah and All praises to Allah Almighty who give me the knowledge to make this application.
# I hope that this will benefit so many people, Insha Allah.

# Best Regards
# Ameer Hamza Ali
# Batch 2022
# NED University of Engineering & Technology, Karachi, Pakistan

import streamlit as st

# PAGE SETUP
st.set_page_config(layout='wide')

# Structural Analysis Section-----------------------------------------------------------------------

beam_analysis_app = st.Page(
    page="Applications/Structural_Analysis/Beam_Analysis/beam_analysis_v2.2.py",
    title="Beam Analysis",
    # icon=":material/bid_landscape:",
)

frame_analysis_app = st.Page(
    page="Applications/Structural_Analysis/Frame_Analysis/frame_analysis_v1.py",
    title="Frame/Truss Analysis",
    # default=True
    # icon=":material/bid_landscape:",
)

section_prop_page = st.Page(
    page="Applications/Structural_Analysis/Section_Properties_Calculator/main_section_prop_calc.py",
    title="Section Properties Calculator",
    # icon=":material/text_select_end:",
)

# RCD Section---------------------------------------------------------------------------------------

short_column_page = st.Page(
    page="Applications/Reinforced_Concrete_Design/Short_Columns/short_column_design.py",
    title="Short Column Design",
    # icon=":material/text_select_end:",
)

slender_column_page = st.Page(
    page="Applications/Reinforced_Concrete_Design/Slender_Columns/slender_column_design.py",
    title="Slender/Long Column Design",
    # icon=":material/text_select_end:",
)

# Main Menu Section---------------------------------------------------------------------------------------
main_menu_page = st.Page(
    page="About_Structor/main_menu.py",
    title="Main Menu",
    icon=":material/home_app_logo:",
    default=True
)

about_app = st.Page(
    page="About_Structor/about_app.py",
    title="About Application",
    icon=":material/info:",
)

# NAVIGATION SETUP (WITH SECTIONS)
pg = st.navigation({
    'Structural Analysis': [beam_analysis_app, frame_analysis_app, section_prop_page],
    'Reinforced Concrete Design': [short_column_page, slender_column_page],
    'Menu': [main_menu_page, about_app]
},
    position='top')

# SHARED ON ALL PAGES

# st.sidebar.link_button(label='About me', url='https://about-hamza-ali.streamlit.app/')
# with 💥''')

# RUN NAVIGATION
pg.run()
