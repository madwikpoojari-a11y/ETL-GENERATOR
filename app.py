"""
app.py — Auto-ETL Generator Agent
Colour theme: Aqua #6BBAA7 | Sunshine #FBA100 | Lavender #6C648B | Dusty Rose #B6A19E
Background: #F4F6F5 (light warm grey) | Cards: #FFFFFF
"""

import os, sys, json, re
import pandas as pd
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "app"))

from pipeline_controller import run_pipeline
from src.loading.db_loader import list_tables, query_table
from src.utils.config import LOG_FILE_PATH, REPORTS_DIR, DATA_DIR

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ETL-GENERATOR",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── THEME: Aqua / Sunshine / Lavender / Dusty Rose ───────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Reset & base ── */
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

/* ── App background ── */
.stApp { background-color: #EEF2F0; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background-color: #1C2B2A !important;
    border-right: 3px solid #6BBAA7;
    min-width: 230px !important;
    max-width: 230px !important;
}
[data-testid="stSidebar"] * { color: #D0E8E3 !important; }
[data-testid="stSidebar"] hr { border-color: #2E4442 !important; }

/* ── Sidebar radio nav ── */
[data-testid="stSidebar"] [data-testid="stRadio"] label {
    display: block;
    padding: 10px 16px;
    border-radius: 8px;
    font-size: 0.9rem;
    font-weight: 500;
    color: #A8C8C0 !important;
    cursor: pointer;
    margin-bottom: 2px;
    transition: background 0.15s;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    background: rgba(107,186,167,0.18) !important;
    color: #6BBAA7 !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] [data-checked="true"] + div label,
[data-testid="stSidebar"] input[type="radio"]:checked + div label {
    background: rgba(107,186,167,0.25) !important;
    color: #6BBAA7 !important;
    border-left: 3px solid #6BBAA7;
}

/* ── Main content area ── */
.block-container {
    padding: 2rem 2.5rem 3rem 2.5rem !important;
    max-width: 1200px;
}

/* ── Page title ── */
h1 { font-size: 1.75rem !important; font-weight: 800 !important; color: #1C2B2A !important; margin-bottom: 0.25rem !important; }
h2 { font-size: 1.3rem !important; font-weight: 700 !important; color: #1C2B2A !important; }
h3 { font-size: 1.05rem !important; font-weight: 600 !important; color: #2E4442 !important; }
p, li { color: #3D5450 !important; }

/* ── Caption / subtext ── */
small, .stCaption, [data-testid="stCaptionContainer"] {
    color: #7A9E99 !important;
    font-size: 0.82rem !important;
}

/* ── Metric widget ── */
[data-testid="metric-container"] {
    background: #FFFFFF;
    border-radius: 12px;
    padding: 1.1rem 1.25rem;
    border: 1px solid #D6E8E4;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
[data-testid="stMetricLabel"] {
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #7A9E99 !important;
}
[data-testid="stMetricValue"] {
    font-size: 1.9rem !important;
    font-weight: 800 !important;
    color: #1C2B2A !important;
}
[data-testid="stMetricDelta"] { font-size: 0.8rem !important; }

/* ── Buttons ── */
.stButton > button {
    background-color: #6BBAA7 !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    padding: 0.55rem 1.4rem !important;
    transition: background 0.2s, box-shadow 0.2s !important;
}
.stButton > button:hover {
    background-color: #58A892 !important;
    box-shadow: 0 4px 14px rgba(107,186,167,0.4) !important;
}
.stButton > button[kind="primary"] {
    background-color: #FBA100 !important;
}
.stButton > button[kind="primary"]:hover {
    background-color: #E09200 !important;
    box-shadow: 0 4px 14px rgba(251,161,0,0.4) !important;
}

/* ── Download buttons ── */
.stDownloadButton > button {
    background-color: #6C648B !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}
.stDownloadButton > button:hover {
    background-color: #5A5375 !important;
    box-shadow: 0 4px 12px rgba(108,100,139,0.35) !important;
}

/* ── Alerts / messages ── */
[data-testid="stAlert"] {
    border-radius: 10px !important;
    border: none !important;
    font-size: 0.88rem !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: #FFFFFF;
    border-radius: 10px;
    padding: 6px;
    gap: 4px;
    border: 1px solid #D6E8E4;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    border-radius: 7px;
    color: #7A9E99 !important;
    font-weight: 600;
    font-size: 0.85rem;
    padding: 8px 16px;
}
.stTabs [aria-selected="true"] {
    background: #6BBAA7 !important;
    color: #FFFFFF !important;
}
[data-testid="stTabsContent"] { padding-top: 1.25rem; }

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
    border-radius: 10px;
    border: 1px solid #D6E8E4;
    overflow: hidden;
}

/* ── Text inputs ── */
.stTextInput input {
    background: #FFFFFF !important;
    border: 1.5px solid #C8DDD9 !important;
    border-radius: 8px !important;
    color: #1C2B2A !important;
    font-size: 0.9rem !important;
    padding: 10px 14px !important;
}
.stTextInput input:focus {
    border-color: #6BBAA7 !important;
    box-shadow: 0 0 0 3px rgba(107,186,167,0.2) !important;
}

/* ── File uploader ── */
[data-testid="stFileUploader"] > section {
    background: #FFFFFF !important;
    border: 2px dashed #6BBAA7 !important;
    border-radius: 12px !important;
    padding: 2rem !important;
}

/* ── Selectbox ── */
[data-baseweb="select"] > div {
    background: #FFFFFF !important;
    border: 1.5px solid #C8DDD9 !important;
    border-radius: 8px !important;
    color: #1C2B2A !important;
}

/* ── Progress bar ── */
.stProgress > div > div > div { background-color: #6BBAA7 !important; }

/* ── Spinner ── */
.stSpinner > div { border-top-color: #6BBAA7 !important; }

/* ── Expander ── */
[data-testid="stExpander"] {
    background: #FFFFFF;
    border-radius: 10px;
    border: 1px solid #D6E8E4;
}

/* ── Custom components ── */
.etl-card {
    background: #FFFFFF;
    border-radius: 12px;
    padding: 1.5rem;
    border: 1px solid #D6E8E4;
    box-shadow: 0 2px 10px rgba(0,0,0,0.04);
    margin-bottom: 1rem;
}
.etl-card-aqua   { border-left: 4px solid #6BBAA7; }
.etl-card-sun    { border-left: 4px solid #FBA100; }
.etl-card-lav    { border-left: 4px solid #6C648B; }
.etl-card-rose   { border-left: 4px solid #B6A19E; }

.hero-banner {
    background: linear-gradient(135deg, #1C2B2A 0%, #2E4442 100%);
    border-radius: 16px;
    padding: 2.5rem 3rem;
    margin-bottom: 2rem;
    box-shadow: 0 8px 32px rgba(0,0,0,0.12);
}
.hero-title {
    font-size: 2.2rem;
    font-weight: 800;
    color: #FFFFFF;
    letter-spacing: -0.03em;
    margin-bottom: 0.4rem;
}
.hero-sub {
    font-size: 1rem;
    color: #6BBAA7;
    font-weight: 500;
    margin-bottom: 2rem;
}
.hero-stats {
    display: flex;
    gap: 2.5rem;
    flex-wrap: wrap;
}
.hero-stat-label {
    font-size: 0.7rem;
    color: #7A9E99;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 4px;
}
.hero-stat-value {
    font-size: 1.4rem;
    font-weight: 700;
    color: #FFFFFF;
}
.hero-stat-value.aqua  { color: #6BBAA7; }
.hero-stat-value.sun   { color: #FBA100; }

.badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 5px 14px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 0.04em;
}
.badge-healthy { background: rgba(107,186,167,0.18); color: #3D8C7A; border: 1px solid #6BBAA7; }
.badge-warning { background: rgba(251,161,0,0.15);   color: #A36B00; border: 1px solid #FBA100; }
.badge-error   { background: rgba(182,161,158,0.2);  color: #7A5F5C; border: 1px solid #B6A19E; }

.stage-card {
    background: #FFFFFF;
    border-radius: 10px;
    padding: 1.1rem 0.75rem;
    text-align: center;
    border: 1.5px solid #D6E8E4;
    height: 110px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}
.stage-card.done { border-color: #6BBAA7; background: rgba(107,186,167,0.07); }
.stage-icon { font-size: 1.5rem; margin-bottom: 4px; }
.stage-name { font-size: 0.75rem; font-weight: 700; color: #1C2B2A; margin-bottom: 2px; }
.stage-desc { font-size: 0.65rem; color: #7A9E99; }
.stage-tick { font-size: 0.95rem; color: #6BBAA7; font-weight: 700; }

.score-bar-wrap {
    background: #EEF2F0;
    border-radius: 8px;
    height: 12px;
    overflow: hidden;
    margin-top: 10px;
}
.score-bar-fill-red  { background: #B6A19E; height: 100%; border-radius: 8px; transition: width 0.6s; }
.score-bar-fill-aqua { background: #6BBAA7; height: 100%; border-radius: 8px; transition: width 0.6s; }

.heal-row {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 10px 14px;
    border-radius: 8px;
    margin-bottom: 6px;
    background: #F8FAF9;
    border: 1px solid #E0EDEA;
    font-size: 0.84rem;
    color: #2E4442;
}
.heal-row.ok  { border-left: 3px solid #6BBAA7; }
.heal-row.warn{ border-left: 3px solid #FBA100; }
.heal-row.na  { border-left: 3px solid #B6A19E; }

.divider {
    height: 1px;
    background: #D6E8E4;
    margin: 1.75rem 0;
}

.label-aqua { color: #3D8C7A; font-weight: 700; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.06em; }
.label-sun  { color: #A36B00; font-weight: 700; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.06em; }
.label-lav  { color: #4E4869; font-weight: 700; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.06em; }

/* ── Hide default streamlit chrome ── */
#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
for k, v in [("pipeline_results", None), ("uploaded_df", None),
             ("file_name", None), ("uploaded_source", None)]:
    if k not in st.session_state:
        st.session_state[k] = v

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding:1.5rem 1rem 1rem 1rem;'>
        <div style='font-size:1.4rem;font-weight:800;color:#6BBAA7;letter-spacing:-0.02em;'>⚡ ETL-GENERATOR</div>
        <div style='font-size:0.75rem;color:#7A9E99;margin-top:3px;'>Self-Healing Data Pipeline</div>
    </div>
    <hr style='border:1px solid #2E4442;margin:0 1rem 1rem 1rem;'>
    """, unsafe_allow_html=True)

    page = st.radio(
        "nav",
        ["🏠  Dashboard", "📂  Upload & Preview", "🔍  Schema & Validation",
         "🚀  Run Pipeline", "📊  Results & Reports"],
        label_visibility="collapsed"
    )

    # Pipeline status indicator
    res = st.session_state.get("pipeline_results")
    if res and res.get("status") == "success":
        score_v = res["summary"]["quality_score_after"]
        clr = "#6BBAA7" if score_v >= 80 else "#FBA100"
        st.markdown(f"""
        <div style='margin:1.5rem 1rem 0 1rem;padding:12px;background:rgba(107,186,167,0.12);
             border-radius:10px;border:1px solid #2E4442;'>
            <div style='font-size:0.7rem;color:#7A9E99;text-transform:uppercase;margin-bottom:4px;'>Last Run</div>
            <div style='font-size:1.4rem;font-weight:800;color:{clr};'>{score_v:.0f}%</div>
            <div style='font-size:0.72rem;color:#7A9E99;'>Quality Score</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div style='margin-top:2rem;padding:0.75rem 1rem;
         font-size:0.7rem;color:#4A6E6A;text-align:center;'>
        DataForge Platform • v1.0
    </div>
    """, unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ═════════════════════════════════════════════════════════════════════════════
if page == "🏠  Dashboard":
    results = st.session_state.get("pipeline_results")

    if results and results.get("status") == "success":
        s = results["summary"]
        sb = results["score_before"]
        sa = results["score_after"]
        healing_log = results.get("healing_log", [])

        health_badge = (
            '<span class="badge badge-healthy">● HEALTHY</span>' if sa["total_score"] >= 80
            else '<span class="badge badge-warning">● DEGRADED</span>' if sa["total_score"] >= 60
            else '<span class="badge badge-error">● CRITICAL</span>'
        )

        # Hero banner
        st.markdown(f"""
        <div class="hero-banner">
            <div class="hero-title">ETL-GENERATOR AGENT</div>
            <div class="hero-sub">Self-Healing Data Pipeline — {s['source_file']}</div>
            <div class="hero-stats">
                <div>
                    <div class="hero-stat-label">Health Score</div>
                    <div class="hero-stat-value aqua">{sa['total_score']:.0f}%</div>
                </div>
                <div>
                    <div class="hero-stat-label">Rows Loaded</div>
                    <div class="hero-stat-value">{s['rows_loaded']:,}</div>
                </div>
                <div>
                    <div class="hero-stat-label">Rows Removed</div>
                    <div class="hero-stat-value sun">{s['rows_removed']:,}</div>
                </div>
                <div>
                    <div class="hero-stat-label">Healing Rules</div>
                    <div class="hero-stat-value">{s['healing_rules_triggered']}</div>
                </div>
                <div>
                    <div class="hero-stat-label">Runtime</div>
                    <div class="hero-stat-value">{s['duration_seconds']:.1f}s</div>
                </div>
                <div style="margin-left:auto;display:flex;align-items:flex-end;">
                    {health_badge}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # KPI row
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Quality Score",    f"{sa['total_score']:.1f}%",
                  delta=f"+{s['score_improvement']:.1f}%")
        c2.metric("Rows Processed",   f"{s['rows_input']:,}")
        c3.metric("Rows Loaded",      f"{s['rows_loaded']:,}",
                  delta=f"-{s['rows_removed']:,} cleaned")
        c4.metric("Load Status",
                  "✓ SUCCESS" if s["load_success"] else "✗ FAILED",
                  delta=f"{s['load_attempts']} attempt(s)")

        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

        # Pipeline stages
        st.markdown("#### Pipeline Execution Flow")
        stages = [
            ("📥", "Extract", "CSV Ingestion"),
            ("🔍", "Schema", "Type Inference"),
            ("✅", "Validate", "Quality Checks"),
            ("🧠", "Heal", f"{s['healing_rules_triggered']} Rules"),
            ("🔧", "Transform", "Cleaning"),
            ("💾", "Load", f"{s['rows_loaded']:,} Rows"),
        ]
        cols = st.columns(6)
        for i, (icon, name, desc) in enumerate(stages):
            complete = True if i < 5 else s["load_success"]
            done_cls = "done" if complete else ""
            tick = "✓" if complete else "○"
            cols[i].markdown(f"""
            <div class="stage-card {done_cls}">
                <div class="stage-icon">{icon}</div>
                <div class="stage-name">{name}</div>
                <div class="stage-desc">{desc}</div>
                <div class="stage-tick">{tick}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

        # Quality before / after
        st.markdown("#### Data Quality Impact")
        col1, col2 = st.columns(2)
        with col1:
            bv = sb["total_score"]
            st.markdown(f"""
            <div class="etl-card etl-card-rose">
                <div class="label-lav" style="color:#7A5F5C;">Before Cleaning</div>
                <div style="font-size:2.8rem;font-weight:800;color:#B6A19E;line-height:1.1;">{bv:.0f}<span style="font-size:1.2rem;">%</span></div>
                <div class="score-bar-wrap"><div class="score-bar-fill-red" style="width:{bv}%;"></div></div>
                <div style="margin-top:12px;display:flex;gap:1rem;flex-wrap:wrap;">
                    <span style="font-size:0.75rem;color:#7A9E99;">Complete: {sb['completeness']:.0f}%</span>
                    <span style="font-size:0.75rem;color:#7A9E99;">Unique: {sb['uniqueness']:.0f}%</span>
                    <span style="font-size:0.75rem;color:#7A9E99;">Valid: {sb['validity']:.0f}%</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            av = sa["total_score"]
            st.markdown(f"""
            <div class="etl-card etl-card-aqua">
                <div class="label-aqua">After Cleaning</div>
                <div style="font-size:2.8rem;font-weight:800;color:#3D8C7A;line-height:1.1;">{av:.0f}<span style="font-size:1.2rem;">%</span></div>
                <div class="score-bar-wrap"><div class="score-bar-fill-aqua" style="width:{av}%;"></div></div>
                <div style="margin-top:12px;display:flex;gap:1rem;flex-wrap:wrap;">
                    <span style="font-size:0.75rem;color:#7A9E99;">Complete: {sa['completeness']:.0f}%</span>
                    <span style="font-size:0.75rem;color:#7A9E99;">Unique: {sa['uniqueness']:.0f}%</span>
                    <span style="font-size:0.75rem;color:#7A9E99;">Valid: {sa['validity']:.0f}%</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

        # Healing log
        st.markdown("#### Self-Healing Agent Log")
        if healing_log:
            st.markdown("<div class='etl-card'>", unsafe_allow_html=True)
            for entry in healing_log[:12]:
                outcome = entry.get("outcome", "")
                row_cls = "ok" if outcome == "HEALED" else "warn" if outcome == "PARTIAL" else "na"
                icon = "✓" if outcome == "HEALED" else "⚠" if outcome == "PARTIAL" else "○"
                st.markdown(f"""
                <div class="heal-row {row_cls}">
                    <span style="font-weight:700;min-width:16px;">{icon}</span>
                    <div>
                        <div style="font-weight:600;">{entry.get('rule_id','')} — {entry.get('rule_name','')}</div>
                        <div style="color:#5A8A82;font-size:0.8rem;">{entry.get('action','')}</div>
                    </div>
                    <span style="margin-left:auto;font-size:0.72rem;color:#7A9E99;">{entry.get('triggered_at','')}</span>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("No healing rules triggered — data was clean.")

        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

        # Side-by-side dataset comparison
        st.markdown("#### Dataset Comparison")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<p class="label-lav" style="color:#7A5F5C;margin-bottom:6px;">RAW DATASET</p>', unsafe_allow_html=True)
            raw_df = st.session_state.get("uploaded_df")
            if raw_df is not None:
                st.dataframe(raw_df.head(8), use_container_width=True, height=280)
        with col2:
            st.markdown('<p class="label-aqua" style="margin-bottom:6px;">CLEANED DATASET</p>', unsafe_allow_html=True)
            cdf = results.get("clean_df")
            if cdf is not None:
                st.dataframe(cdf.head(8), use_container_width=True, height=280)

    else:
        # No run yet — onboarding
        st.markdown("""
        <div class="hero-banner">
            <div class="hero-title">⚡ ETL-GENERATOR</div>
            <div class="hero-sub">Self-Healing Data Pipeline Platform</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("#### Get Started in 3 Steps")
        c1, c2, c3 = st.columns(3)
        steps = [
            ("📂", "1. Upload Dataset", "Go to Upload & Preview and load a CSV file", "etl-card-aqua"),
            ("🚀", "2. Run Pipeline",   "Execute ETL + self-healing in one click",   "etl-card-sun"),
            ("📊", "3. View Results",   "Explore metrics, charts, and reports",       "etl-card-lav"),
        ]
        for col, (icon, title, desc, cls) in zip([c1, c2, c3], steps):
            col.markdown(f"""
            <div class="etl-card {cls}" style="text-align:center;padding:2rem 1rem;">
                <div style="font-size:2.5rem;margin-bottom:0.75rem;">{icon}</div>
                <div style="font-weight:700;font-size:0.95rem;color:#1C2B2A;margin-bottom:6px;">{title}</div>
                <div style="font-size:0.82rem;color:#7A9E99;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# PAGE: UPLOAD & PREVIEW
# ═════════════════════════════════════════════════════════════════════════════
elif page == "📂  Upload & Preview":
    st.title("📂 Upload & Preview")
    st.caption("Load a CSV dataset to begin. The pipeline accepts any CSV with a header row.")

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    # Upload zone
    uploaded_file = st.file_uploader(
        "Drop your CSV here or click to browse",
        type=["csv"],
        help="Max 10 MB · Must have a header row",
        label_visibility="visible"
    )

    # Sample dataset
    st.markdown("<div style='text-align:center;color:#7A9E99;font-size:0.85rem;margin:0.75rem 0;'>— or —</div>", unsafe_allow_html=True)
    sample_path = os.path.join(DATA_DIR, "dirty_data.csv")
    real_path   = os.path.join(DATA_DIR, "ecommerce_dataset.csv")

    col_a, col_b, col_c = st.columns([1, 1, 1])
    with col_a:
        use_synth = st.button("📥 Synthetic dirty_data.csv",
                              disabled=not os.path.exists(sample_path),
                              use_container_width=True)
    with col_b:
        use_real  = st.button("🌐 Real E-Commerce Dataset",
                              disabled=not os.path.exists(real_path),
                              use_container_width=True)
    with col_c:
        pass  # spacer

    if not os.path.exists(sample_path):
        st.warning("⚠ Synthetic dataset not found — run `python data/generate_dataset.py`")
    if not os.path.exists(real_path):
        st.info("ℹ Real e-commerce dataset not downloaded yet — run `python data/download_real_data.py`")

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

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

            # Validate column names
            for col in df.columns:
                if not re.match(r'^[a-zA-Z0-9_ \-]+$', str(col)):
                    st.error(f"❌ Invalid column name: '{col}'")
                    st.stop()

            st.session_state["uploaded_df"]     = df
            st.session_state["uploaded_source"] = source

            st.success(f"✅ Loaded **{st.session_state['file_name']}**")

            # Metadata row
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Rows", f"{df.shape[0]:,}")
            m2.metric("Columns", df.shape[1])
            sz = round(os.path.getsize(source) / 1024, 1) if isinstance(source, str) \
                 else round(len(source.getvalue()) / 1024, 1)
            m3.metric("File Size", f"{sz} KB")
            m4.metric("Null Cells", f"{df.isnull().sum().sum():,}")

            st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
            st.markdown("#### Raw Data Preview — first 20 rows")
            st.dataframe(df.head(20), use_container_width=True, height=420)

        except pd.errors.EmptyDataError:
            st.error("❌ File is empty.")
        except pd.errors.ParserError as e:
            st.error(f"❌ CSV parse error: {e}")
        except Exception as e:
            st.error(f"❌ Unexpected error: {e}")

    elif st.session_state["uploaded_df"] is not None:
        df = st.session_state["uploaded_df"]
        st.info(f"Currently loaded: **{st.session_state['file_name']}** · {df.shape[0]:,} rows × {df.shape[1]} columns")
        st.dataframe(df.head(20), use_container_width=True, height=420)
    else:
        st.markdown("""
        <div class="etl-card" style="text-align:center;padding:3rem;">
            <div style="font-size:3rem;margin-bottom:1rem;">📂</div>
            <div style="font-size:1rem;font-weight:600;color:#1C2B2A;">No dataset loaded</div>
            <div style="font-size:0.85rem;color:#7A9E99;margin-top:6px;">Upload a CSV or choose a sample above</div>
        </div>
        """, unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# PAGE: SCHEMA & VALIDATION
# ═════════════════════════════════════════════════════════════════════════════
elif page == "🔍  Schema & Validation":
    st.title("🔍 Schema & Validation")
    st.caption("Automatic type detection and pre-pipeline quality analysis")

    df = st.session_state.get("uploaded_df")
    if df is None:
        st.warning("⚠ No dataset loaded — go to **📂 Upload & Preview** first.")
        st.stop()

    from src.validation.schema_inferrer    import get_schema_report
    from src.validation.null_detector      import get_null_report
    from src.validation.duplicate_detector import detect as detect_dupes
    from src.validation.format_validator   import validate_emails, validate_dates
    from src.validation.type_validator     import detect as detect_types
    from src.reporting.quality_scorer      import calculate as score_calc

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(
        ["📋  Schema", "🔎  Null Analysis", "⚠  Issues", "📊  Quality Score"]
    )

    with tab1:
        st.markdown("#### Inferred Column Schema")
        schema_df = get_schema_report(df)
        st.dataframe(schema_df, use_container_width=True, height=440)

    with tab2:
        st.markdown("#### Null Value Distribution")
        null_df = get_null_report(df)
        col1, col2 = st.columns([2, 1])
        with col1:
            st.dataframe(null_df, use_container_width=True, height=380)
        with col2:
            chart = null_df[null_df["null_count"] > 0].set_index("column_name")["null_count"]
            if not chart.empty:
                st.bar_chart(chart, height=380)
            else:
                st.success("✓ No nulls detected")

    with tab3:
        col1, col2 = st.columns(2)
        dupe_result  = detect_dupes(df)
        email_result = validate_emails(df)
        date_result  = validate_dates(df)
        type_result  = detect_types(df)

        with col1:
            st.markdown("#### Duplicate Rows")
            st.metric("Count",   dupe_result["duplicate_count"])
            st.metric("Percent", f"{dupe_result['duplicate_pct']}%")
        with col2:
            st.markdown("#### Format Issues")
            st.metric("Invalid Emails", email_result["invalid_count"])
            st.metric("Invalid Dates",  date_result["invalid_count"])

        if type_result:
            st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
            st.markdown("#### Type Mismatches")
            for col, info in type_result.items():
                if info["invalid_count"] > 0:
                    st.warning(f"**{col}** — {info['invalid_count']} values cannot convert to {info['type']}")

    with tab4:
        q = score_calc(df)
        st.markdown("#### Quality Score Before Cleaning")

        sc = "#3D8C7A" if q["total_score"] >= 80 else "#A36B00" if q["total_score"] >= 60 else "#7A5F5C"
        col_l, col_m, col_r = st.columns([1, 2, 1])
        with col_m:
            st.markdown(f"""
            <div class="etl-card" style="text-align:center;padding:2rem;">
                <div style="font-size:0.75rem;color:#7A9E99;text-transform:uppercase;letter-spacing:.06em;">Total Score</div>
                <div style="font-size:4rem;font-weight:800;color:{sc};line-height:1;">{q['total_score']:.0f}</div>
                <div style="font-size:1rem;color:#7A9E99;">/ 100</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
        st.markdown("#### Dimension Breakdown")
        d1, d2, d3, d4, d5 = st.columns(5)
        d1.metric("Completeness", f"{q['completeness']:.0f}%")
        d2.metric("Uniqueness",   f"{q['uniqueness']:.0f}%")
        d3.metric("Validity",     f"{q['validity']:.0f}%")
        d4.metric("Consistency",  f"{q['consistency']:.0f}%")
        d5.metric("Accuracy",     f"{q['accuracy']:.0f}%")


# ═════════════════════════════════════════════════════════════════════════════
# PAGE: RUN PIPELINE
# ═════════════════════════════════════════════════════════════════════════════
elif page == "🚀  Run Pipeline":
    st.title("🚀 Run Pipeline")
    st.caption("Execute the full ETL workflow — Extract · Validate · Heal · Transform · Load")

    df     = st.session_state.get("uploaded_df")
    source = st.session_state.get("uploaded_source")

    if df is None or source is None:
        st.warning("⚠ No dataset loaded — go to **📂 Upload & Preview** first.")
        st.stop()

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    col1.metric("Source File", st.session_state.get("file_name", "unknown"))
    col2.metric("Rows", f"{df.shape[0]:,}")

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    st.markdown("#### Target Table Configuration")
    table_name = st.text_input(
        "SQLite table name",
        value="cleaned_data",
        help="Letters, numbers, and underscores only — no spaces.",
        max_chars=64
    )

    if table_name.strip():
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', table_name.strip()):
            st.error("❌ Table name must start with a letter/underscore and contain only alphanumeric characters and underscores.")
            st.stop()
    else:
        st.error("❌ Table name cannot be empty.")
        st.stop()

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    col_l, col_m, col_r = st.columns([1, 2, 1])
    with col_m:
        run_btn = st.button("▶  Execute Pipeline", type="primary", use_container_width=True)

    if run_btn:
        with st.spinner("Running ETL pipeline…"):
            if hasattr(source, "seek"):
                source.seek(0)
            prog = st.progress(0, text="Starting…")
            results = run_pipeline(source, table_name=table_name.strip())
            prog.progress(100, text="Complete ✓")

        st.session_state["pipeline_results"] = results

        if results["status"] == "success":
            s = results["summary"]
            st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
            st.success("✅ Pipeline completed successfully!")

            r1, r2, r3, r4 = st.columns(4)
            r1.metric("Rows Input",   f"{s['rows_input']:,}")
            r2.metric("Rows Loaded",  f"{s['rows_loaded']:,}")
            r3.metric("Score",
                      f"{s['quality_score_after']:.1f}%",
                      delta=f"+{s['score_improvement']:.1f}%")
            r4.metric("Duration",     f"{s['duration_seconds']:.1f}s")

            st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
            st.info("💡 Navigate to **🏠 Dashboard** for the full analysis.")
        else:
            st.error(f"❌ Pipeline failed: {results.get('error', 'Unknown error')}")
            with st.expander("Error Details"):
                st.code(results.get("error", ""), language="python")

    elif st.session_state["pipeline_results"] is not None:
        prev = st.session_state["pipeline_results"]
        if prev.get("status") == "success":
            st.success("✅ Pipeline already executed — results available in Dashboard.")
        col_l2, col_m2, col_r2 = st.columns([1, 2, 1])
        with col_m2:
            if st.button("🔄  Re-run Pipeline", use_container_width=True):
                st.session_state["pipeline_results"] = None
                st.rerun()


# ═════════════════════════════════════════════════════════════════════════════
# PAGE: RESULTS & REPORTS
# ═════════════════════════════════════════════════════════════════════════════
elif page == "📊  Results & Reports":
    st.title("📊 Results & Reports")
    st.caption("Download reports, inspect logs, and query the loaded SQLite table")

    results = st.session_state.get("pipeline_results")
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    # ETL Summary card
    summary_path = os.path.join(REPORTS_DIR, "etl_summary.json")
    if os.path.exists(summary_path):
        with open(summary_path, "r", encoding="utf-8") as f:
            sd = json.load(f)
        st.markdown("#### ETL Run Summary")
        s1, s2, s3 = st.columns(3)
        s1.metric("Run At",       sd.get("run_timestamp", "—"))
        s2.metric("Source",       sd.get("source_file",   "—"))
        s3.metric("Target Table", sd.get("target_table",  "—"))
        with st.expander("Full JSON"):
            st.json(sd)
    else:
        st.info("No completed pipeline run found. Run the pipeline first.")

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    # Downloads
    st.markdown("#### Download Reports")
    dc1, dc2 = st.columns(2)
    left_files  = [("Schema Report",   "schema_report.csv",  "text/csv"),
                   ("Cleaning Report", "cleaning_report.csv","text/csv")]
    right_files = [("Healing Report",  "healing_report.csv", "text/csv"),
                   ("ETL Summary",     "etl_summary.json",   "application/json")]

    with dc1:
        for label, fname, mime in left_files:
            path = os.path.join(REPORTS_DIR, fname)
            if os.path.exists(path):
                with open(path, "rb") as f:
                    st.download_button(f"⬇  {label}", f, file_name=fname,
                                       mime=mime, use_container_width=True)
            else:
                st.caption(f"⚠ {label} not yet generated")

    with dc2:
        for label, fname, mime in right_files:
            path = os.path.join(REPORTS_DIR, fname)
            if os.path.exists(path):
                with open(path, "rb") as f:
                    st.download_button(f"⬇  {label}", f, file_name=fname,
                                       mime=mime, use_container_width=True)
            else:
                st.caption(f"⚠ {label} not yet generated")

    # Cleaned data download
    if results and results.get("status") == "success":
        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
        col_l, col_m, col_r = st.columns([1, 2, 1])
        with col_m:
            csv_bytes = results["clean_df"].to_csv(index=False).encode("utf-8")
            st.download_button("⬇  Download Cleaned Dataset (CSV)",
                               csv_bytes, "cleaned_data.csv",
                               "text/csv", use_container_width=True, type="primary")

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    # SQLite table preview
    st.markdown("#### SQLite Table Preview")
    tables = list_tables()
    if tables:
        sel = st.selectbox("Select table", tables)
        prev_df = query_table(sel, limit=50)
        st.dataframe(prev_df, use_container_width=True, height=360)
        st.caption(f"Showing up to 50 rows from '{sel}'")
    else:
        st.info("No tables loaded yet.")

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    # Log viewer
    st.markdown("#### Pipeline Log")
    if os.path.exists(LOG_FILE_PATH):
        log_level = st.selectbox("Filter", ["ALL", "INFO", "WARNING", "ERROR"],
                                 label_visibility="collapsed")
        with open(LOG_FILE_PATH, "r", encoding="utf-8") as f:
            lines = f.readlines()
        filtered = lines if log_level == "ALL" else [l for l in lines if f"| {log_level}" in l]
        st.text_area("Log Output", "".join(filtered[-200:]), height=380,
                     label_visibility="collapsed")
        st.caption(f"Showing {min(200, len(filtered))} of {len(filtered)} entries")
    else:
        st.info("No log file found — run the pipeline first.")
