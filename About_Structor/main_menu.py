import streamlit as st
from streamlit_echarts import st_echarts
from pyecharts.charts import Tree
import pyecharts.options as opts

# ---------- CUSTOM CSS ----------
st.markdown(
    """
    <style>
    /* Background */
    .stApp {
        background: #252C37; /* Midnight */
        color: #F8C61E; /* Sunburst */
        font-family: 'Helvetica Neue', sans-serif;
    }

    /* Floating animation */
    @keyframes float {
        0% { transform: translatey(0px);}
        50% { transform: translatey(-10px);}
        100% { transform: translatey(0px);}
    }
    .floating { animation: float 4s ease-in-out infinite; }

    /* Hero Section */
    .hero {
        text-align: center;
        padding: 80px 20px 50px 20px;
    }
    .hero h1 {
        font-size: 4.5em;
        font-weight: 900;
        letter-spacing: 2px;
        margin-bottom: 10px;
        color: #F8C61E;
    }
    .hero h3 {
        font-size: 1.5em;
        font-weight: 300;
        color: #ddd;
    }

    /* Feature Cards */
    .card {
        display: block;
        background: rgba(255,255,255,0.05);
        border-radius: 15px;
        padding: 25px;
        text-align: center;
        transition: all 0.3s ease-in-out;
        cursor: pointer;
        box-shadow: 0 4px 20px rgba(0,0,0,0.4);
        text-decoration: none !important;
        color: inherit !important;
    }
    .card h2, .card p {
        text-decoration: none !important;
    }
    .card:hover {
        transform: translateY(-8px);
        background: rgba(248,198,30,0.1); /* Sunburst glow */
        box-shadow: 0 8px 30px rgba(248,198,30,0.5);
    }
    .card h2 {
        color: #F8C61E;
        margin-bottom: 10px;
    }
    .card p {
        color: #eee;
        font-size: 0.95em;
    }

    /* Contact Section */
    .contact {
        padding: 50px 20px;
        background: rgba(255,255,255,0.02);
        border-radius: 15px;
        margin-top: 50px;
        text-align: center;
    }
    .contact h2 {
        font-size: 2em;
        margin-bottom: 15px;
        color: #F8C61E;
    }
    .contact p {
        color: #bbb;
        font-size: 1em;
    }

    /* Footer */
    .footer {
        text-align: center;
        font-size: 0.85em;
        margin-top: 50px;
        color: #888;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- HERO SECTION ----------
st.markdown(
    """
    <div class="hero floating">
        <h1>Structor</h1>
        <h3>Structural Analysis Made Simple</h3>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------- FEATURE CARDS ----------
st.markdown("<h2 style='text-align:center;'>Explore Apps</h2>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        """<a href="/beam_analysis_v2.2" target="_self" class="card">
            <h2>Beam Analysis</h2>
            <p>Analyze statically determinate and indeterminate beams.</p>
        </a>""",
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        """<a href="/frame_analysis_v1" target="_self" class="card">
            <h2>Frame / Truss Analysis</h2>
            <p>Model and solve 2D frame and truss structures.</p>
        </a>""",
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        """<a href="/main_section_prop_calc" target="_self" class="card">
            <h2>Section Properties</h2>
            <p>Calculate area, centroid, and moments of inertia etc. for any section.</p>
        </a>""",
        unsafe_allow_html=True,
    )

# ---------- TREE CHART FUNCTION ----------
def app_tree_chart():
    # Structor Tree Data
    data = [
        {
            "name": "Structor",
            "children": [
                {
                    "name": "Menu",
                    "children": [
                        {"name": "Main Menu"},
                        {"name": "About Application"},
                    ],
                },
                {
                    "name": "Structural Analysis",
                    "children": [
                        {"name": "Beam Analysis"},
                        {"name": "Frame / Truss Analysis"},
                        {"name": "Section Properties Calculator"},
                    ],
                },
                {
                    "name": "Reinforced Concrete design",
                    "children": [
                        {"name": "Short Column Design"},
                        {"name": "Slender/Long Column Design"},
                    ],
                },
            ],
        }
    ]

    tree = (
        Tree()
        .add(
            series_name="",
            data=data,
            orient="LR",
            collapse_interval=2,
            symbol="circle",
            symbol_size=15,
            edge_fork_position="63%",
            # line_style=opts.LineStyleOpts(color="#F8C61E", width=2),  # golden edges
            label_opts=opts.LabelOpts(
                position="top",
                horizontal_align="center",
                vertical_align="middle",
                font_size=14,
                color="#F8C61E",  # golden text
            ),
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(
                # title="Structor Roadmap",
                pos_left="center",
                title_textstyle_opts=opts.TextStyleOpts(
                    font_size=20, color="#F8C61E", font_weight="bold"
                ),
            ),
            toolbox_opts=opts.ToolboxOpts(is_show=False),
            legend_opts=opts.LegendOpts(is_show=False),
        )
    )

    import json

    st_echarts(
        options=json.loads(tree.dump_options()),
        height="500px",
        # key=f"{force_type}-chart"
    )

# ---------- RENDER TREE ----------
st.markdown("<h2 style='text-align:center;margin-top:40px;'>Structor Roadmap</h2>", unsafe_allow_html=True)
app_tree_chart()

# ---------- CONTACT SECTION ----------
st.markdown(
    """
    <div class="contact">
        <h2>About Structor</h2>
        <p>Structor is your companion for learning & applying structural analysis. <br>
        From beams to frames to section properties — everything in one intuitive app.</p>
        <br>
        <p>More apps and features coming soon!<p>
        <p> <p>
        <p><b>Contact:</b> ameer.hamza.alee3011@gmail.com</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------- FOOTER ----------
st.markdown(
    """
    <style>
        .footer {
            text-align: center;
            padding: 10px;
            font-size: 14px;
            color: #888;
        }
        .footer a {
            color: #888;
            text-decoration: none;
            font-weight: bold;
        }
        .footer a:hover {
            color: #00AEEF; /* LinkedIn blue on hover */
            text-decoration: underline;
        }
    </style>
    <div class="footer">
        Made with ❤️ by <a href="https://www.linkedin.com/in/hamza-ali-35449a2aa/" target="_blank">Ameer Hamza Ali</a> | © 2026 Structor
    </div>
    """,
    unsafe_allow_html=True,
)
