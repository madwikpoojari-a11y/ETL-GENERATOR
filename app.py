"""
app.py — ETL-GENERATOR AGENT
Enterprise Data Operations Dashboard
RiskGraph-inspired dark premium UI
"""

import os, sys, json, re, time
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "app"))

from pipeline_controller import run_pipeline
from src.loading.db_loader import list_tables, query_table
from src.utils.config import LOG_FILE_PATH, REPORTS_DIR, DATA_DIR

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ETL-GENERATOR · Data Operations",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── THEME CONSTANTS ───────────────────────────────────────────────────────────
THEME = {
    "bg":         "#0B1020",
    "surface":    "#121826",
    "card":       "#1E293B",
    "border":     "#334155",
    "aqua":       "#6BBAA7",
    "aqua_dim":   "#3D8C7A",
    "gold":       "#FBA100",
    "gold_dim":   "#A36B00",
    "lavender":   "#6C648B",
    "rose":       "#B6A19E",
    "text":       "#F8FAFC",
    "text_muted": "#CBD5E1",
    "success":    "#22C55E",
    "warning":    "#F59E0B",
    "error":      "#EF4444",
    "blue":       "#3B82F6",
}

# ── GLOBAL CSS ────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* ── Reset ── */
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body, [class*="css"] {{ font-family: 'Inter', sans-serif !important; }}

/* ── App background ── */
.stApp {{ background-color: {THEME['bg']}; color: {THEME['text']}; }}
.main .block-container {{ padding: 1.5rem 2rem 3rem 2rem !important; max-width: 1400px !important; }}

/* ── Sidebar ── */
[data-testid="stSidebar"] {{
    background: {THEME['surface']} !important;
    border-right: 1px solid {THEME['border']};
    min-width: 240px !important;
    max-width: 240px !important;
}}
[data-testid="stSidebar"] * {{ color: {THEME['text_muted']} !important; }}
[data-testid="stSidebar"] hr {{ border-color: {THEME['border']} !important; }}
[data-testid="stSidebar"] [data-testid="stRadio"] > label {{ display: none; }}
[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] {{
    display: flex; flex-direction: column; gap: 2px;
}}
[data-testid="stSidebar"] [data-testid="stRadio"] label {{
    display: flex !important;
    align-items: center;
    padding: 10px 16px !important;
    border-radius: 8px !important;
    font-size: 0.875rem !important;
    font-weight: 500 !important;
    color: {THEME['text_muted']} !important;
    cursor: pointer;
    transition: all 0.15s ease;
    border: 1px solid transparent;
}}
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {{
    background: rgba(107,186,167,0.1) !important;
    color: {THEME['aqua']} !important;
    border-color: rgba(107,186,167,0.2) !important;
}}
[data-testid="stSidebar"] [data-testid="stRadio"] [data-checked="true"] + div label,
[data-testid="stSidebar"] [aria-checked="true"] {{
    background: rgba(107,186,167,0.15) !important;
    color: {THEME['aqua']} !important;
    border-left: 3px solid {THEME['aqua']} !important;
    font-weight: 600 !important;
}}

/* ── Typography ── */
h1 {{ font-size: 1.6rem !important; font-weight: 800 !important; color: {THEME['text']} !important; letter-spacing: -0.03em; }}
h2 {{ font-size: 1.25rem !important; font-weight: 700 !important; color: {THEME['text']} !important; }}
h3 {{ font-size: 1rem !important; font-weight: 600 !important; color: {THEME['text_muted']} !important; }}
p, li {{ color: {THEME['text_muted']} !important; font-size: 0.9rem; }}

/* ── Metric cards ── */
[data-testid="metric-container"] {{
    background: {THEME['card']} !important;
    border: 1px solid {THEME['border']} !important;
    border-radius: 10px !important;
    padding: 1.25rem !important;
}}
[data-testid="stMetricLabel"] {{
    font-size: 0.7rem !important; font-weight: 600 !important;
    text-transform: uppercase; letter-spacing: 0.08em;
    color: {THEME['text_muted']} !important;
}}
[data-testid="stMetricValue"] {{
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 1.75rem !important; font-weight: 700 !important;
    color: {THEME['text']} !important;
}}
[data-testid="stMetricDelta"] {{ font-size: 0.78rem !important; font-weight: 600 !important; }}

/* ── Buttons ── */
.stButton > button {{
    background: {THEME['aqua']} !important; color: #0B1020 !important;
    border: none !important; border-radius: 8px !important;
    font-weight: 700 !important; font-size: 0.875rem !important;
    padding: 0.6rem 1.5rem !important;
    transition: all 0.2s ease !important;
    letter-spacing: 0.02em;
}}
.stButton > button:hover {{
    background: {THEME['aqua_dim']} !important;
    box-shadow: 0 0 24px rgba(107,186,167,0.5) !important;
    transform: translateY(-1px) !important;
}}
.stButton > button[kind="primary"] {{
    background: {THEME['gold']} !important; color: #0B1020 !important;
}}
.stButton > button[kind="primary"]:hover {{
    background: {THEME['gold_dim']} !important;
    box-shadow: 0 0 24px rgba(251,161,0,0.5) !important;
}}

/* ── Download buttons ── */
.stDownloadButton > button {{
    background: {THEME['card']} !important; color: {THEME['aqua']} !important;
    border: 1px solid {THEME['aqua']} !important; border-radius: 8px !important;
    font-weight: 600 !important;
}}
.stDownloadButton > button:hover {{
    background: rgba(107,186,167,0.1) !important;
}}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {{
    background: {THEME['surface']} !important;
    border: 1px solid {THEME['border']} !important;
    border-radius: 10px !important; padding: 6px !important; gap: 4px !important;
}}
.stTabs [data-baseweb="tab"] {{
    background: transparent !important; border-radius: 7px !important;
    color: {THEME['text_muted']} !important; font-weight: 600 !important;
    font-size: 0.82rem !important; padding: 8px 16px !important;
    border: none !important;
}}
.stTabs [aria-selected="true"] {{
    background: {THEME['aqua']} !important; color: #0B1020 !important;
}}
[data-testid="stTabsContent"] {{ padding-top: 1.25rem !important; }}

/* ── Inputs ── */
.stTextInput input, .stSelectbox select {{
    background: {THEME['card']} !important; color: {THEME['text']} !important;
    border: 1px solid {THEME['border']} !important; border-radius: 8px !important;
    font-size: 0.875rem !important;
}}
.stTextInput input:focus {{
    border-color: {THEME['aqua']} !important;
    box-shadow: 0 0 0 3px rgba(107,186,167,0.2) !important;
}}
[data-baseweb="select"] > div {{
    background: {THEME['card']} !important; border: 1px solid {THEME['border']} !important;
    border-radius: 8px !important; color: {THEME['text']} !important;
}}

/* ── File uploader ── */
[data-testid="stFileUploader"] > section {{
    background: {THEME['card']} !important;
    border: 2px dashed {THEME['border']} !important;
    border-radius: 12px !important;
    transition: border-color 0.2s;
}}
[data-testid="stFileUploader"] > section:hover {{
    border-color: {THEME['aqua']} !important;
}}

/* ── Alerts ── */
.stSuccess > div {{ background: rgba(34,197,94,0.08) !important; border-left: 3px solid {THEME['success']} !important; border-radius: 8px !important; }}
.stWarning > div {{ background: rgba(245,158,11,0.08) !important; border-left: 3px solid {THEME['warning']} !important; border-radius: 8px !important; }}
.stError > div   {{ background: rgba(239,68,68,0.08) !important;  border-left: 3px solid {THEME['error']}   !important; border-radius: 8px !important; }}
.stInfo > div    {{ background: rgba(59,130,246,0.08) !important;  border-left: 3px solid {THEME['blue']}    !important; border-radius: 8px !important; }}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {{
    border: 1px solid {THEME['border']} !important; border-radius: 10px !important; overflow: hidden !important;
}}

/* ── Progress bar ── */
.stProgress > div > div > div {{ background: {THEME['aqua']} !important; }}

/* ── Expander ── */
[data-testid="stExpander"] {{
    background: {THEME['card']} !important; border: 1px solid {THEME['border']} !important; border-radius: 10px !important;
}}
[data-testid="stExpander"] summary {{ color: {THEME['text']} !important; font-weight: 600 !important; }}

/* ── Custom classes ── */
.etl-card {{
    background: {THEME['card']}; border: 1px solid {THEME['border']};
    border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem;
    transition: border-color 0.2s, box-shadow 0.2s;
}}
.etl-card:hover {{
    border-color: rgba(107,186,167,0.4);
    box-shadow: 0 4px 24px rgba(0,0,0,0.3);
}}
.etl-card-aqua   {{ border-left: 3px solid {THEME['aqua']}; }}
.etl-card-gold   {{ border-left: 3px solid {THEME['gold']}; }}
.etl-card-lav    {{ border-left: 3px solid {THEME['lavender']}; }}
.etl-card-rose   {{ border-left: 3px solid {THEME['rose']}; }}
.etl-card-green  {{ border-left: 3px solid {THEME['success']}; }}
.etl-card-red    {{ border-left: 3px solid {THEME['error']}; }}

.section-label {{
    font-size: 0.7rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.1em; color: {THEME['text_muted']}; margin-bottom: 1rem;
}}
.section-divider {{
    height: 1px; background: {THEME['border']}; margin: 1.75rem 0;
}}
.mono {{ font-family: 'JetBrains Mono', monospace !important; }}

.kpi-card {{
    background: {THEME['card']}; border: 1px solid {THEME['border']};
    border-radius: 12px; padding: 1.25rem 1.5rem;
    display: flex; flex-direction: column; gap: 6px;
    transition: all 0.2s ease;
}}
.kpi-card:hover {{
    border-color: rgba(107,186,167,0.4);
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
    transform: translateY(-2px);
}}
.kpi-label {{ font-size: 0.68rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; color: {THEME['text_muted']}; }}
.kpi-value {{ font-family: 'JetBrains Mono', monospace; font-size: 2rem; font-weight: 700; color: {THEME['text']}; line-height: 1; }}
.kpi-delta {{ font-size: 0.75rem; font-weight: 600; }}
.kpi-delta.up   {{ color: {THEME['success']}; }}
.kpi-delta.down {{ color: {THEME['error']}; }}
.kpi-delta.neu  {{ color: {THEME['text_muted']}; }}

.pipeline-node {{
    background: {THEME['card']}; border: 1px solid {THEME['border']};
    border-radius: 10px; padding: 1rem 0.75rem;
    text-align: center; transition: all 0.25s ease;
    position: relative;
}}
.pipeline-node.done  {{ border-color: {THEME['success']}; background: rgba(34,197,94,0.06); }}
.pipeline-node.run   {{ border-color: {THEME['blue']};    background: rgba(59,130,246,0.06); animation: pulse 1.5s infinite; }}
.pipeline-node.warn  {{ border-color: {THEME['warning']}; background: rgba(245,158,11,0.06); }}
.pipeline-node.fail  {{ border-color: {THEME['error']};   background: rgba(239,68,68,0.06); }}
.pipeline-node.idle  {{ border-color: {THEME['border']};  opacity: 0.6; }}
@keyframes pulse {{ 0%,100%{{ box-shadow:0 0 0 0 rgba(59,130,246,0.4); }} 50%{{ box-shadow:0 0 0 8px rgba(59,130,246,0); }} }}

.node-icon  {{ font-size: 1.75rem; margin-bottom: 6px; }}
.node-name  {{ font-size: 0.75rem; font-weight: 700; color: {THEME['text']}; margin-bottom: 2px; }}
.node-desc  {{ font-size: 0.62rem; color: {THEME['text_muted']}; }}
.node-tick  {{ font-size: 0.85rem; margin-top: 6px; font-weight: 700; }}

.heal-card {{
    background: {THEME['surface']}; border: 1px solid {THEME['border']};
    border-radius: 10px; padding: 1rem 1.25rem; margin-bottom: 8px;
    transition: border-color 0.2s;
}}
.heal-card.healed  {{ border-left: 3px solid {THEME['success']}; }}
.heal-card.partial {{ border-left: 3px solid {THEME['warning']}; }}
.heal-card.unres   {{ border-left: 3px solid {THEME['text_muted']}; }}
.heal-rule   {{ font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; }}
.heal-action {{ font-size: 0.85rem; font-weight: 500; color: {THEME['text']}; margin: 2px 0; }}
.heal-time   {{ font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: {THEME['text_muted']}; }}

.timeline-row {{
    display: flex; align-items: flex-start; gap: 1rem; padding: 0.75rem 0;
    border-bottom: 1px solid rgba(51,65,85,0.5);
}}
.timeline-dot {{
    width: 10px; height: 10px; border-radius: 50%;
    margin-top: 4px; flex-shrink: 0;
}}
.timeline-time {{ font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: {THEME['text_muted']}; min-width: 80px; }}
.timeline-msg  {{ font-size: 0.84rem; color: {THEME['text']}; }}

.score-ring-wrap {{ text-align: center; padding: 1rem; }}

/* ── Hide chrome ── */
#MainMenu, footer, header[data-testid="stHeader"] {{ visibility: hidden; }}
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
for k, v in [("pipeline_results", None), ("uploaded_df", None),
             ("file_name", None), ("uploaded_source", None)]:
    if k not in st.session_state:
        st.session_state[k] = v


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def plotly_config():
    return {"displayModeBar": False, "responsive": True}

def plotly_layout(**kwargs):
    base = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color=THEME["text_muted"], size=11),
        margin=dict(l=0, r=0, t=30, b=0),
        showlegend=False,
    )
    base.update(kwargs)
    return base

def gauge_chart(value, title, color=None):
    color = color or THEME["aqua"]
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={"text": title, "font": {"size": 11, "color": THEME["text_muted"]}},
        number={"font": {"size": 36, "family": "JetBrains Mono", "color": THEME["text"]},
                "suffix": "%"},
        gauge={
            "axis": {
                "range": [0, 100],
                "tickcolor": THEME["text_muted"],
                "tickfont": {"size": 9},
                "nticks": 6,
            },
            "bar": {"color": color, "thickness": 0.65},
            "bgcolor": THEME["card"],
            "bordercolor": THEME["border"],
            "borderwidth": 1,
            "steps": [
                {"range": [0,  40], "color": "rgba(239,68,68,0.12)"},
                {"range": [40, 70], "color": "rgba(245,158,11,0.12)"},
                {"range": [70,100], "color": "rgba(34,197,94,0.08)"},
            ],
            "threshold": {
                "line": {"color": color, "width": 2},
                "thickness": 0.8,
                "value": value,
            },
        },
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color=THEME["text_muted"], size=11),
        height=260,
        margin=dict(l=20, r=20, t=40, b=30),
    )
    return fig

def bar_chart(x, y, title, color=None, horizontal=False):
    color = color or THEME["aqua"]
    if horizontal:
        fig = go.Figure(go.Bar(
            x=y, y=x, orientation="h",
            marker=dict(color=color, opacity=0.85,
                        line=dict(color=THEME["border"], width=0)),
        ))
    else:
        fig = go.Figure(go.Bar(
            x=x, y=y,
            marker=dict(color=color, opacity=0.85,
                        line=dict(color=THEME["border"], width=0)),
        ))
    fig.update_layout(**plotly_layout(
        title=dict(text=title, font=dict(size=12)),
        height=260,
        xaxis=dict(gridcolor=THEME["border"], zeroline=False),
        yaxis=dict(gridcolor=THEME["border"], zeroline=False),
    ))
    return fig

def donut_chart(labels, values, title):
    colors = [THEME["aqua"], THEME["gold"], THEME["lavender"], THEME["rose"],
              THEME["success"], THEME["error"]]
    fig = go.Figure(go.Pie(
        labels=labels, values=values,
        hole=0.6,
        marker=dict(colors=colors[:len(labels)],
                    line=dict(color=THEME["bg"], width=2)),
        textfont=dict(size=10, color=THEME["text"]),
        textinfo="label+percent",
    ))
    fig.update_layout(**plotly_layout(
        title=dict(text=title, font=dict(size=12)),
        height=280,
        showlegend=True,
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=10)),
    ))
    return fig

def area_chart(x, y, title, color=None):
    color = color or THEME["aqua"]
    fig = go.Figure(go.Scatter(
        x=x, y=y, mode="lines",
        fill="tozeroy",
        line=dict(color=color, width=2),
        fillcolor=f"rgba(107,186,167,0.1)",
    ))
    fig.update_layout(**plotly_layout(
        title=dict(text=title, font=dict(size=12)),
        height=220,
        xaxis=dict(gridcolor=THEME["border"], zeroline=False),
        yaxis=dict(gridcolor=THEME["border"], zeroline=False),
    ))
    return fig

def kpi(label, value, delta=None, delta_dir="neu", icon=""):
    delta_html = ""
    if delta:
        arrow = "▲" if delta_dir == "up" else ("▼" if delta_dir == "down" else "—")
        delta_html = f"<div class='kpi-delta {delta_dir}'>{arrow} {delta}</div>"
    return f"""
    <div class="kpi-card">
        <div class="kpi-label">{icon} {label}</div>
        <div class="kpi-value">{value}</div>
        {delta_html}
    </div>
    """

def divider():
    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

def section_label(text):
    st.markdown(f"<div class='section-label'>{text}</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f"""
    <div style='padding:1.5rem 1rem 1.25rem;'>
        <div style='font-size:1.3rem;font-weight:900;color:{THEME["aqua"]};
             letter-spacing:-0.03em;line-height:1;'>⚡ ETL</div>
        <div style='font-size:1.3rem;font-weight:900;color:{THEME["text"]};
             letter-spacing:-0.03em;'>GENERATOR</div>
        <div style='font-size:0.7rem;color:{THEME["text_muted"]};margin-top:4px;
             letter-spacing:0.05em;'>DATA OPERATIONS PLATFORM</div>
    </div>
    <hr style='border:1px solid {THEME["border"]};margin:0 1rem 1rem;'>
    """, unsafe_allow_html=True)

    page = st.radio("nav", [
        "⬛  Command Center",
        "📂  Data Upload",
        "🔍  Validation",
        "🚀  Run Pipeline",
        "📊  Results & Reports",
    ], label_visibility="collapsed")

    # Status indicator
    res = st.session_state.get("pipeline_results")
    if res and res.get("status") == "success":
        s = res["summary"]
        clr = THEME["success"] if s["quality_score_after"] >= 80 else THEME["warning"]
        st.markdown(f"""
        <div style='margin:1.5rem 1rem 0;padding:1rem;background:{THEME["card"]};
             border-radius:10px;border:1px solid {THEME["border"]};'>
            <div style='font-size:0.65rem;color:{THEME["text_muted"]};text-transform:uppercase;
                 letter-spacing:.08em;margin-bottom:6px;'>LAST RUN</div>
            <div style='font-family:"JetBrains Mono",monospace;font-size:1.6rem;
                 font-weight:700;color:{clr};line-height:1;'>{s["quality_score_after"]:.0f}%</div>
            <div style='font-size:0.7rem;color:{THEME["text_muted"]};margin-top:3px;'>Quality Score</div>
            <div style='margin-top:8px;display:flex;gap:6px;flex-wrap:wrap;'>
                <span style='font-size:0.65rem;background:rgba(34,197,94,0.1);color:{THEME["success"]};
                      padding:2px 8px;border-radius:12px;border:1px solid rgba(34,197,94,0.3);'>
                    ● LOADED
                </span>
                <span style='font-size:0.65rem;color:{THEME["text_muted"]};'>{s["rows_loaded"]:,} rows</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style='margin:1.5rem 1rem 0;padding:1rem;background:{THEME["card"]};
             border-radius:10px;border:1px solid {THEME["border"]};'>
            <div style='font-size:0.65rem;color:{THEME["text_muted"]};text-transform:uppercase;
                 letter-spacing:.08em;margin-bottom:6px;'>STATUS</div>
            <div style='font-size:0.85rem;color:{THEME["text_muted"]};'>No pipeline run yet</div>
            <div style='margin-top:6px;'>
                <span style='font-size:0.65rem;background:rgba(251,161,0,0.1);color:{THEME["gold"]};
                      padding:2px 8px;border-radius:12px;border:1px solid rgba(251,161,0,0.3);'>
                    ● IDLE
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style='padding:1.5rem 1rem 1rem;font-size:0.65rem;color:{THEME["text_muted"]};'>
        DataForge Platform · v2.0<br>
        <span style='color:rgba(107,186,167,0.5);'>◆</span> Enterprise Edition
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: COMMAND CENTER (DASHBOARD)
# ══════════════════════════════════════════════════════════════════════════════
if page == "⬛  Command Center":
    results = st.session_state.get("pipeline_results")

    if results and results.get("status") == "success":
        s   = results["summary"]
        sb  = results["score_before"]
        sa  = results["score_after"]
        hl  = results.get("healing_log", [])
        raw = st.session_state.get("uploaded_df")
        cdf = results.get("clean_df")

        # ── Top bar ────────────────────────────────────────────────────────
        col_title, col_badge = st.columns([3, 1])
        with col_title:
            st.markdown(f"""
            <div>
                <div style='font-size:0.7rem;color:{THEME["text_muted"]};text-transform:uppercase;
                     letter-spacing:.1em;margin-bottom:4px;'>DATA OPERATIONS · COMMAND CENTER</div>
                <div style='font-size:1.8rem;font-weight:900;color:{THEME["text"]};
                     letter-spacing:-0.03em;'>{s['source_file']}</div>
            </div>
            """, unsafe_allow_html=True)
        with col_badge:
            clr = THEME["success"] if sa["total_score"] >= 80 else THEME["warning"]
            status_text = "HEALTHY" if sa["total_score"] >= 80 else "DEGRADED"
            st.markdown(f"""
            <div style='text-align:right;padding-top:0.5rem;'>
                <span style='background:rgba(34,197,94,0.1);color:{clr};
                      border:1px solid {clr};padding:6px 14px;border-radius:20px;
                      font-size:0.75rem;font-weight:700;letter-spacing:.06em;'>
                    ● {status_text}
                </span>
                <div style='font-size:0.7rem;color:{THEME["text_muted"]};margin-top:6px;'>
                    {s['run_timestamp']}
                </div>
            </div>
            """, unsafe_allow_html=True)

        divider()

        # ── KPI Row ────────────────────────────────────────────────────────
        section_label("KEY METRICS")
        k1, k2, k3, k4, k5, k6 = st.columns(6)
        kpis = [
            (k1, "Quality Score",    f"{sa['total_score']:.0f}%",   f"+{s['score_improvement']:.1f}%", "up",   "📈"),
            (k2, "Rows Input",       f"{s['rows_input']:,}",         None,                              "neu",  "📥"),
            (k3, "Rows Loaded",      f"{s['rows_loaded']:,}",        f"-{s['rows_removed']:,} cleaned", "up",   "💾"),
            (k4, "Rules Triggered",  str(s['healing_rules_triggered']), "self-healing",                "neu",  "🧠"),
            (k5, "Runtime",          f"{s['duration_seconds']:.2f}s", None,                            "neu",  "⚡"),
            (k6, "Load Status",      "SUCCESS" if s["load_success"] else "FAILED",
                                     f"{s['load_attempts']}×", "up" if s["load_success"] else "down", "🗄"),
        ]
        for col, label, val, delta, ddir, icon in kpis:
            with col:
                st.markdown(kpi(label, val, delta, ddir, icon), unsafe_allow_html=True)

        divider()

        # ── Pipeline Flow ──────────────────────────────────────────────────
        section_label("PIPELINE EXECUTION")
        stages = [
            ("📥", "Extract",    f"{s['rows_input']:,} rows",      "done"),
            ("🔍", "Schema",     "Types inferred",                  "done"),
            ("✅", "Validate",   "Quality checked",                 "done"),
            ("🧠", "Heal",       f"{s['healing_rules_triggered']} rules", "done" if hl else "idle"),
            ("🧹", "Clean",      f"{s['rows_removed']:,} removed",  "done"),
            ("⚙️", "Transform",  "Standardized",                   "done"),
            ("💾", "Load",       f"{s['rows_loaded']:,} rows",      "done" if s["load_success"] else "fail"),
            ("📊", "Report",     "Generated",                       "done"),
        ]
        node_cols = st.columns(len(stages))
        tick_map = {
            "done": f"<span style='color:{THEME['success']};'>✓</span>",
            "fail": f"<span style='color:{THEME['error']};'>✗</span>",
            "idle": f"<span style='color:{THEME['text_muted']};'>○</span>",
            "run":  f"<span style='color:{THEME['blue']};'>◉</span>",
        }
        for i, (icon, name, desc, state) in enumerate(stages):
            with node_cols[i]:
                st.markdown(f"""
                <div class="pipeline-node {state}">
                    <div class="node-icon">{icon}</div>
                    <div class="node-name">{name}</div>
                    <div class="node-desc">{desc}</div>
                    <div class="node-tick">{tick_map.get(state, '')}</div>
                </div>
                """, unsafe_allow_html=True)

        divider()

        # ── Quality analytics ──────────────────────────────────────────────
        section_label("DATA QUALITY ANALYTICS")
        qcol1, qcol2, qcol3 = st.columns([1, 1, 1])

        with qcol1:
            st.plotly_chart(gauge_chart(sb["total_score"], "BEFORE CLEANING",
                                        THEME["rose"]), use_container_width=True,
                           config=plotly_config())
        with qcol2:
            st.plotly_chart(gauge_chart(sa["total_score"], "AFTER CLEANING",
                                        THEME["aqua"]), use_container_width=True,
                           config=plotly_config())
        with qcol3:
            dims = ["Completeness", "Uniqueness", "Validity", "Consistency", "Accuracy"]
            before_vals = [sb["completeness"], sb["uniqueness"], sb["validity"],
                          sb["consistency"], sb["accuracy"]]
            after_vals  = [sa["completeness"], sa["uniqueness"], sa["validity"],
                          sa["consistency"], sa["accuracy"]]

            fig = go.Figure()
            fig.add_trace(go.Bar(name="Before", x=dims, y=before_vals,
                                 marker_color=THEME["rose"], opacity=0.7))
            fig.add_trace(go.Bar(name="After",  x=dims, y=after_vals,
                                 marker_color=THEME["aqua"], opacity=0.9))
            fig.update_layout(**plotly_layout(
                barmode="group", height=200,
                showlegend=True,
                legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=9), orientation="h", y=1.15),
                xaxis=dict(tickfont=dict(size=9), gridcolor=THEME["border"]),
                yaxis=dict(range=[0,105], gridcolor=THEME["border"]),
                title=dict(text="DIMENSION COMPARISON", font=dict(size=11)),
                margin=dict(l=0, r=0, t=40, b=0),
            ))
            st.plotly_chart(fig, use_container_width=True, config=plotly_config())

        divider()

        # ── Healing monitor + charts row ───────────────────────────────────
        hcol, ccol = st.columns([1, 1])

        with hcol:
            section_label("SELF-HEALING MONITOR")
            if hl:
                for entry in hl[:6]:
                    outcome = entry.get("outcome", "")
                    cls  = "healed" if outcome == "HEALED" else "partial" if outcome == "PARTIAL" else "unres"
                    clr  = THEME["success"] if outcome == "HEALED" else THEME["warning"] if outcome == "PARTIAL" else THEME["text_muted"]
                    icon = "✓" if outcome == "HEALED" else "⚠" if outcome == "PARTIAL" else "○"
                    st.markdown(f"""
                    <div class="heal-card {cls}">
                        <div style='display:flex;justify-content:space-between;align-items:center;'>
                            <div class="heal-rule" style='color:{clr};'>
                                {icon} {entry.get("rule_id","")} · {entry.get("rule_name","")}
                            </div>
                            <span style='font-size:0.65rem;background:rgba(255,255,255,0.05);
                                  color:{clr};padding:2px 8px;border-radius:10px;
                                  border:1px solid {clr}30;'>{outcome}</span>
                        </div>
                        <div class="heal-action">{entry.get("action","")}</div>
                        <div class="heal-time">{entry.get("triggered_at","")}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No healing rules triggered — data was already clean.")

        with ccol:
            section_label("ISSUE DISTRIBUTION")
            # Build issue distribution from null report
            nr = results.get("null_report", {})
            per_col = nr.get("per_column", {})
            null_total = sum(v["count"] for v in per_col.values())
            dupe_count = results.get("duplicate_report", {}).get("duplicate_count", 0)
            email_inv  = results.get("email_report", {}).get("invalid_count", 0)
            date_inv   = results.get("date_report",  {}).get("invalid_count", 0)

            issue_labels = ["Nulls", "Duplicates", "Bad Emails", "Bad Dates"]
            issue_values = [null_total, dupe_count, email_inv, date_inv]
            if sum(issue_values) > 0:
                st.plotly_chart(donut_chart(issue_labels, issue_values, "ISSUES DETECTED"),
                               use_container_width=True, config=plotly_config())
            else:
                st.markdown(f"""
                <div class="etl-card etl-card-aqua" style="text-align:center;padding:2rem;">
                    <div style="font-size:2rem;">✓</div>
                    <div style="color:{THEME['success']};font-weight:700;margin-top:8px;">No Issues Found</div>
                    <div style="font-size:0.8rem;color:{THEME['text_muted']};margin-top:4px;">Dataset was clean</div>
                </div>
                """, unsafe_allow_html=True)

        divider()

        # ── Null bar chart ──────────────────────────────────────────────────
        if per_col:
            null_cols  = [c for c, v in per_col.items() if v["count"] > 0]
            null_cnts  = [per_col[c]["count"] for c in null_cols]
            if null_cols:
                section_label("NULL DISTRIBUTION BY COLUMN")
                st.plotly_chart(
                    bar_chart(null_cols, null_cnts, "NULL VALUES PER COLUMN",
                              color=THEME["lavender"]),
                    use_container_width=True, config=plotly_config()
                )
                divider()

        # ── Execution timeline ──────────────────────────────────────────────
        section_label("EXECUTION TIMELINE")
        st.markdown(f"""
        <div class="etl-card">
        """, unsafe_allow_html=True)
        timeline_steps = [
            (THEME["aqua"],    "CSV Loaded",             f"{s['rows_input']:,} rows ingested"),
            (THEME["lavender"],"Schema Inferred",         "9–10 column types detected"),
            (THEME["gold"],    "Validation Complete",    f"Nulls: {null_total} · Dupes: {dupe_count}"),
            (THEME["rose"],    "Healing Agent Executed", f"{s['healing_rules_triggered']} rules evaluated"),
            (THEME["aqua"],    "Cleaning Complete",      f"{s['rows_removed']:,} rows removed"),
            (THEME["lavender"],"Transformation Done",    "Columns standardized to snake_case"),
            (THEME["success"], "Loaded to SQLite",       f"{s['rows_loaded']:,} rows → {s['target_table']}"),
            (THEME["gold"],    "Reports Generated",      "schema · cleaning · healing · summary"),
        ]
        for dot_color, step_title, step_detail in timeline_steps:
            st.markdown(f"""
            <div class="timeline-row">
                <div class="timeline-dot" style="background:{dot_color};"></div>
                <div>
                    <div class="timeline-msg">{step_title}</div>
                    <div class="heal-time">{step_detail}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        divider()

        # ── Dataset comparison ──────────────────────────────────────────────
        section_label("DATASET COMPARISON")
        dcol1, dcol2 = st.columns(2)
        with dcol1:
            st.markdown(f"<div style='font-size:0.72rem;font-weight:700;color:{THEME['rose']};text-transform:uppercase;letter-spacing:.08em;margin-bottom:8px;'>■ RAW DATASET</div>", unsafe_allow_html=True)
            if raw is not None:
                st.dataframe(raw.head(8), use_container_width=True, height=260)
        with dcol2:
            st.markdown(f"<div style='font-size:0.72rem;font-weight:700;color:{THEME['aqua']};text-transform:uppercase;letter-spacing:.08em;margin-bottom:8px;'>■ CLEANED DATASET</div>", unsafe_allow_html=True)
            if cdf is not None:
                st.dataframe(cdf.head(8), use_container_width=True, height=260)

    else:
        # ── Idle state ──────────────────────────────────────────────────────
        st.markdown(f"""
        <div style='padding:3rem 0 1rem;text-align:center;'>
            <div style='font-size:0.7rem;color:{THEME["text_muted"]};text-transform:uppercase;
                 letter-spacing:.1em;margin-bottom:12px;'>DATA OPERATIONS PLATFORM</div>
            <div style='font-size:3rem;font-weight:900;color:{THEME["text"]};
                 letter-spacing:-0.04em;line-height:1;'>ETL-GENERATOR</div>
            <div style='font-size:1rem;color:{THEME["aqua"]};font-weight:500;margin-top:8px;'>
                Autonomous Self-Healing Data Pipeline
            </div>
        </div>
        """, unsafe_allow_html=True)

        divider()
        section_label("GET STARTED")

        sc1, sc2, sc3 = st.columns(3)
        steps = [
            (sc1, "📂", "01 · Upload", "Load a CSV dataset via the Data Upload page", "etl-card-aqua"),
            (sc2, "🚀", "02 · Execute", "Run the full ETL pipeline with one click",  "etl-card-gold"),
            (sc3, "📊", "03 · Analyse", "Explore metrics, charts, and audit logs",   "etl-card-lav"),
        ]
        for col, icon, title, desc, cls in steps:
            with col:
                col.markdown(f"""
                <div class="etl-card {cls}" style="text-align:center;padding:2.5rem 1rem;">
                    <div style="font-size:2.5rem;margin-bottom:12px;">{icon}</div>
                    <div style="font-weight:800;font-size:0.95rem;color:{THEME['text']};
                         margin-bottom:6px;">{title}</div>
                    <div style="font-size:0.82rem;color:{THEME['text_muted']};">{desc}</div>
                </div>
                """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: DATA UPLOAD
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📂  Data Upload":
    st.markdown(f"""
    <div style='margin-bottom:1.5rem;'>
        <div class='section-label'>DATA OPERATIONS · INGESTION</div>
        <h1>Data Upload</h1>
        <p style='margin-top:4px;'>Load a CSV dataset to begin the ETL pipeline. Any CSV with a header row is accepted.</p>
    </div>
    """, unsafe_allow_html=True)

    divider()

    up_col, info_col = st.columns([3, 2])

    with up_col:
        section_label("UPLOAD FILE")
        uploaded_file = st.file_uploader(
            "Drop CSV here or click to browse",
            type=["csv"],
            help="Max 10 MB · Must have a header row",
            label_visibility="visible"
        )

        st.markdown(f"<div style='text-align:center;color:{THEME['text_muted']};font-size:0.8rem;margin:1rem 0;'>— or choose a sample —</div>", unsafe_allow_html=True)

        sample_path = os.path.join(DATA_DIR, "dirty_data.csv")
        real_path   = os.path.join(DATA_DIR, "ecommerce_dataset.csv")

        bc1, bc2 = st.columns(2)
        with bc1:
            use_synth = st.button("📊 Synthetic Dataset",
                                  disabled=not os.path.exists(sample_path),
                                  use_container_width=True)
        with bc2:
            use_real  = st.button("🌐 Kaggle Retail Dataset",
                                  disabled=not os.path.exists(real_path),
                                  use_container_width=True)

        if not os.path.exists(sample_path):
            st.warning("Run `python data/generate_dataset.py` to generate the synthetic dataset.")
        if not os.path.exists(real_path):
            st.info("Run `python data/download_real_data.py` to fetch the Kaggle dataset.")

    with info_col:
        st.markdown(f"""
        <div class="etl-card etl-card-aqua">
            <div class="section-label">DATASET SPECIFICATIONS</div>
            <div style='display:flex;flex-direction:column;gap:12px;margin-top:8px;'>
                <div>
                    <div style='font-size:0.72rem;color:{THEME["text_muted"]};'>Synthetic Dataset</div>
                    <div style='font-size:0.88rem;color:{THEME["text"]};font-weight:600;'>10,350 rows · 10 columns</div>
                    <div style='font-size:0.72rem;color:{THEME["text_muted"]};'>Retail transactions with injected errors</div>
                </div>
                <div style='height:1px;background:{THEME["border"]};'></div>
                <div>
                    <div style='font-size:0.72rem;color:{THEME["text_muted"]};'>Kaggle Dataset</div>
                    <div style='font-size:0.88rem;color:{THEME["text"]};font-weight:600;'>1,050 rows · 9 columns</div>
                    <div style='font-size:0.72rem;color:{THEME["text_muted"]};'>Real retail transactions (mohammadtalib786)</div>
                </div>
                <div style='height:1px;background:{THEME["border"]};'></div>
                <div>
                    <div style='font-size:0.72rem;color:{THEME["text_muted"]};'>Custom Upload</div>
                    <div style='font-size:0.88rem;color:{THEME["text"]};font-weight:600;'>Any CSV · Max 10 MB · 50K rows</div>
                    <div style='font-size:0.72rem;color:{THEME["text_muted"]};'>Must have header row</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    divider()

    # Decide source
    source = None
    if uploaded_file is not None:
        if uploaded_file.size > 10 * 1024 * 1024:
            st.error("❌ File exceeds 10 MB limit.")
            st.stop()
        source = uploaded_file
        st.session_state["file_name"] = uploaded_file.name
    elif use_synth:
        source = sample_path
        st.session_state["file_name"] = "dirty_data.csv"
    elif use_real:
        source = real_path
        st.session_state["file_name"] = "ecommerce_dataset.csv"

    if source is not None:
        try:
            df = pd.read_csv(source, dtype=str, nrows=50000) if isinstance(source, str) \
                 else pd.read_csv(source, dtype=str, nrows=50000)
            if not isinstance(source, str):
                source.seek(0)

            for col in df.columns:
                if not re.match(r'^[a-zA-Z0-9_ \-]+$', str(col)):
                    st.error(f"❌ Invalid column name: '{col}'")
                    st.stop()

            st.session_state["uploaded_df"]     = df
            st.session_state["uploaded_source"] = source

            st.success(f"✅ Loaded **{st.session_state['file_name']}**")

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Rows",       f"{df.shape[0]:,}")
            m2.metric("Columns",    df.shape[1])
            sz = round(os.path.getsize(source) / 1024, 1) if isinstance(source, str) \
                 else round(len(source.getvalue()) / 1024, 1)
            m3.metric("File Size",  f"{sz} KB")
            m4.metric("Null Cells", f"{df.isnull().sum().sum():,}")

            divider()
            section_label("RAW DATA PREVIEW — FIRST 20 ROWS")
            st.dataframe(df.head(20), use_container_width=True, height=420)

        except pd.errors.EmptyDataError:
            st.error("❌ File is empty.")
        except Exception as e:
            st.error(f"❌ Error: {e}")

    elif st.session_state["uploaded_df"] is not None:
        df = st.session_state["uploaded_df"]
        st.info(f"Currently loaded: **{st.session_state['file_name']}** · {df.shape[0]:,} rows × {df.shape[1]} columns")
        section_label("RAW DATA PREVIEW")
        st.dataframe(df.head(20), use_container_width=True, height=420)
    else:
        st.markdown(f"""
        <div class="etl-card" style="text-align:center;padding:4rem 2rem;">
            <div style="font-size:3rem;margin-bottom:1rem;opacity:.4;">📂</div>
            <div style="font-size:1rem;font-weight:700;color:{THEME['text']};">No dataset loaded</div>
            <div style="font-size:0.85rem;color:{THEME['text_muted']};margin-top:6px;">Upload a CSV or choose a sample above</div>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: VALIDATION
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🔍  Validation":
    st.markdown(f"""
    <div style='margin-bottom:1.5rem;'>
        <div class='section-label'>DATA OPERATIONS · ANALYSIS</div>
        <h1>Schema & Validation</h1>
        <p style='margin-top:4px;'>Automatic type detection and data quality analysis before pipeline execution.</p>
    </div>
    """, unsafe_allow_html=True)

    df = st.session_state.get("uploaded_df")
    if df is None:
        st.warning("⚠ No dataset loaded — go to **📂 Data Upload** first.")
        st.stop()

    from src.validation.schema_inferrer    import get_schema_report
    from src.validation.null_detector      import get_null_report
    from src.validation.duplicate_detector import detect as detect_dupes
    from src.validation.format_validator   import validate_emails, validate_dates
    from src.validation.type_validator     import detect as detect_types
    from src.reporting.quality_scorer      import calculate as score_calc

    divider()

    tab1, tab2, tab3, tab4 = st.tabs([
        "📋  Schema",
        "🔎  Null Analysis",
        "⚠  Issues",
        "📊  Quality Score",
    ])

    with tab1:
        section_label("INFERRED COLUMN SCHEMA")
        schema_df = get_schema_report(df)
        st.dataframe(schema_df, use_container_width=True, height=460)

    with tab2:
        section_label("NULL VALUE ANALYSIS")
        null_df = get_null_report(df)
        nc1, nc2 = st.columns([2, 1])
        with nc1:
            st.dataframe(null_df, use_container_width=True, height=380)
        with nc2:
            chart_data = null_df[null_df["null_count"] > 0]
            if not chart_data.empty:
                fig = go.Figure(go.Bar(
                    x=chart_data["null_count"].tolist(),
                    y=chart_data["column_name"].tolist(),
                    orientation="h",
                    marker=dict(color=THEME["lavender"], opacity=0.85),
                ))
                fig.update_layout(**plotly_layout(height=380,
                    xaxis=dict(gridcolor=THEME["border"]),
                    yaxis=dict(gridcolor=THEME["border"]),
                    title=dict(text="NULLS BY COLUMN", font=dict(size=11))))
                st.plotly_chart(fig, use_container_width=True, config=plotly_config())
            else:
                st.success("✓ No null values detected")

    with tab3:
        ic1, ic2 = st.columns(2)
        dupe_result  = detect_dupes(df)
        email_result = validate_emails(df)
        date_result  = validate_dates(df)
        type_result  = detect_types(df)

        with ic1:
            section_label("DUPLICATE ROWS")
            st.metric("Count",   dupe_result["duplicate_count"])
            st.metric("Percent", f"{dupe_result['duplicate_pct']}%")
        with ic2:
            section_label("FORMAT ISSUES")
            st.metric("Invalid Emails", email_result["invalid_count"])
            st.metric("Invalid Dates",  date_result["invalid_count"])

        if type_result:
            divider()
            section_label("TYPE MISMATCHES")
            for col, info in type_result.items():
                if info["invalid_count"] > 0:
                    st.warning(f"**{col}** — {info['invalid_count']} values cannot convert to `{info['type']}`")

    with tab4:
        q = score_calc(df)
        section_label("DATA QUALITY SCORE BEFORE CLEANING")

        sc_col = "#3D8C7A" if q["total_score"] >= 80 else THEME["warning"] if q["total_score"] >= 60 else THEME["error"]
        ql, qm, qr = st.columns([1, 3, 1])
        with qm:
            st.markdown(f"""
            <div class="etl-card" style="text-align:center;padding:2.5rem 2rem;">
                <div style="font-size:0.7rem;font-weight:700;text-transform:uppercase;
                     letter-spacing:.1em;color:{THEME['text_muted']};margin-bottom:1rem;">
                     Total Quality Score
                </div>
                <div style="font-family:'JetBrains Mono',monospace;font-size:5rem;
                     font-weight:800;color:{sc_col};line-height:1;">
                     {q['total_score']:.1f}
                </div>
                <div style="font-size:1.5rem;color:{THEME['text_muted']};margin-bottom:1.5rem;">/ 100</div>
                <div style="background:{THEME['border']};border-radius:8px;height:10px;overflow:hidden;">
                    <div style="background:{sc_col};width:{q['total_score']}%;height:100%;
                         border-radius:8px;transition:width .6s ease;"></div>
                </div>
                <div style="display:flex;justify-content:space-between;
                     font-size:0.7rem;color:{THEME['text_muted']};margin-top:4px;">
                    <span>0</span><span>50</span><span>100</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        divider()
        section_label("DIMENSION BREAKDOWN")
        d1, d2, d3, d4, d5 = st.columns(5)
        dims = [
            (d1, "Completeness", q["completeness"]),
            (d2, "Uniqueness",   q["uniqueness"]),
            (d3, "Validity",     q["validity"]),
            (d4, "Consistency",  q["consistency"]),
            (d5, "Accuracy",     q["accuracy"]),
        ]
        for col, name, val in dims:
            col.metric(name, f"{val:.0f}%")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: RUN PIPELINE
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🚀  Run Pipeline":
    st.markdown(f"""
    <div style='margin-bottom:1.5rem;'>
        <div class='section-label'>DATA OPERATIONS · EXECUTION</div>
        <h1>Run Pipeline</h1>
        <p style='margin-top:4px;'>Execute the full 10-stage ETL workflow — Extract · Validate · Heal · Transform · Load · Report</p>
    </div>
    """, unsafe_allow_html=True)

    df     = st.session_state.get("uploaded_df")
    source = st.session_state.get("uploaded_source")

    if df is None or source is None:
        st.warning("⚠ No dataset loaded — go to **📂 Data Upload** first.")
        st.stop()

    divider()

    pc1, pc2 = st.columns(2)
    pc1.metric("Source File", st.session_state.get("file_name", "unknown"))
    pc2.metric("Rows", f"{df.shape[0]:,}")

    divider()
    section_label("TARGET CONFIGURATION")

    tc1, tc2 = st.columns([2, 3])
    with tc1:
        table_name = st.text_input(
            "SQLite table name",
            value="cleaned_data",
            help="Letters, numbers, underscores only — no spaces.",
            max_chars=64
        )
    with tc2:
        st.markdown(f"""
        <div class="etl-card" style="margin-top:0;padding:1rem;">
            <div style="font-size:0.72rem;color:{THEME['text_muted']};">Data will be loaded into</div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:0.95rem;
                 color:{THEME['aqua']};margin-top:4px;">database/etl_database.db → {table_name or '...'}</div>
        </div>
        """, unsafe_allow_html=True)

    if table_name.strip():
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', table_name.strip()):
            st.error("❌ Table name must start with a letter/underscore and contain only alphanumeric characters and underscores.")
            st.stop()
    else:
        st.error("❌ Table name cannot be empty.")
        st.stop()

    divider()

    ec1, ec2, ec3 = st.columns([1, 2, 1])
    with ec2:
        run_btn = st.button("▶  EXECUTE PIPELINE", type="primary", use_container_width=True)

    if run_btn:
        with st.spinner(""):
            if hasattr(source, "seek"):
                source.seek(0)

            # Animated progress
            prog_placeholder = st.empty()
            stages_progress = [
                (10,  "Extracting CSV…"),
                (25,  "Inferring schema…"),
                (40,  "Validating data…"),
                (55,  "Running self-healing agent…"),
                (70,  "Cleaning data…"),
                (82,  "Transforming columns…"),
                (90,  "Scoring quality…"),
                (95,  "Loading to SQLite…"),
            ]
            for pct, msg in stages_progress:
                prog_placeholder.progress(pct, text=msg)
                time.sleep(0.1)

            results = run_pipeline(source, table_name=table_name.strip())
            prog_placeholder.progress(100, text="Complete ✓")

        st.session_state["pipeline_results"] = results

        if results["status"] == "success":
            s = results["summary"]
            divider()
            st.success("✅ Pipeline executed successfully")

            r1, r2, r3, r4 = st.columns(4)
            r1.metric("Rows Input",  f"{s['rows_input']:,}")
            r2.metric("Rows Loaded", f"{s['rows_loaded']:,}")
            r3.metric("Score",       f"{s['quality_score_after']:.1f}%",
                      delta=f"+{s['score_improvement']:.1f}%")
            r4.metric("Duration",    f"{s['duration_seconds']:.2f}s")

            divider()
            st.info("💡 Navigate to **⬛ Command Center** for the full analytics dashboard.")
        else:
            st.error(f"❌ Pipeline failed: {results.get('error','Unknown error')}")
            with st.expander("Error Details"):
                st.code(results.get("error", ""), language="python")

    elif st.session_state["pipeline_results"] is not None:
        prev = st.session_state["pipeline_results"]
        if prev.get("status") == "success":
            st.success("✅ Pipeline already executed — results available in Command Center.")
        bc1, bc2, bc3 = st.columns([1, 2, 1])
        with bc2:
            if st.button("🔄  Re-run Pipeline", use_container_width=True):
                st.session_state["pipeline_results"] = None
                st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: RESULTS & REPORTS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📊  Results & Reports":
    st.markdown(f"""
    <div style='margin-bottom:1.5rem;'>
        <div class='section-label'>DATA OPERATIONS · REPORTING</div>
        <h1>Results & Reports</h1>
        <p style='margin-top:4px;'>Download reports, inspect the execution log, and query the loaded SQLite table.</p>
    </div>
    """, unsafe_allow_html=True)

    results = st.session_state.get("pipeline_results")
    divider()

    # ETL Summary
    summary_path = os.path.join(REPORTS_DIR, "etl_summary.json")
    if os.path.exists(summary_path):
        with open(summary_path, "r", encoding="utf-8") as f:
            sd = json.load(f)

        section_label("RUN SUMMARY")
        sm1, sm2, sm3, sm4 = st.columns(4)
        sm1.metric("Run At",       sd.get("run_timestamp", "—"))
        sm2.metric("Source",       sd.get("source_file",   "—"))
        sm3.metric("Table",        sd.get("target_table",  "—"))
        sm4.metric("Duration",     f"{sd.get('duration_seconds', 0):.2f}s")

        divider()

        # Score delta card
        sc_before = sd.get("quality_score_before", 0)
        sc_after  = sd.get("quality_score_after",  0)
        improvement = sd.get("score_improvement", 0)
        sa_color = THEME["aqua"] if sc_after >= 80 else THEME["warning"]
        st.markdown(f"""
        <div class="etl-card etl-card-aqua" style="display:flex;align-items:center;gap:2rem;flex-wrap:wrap;">
            <div>
                <div class="section-label">BEFORE</div>
                <div style="font-family:'JetBrains Mono',monospace;font-size:2.5rem;
                     font-weight:700;color:{THEME['rose']};line-height:1;">{sc_before:.0f}%</div>
            </div>
            <div style="font-size:2rem;color:{THEME['text_muted']};">→</div>
            <div>
                <div class="section-label">AFTER</div>
                <div style="font-family:'JetBrains Mono',monospace;font-size:2.5rem;
                     font-weight:700;color:{sa_color};line-height:1;">{sc_after:.0f}%</div>
            </div>
            <div style="margin-left:auto;">
                <div class="section-label">IMPROVEMENT</div>
                <div style="font-family:'JetBrains Mono',monospace;font-size:2.5rem;
                     font-weight:700;color:{THEME['success']};line-height:1;">+{improvement:.1f}%</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("Full JSON Summary"):
            st.json(sd)
    else:
        st.info("No completed pipeline run found. Run the pipeline first.")

    divider()

    # Downloads
    section_label("DOWNLOAD REPORTS")
    dc1, dc2, dc3 = st.columns(3)
    report_files = [
        (dc1, "Schema Report",   "schema_report.csv",   "text/csv"),
        (dc2, "Cleaning Report", "cleaning_report.csv", "text/csv"),
        (dc1, "Healing Report",  "healing_report.csv",  "text/csv"),
        (dc2, "ETL Summary",     "etl_summary.json",    "application/json"),
    ]
    for col, label, fname, mime in report_files:
        path = os.path.join(REPORTS_DIR, fname)
        if os.path.exists(path):
            with open(path, "rb") as f:
                col.download_button(f"⬇  {label}", f, file_name=fname,
                                    mime=mime, use_container_width=True)
        else:
            col.caption(f"⚠ {label} not yet generated")

    if results and results.get("status") == "success":
        csv_bytes = results["clean_df"].to_csv(index=False).encode("utf-8")
        with dc3:
            st.download_button("⬇  Cleaned Dataset (CSV)", csv_bytes,
                               "cleaned_data.csv", "text/csv",
                               use_container_width=True, type="primary")

    divider()

    # SQLite preview
    section_label("SQLITE TABLE PREVIEW")
    tables = list_tables()
    if tables:
        sel = st.selectbox("Select table", tables, label_visibility="collapsed")
        prev_df = query_table(sel, limit=50)
        st.dataframe(prev_df, use_container_width=True, height=360)
        st.caption(f"Showing up to 50 rows from '{sel}'")
    else:
        st.info("No tables loaded yet.")

    divider()

    # Log viewer
    section_label("PIPELINE EXECUTION LOG")
    if os.path.exists(LOG_FILE_PATH):
        log_level = st.selectbox("Filter", ["ALL", "INFO", "WARNING", "ERROR"],
                                 label_visibility="collapsed")
        with open(LOG_FILE_PATH, "r", encoding="utf-8") as f:
            lines = f.readlines()
        filtered = lines if log_level == "ALL" else [l for l in lines if f"| {log_level}" in l]
        st.text_area("Log Output", "".join(filtered[-200:]), height=380,
                     label_visibility="collapsed")
        st.caption(f"{min(200, len(filtered))} of {len(filtered)} entries")
    else:
        st.info("No log file found — run the pipeline first.")
