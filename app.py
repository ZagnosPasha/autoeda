import streamlit as st
import pandas as pd
from analyser import load_data, get_summary, get_missing_report, get_column_stats
from visualiser import plot_histogram, plot_bar, plot_correlation, plot_missing
from narrator import generate_narrative, answer_question
 
# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Perceiv",
    page_icon="📊",
    layout="wide"
)
 
# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  #MainMenu {visibility: hidden;}
  footer    {visibility: hidden;}
  header    {visibility: hidden;}
 
  /* ── App background ── */
  .stApp {
      background: linear-gradient(135deg, #1a1f2e 0%, #242938 100%);
  }
 
  /* ── Hide default Streamlit padding ── */
  .block-container {
      padding: 0 !important;
      max-width: 100% !important;
  }
 
  /* ── Sidebar panel ── */
  [data-testid="stSidebar"] {
      background: rgba(15, 18, 30, 0.85) !important;
      border-right: 1px solid rgba(255,255,255,0.07) !important;
  }
  [data-testid="stSidebar"] * {
      color: rgba(255,255,255,0.85) !important;
  }
 
  /* ── Metric tiles in sidebar ── */
  [data-testid="metric-container"] {
      background: rgba(255,255,255,0.06) !important;
      border: 1px solid rgba(255,255,255,0.10) !important;
      border-radius: 10px !important;
      padding: 12px 14px !important;
  }
  [data-testid="metric-container"] label {
      color: rgba(255,255,255,0.55) !important;
      font-size: 11px !important;
      text-transform: uppercase;
      letter-spacing: 0.07em;
  }
  [data-testid="metric-container"] [data-testid="stMetricValue"] {
      color: #ffffff !important;
      font-size: 22px !important;
      font-weight: 700 !important;
  }
 
  /* ── Column badge chips ── */
  .col-chip {
      display: inline-block;
      font-size: 10px;
      font-weight: 600;
      padding: 2px 7px;
      border-radius: 10px;
      letter-spacing: 0.04em;
      text-transform: uppercase;
  }
  .chip-num  { background: rgba(99,102,241,0.25); color: #a5b4fc; }
  .chip-text { background: rgba(52,211,153,0.18); color: #6ee7b7; }
  .chip-dt   { background: rgba(251,191,36,0.20); color: #fcd34d; }
  .chip-other{ background: rgba(255,255,255,0.10); color: rgba(255,255,255,0.5); }
 
  /* ── Chat bubbles ── */
  .chat-wrap {
      display: flex;
      flex-direction: column;
      gap: 16px;
      padding: 24px 28px 8px;
  }
  .bubble-ai {
      background: rgba(255,255,255,0.06);
      border: 1px solid rgba(255,255,255,0.10);
      border-radius: 16px 16px 16px 4px;
      padding: 16px 20px;
      max-width: 88%;
      align-self: flex-start;
      color: #e2e8f0;
      font-size: 14px;
      line-height: 1.75;
  }
  .bubble-user {
      background: rgba(99,102,241,0.22);
      border: 1px solid rgba(99,102,241,0.35);
      border-radius: 16px 16px 4px 16px;
      padding: 12px 18px;
      max-width: 78%;
      align-self: flex-end;
      color: #e0e7ff;
      font-size: 14px;
      line-height: 1.65;
  }
  .msg-label {
      font-size: 10px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      margin-bottom: 6px;
  }
  .label-ai   { color: #818cf8; }
  .label-user { color: rgba(255,255,255,0.4); text-align: right; }
 
  /* ── Suggestion chips ── */
  .chips-row {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 12px;
  }
 
  /* ── File uploader ── */
  [data-testid="stFileUploadDropzone"] {
      background: rgba(255,255,255,0.03) !important;
      border: 2px dashed rgba(99,102,241,0.35) !important;
      border-radius: 12px !important;
  }
 
  /* ── Tabs ── */
  .stTabs [data-baseweb="tab-list"] {
      background: rgba(255,255,255,0.04);
      border-radius: 10px;
      padding: 3px;
      gap: 2px;
  }
  .stTabs [data-baseweb="tab"] {
      border-radius: 8px;
      color: rgba(255,255,255,0.5);
      font-weight: 500;
      font-size: 13px;
  }
  .stTabs [aria-selected="true"] {
      background: rgba(99,102,241,0.28) !important;
      color: #ffffff !important;
  }
 
  /* ── Chat input ── */
  [data-testid="stChatInput"] {
      background: rgba(255,255,255,0.05) !important;
      border: 1px solid rgba(255,255,255,0.12) !important;
      border-radius: 14px !important;
  }
  [data-testid="stChatInput"] textarea {
      color: rgba(255,255,255,0.9) !important;
      font-size: 14px !important;
  }
 
  /* ── Expanders ── */
  [data-testid="stExpander"] details {
      background: rgba(255,255,255,0.03) !important;
      border: 1px solid rgba(255,255,255,0.08) !important;
      border-radius: 10px !important;
  }
  [data-testid="stExpander"] details summary {
      color: rgba(255,255,255,0.75) !important;
  }
  [data-testid="stExpander"] details summary:hover {
      background: rgba(99,102,241,0.15) !important;
      color: #ffffff !important;
  }
 
  /* ── Dataframe ── */
  [data-testid="stDataFrame"] iframe {
      background: #1a1f2e !important;
  }
 
  /* ── Scrollbar ── */
  ::-webkit-scrollbar { width: 5px; height: 5px; }
  ::-webkit-scrollbar-track { background: rgba(255,255,255,0.04); }
  ::-webkit-scrollbar-thumb { background: rgba(99,102,241,0.4); border-radius: 4px; }
 
  /* ── Code blocks ── */
  pre { background: #0d1117 !important; border: 1px solid rgba(255,255,255,0.08) !important; border-radius: 8px !important; }
  pre code { color: #c9d1d9 !important; background: transparent !important; }
 
  /* ── General text ── */
  p, span, div, label { color: rgba(255,255,255,0.82); }
  h1, h2, h3 { color: #ffffff !important; }
  hr { border-color: rgba(255,255,255,0.07); }
</style>
""", unsafe_allow_html=True)
 
 
# ── Session state defaults ─────────────────────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []        # {"role": "ai"|"user", "content": str}
if "llm_history" not in st.session_state:
    st.session_state.llm_history = []         # {"role": "assistant"|"user", "content": str}
if "data_loaded" not in st.session_state:
    st.session_state.data_loaded = False
if "suggestion_used" not in st.session_state:
    st.session_state.suggestion_used = None
 
 
# ── Helper: column type badge ──────────────────────────────────────────────────
def col_badge(col_name, col_stats, datetime_col_names):
    if col_name in datetime_col_names:
        return '<span class="col-chip chip-dt">date</span>'
    s = col_stats.get(col_name, {})
    t = s.get("type", "other")
    if t == "numeric":
        return '<span class="col-chip chip-num">num</span>'
    if t == "text":
        return '<span class="col-chip chip-text">text</span>'
    return '<span class="col-chip chip-other">?</span>'
 
 
# ── Helper: render a chat bubble ───────────────────────────────────────────────
def render_bubble(role, content):
    if role == "ai":
        st.markdown(f"""
        <div class="bubble-ai">
            <div class="msg-label label-ai">Perceiv</div>
            {content}
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="display:flex;justify-content:flex-end;">
        <div class="bubble-user">
            <div class="msg-label label-user">You</div>
            {content}
        </div></div>""", unsafe_allow_html=True)
 
 
# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 📊 Perceiv")
    st.markdown(
        '<p style="color:rgba(255,255,255,0.4);margin-top:-10px;font-size:13px;">'
        'AI-powered data analysis</p>',
        unsafe_allow_html=True
    )
 
    uploaded_file = st.file_uploader(
        "Upload CSV or Excel",
        type=["csv", "xlsx"],
        label_visibility="collapsed"
    )
 
    if uploaded_file is None:
        st.markdown(
            '<div style="border:2px dashed rgba(99,102,241,0.3);border-radius:12px;'
            'padding:24px;text-align:center;margin-top:8px;">'
            '<div style="font-size:28px;margin-bottom:8px;">📂</div>'
            '<div style="font-size:13px;color:rgba(255,255,255,0.4);">Drop a CSV or Excel file</div>'
            '</div>',
            unsafe_allow_html=True
        )
 
    # ── If data is loaded, show sidebar stats ──────────────────────────────────
    if st.session_state.data_loaded:
        df       = st.session_state.df
        summary  = st.session_state.summary
        col_stats = st.session_state.col_stats
        dt_names = summary.get("datetime_col_names", [])
 
        # File chip
        st.markdown(
            f'<div style="background:rgba(99,102,241,0.15);border:1px solid rgba(99,102,241,0.3);'
            f'border-radius:8px;padding:7px 12px;font-size:12px;color:#a5b4fc;margin:10px 0 16px;">'
            f'📄 {st.session_state.filename}</div>',
            unsafe_allow_html=True
        )
 
        # Metric tiles
        st.markdown('<div style="font-size:10px;text-transform:uppercase;letter-spacing:0.07em;color:rgba(255,255,255,0.4);margin-bottom:8px;">Overview</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        c1.metric("Rows",    summary["rows"])
        c2.metric("Columns", summary["columns"])
        c3, c4 = st.columns(2)
        c3.metric("Missing", f"{summary['missing_pct']}%")
        c4.metric("Numeric", summary["numeric_cols"])
 
        # Column list
        st.markdown('<div style="font-size:10px;text-transform:uppercase;letter-spacing:0.07em;color:rgba(255,255,255,0.4);margin:16px 0 8px;">Columns</div>', unsafe_allow_html=True)
        for col in df.columns:
            badge = col_badge(col, col_stats, dt_names)
            st.markdown(
                f'<div style="display:flex;justify-content:space-between;align-items:center;'
                f'padding:5px 8px;border-radius:6px;margin-bottom:3px;'
                f'background:rgba(255,255,255,0.04);font-size:12px;">'
                f'<span style="color:rgba(255,255,255,0.75);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:70%;">{col}</span>'
                f'{badge}</div>',
                unsafe_allow_html=True
            )
 
 
# ══════════════════════════════════════════════════════════════════════════════
# MAIN AREA
# ══════════════════════════════════════════════════════════════════════════════
 
# ── Handle new file upload ─────────────────────────────────────────────────────
if uploaded_file is not None:
    file_key = uploaded_file.name + str(uploaded_file.size)
 
    if st.session_state.get("file_key") != file_key:
        # New file — reset everything
        with st.spinner("Loading dataset..."):
            df = load_data(uploaded_file)
 
        if df is None:
            st.error("Could not load file. Please check the format.")
            st.stop()
 
        summary        = get_summary(df)
        missing_report = get_missing_report(df)
        col_stats      = get_column_stats(df)
 
        # Generate richer initial narrative
        with st.spinner("🤖 Analysing dataset..."):
            narrative = generate_narrative(summary, missing_report, col_stats)
 
        # Store in session state
        st.session_state.df             = df
        st.session_state.summary        = summary
        st.session_state.missing_report = missing_report
        st.session_state.col_stats      = col_stats
        st.session_state.filename       = uploaded_file.name
        st.session_state.file_key       = file_key
        st.session_state.data_loaded    = True
 
        # Seed chat with initial narrative
        st.session_state.chat_history = [{"role": "ai", "content": narrative}]
        st.session_state.llm_history  = [{"role": "assistant", "content": narrative}]
        st.session_state.suggestion_used = None
 
 
# ── Main tabs ──────────────────────────────────────────────────────────────────
if st.session_state.data_loaded:
    df            = st.session_state.df
    summary       = st.session_state.summary
    missing_report = st.session_state.missing_report
    col_stats     = st.session_state.col_stats
 
    tab_chat, tab_charts, tab_data = st.tabs(["💬  AI Chat", "📈  Charts", "🗂️  Data"])
 
    # ══════════════════════════════════════════════════════════════════════════
    # TAB 1 — AI CHAT
    # ══════════════════════════════════════════════════════════════════════════
    with tab_chat:
 
        # ── Render conversation history ────────────────────────────────────
        st.markdown('<div class="chat-wrap">', unsafe_allow_html=True)
        for msg in st.session_state.chat_history:
            render_bubble(msg["role"], msg["content"])
        st.markdown('</div>', unsafe_allow_html=True)
 
        # ── Suggestion chips (shown once, below the first AI message) ──────
        if len(st.session_state.chat_history) == 1:
            st.markdown('<div style="padding: 0 28px;">', unsafe_allow_html=True)
 
            # Build dynamic suggestions based on column types
            suggestions = []
            dt_names = summary.get("datetime_col_names", [])
            num_cols = [c for c, s in col_stats.items() if s.get("type") == "numeric"]
            txt_cols = [c for c, s in col_stats.items() if s.get("type") == "text"]
 
            if num_cols:
                suggestions.append(f"Show outliers in {num_cols[0]}")
            if txt_cols:
                suggestions.append(f"Break down by {txt_cols[0]}")
            if any(r["flag"] == "HIGH" for r in missing_report):
                suggestions.append("How should I handle missing values?")
            if len(num_cols) >= 2:
                suggestions.append(f"Correlate {num_cols[0]} and {num_cols[1]}")
            if dt_names:
                suggestions.append(f"What's the time range of {dt_names[0]}?")
            suggestions.append("What should I clean first?")
 
            cols_btn = st.columns(min(len(suggestions), 3))
            for i, sug in enumerate(suggestions[:3]):
                with cols_btn[i]:
                    if st.button(sug, key=f"sug_{i}", use_container_width=True):
                        st.session_state.suggestion_used = sug
                        st.rerun()
 
            # Second row of suggestions
            if len(suggestions) > 3:
                cols_btn2 = st.columns(min(len(suggestions) - 3, 3))
                for i, sug in enumerate(suggestions[3:6]):
                    with cols_btn2[i]:
                        if st.button(sug, key=f"sug2_{i}", use_container_width=True):
                            st.session_state.suggestion_used = sug
                            st.rerun()
 
            st.markdown('</div>', unsafe_allow_html=True)
 
        # ── Process a suggestion chip click ────────────────────────────────
        if st.session_state.suggestion_used:
            question = st.session_state.suggestion_used
            st.session_state.suggestion_used = None
 
            st.session_state.chat_history.append({"role": "user", "content": question})
 
            with st.spinner("Thinking..."):
                answer = answer_question(
                    question,
                    summary,
                    col_stats,
                    st.session_state.llm_history
                )
 
            st.session_state.chat_history.append({"role": "ai", "content": answer})
            st.session_state.llm_history.append({"role": "user",      "content": question})
            st.session_state.llm_history.append({"role": "assistant", "content": answer})
            st.rerun()
 
        # ── Chat input ─────────────────────────────────────────────────────
        st.markdown('<div style="padding: 8px 20px 0;">', unsafe_allow_html=True)
        user_input = st.chat_input("Ask anything about your data...")
        st.markdown('</div>', unsafe_allow_html=True)
 
        if user_input:
            st.session_state.chat_history.append({"role": "user", "content": user_input})
 
            with st.spinner("Thinking..."):
                answer = answer_question(
                    user_input,
                    summary,
                    col_stats,
                    st.session_state.llm_history
                )
 
            st.session_state.chat_history.append({"role": "ai", "content": answer})
            st.session_state.llm_history.append({"role": "user",      "content": user_input})
            st.session_state.llm_history.append({"role": "assistant", "content": answer})
            st.rerun()
 
    # ══════════════════════════════════════════════════════════════════════════
    # TAB 2 — CHARTS
    # ══════════════════════════════════════════════════════════════════════════
    with tab_charts:
        st.markdown("### Visualisations")
 
        dt_names = summary.get("datetime_col_names", [])
        numeric_cols = [
            c for c in df.select_dtypes(include="number").columns
            if c not in dt_names
        ]
        text_cols = list(df.select_dtypes(include="object").columns)
 
        cols_per_row = 2
 
        if numeric_cols:
            st.markdown("**Numeric distributions**")
            for i in range(0, len(numeric_cols), cols_per_row):
                row_cols = st.columns(cols_per_row)
                for j, col in enumerate(numeric_cols[i:i + cols_per_row]):
                    with row_cols[j]:
                        fig = plot_histogram(df, col)
                        if fig:
                            ax = fig.axes[0]
                            ax.set_xlim(left=df[col].min())
                            st.pyplot(fig)
                        with st.expander("📋 Copy code"):
                            st.code(f"""
import matplotlib.pyplot as plt
import pandas as pd
 
df = pd.read_csv("your_file.csv")
df["{col}"].hist(bins=30, color="steelblue", edgecolor="white")
plt.title("Distribution of {col}")
plt.xlabel("{col}")
plt.ylabel("Count")
plt.xlim(left=df["{col}"].min())
plt.show()
""", language="python")
 
        if text_cols:
            st.markdown("**Categorical columns**")
            for i in range(0, len(text_cols), cols_per_row):
                row_cols = st.columns(cols_per_row)
                for j, col in enumerate(text_cols[i:i + cols_per_row]):
                    with row_cols[j]:
                        st.pyplot(plot_bar(df, col))
                        with st.expander("📋 Copy code"):
                            st.code(f"""
import matplotlib.pyplot as plt
import pandas as pd
 
df = pd.read_csv("your_file.csv")
counts = df["{col}"].value_counts().head(10)
plt.bar(range(len(counts)), counts.values,
        color="steelblue", edgecolor="white")
plt.xticks(range(len(counts)), counts.index, rotation=45)
plt.title("Value counts of {col}")
plt.tight_layout()
plt.show()
""", language="python")
 
        if len(numeric_cols) >= 2:
            st.markdown("**Correlation heatmap**")
            st.pyplot(plot_correlation(df[numeric_cols]))
            with st.expander("📋 Copy code"):
                st.code("""
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
 
df = pd.read_csv("your_file.csv")
corr = df.corr(numeric_only=True)
fig, ax = plt.subplots(figsize=(10, 5))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", ax=ax)
plt.title("Correlation Heatmap")
plt.show()
""", language="python")
 
        missing_only = [r for r in missing_report if r["missing"] > 0]
        if missing_only:
            st.markdown("**Missing values**")
            st.pyplot(plot_missing(missing_report))
 
    # ══════════════════════════════════════════════════════════════════════════
    # TAB 3 — DATA
    # ══════════════════════════════════════════════════════════════════════════
    with tab_data:
        st.markdown("### Dataset preview")
        st.markdown(
            f'<p style="color:rgba(255,255,255,0.45);font-size:13px;">'
            f'{summary["rows"]} rows × {summary["columns"]} columns — '
            f'showing first 100 rows</p>',
            unsafe_allow_html=True
        )
        st.dataframe(df.head(100), use_container_width=True, hide_index=True)
 
        st.markdown("### Column statistics")
        stats_rows = []
        for col_name, values in col_stats.items():
            row = {"column": col_name}
            row.update(values)
            stats_rows.append(row)
        stats_df = pd.DataFrame(stats_rows)
        st.dataframe(stats_df, use_container_width=True, hide_index=True)
 
        st.markdown("### Missing values report")
        missing_df = pd.DataFrame(missing_report)
        missing_only_df = missing_df[missing_df["missing"] > 0]
 
        if missing_only_df.empty:
            st.success("✅ No missing values found.")
        else:
            st.warning(
                f"⚠️ {len(missing_only_df)} column(s) have missing values "
                f"out of {summary['columns']} total."
            )
            def colour_flag(val):
                if val == "HIGH":   return "color: #f87171; font-weight: 600"
                if val == "LOW":    return "color: #fbbf24; font-weight: 600"
                return "color: #34d399; font-weight: 600"
            styled = missing_only_df.style.map(colour_flag, subset=["flag"])
            st.dataframe(styled, use_container_width=True, hide_index=True)
 
else:
    # ── Empty state ────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;
                height:80vh;text-align:center;padding:40px;">
        <div style="font-size:52px;margin-bottom:20px;">📂</div>
        <div style="font-size:22px;font-weight:600;color:rgba(255,255,255,0.7);margin-bottom:10px;">
            Upload a dataset to get started
        </div>
        <div style="font-size:14px;color:rgba(255,255,255,0.35);">
            Supports .csv and .xlsx — upload using the panel on the left
        </div>
    </div>
    """, unsafe_allow_html=True)