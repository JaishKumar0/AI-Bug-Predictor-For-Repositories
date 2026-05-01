import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="BugRadar AI",
    layout="wide",
    page_icon="🔬",
    initial_sidebar_state="collapsed"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');

/* ── Root Variables ── */
:root {
    --bg: #0a0c10;
    --surface: #111318;
    --surface2: #181c24;
    --border: #242830;
    --accent: #00e5ff;
    --accent2: #ff4d6d;
    --accent3: #ffd60a;
    --text: #e8eaf0;
    --muted: #6b7280;
    --high: #ff2d55;
    --mid: #ff9f0a;
    --low: #30d158;
}

/* ── Global Reset ── */
html, body, .stApp {
    background-color: var(--bg) !important;
    font-family: 'DM Sans', sans-serif;
    color: var(--text);
}

.block-container {
    padding: 2rem 3rem !important;
    max-width: 1400px !important;
}

/* ── Hide Streamlit Branding ── */
#MainMenu, footer, header { visibility: hidden; }

/* ── Hero Banner ── */
.hero {
    background: linear-gradient(135deg, #0d1117 0%, #111827 50%, #0a0c10 100%);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 3rem 3.5rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -10%;
    width: 500px;
    height: 500px;
    background: radial-gradient(circle, rgba(0,229,255,0.06) 0%, transparent 70%);
    pointer-events: none;
}
.hero::after {
    content: '';
    position: absolute;
    bottom: -30%;
    right: 5%;
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, rgba(255,77,109,0.05) 0%, transparent 70%);
    pointer-events: none;
}
.hero-tag {
    display: inline-block;
    background: rgba(0,229,255,0.1);
    border: 1px solid rgba(0,229,255,0.3);
    color: var(--accent);
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.15em;
    padding: 0.3rem 0.8rem;
    border-radius: 20px;
    margin-bottom: 1rem;
}
.hero h1 {
    font-family: 'Space Mono', monospace;
    font-size: 2.8rem;
    font-weight: 700;
    color: #fff;
    margin: 0.5rem 0;
    line-height: 1.15;
    letter-spacing: -0.02em;
}
.hero h1 span { color: var(--accent); }
.hero p {
    color: var(--muted);
    font-size: 1rem;
    max-width: 560px;
    line-height: 1.7;
    margin-top: 0.8rem;
}
.tech-pills {
    display: flex;
    gap: 0.5rem;
    margin-top: 1.5rem;
    flex-wrap: wrap;
}
.tech-pill {
    background: var(--surface2);
    border: 1px solid var(--border);
    color: var(--muted);
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    padding: 0.3rem 0.7rem;
    border-radius: 6px;
    letter-spacing: 0.05em;
}

/* ── Input Card ── */
.input-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.8rem 2rem;
    margin-bottom: 1.5rem;
}
.input-label {
    font-family: 'Space Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.12em;
    color: var(--muted);
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}

/* ── Streamlit Input Overrides ── */
.stTextInput > div > div > input {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.85rem !important;
    padding: 0.8rem 1rem !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px rgba(0,229,255,0.15) !important;
}
.stTextInput > div > div > input::placeholder { color: var(--muted) !important; }

.stButton > button {
    background: var(--accent) !important;
    color: #000 !important;
    font-family: 'Space Mono', monospace !important;
    font-weight: 700 !important;
    font-size: 0.8rem !important;
    letter-spacing: 0.08em !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.7rem 2rem !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    background: #33ecff !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 20px rgba(0,229,255,0.3) !important;
}

/* ── Metric Cards ── */
.metrics-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin-bottom: 1.5rem;
}
.metric-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.4rem 1.6rem;
    position: relative;
    overflow: hidden;
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    border-radius: 12px 12px 0 0;
}
.metric-card.danger::before  { background: var(--high); }
.metric-card.warning::before { background: var(--mid); }
.metric-card.success::before { background: var(--low); }
.metric-card.info::before    { background: var(--accent); }
.metric-label {
    font-family: 'Space Mono', monospace;
    font-size: 0.62rem;
    letter-spacing: 0.12em;
    color: var(--muted);
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}
.metric-value {
    font-family: 'Space Mono', monospace;
    font-size: 2rem;
    font-weight: 700;
    line-height: 1;
}
.metric-card.danger  .metric-value { color: var(--high); }
.metric-card.warning .metric-value { color: var(--mid); }
.metric-card.success .metric-value { color: var(--low); }
.metric-card.info    .metric-value { color: var(--accent); }
.metric-sub {
    font-size: 0.72rem;
    color: var(--muted);
    margin-top: 0.4rem;
}

/* ── Section Headers ── */
.section-header {
    display: flex;
    align-items: center;
    gap: 0.7rem;
    margin-bottom: 1rem;
    margin-top: 0.5rem;
}
.section-header .dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: var(--accent);
    flex-shrink: 0;
}
.section-header h3 {
    font-family: 'Space Mono', monospace;
    font-size: 0.78rem;
    letter-spacing: 0.12em;
    color: var(--muted);
    text-transform: uppercase;
    margin: 0;
}

/* ── Legend ── */
.legend-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.8rem;
    margin-bottom: 1.5rem;
}
.legend-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1.2rem 1.4rem;
    display: flex;
    gap: 1rem;
    align-items: flex-start;
}
.legend-icon {
    width: 36px; height: 36px;
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1rem;
    flex-shrink: 0;
    margin-top: 2px;
}
.legend-card.high  .legend-icon { background: rgba(255,45,85,0.15); }
.legend-card.mid   .legend-icon { background: rgba(255,159,10,0.15); }
.legend-card.low   .legend-icon { background: rgba(48,209,88,0.15); }
.legend-title {
    font-family: 'Space Mono', monospace;
    font-size: 0.72rem;
    font-weight: 700;
    margin-bottom: 0.3rem;
}
.legend-card.high .legend-title { color: var(--high); }
.legend-card.mid  .legend-title { color: var(--mid); }
.legend-card.low  .legend-title { color: var(--low); }
.legend-desc { font-size: 0.78rem; color: var(--muted); line-height: 1.5; }
.legend-range {
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    margin-top: 0.4rem;
    opacity: 0.7;
}
.legend-card.high .legend-range { color: var(--high); }
.legend-card.mid  .legend-range { color: var(--mid); }
.legend-card.low  .legend-range { color: var(--low); }

/* ── Table Overrides ── */
.stDataFrame { border-radius: 10px; overflow: hidden; }
.stDataFrame iframe { background: var(--surface) !important; }

/* ── How It Works ── */
.steps-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0.8rem;
    margin-bottom: 1.5rem;
}
.step-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1.2rem;
    text-align: center;
}
.step-num {
    font-family: 'Space Mono', monospace;
    font-size: 1.4rem;
    font-weight: 700;
    color: var(--accent);
    margin-bottom: 0.5rem;
}
.step-title {
    font-weight: 600;
    font-size: 0.85rem;
    color: var(--text);
    margin-bottom: 0.3rem;
}
.step-desc { font-size: 0.75rem; color: var(--muted); line-height: 1.5; }

/* ── Success Banner ── */
.success-banner {
    background: rgba(48,209,88,0.08);
    border: 1px solid rgba(48,209,88,0.25);
    border-radius: 10px;
    padding: 1rem 1.4rem;
    display: flex;
    align-items: center;
    gap: 0.8rem;
    margin-bottom: 1.5rem;
}
.success-banner span { color: var(--low); font-weight: 600; font-size: 0.9rem; }
.success-banner small { color: var(--muted); font-size: 0.78rem; }

/* ── Error / Warning Overrides ── */
.stAlert { border-radius: 10px !important; }

/* ── Spinner ── */
.stSpinner > div { color: var(--accent) !important; }

/* ── Separator ── */
hr { border-color: var(--border) !important; margin: 1.5rem 0 !important; }
</style>
""", unsafe_allow_html=True)


# ── Hero Section ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-tag">🔬 POWERED BY CODEBERT + PYTORCH</div>
    <h1>Bug<span>Radar</span> AI</h1>
    <p>Point it at any public Python repository. Our model scans every file, runs it through CodeBERT embeddings, and ranks each file by bug probability — in seconds.</p>
    <div class="tech-pills">
        <span class="tech-pill">CodeBERT</span>
        <span class="tech-pill">PyTorch Neural Net</span>
        <span class="tech-pill">FastAPI Backend</span>
        <span class="tech-pill">770-dim Embeddings</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ── How It Works ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="section-header"><div class="dot"></div><h3>How It Works</h3></div>
<div class="steps-row">
    <div class="step-card">
        <div class="step-num">01</div>
        <div class="step-title">Paste GitHub URL</div>
        <div class="step-desc">Enter any public Python repo link below. Private repos are not supported.</div>
    </div>
    <div class="step-card">
        <div class="step-num">02</div>
        <div class="step-title">Clone &amp; Parse</div>
        <div class="step-desc">The backend clones the repo and extracts all <code>.py</code> files automatically.</div>
    </div>
    <div class="step-card">
        <div class="step-num">03</div>
        <div class="step-title">AI Analysis</div>
        <div class="step-desc">CodeBERT converts each file into a 768-dim vector. Our PyTorch model scores it.</div>
    </div>
    <div class="step-card">
        <div class="step-num">04</div>
        <div class="step-title">Risk Report</div>
        <div class="step-desc">Files are ranked by bug probability. Review the highest-risk ones first.</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ── Input Section ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="input-card">
    <div class="input-label">🔗 GitHub Repository URL</div>
""", unsafe_allow_html=True)

col_inp, col_btn = st.columns([5, 1])
with col_inp:
    repo_url = st.text_input(
        "", 
        placeholder="https://github.com/username/repository",
        label_visibility="collapsed"
    )
with col_btn:
    st.write("")
    analyze = st.button("🚀 SCAN REPO", type="primary", use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)


# ── Analysis ──────────────────────────────────────────────────────────────────
if analyze:
    if not repo_url:
        st.warning("⚠️ Please enter a GitHub repository URL first.")
    else:
        with st.spinner(f"Cloning and analyzing `{repo_url}` ..."):
            try:
                response = requests.post("http://127.0.0.1:8000/analyze", json={"url": repo_url})

                if response.status_code == 200:
                    data = response.json()

                    if data.get("status") == "error":
                        st.error(f"❌ {data['message']}")
                    else:
                        df = pd.DataFrame(data["predictions"]).sort_values(
                            by="bug_probability", ascending=False
                        ).reset_index(drop=True)

                        # ── Categorise ──────────────────────────────────────
                        def risk_label(p):
                            if p >= 60: return "🔴 High"
                            if p >= 30: return "🟠 Medium"
                            return "🟢 Low"
                        def risk_color(p):
                            if p >= 60: return "#ff2d55"
                            if p >= 30: return "#ff9f0a"
                            return "#30d158"

                        df["risk"]  = df["bug_probability"].apply(risk_label)
                        df["color"] = df["bug_probability"].apply(risk_color)

                        high_count = (df["bug_probability"] >= 60).sum()
                        mid_count  = ((df["bug_probability"] >= 30) & (df["bug_probability"] < 60)).sum()
                        low_count  = (df["bug_probability"] < 30).sum()
                        avg_prob   = df["bug_probability"].mean()

                        # ── Success Banner ───────────────────────────────────
                        st.markdown(f"""
                        <div class="success-banner">
                            <span>✅ Analysis Complete</span>
                            <small>— {len(df)} Python files scanned across the repository</small>
                        </div>
                        """, unsafe_allow_html=True)

                        # ── Summary Metrics ──────────────────────────────────
                        st.markdown("""
                        <div class="section-header"><div class="dot"></div><h3>Repository Overview</h3></div>
                        <div class="metrics-row">
                        """, unsafe_allow_html=True)

                        m1, m2, m3, m4 = st.columns(4)
                        with m1:
                            st.markdown(f"""
                            <div class="metric-card danger">
                                <div class="metric-label">High Risk Files</div>
                                <div class="metric-value">{high_count}</div>
                                <div class="metric-sub">Requires immediate review</div>
                            </div>""", unsafe_allow_html=True)
                        with m2:
                            st.markdown(f"""
                            <div class="metric-card warning">
                                <div class="metric-label">Medium Risk Files</div>
                                <div class="metric-value">{mid_count}</div>
                                <div class="metric-sub">Worth investigating</div>
                            </div>""", unsafe_allow_html=True)
                        with m3:
                            st.markdown(f"""
                            <div class="metric-card success">
                                <div class="metric-label">Low Risk Files</div>
                                <div class="metric-value">{low_count}</div>
                                <div class="metric-sub">Clean — no action needed</div>
                            </div>""", unsafe_allow_html=True)
                        with m4:
                            st.markdown(f"""
                            <div class="metric-card info">
                                <div class="metric-label">Avg Bug Probability</div>
                                <div class="metric-value">{avg_prob:.1f}%</div>
                                <div class="metric-sub">Across all {len(df)} files</div>
                            </div>""", unsafe_allow_html=True)

                        st.markdown("</div>", unsafe_allow_html=True)

                        # ── Risk Legend ──────────────────────────────────────
                        st.markdown("""
                        <div class="section-header" style="margin-top:1.5rem;"><div class="dot"></div><h3>Risk Level Guide — What Do These Scores Mean?</h3></div>
                        <div class="legend-grid">
                            <div class="legend-card high">
                                <div class="legend-icon">🔴</div>
                                <div>
                                    <div class="legend-title">HIGH RISK</div>
                                    <div class="legend-desc">The AI is highly confident this file contains buggy patterns similar to real-world commits. <strong>Open this file first.</strong></div>
                                    <div class="legend-range">Score ≥ 60% · Immediately review</div>
                                </div>
                            </div>
                            <div class="legend-card mid">
                                <div class="legend-icon">🟠</div>
                                <div>
                                    <div class="legend-title">MEDIUM RISK</div>
                                    <div class="legend-desc">Moderate complexity patterns detected. The file may be fine, but it's worth a manual glance during code review.</div>
                                    <div class="legend-range">Score 30–59% · Review when possible</div>
                                </div>
                            </div>
                            <div class="legend-card low">
                                <div class="legend-icon">🟢</div>
                                <div>
                                    <div class="legend-title">LOW RISK</div>
                                    <div class="legend-desc">Standard, clean Python patterns. The model found no suspicious structures here. You can safely deprioritize these.</div>
                                    <div class="legend-range">Score &lt; 30% · No action needed</div>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        st.markdown("<hr>", unsafe_allow_html=True)

                        # ── Charts + Table ───────────────────────────────────
                        st.markdown("""
                        <div class="section-header"><div class="dot"></div><h3>Detailed Results</h3></div>
                        """, unsafe_allow_html=True)

                        col_chart1, col_chart2 = st.columns([3, 2])

                        # ── Chart 1: Horizontal Bar ──────────────────────────
                        with col_chart1:
                            st.markdown("**📊 Top Files by Bug Probability** — sorted highest to lowest risk")
                            top20 = df.head(20).copy()

                            fig_bar = go.Figure()
                            fig_bar.add_trace(go.Bar(
                                x=top20["bug_probability"],
                                y=top20["file"],
                                orientation='h',
                                marker=dict(
                                    color=top20["bug_probability"],
                                    colorscale=[
                                        [0.0,  "#1a2a1a"],
                                        [0.3,  "#30d158"],
                                        [0.59, "#ff9f0a"],
                                        [1.0,  "#ff2d55"]
                                    ],
                                    cmin=0, cmax=100,
                                    line=dict(width=0)
                                ),
                                text=[f"{p:.1f}%" for p in top20["bug_probability"]],
                                textposition='outside',
                                textfont=dict(color="#e8eaf0", size=11, family="Space Mono"),
                                hovertemplate="<b>%{y}</b><br>Bug Probability: %{x:.1f}%<extra></extra>"
                            ))
                            fig_bar.update_layout(
                                plot_bgcolor='rgba(0,0,0,0)',
                                paper_bgcolor='rgba(0,0,0,0)',
                                font=dict(color="#6b7280", family="DM Sans"),
                                height=500,
                                margin=dict(l=10, r=60, t=10, b=30),
                                xaxis=dict(
                                    range=[0, 115],
                                    showgrid=True,
                                    gridcolor='rgba(255,255,255,0.05)',
                                    ticksuffix="%",
                                    tickfont=dict(color="#6b7280", size=10),
                                    zeroline=False
                                ),
                                yaxis=dict(
                                    categoryorder='total ascending',
                                    tickfont=dict(color="#aab0bd", size=11),
                                    automargin=True
                                ),
                                bargap=0.3
                            )
                            # Add threshold reference line at 60%
                            fig_bar.add_vline(
                                x=60,
                                line_dash="dash",
                                line_color="rgba(255,45,85,0.4)",
                                annotation_text="High Risk Threshold",
                                annotation_font_color="#ff2d55",
                                annotation_font_size=10
                            )
                            st.plotly_chart(fig_bar, use_container_width=True)

                        # ── Chart 2: Donut ───────────────────────────────────
                        with col_chart2:
                            st.markdown("**🍩 Risk Distribution** — breakdown of your repository health")
                            fig_donut = go.Figure(go.Pie(
                                labels=["High Risk", "Medium Risk", "Low Risk"],
                                values=[high_count, mid_count, low_count],
                                hole=0.65,
                                marker=dict(
                                    colors=["#ff2d55", "#ff9f0a", "#30d158"],
                                    line=dict(color="#0a0c10", width=3)
                                ),
                                textfont=dict(family="Space Mono", size=11, color="#e8eaf0"),
                                hovertemplate="<b>%{label}</b><br>%{value} files (%{percent})<extra></extra>"
                            ))
                            fig_donut.update_layout(
                                plot_bgcolor='rgba(0,0,0,0)',
                                paper_bgcolor='rgba(0,0,0,0)',
                                font=dict(color="#6b7280", family="DM Sans"),
                                height=280,
                                margin=dict(l=0, r=0, t=0, b=0),
                                showlegend=True,
                                legend=dict(
                                    orientation="h",
                                    yanchor="bottom", y=-0.15,
                                    xanchor="center", x=0.5,
                                    font=dict(color="#aab0bd", size=11)
                                ),
                                annotations=[dict(
                                    text=f"<b>{len(df)}</b><br><span style='font-size:10px'>FILES</span>",
                                    x=0.5, y=0.5,
                                    font=dict(size=18, color="#e8eaf0", family="Space Mono"),
                                    showarrow=False
                                )]
                            )
                            st.plotly_chart(fig_donut, use_container_width=True)

                            # ── Scatter plot: LOC vs Risk ────────────────────
                            if "loc" in df.columns:
                                st.markdown("**🔵 File Size vs Risk** — larger files tend to have more bugs")
                                fig_scatter = px.scatter(
                                    df,
                                    x="loc",
                                    y="bug_probability",
                                    color="bug_probability",
                                    color_continuous_scale=[
                                        [0.0, "#30d158"],
                                        [0.5, "#ff9f0a"],
                                        [1.0, "#ff2d55"]
                                    ],
                                    hover_name="file",
                                    labels={"loc": "Lines of Code", "bug_probability": "Bug Probability (%)"},
                                    size_max=12
                                )
                                fig_scatter.update_traces(
                                    marker=dict(size=8, opacity=0.8, line=dict(width=0))
                                )
                                fig_scatter.update_layout(
                                    plot_bgcolor='rgba(0,0,0,0)',
                                    paper_bgcolor='rgba(0,0,0,0)',
                                    font=dict(color="#6b7280", family="DM Sans", size=10),
                                    height=200,
                                    margin=dict(l=0, r=20, t=10, b=30),
                                    coloraxis_showscale=False,
                                    xaxis=dict(gridcolor='rgba(255,255,255,0.05)', zeroline=False),
                                    yaxis=dict(
                                        gridcolor='rgba(255,255,255,0.05)',
                                        zeroline=False,
                                        ticksuffix="%"
                                    )
                                )
                                st.plotly_chart(fig_scatter, use_container_width=True)

                        st.markdown("<hr>", unsafe_allow_html=True)

                        # ── Full Risk Table ──────────────────────────────────
                        st.markdown("""
                        <div class="section-header"><div class="dot"></div><h3>Full File Risk Table — Click any column header to sort</h3></div>
                        """, unsafe_allow_html=True)

                        display_df = df[["file", "bug_probability", "risk"] + (["loc"] if "loc" in df.columns else [])].copy()
                        display_df.columns = (
                            ["File", "Bug Probability (%)", "Risk Level"] +
                            (["Lines of Code"] if "loc" in df.columns else [])
                        )
                        display_df.index = display_df.index + 1

                        st.dataframe(
                            display_df.style
                                .background_gradient(cmap="RdYlGn_r", subset=["Bug Probability (%)"])
                                .format({"Bug Probability (%)": "{:.1f}%"})
                                .set_properties(**{
                                    'background-color': '#111318',
                                    'color': '#e8eaf0',
                                    'border-color': '#242830'
                                }),
                            use_container_width=True,
                            height=420
                        )

                        # ── Action Guide ─────────────────────────────────────
                        st.markdown("<hr>", unsafe_allow_html=True)
                        st.markdown("""
                        <div class="section-header"><div class="dot"></div><h3>What To Do Next</h3></div>
                        <div class="steps-row">
                            <div class="step-card">
                                <div class="step-num" style="color:var(--high)">①</div>
                                <div class="step-title">Open High-Risk Files</div>
                                <div class="step-desc">Any file scoring ≥ 60% should be manually reviewed. Look for complex logic, missing error handling, or edge cases.</div>
                            </div>
                            <div class="step-card">
                                <div class="step-num" style="color:var(--mid)">②</div>
                                <div class="step-title">Check Medium-Risk Files</div>
                                <div class="step-desc">Files scoring 30–59% are worth a glance during code review. They may be fine but deserve attention.</div>
                            </div>
                            <div class="step-card">
                                <div class="step-num" style="color:var(--low)">③</div>
                                <div class="step-title">Write Tests for High-Risk</div>
                                <div class="step-desc">For flagged files, add unit tests to cover edge cases. Tests confirm whether bugs exist and prevent future regressions.</div>
                            </div>
                            <div class="step-card">
                                <div class="step-num" style="color:var(--accent)">④</div>
                                <div class="step-title">Re-scan After Fixes</div>
                                <div class="step-desc">After fixing issues, scan the repo again. You should see scores drop. Use this as a health tracker over time.</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                else:
                    st.error("❌ Backend returned an error. Make sure FastAPI is running on port 8000.")

            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to backend. Run: `uvicorn main:app --reload` in your terminal first.")
            except Exception as e:
                st.error(f"❌ Unexpected error: {str(e)}")