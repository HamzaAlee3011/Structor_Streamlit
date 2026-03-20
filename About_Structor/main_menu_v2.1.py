import streamlit as st
import streamlit.components.v1 as components
from streamlit_echarts import st_echarts
import base64
import os

# ── Logo loader ───────────────────────────────────────────────────────────────
def load_logo_b64(path: str) -> str:
    if os.path.exists(path):
        with open(path, "rb") as f:
            data = base64.b64encode(f.read()).decode()
        ext = path.rsplit(".", 1)[-1].lower()
        mime = "image/png" if ext == "png" else f"image/{ext}"
        return f"data:{mime};base64,{data}"
    return ""

LOGO_PATH = "images/structor_logo-removebg-preview.png"
LOGO_B64  = load_logo_b64(LOGO_PATH)
_favicon  = LOGO_PATH if os.path.exists(LOGO_PATH) else "S"

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Structor – Structural Engineering Platform",
    # page_icon=_favicon,
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Page map ──────────────────────────────────────────────────────────────────
PAGE_MAP = {
    "beam":       "Applications/Structural_Analysis/Beam_Analysis/beam_analysis_v2.2.py",
    "frame":      "Applications/Structural_Analysis/Frame_Analysis/frame_analysis_v1.py",
    "section":    "Applications/Structural_Analysis/Section_Properties_Calculator/main_section_prop_calc.py",
    "rc_short":   "Applications/Reinforced_Concrete_Design/Short_Columns/short_column_design.py",
    "rc_slender": "Applications/Reinforced_Concrete_Design/Slender_Columns/slender_column_design.py",
    "about":      "About_Structor/about_app.py",
}

# Handle navigation via query params
params = st.query_params
if "goto" in params and params["goto"] in PAGE_MAP:
    st.switch_page(PAGE_MAP[params["goto"]])

# ── Shared CSS string (injected into both st.markdown and components.html) ───
SHARED_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,600&display=swap');

*, *::before, *::after { box-sizing: border-box; }

:root {
  --bg:      #252C37;
  --bg2:     #1E242E;
  --surface: rgba(42,51,64,0.72);
  --border:  rgba(255,255,255,0.07);
  --accent:  #F8C61E;
  --text:    #DDE3EC;
  --muted:   #7A8799;
  --radius:  12px;
  --pad:     clamp(1.2rem, 5vw, 4rem);
}

body { margin: 0; padding: 0; background: transparent; font-family: 'DM Sans', sans-serif; color: var(--text); }

/* ── Card grid ── */
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(240px, 100%), 1fr));
  gap: 1rem;
  width: 100%;
  padding: 0;
}

.mod-card {
  background: rgba(42,51,64,0.72);
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: 12px;
  padding: 1.5rem 1.4rem 1.3rem;
  position: relative; overflow: hidden;
  display: block; text-decoration: none;
  color: inherit;
  cursor: pointer;
  transition: border-color 0.22s, transform 0.22s, box-shadow 0.22s;
}
.mod-card::before {
  content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
  background: #F8C61E; transform: scaleX(0);
  transform-origin: left; transition: transform 0.25s ease;
}
.mod-card:hover {
  border-color: rgba(248,198,30,0.22);
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(0,0,0,0.28);
  text-decoration: none; color: inherit;
}
.mod-card:hover::before { transform: scaleX(1); }

.card-icon  { width: 22px; height: 22px; margin-bottom: 0.9rem; opacity: 0.70; display: block; }
.card-index { font-size: 0.57rem; font-weight: 600; letter-spacing: 0.14em; text-transform: uppercase; color: #7A8799; margin-bottom: 0.28rem; }
.card-title { font-family: 'Syne', sans-serif; font-weight: 700; font-size: 0.96rem; color: #DDE3EC; margin-bottom: 0.45rem; line-height: 1.2; }
.card-desc  { font-size: 0.77rem; color: #7A8799; line-height: 1.65; margin-bottom: 1rem; }
.card-cta   { font-size: 0.72rem; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; color: #F8C61E; display: block; transition: letter-spacing 0.2s; }
.mod-card:hover .card-cta { letter-spacing: 0.13em; }

.card-tag { display: inline-block; font-size: 0.55rem; font-weight: 600; letter-spacing: 0.10em; text-transform: uppercase; padding: 0.13rem 0.44rem; border-radius: 3px; margin-bottom: 0.75rem; white-space: nowrap; }
.tag-live { background: rgba(74,222,128,0.09);  color: #4ade80; border: 1px solid rgba(74,222,128,0.20); }
.tag-beta { background: rgba(165,180,252,0.09); color: #a5b4fc; border: 1px solid rgba(165,180,252,0.20); }
.tag-rc   { background: rgba(248,198,30,0.09);  color: #F8C61E; border: 1px solid rgba(248,198,30,0.20); }
.tag-info { background: rgba(125,211,252,0.09); color: #7dd3fc; border: 1px solid rgba(125,211,252,0.20); }
"""

SVG = {
    "beam":    '<svg class="card-icon" viewBox="0 0 24 24" fill="none" stroke="#F8C61E" stroke-width="1.5" stroke-linecap="round"><line x1="2" y1="12" x2="22" y2="12"/><line x1="2" y1="8" x2="2" y2="16"/><line x1="22" y1="8" x2="22" y2="16"/><line x1="8" y1="7" x2="8" y2="12"/><line x1="16" y1="7" x2="16" y2="12"/></svg>',
    "frame":   '<svg class="card-icon" viewBox="0 0 24 24" fill="none" stroke="#F8C61E" stroke-width="1.5" stroke-linecap="round"><rect x="3" y="3" width="18" height="18" rx="1"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="3" y1="15" x2="21" y2="15"/><line x1="9" y1="3" x2="9" y2="21"/><line x1="15" y1="3" x2="15" y2="21"/></svg>',
    "section": '<svg class="card-icon" viewBox="0 0 24 24" fill="none" stroke="#F8C61E" stroke-width="1.5" stroke-linecap="round"><rect x="4" y="4" width="16" height="16"/><line x1="4" y1="12" x2="20" y2="12"/><line x1="12" y1="4" x2="12" y2="20"/></svg>',
    "column":  '<svg class="card-icon" viewBox="0 0 24 24" fill="none" stroke="#F8C61E" stroke-width="1.5" stroke-linecap="round"><rect x="8" y="2" width="8" height="20" rx="1"/><line x1="4" y1="2" x2="20" y2="2"/><line x1="4" y1="22" x2="20" y2="22"/></svg>',
    "tall":    '<svg class="card-icon" viewBox="0 0 24 24" fill="none" stroke="#F8C61E" stroke-width="1.5" stroke-linecap="round"><rect x="9" y="2" width="6" height="20" rx="1"/><line x1="5" y1="2" x2="19" y2="2"/><line x1="5" y1="22" x2="19" y2="22"/><line x1="12" y1="8" x2="12" y2="16" stroke-dasharray="2 2"/></svg>',
    "info":    '<svg class="card-icon" viewBox="0 0 24 24" fill="none" stroke="#F8C61E" stroke-width="1.5" stroke-linecap="round"><circle cx="12" cy="12" r="9"/><line x1="12" y1="8" x2="12" y2="12"/><circle cx="12" cy="16" r="0.5" fill="#F8C61E"/></svg>',
}

def card_html(icon, tag_cls, tag_txt, idx, title, desc, goto, url):
    """Single card — target="_parent" navigates the Streamlit parent frame."""
    return f"""
    <a class="mod-card" href="{url}" target="_parent">
      {SVG[icon]}
      <div class="card-tag {tag_cls}">{tag_txt}</div>
      <div class="card-index">{idx}</div>
      <div class="card-title">{title}</div>
      <p class="card-desc">{desc}</p>
      <span class="card-cta">Open &rarr;</span>
    </a>"""

def card_section(bg, cards_html, height=420):
    """Renders card grid via components.html — bypasses Streamlit HTML sanitizer."""
    html = f"""<!DOCTYPE html>
<html><head>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
{SHARED_CSS}
html, body {{ background: {bg}; overflow: hidden; margin: 0; padding: 0; }}
.wrap {{
  background: {bg};
  padding: 1rem clamp(1.2rem, 5vw, 4rem) 2.5rem;
  max-width: 1160px;
  margin: 0 auto;
  box-sizing: border-box;
  width: 100%;
}}
</style>
</head>
<body>
<div class="wrap">
  <div class="card-grid">{cards_html}</div>
</div>
</body></html>"""
    components.html(html, height=height, scrolling=False)

# ── Global page CSS (applied to st.markdown sections) ────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,600&display=swap');

*, *::before, *::after { box-sizing: border-box !important; }

:root {
  --bg:      #252C37;
  --bg2:     #1E242E;
  --surface: rgba(42,51,64,0.72);
  --border:  rgba(255,255,255,0.07);
  --accent:  #F8C61E;
  --text:    #DDE3EC;
  --muted:   #7A8799;
  --radius:  12px;
  --pad:     clamp(1.2rem, 5vw, 4rem);
  --maxw:    1160px;
}

#MainMenu, header, footer { visibility: hidden !important; }
section[data-testid="stSidebar"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"] { display: none !important; }

.block-container,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"],
[data-testid="stVerticalBlock"] {
  padding: 0 !important; margin: 0 !important;
  max-width: 100% !important; min-width: 0 !important; width: 100% !important;
}

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {
  background: var(--bg) !important;
  font-family: 'DM Sans', sans-serif;
  color: var(--text); overflow-x: hidden !important;
}

/* Remove iframe border/shadow that components.html adds */
iframe { border: none !important; display: block !important; }

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: var(--bg2); }
::-webkit-scrollbar-thumb { background: rgba(248,198,30,0.35); border-radius: 2px; }

.divider { border: none; border-top: 1px solid var(--border); margin: 0; display: block; }

/* Shared section containers */
.S     { width: 100%; overflow: hidden; }
.S.alt { background: var(--bg2); }
.W     { max-width: var(--maxw); margin: 0 auto; padding: 4rem var(--pad); width: 100%; }
.W.nb  { padding-bottom: 0.5rem; }

.sec-label {
  display: block; font-size: 0.64rem; font-weight: 600;
  letter-spacing: 0.16em; text-transform: uppercase;
  color: var(--accent); margin-bottom: 0.55rem;
}
.sec-heading {
  font-family: 'Syne', sans-serif; font-weight: 800;
  font-size: clamp(1.5rem, 2.6vw, 2.3rem);
  letter-spacing: -0.025em; color: var(--text);
  margin: 0 0 0.7rem; line-height: 1.15;
}
.sec-body { font-size: 0.87rem; font-weight: 300; color: var(--muted); line-height: 1.75; max-width: 400px; }

/* ── NAVBAR ── */
.navbar {
  position: fixed; top: 0; left: 0; right: 0; z-index: 9999;
  height: 58px; display: flex; align-items: center; justify-content: space-between;
  padding: 0 var(--pad);
  background: rgba(28,34,44,0.92);
  backdrop-filter: blur(24px); -webkit-backdrop-filter: blur(24px);
  border-bottom: 1px solid var(--border); width: 100%;
}
.nav-logo { display: flex; align-items: center; text-decoration: none; flex-shrink: 0; }
.nav-logo img { height: 27px; width: auto; max-width: 130px; object-fit: contain; display: block; }
.nav-logo-text { font-family: 'Syne', sans-serif; font-weight: 800; font-size: 1rem; color: var(--text); }
.nav-logo-text span { color: var(--accent); }
.nav-links { display: flex; align-items: center; gap: clamp(0.8rem, 1.8vw, 1.8rem); }
.nav-links a { color: var(--muted); text-decoration: none; font-size: 0.80rem; font-weight: 500; white-space: nowrap; transition: color 0.18s; }
.nav-links a:hover { color: var(--text); }
.nav-pill {
  background: var(--accent) !important; color: #18202A !important;
  font-weight: 600 !important; font-size: 0.74rem !important;
  padding: 0.30rem 0.88rem !important; border-radius: 6px !important;
  white-space: nowrap !important; transition: opacity 0.18s !important;
}
.nav-pill:hover { opacity: 0.84 !important; color: #18202A !important; }
.top-spacer { height: 58px; display: block; }

/* ── HERO ── */
.hero {
  min-height: 92vh; width: 100%;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  text-align: center; padding: 6rem var(--pad) 5rem;
  position: relative; overflow: hidden;
}
.hero::before {
  content: ''; position: absolute; inset: 0;
  background-image: radial-gradient(circle, rgba(248,198,30,0.09) 1px, transparent 1px);
  background-size: 36px 36px;
  mask-image: radial-gradient(ellipse 80% 70% at 50% 50%, black 0%, transparent 100%);
  pointer-events: none;
}
.hero-tag {
  display: inline-block; border: 1px solid rgba(248,198,30,0.22); color: var(--accent);
  font-size: 0.63rem; font-weight: 600; letter-spacing: 0.16em; text-transform: uppercase;
  padding: 0.23rem 0.78rem; border-radius: 4px; margin-bottom: 1.7rem;
  animation: up 0.5s ease both; position: relative; z-index: 1;
}
.hero-logo {
  display: block; height: clamp(55px, 8.5vw, 100px);
  width: auto; max-width: min(320px, 82vw);
  margin: 0 auto 0.5rem; object-fit: contain;
  animation: up 0.5s 0.07s ease both; position: relative; z-index: 1;
  filter: drop-shadow(0 0 18px rgba(248,198,30,0.12));
}
.hero-title {
  font-family: 'Syne', sans-serif; font-weight: 800;
  font-size: clamp(3rem, 8vw, 6.2rem); line-height: 1;
  letter-spacing: -0.04em; color: var(--text); margin: 0;
  animation: up 0.5s 0.07s ease both; position: relative; z-index: 1;
}
.hero-title span { color: var(--accent); }
.hero-sub {
  font-size: clamp(0.85rem, 1.6vw, 1rem); font-weight: 300; color: var(--muted);
  margin: 1.1rem auto 2.2rem; max-width: 370px; line-height: 1.72;
  animation: up 0.5s 0.14s ease both; position: relative; z-index: 1;
}
.hero-actions { display: flex; gap: 0.65rem; justify-content: center; flex-wrap: wrap; animation: up 0.5s 0.21s ease both; position: relative; z-index: 1; }
.btn-primary { display: inline-flex; align-items: center; background: var(--accent); color: #18202A !important; font-weight: 600; font-size: 0.79rem; padding: 0.60rem 1.4rem; border-radius: 7px; text-decoration: none !important; white-space: nowrap; transition: opacity 0.18s, transform 0.18s; }
.btn-primary:hover { opacity: 0.88; transform: translateY(-2px); }
.btn-ghost { display: inline-flex; align-items: center; background: transparent; color: var(--text) !important; font-weight: 500; font-size: 0.79rem; padding: 0.60rem 1.4rem; border-radius: 7px; text-decoration: none !important; white-space: nowrap; border: 1px solid var(--border); transition: border-color 0.18s, transform 0.18s; }
.btn-ghost:hover { border-color: rgba(248,198,30,0.28); transform: translateY(-2px); }

.stats-row {
  display: flex; align-items: stretch; flex-wrap: wrap; margin-top: 3rem;
  border: 1px solid var(--border); border-radius: var(--radius);
  background: rgba(28,34,44,0.68); backdrop-filter: blur(12px);
  overflow: hidden; width: fit-content; max-width: 100%;
  margin-left: auto; margin-right: auto;
  animation: up 0.5s 0.28s ease both; position: relative; z-index: 1;
}
.stat-cell { padding: 0.88rem clamp(0.8rem, 1.8vw, 1.6rem); text-align: center; border-right: 1px solid var(--border); min-width: 0; }
.stat-cell:last-child { border-right: none; }
.stat-num { font-family: 'Syne', sans-serif; font-weight: 800; font-size: clamp(1rem, 2vw, 1.3rem); color: var(--accent); line-height: 1; }
.stat-lbl { font-size: 0.57rem; color: var(--muted); letter-spacing: 0.08em; text-transform: uppercase; margin-top: 0.18rem; }

/* ── FEATURE GRID ── */
.feat-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(195px, 100%), 1fr)); gap: 1px; border: 1px solid var(--border); border-radius: var(--radius); overflow: hidden; background: var(--border); margin-top: 2.5rem; width: 100%; }
.feat-item { background: var(--bg); padding: 1.55rem 1.4rem; min-width: 0; transition: background 0.2s; }
.feat-item:hover { background: #2b3343; }
.feat-icon  { width: 22px; height: 22px; margin-bottom: 0.85rem; opacity: 0.75; display: block; }
.feat-title { font-family: 'Syne', sans-serif; font-weight: 700; font-size: 0.87rem; color: var(--text); margin-bottom: 0.36rem; }
.feat-desc  { font-size: 0.76rem; color: var(--muted); line-height: 1.65; }

/* ── COMING SOON ── */
.soon-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(185px, 100%), 1fr)); gap: 1px; border: 1px solid var(--border); border-radius: var(--radius); overflow: hidden; background: var(--border); margin-top: 2.4rem; width: 100%; }
.soon-item { background: var(--bg2); padding: 1.5rem 1.3rem; min-width: 0; transition: background 0.2s; }
.soon-item:hover { background: #1a2028; }
.soon-qtr   { font-size: 0.56rem; font-weight: 600; letter-spacing: 0.14em; text-transform: uppercase; color: var(--accent); margin-bottom: 0.6rem; }
.soon-title { font-family: 'Syne', sans-serif; font-weight: 700; font-size: 0.87rem; color: var(--text); margin-bottom: 0.34rem; }
.soon-desc  { font-size: 0.74rem; color: var(--muted); line-height: 1.6; }

/* ── ABOUT ── */
.about-inner { max-width: 560px; margin: 0 auto; text-align: center; padding: 4.5rem var(--pad); }
.about-inner p { font-size: 0.88rem; font-weight: 300; color: var(--muted); line-height: 1.85; margin-top: 1rem; }

/* ── ROADMAP ── */
.roadmap-wrap { max-width: var(--maxw); margin: 0 auto; padding: 0 var(--pad) 3.5rem; width: 100%; overflow: hidden; }

/* ── FOOTER ── */
.site-footer { background: var(--bg2); border-top: 1px solid var(--border); padding: 1.5rem var(--pad); display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 0.75rem; width: 100%; }
.footer-brand { font-family: 'Syne', sans-serif; font-weight: 800; font-size: 0.87rem; color: var(--text); }
.footer-brand span { color: var(--accent); }
.footer-meta  { font-size: 0.71rem; color: var(--muted); }
.footer-nav   { display: flex; gap: 1.1rem; flex-wrap: wrap; }
.footer-nav a { font-size: 0.71rem; color: var(--muted); text-decoration: none; white-space: nowrap; transition: color 0.18s; }
.footer-nav a:hover { color: var(--text); }

@media (max-width: 680px) {
  .nav-links a:not(.nav-pill) { display: none; }
  .hero-actions { flex-direction: column; align-items: center; }
  .stats-row { width: 100%; }
  .stat-cell { flex: 1 1 64px; }
  .site-footer { flex-direction: column; align-items: flex-start; }
}

@keyframes up {
  from { opacity: 0; transform: translateY(14px); }
  to   { opacity: 1; transform: translateY(0); }
}
</style>
""", unsafe_allow_html=True)

# ── Page-level SVG icons (for st.markdown sections) ──────────────────────────
FEAT_ICONS = {
    "bolt":   '<svg class="feat-icon" viewBox="0 0 24 24" fill="none" stroke="#F8C61E" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg>',
    "wave":   '<svg class="feat-icon" viewBox="0 0 24 24" fill="none" stroke="#F8C61E" stroke-width="1.6" stroke-linecap="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>',
    "layers": '<svg class="feat-icon" viewBox="0 0 24 24" fill="none" stroke="#F8C61E" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/></svg>',
    "grid":   '<svg class="feat-icon" viewBox="0 0 24 24" fill="none" stroke="#F8C61E" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>',
}

# ── Logo helpers ──────────────────────────────────────────────────────────────
_nav_logo = (
    f'<img src="{LOGO_B64}" alt="Structor" />' if LOGO_B64
    else '<span class="nav-logo-text">Structor<span>.</span></span>'
)
_hero_logo = (
    f'<img class="hero-logo" src="{LOGO_B64}" alt="Structor" />' if LOGO_B64
    else '<h1 class="hero-title">Structor<span>.</span></h1>'
)
_footer_logo = (
    f'<img src="{LOGO_B64}" alt="Structor" style="height:20px;width:auto;opacity:0.78;display:block;" />'
    if LOGO_B64 else '<span class="footer-brand">Structor<span>.</span></span>'
)


# ══════════════════════════════════════════════════════════════════════════════
# NAVBAR
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="navbar">
  <a href="/" class="nav-logo">{_nav_logo}</a>
  <nav class="nav-links">
    <a href="#features">Features</a>
    <a href="#apps">Modules</a>
    <a href="#roadmap">Roadmap</a>
    <a href="#about">About</a>
    <a href="?goto=beam" class="nav-pill">Launch</a>
  </nav>
</div>
<div class="top-spacer"></div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# HERO
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<section class="hero" id="home">
  <div class="hero-tag">Structural Engineering Platform</div>
  {_hero_logo}
  <p class="hero-sub">Professional structural analysis and RC design — precise, visual, browser-based.</p>
  <div class="hero-actions">
    <a href="?goto=beam" class="btn-primary">Get Started</a>
    <a href="#apps"      class="btn-ghost">View Modules</a>
  </div>
  <div class="stats-row">
    <div class="stat-cell"><div class="stat-num">5</div><div class="stat-lbl">Modules</div></div>
    <div class="stat-cell"><div class="stat-num">2D</div><div class="stat-lbl">Analysis</div></div>
    <div class="stat-cell"><div class="stat-num">RC</div><div class="stat-lbl">Design</div></div>
  </div>
</section>
""", unsafe_allow_html=True)

st.markdown('<hr class="divider"/>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# FEATURES
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="S" id="features">
  <div class="W">
    <span class="sec-label">Capabilities</span>
    <h2 class="sec-heading">Built around real<br/>engineering workflows.</h2>
    <p class="sec-body">Every module is purpose-built — no general tools, no compromises on accuracy.</p>
    <div class="feat-grid">
      <div class="feat-item">{FEAT_ICONS['bolt']}<div class="feat-title">Instant Computation</div><p class="feat-desc">Shear force, bending moment, deflection and reactions computed in real time.</p></div>
      <div class="feat-item">{FEAT_ICONS['wave']}<div class="feat-title">Interactive Diagrams</div><p class="feat-desc">SFD, BMD, deflection and force diagrams — hover, zoom, inspect values.</p></div>
      <div class="feat-item">{FEAT_ICONS['layers']}<div class="feat-title">RC Design Suite</div><p class="feat-desc">Code-based RC column design with automatic Word calculation report output.</p></div>
      <div class="feat-item">{FEAT_ICONS['grid']}<div class="feat-title">Modular Platform</div><p class="feat-desc">Independent modules — beam, frame, section, columns — one design language.</p></div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<hr class="divider"/>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# STRUCTURAL ANALYSIS — section header via st.markdown, cards via components.html
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="S" id="apps">
  <div class="W nb">
    <span class="sec-label">Structural Analysis</span>
    <h2 class="sec-heading">Analysis Modules.</h2>
    <p class="sec-body">Click any module to launch it. Each tool is self-contained.</p>
  </div>
</div>
""", unsafe_allow_html=True)

sa_html = (
    card_html("beam",    "tag-live", "v2.2", "Module 01", "Beam Analysis",
              "Simply supported, cantilever and continuous beams. Point loads, UDLs, moments. SFD, BMD and deflection.",
              "beam", "/beam_analysis_v2_2") +
    card_html("frame",   "tag-live", "Live (Beta)", "Module 02", "Frame Analysis",
              "2D frame solver via Pynite FEM Package. Member forces, joint reactions and deformed shape.",
              "frame", "/frame_analysis_v1") +
    card_html("section", "tag-live", "Live", "Module 03", "Section Properties",
              "Area, centroid, moment of inertia and section modulus for standard and custom cross-sections.",
              "section", "/main_section_prop_calc")
)
card_section(bg="#252C37", cards_html=sa_html, height=440)

st.markdown('<hr class="divider"/>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# RC DESIGN — section header + cards
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="S alt">
  <div class="W nb">
    <span class="sec-label">RC Design</span>
    <h2 class="sec-heading">Design Modules.</h2>
    <p class="sec-body">Code-based reinforced concrete design with automated calculations and output.</p>
  </div>
</div>
""", unsafe_allow_html=True)

rc_html = (
    card_html("column", "tag-rc",   "Live", "Module 04", "Short Column Design",
              "Axial load for short RC columns. Generates a formatted Word calculation report.",
              "rc_short", "/short_column_design") +
    card_html("tall",   "tag-rc", "Live",      "Module 05", "Slender Column Design",
              "Design of slender RC columns. Moment magnification per code provisions.",
              "rc_slender", "/slender_column_design")
    # card_html("info",   "tag-info", "Info",      "About",     "About Structor",
    #           "Platform overview, development background and guidance on getting the most from each module.",
    #           "about", "/about_app")
)
card_section(bg="#1E242E", cards_html=rc_html, height=440)

st.markdown('<hr class="divider"/>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# ROADMAP
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="S alt" id="roadmap">
  <div class="W nb">
    <span class="sec-label">Product Roadmap</span>
    <h2 class="sec-heading">What's next.</h2>
    <p class="sec-body">From current modules to a fully integrated structural design platform.</p>
  </div>
</div>
""", unsafe_allow_html=True)

roadmap_option = {
    "backgroundColor": "transparent",
    "tooltip": {
        "trigger": "item", "triggerOn": "mousemove",
        "backgroundColor": "rgba(22,28,36,0.96)",
        "borderColor": "rgba(248,198,30,0.22)", "borderWidth": 1,
        "textStyle": {"color": "#DDE3EC", "fontFamily": "DM Sans", "fontSize": 12},
    },
    "series": [{
        "type": "tree",
        "data": [{
            "name": "Structor",
            "itemStyle": {"color": "#F8C61E", "borderColor": "#F8C61E", "borderWidth": 2},
            "children": [
                {
                    "name": "Released",
                    "itemStyle": {"color": "#4ade80", "borderColor": "#4ade80"},
                    "children": [
                        {"name": "Beam Analysis v2.2"}, {"name": "Frame Analysis v1"},
                        {"name": "Section Properties"}, {"name": "Short Column Design"},
                        {"name": "Slender Column Design"},
                    ],
                },
                {
                    "name": "In Progress",
                    "itemStyle": {"color": "#fb923c", "borderColor": "#fb923c"},
                    "children": [
                        {"name": "RC Beam Design"}, {"name": "Steel Design"},
                        {"name": "PDF Export Engine"},
                    ],
                },
                {
                    "name": "Planned",
                    "itemStyle": {"color": "#a5b4fc", "borderColor": "#a5b4fc"},
                    "children": [
                        {"name": "More RC Design Modules"}, {"name": "Steel Design Modules"},
                        {"name": "Material and Cost Optimization"}, {"name": "More Analysis Options"},
                    ],
                },
            ],
        }],
        "top": "6%", "left": "14%", "bottom": "6%", "right": "20%",
        "symbolSize": 7,
        "label": {"position": "left", "verticalAlign": "middle", "align": "right",
                  "fontSize": 12, "color": "#DDE3EC", "fontFamily": "DM Sans"},
        "leaves": {"label": {"position": "right", "verticalAlign": "middle", "align": "left",
                              "color": "#7A8799", "fontSize": 11}},
        "itemStyle": {"color": "#F8C61E", "borderColor": "#F8C61E", "borderWidth": 1.5},
        "lineStyle": {"color": "rgba(248,198,30,0.18)", "width": 1.2, "curveness": 0.5},
        "emphasis": {"focus": "descendant", "itemStyle": {"color": "#FFD84D"}, "label": {"color": "#F8C61E"}},
        "expandAndCollapse": True, "animationDuration": 400, "animationDurationUpdate": 600,
    }],
}

st.markdown('<div class="S alt"><div class="roadmap-wrap">', unsafe_allow_html=True)
st_echarts(options=roadmap_option, height="430px")
st.markdown('</div></div>', unsafe_allow_html=True)

st.markdown('<hr class="divider"/>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# ABOUT
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="S" id="about">
  <div class="about-inner">
    <span class="sec-label" style="text-align:center;">About</span>
    <h2 class="sec-heading" style="text-align:center;">What is Structor?</h2>
    <p>Structor is a web-based structural analysis and design platform for civil and structural engineers, specially students.
       Professional-grade computation in the browser — no installation, no license fees.</p>
    <p>Each module pairs rigorous engineering mathematics with a clean, minimal interface.
       Built with Python and Streamlit by Hamza Ali as a growing open-source engineering toolkit.</p>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<hr class="divider"/>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# COMING SOON
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="S alt">
  <div class="W">
    <span class="sec-label">Coming Soon</span>
    <h2 class="sec-heading">In development.</h2>
    <p class="sec-body">Modules currently being designed and built.</p>
    <div class="soon-grid">
      <div class="soon-item"><div class="soon-qtr">Coming Soon</div><div class="soon-title">More R.C Design Modules</div><p class="soon-desc">Reinforced Concrete analysis and reinforcement design per ACI code provisions.</p></div>
      <div class="soon-item"><div class="soon-qtr">Coming Soon</div><div class="soon-title">Steel Design Modules</div><p class="soon-desc">Design of steel elements and connection as per AISC LRFD design methods.</p></div>
      <div class="soon-item"><div class="soon-qtr">Coming Soon</div><div class="soon-title">More Analysis Options</div><p class="soon-desc">Planned for adding more analysis options like Response Spectrum and Modal Analysis.</p></div>
      <div class="soon-item"><div class="soon-qtr">Coming Soon</div><div class="soon-title">Material and Cost Optimization</div><p class="soon-desc">Section and reinforcement optimization techniques.</p></div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="site-footer" id="contact">
  <div>{_footer_logo}</div>
  <div class="footer-meta">© 2026 · Built by Ameer Hamza Ali</div>
  <nav class="footer-nav">
    <a href="https://www.linkedin.com/in/hamza-ali-3011" target="_blank">LinkedIn</a>
    <a href="https://github.com/HamzaAlee3011/Structor_Streamlit" target="_blank">GitHub</a>
    <a href="#home">Top</a>
</div>
""", unsafe_allow_html=True)