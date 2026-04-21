import re
import streamlit as st
import pandas as pd
from analyser import load_data, get_summary, get_missing_report, get_column_stats
from visualiser import (plot_histogram, plot_bar, plot_correlation,
                        plot_missing_inline, HEATMAP_COL_LIMIT)
from narrator import generate_narrative, answer_question

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Perceiv", page_icon="📊", layout="wide")

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  #MainMenu {visibility: hidden;}
  footer    {visibility: hidden;}
  header    {visibility: hidden;}

  /* App shell — dark gradient kept */
  .stApp { background: linear-gradient(135deg, #1a1f2e 0%, #242938 100%); }
  .block-container { padding: 0 !important; max-width: 100% !important; }

  /* Sidebar */
  [data-testid="stSidebar"] {
      background: rgba(15,18,30,0.92) !important;
      border-right: 1px solid rgba(255,255,255,0.07) !important;
  }
  [data-testid="stSidebar"] * { color: rgba(255,255,255,0.85) !important; }

  /* Sidebar metrics */
  [data-testid="metric-container"] {
      background: rgba(255,255,255,0.06) !important;
      border: 1px solid rgba(255,255,255,0.10) !important;
      border-radius: 10px !important;
      padding: 12px 14px !important;
  }
  [data-testid="metric-container"] label {
      color: rgba(255,255,255,0.5) !important;
      font-size: 11px !important;
      text-transform: uppercase;
      letter-spacing: 0.07em;
  }
  [data-testid="metric-container"] [data-testid="stMetricValue"] {
      color: #fff !important; font-size: 22px !important; font-weight: 700 !important;
  }

  /* Column chips */
  .col-chip {
      display: inline-block; font-size: 10px; font-weight: 600;
      padding: 2px 7px; border-radius: 10px;
      letter-spacing: 0.04em; text-transform: uppercase;
  }
  .chip-num  { background: rgba(99,102,241,0.25); color: #a5b4fc; }
  .chip-text { background: rgba(52,211,153,0.18); color: #6ee7b7; }
  .chip-dt   { background: rgba(251,191,36,0.20); color: #fcd34d; }
  .chip-miss { background: rgba(249,115,22,0.22); color: #fdba74; font-size:9px; }
  .chip-other{ background: rgba(255,255,255,0.10); color: rgba(255,255,255,0.5); }

  /* ── MAIN CONTENT AREA — white/light ── */
  .main-card {
      background: #ffffff;
      border-radius: 16px;
      margin: 16px 16px 0 8px;
      min-height: calc(100vh - 32px);
      display: flex;
      flex-direction: column;
      overflow: hidden;
  }

  /* Tabs inside main card */
  .stTabs [data-baseweb="tab-list"] {
      background: #f1f5f9;
      border-radius: 10px;
      padding: 3px;
      gap: 2px;
      margin: 12px 20px 0;
  }
  .stTabs [data-baseweb="tab"] {
      border-radius: 8px;
      color: #64748b;
      font-weight: 500;
      font-size: 13px;
  }
  .stTabs [aria-selected="true"] {
      background: #ffffff !important;
      color: #6366f1 !important;
      font-weight: 600 !important;
      box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  }

  /* AI bubble — light card style matching image 2 */
  .bubble-ai {
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 16px 16px 16px 4px;
      padding: 16px 20px;
      max-width: 90%;
      color: #1e293b;
      font-size: 14px;
      line-height: 1.75;
  }
  .bubble-ai p { margin: 0 0 8px; color: #1e293b; }
  .bubble-ai p:last-child { margin-bottom: 0; }
  .bubble-ai strong { color: #1e293b; font-weight: 600; }
  .bubble-ai ul { margin: 6px 0; padding-left: 20px; }
  .bubble-ai li { margin-bottom: 4px; color: #334155; }

  /* User bubble */
  .bubble-user {
      background: #eef2ff;
      border: 1px solid #c7d2fe;
      border-radius: 16px 16px 4px 16px;
      padding: 12px 18px;
      max-width: 78%;
      color: #3730a3;
      font-size: 14px;
      line-height: 1.65;
  }

  /* Labels above bubbles */
  .msg-label {
      font-size: 10px; font-weight: 700; text-transform: uppercase;
      letter-spacing: 0.09em; margin-bottom: 5px;
  }
  .label-ai   { color: #6366f1; }
  .label-user { color: #94a3b8; text-align: right; }

  /* Suggestion chips — pill style */
  div[data-testid="stHorizontalBlock"] > div > div > button {
      background: #ffffff !important;
      border: 1px solid #c7d2fe !important;
      border-radius: 20px !important;
      color: #4f46e5 !important;
      font-size: 12px !important;
      padding: 5px 14px !important;
      font-weight: 500 !important;
      transition: all 0.15s !important;
  }
  div[data-testid="stHorizontalBlock"] > div > div > button:hover {
      background: #eef2ff !important;
      border-color: #6366f1 !important;
  }

  /* Chat input — light style */
  [data-testid="stChatInput"] {
      background: #f8fafc !important;
      border: 1px solid #e2e8f0 !important;
      border-radius: 14px !important;
  }
  [data-testid="stChatInput"] textarea {
      color: #1e293b !important;
      font-size: 14px !important;
  }
  [data-testid="stChatInput"] textarea::placeholder { color: #94a3b8 !important; }

  /* Charts tab — white bg, cards */
  .chart-card {
      background: #ffffff;
      border: 1px solid #e2e8f0;
      border-radius: 12px;
      padding: 16px;
      margin-bottom: 12px;
  }

  /* Expanders — light */
  [data-testid="stExpander"] details {
      background: #f8fafc !important;
      border: 1px solid #e2e8f0 !important;
      border-radius: 10px !important;
  }
  [data-testid="stExpander"] details summary { color: #475569 !important; }
  [data-testid="stExpander"] details summary:hover {
      background: #eef2ff !important; color: #4f46e5 !important;
  }

  /* Dataframe in data tab */
  [data-testid="stDataFrame"] iframe { background: #ffffff !important; }

  /* Scrollbar */
  ::-webkit-scrollbar { width: 5px; height: 5px; }
  ::-webkit-scrollbar-track { background: #f1f5f9; }
  ::-webkit-scrollbar-thumb { background: #c7d2fe; border-radius: 4px; }

  /* Code blocks */
  pre { background: #f8fafc !important; border: 1px solid #e2e8f0 !important;
        border-radius: 8px !important; }
  pre code { color: #334155 !important; background: transparent !important; }

  /* General text in main area */
  .stTabs p, .stTabs span, .stTabs div, .stTabs label { color: #334155; }
  .stTabs h1, .stTabs h2, .stTabs h3 { color: #1e293b !important; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ────────────────────────────────────────────────────────────────────

def strip_markdown_headings(text: str) -> str:
    """Convert markdown headings to bold inline text, clean up excess newlines."""
    # Convert ## Heading → <strong>Heading</strong>
    text = re.sub(r'^#{1,4}\s+(.+)$', r'<strong>\1</strong>', text, flags=re.MULTILINE)
    # Convert **bold** → <strong>bold</strong>
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    # Convert *italic* → <em>em</em>
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    # Bullet lines → wrapped in <ul><li>
    lines = text.split('\n')
    out, in_list = [], False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('- ') or stripped.startswith('• '):
            if not in_list:
                out.append('<ul>')
                in_list = True
            out.append(f'<li>{stripped[2:]}</li>')
        else:
            if in_list:
                out.append('</ul>')
                in_list = False
            if stripped:
                out.append(f'<p>{stripped}</p>')
    if in_list:
        out.append('</ul>')
    return '\n'.join(out)


def col_badge(col_name, col_stats, dt_names, missing_report):
    # Missing badge takes priority if severe
    for r in missing_report:
        if r["column"] == col_name and r["flag"] == "HIGH":
            return f'<span class="col-chip chip-miss">{r["pct"]}% miss</span>'
    if col_name in dt_names:
        return '<span class="col-chip chip-dt">date</span>'
    s = col_stats.get(col_name, {})
    t = s.get("type", "other")
    if t == "numeric": return '<span class="col-chip chip-num">num</span>'
    if t == "text":    return '<span class="col-chip chip-text">text</span>'
    return '<span class="col-chip chip-other">?</span>'


def render_bubble(role, content):
    if role == "ai":
        st.markdown(f"""
        <div style="display:flex;flex-direction:column;align-items:flex-start;margin-bottom:4px;">
          <div class="msg-label label-ai">PERCEIV</div>
          <div class="bubble-ai">{content}</div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="display:flex;flex-direction:column;align-items:flex-end;margin-bottom:4px;">
          <div class="msg-label label-user">YOU</div>
          <div class="bubble-user">{content}</div>
        </div>""", unsafe_allow_html=True)


# ── Session state ──────────────────────────────────────────────────────────────
for key, default in [
    ("chat_history", []),
    ("llm_history",  []),
    ("data_loaded",  False),
    ("suggestion_used", None),
]:
    if key not in st.session_state:
        st.session_state[key] = default


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 📊 Perceiv")
    st.markdown('<p style="color:rgba(255,255,255,0.38);margin-top:-10px;font-size:12px;">AI-powered data analysis</p>',
                unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload CSV or Excel", type=["csv","xlsx"],
        label_visibility="collapsed"
    )

    if uploaded_file is None:
        st.markdown(
            '<div style="border:2px dashed rgba(99,102,241,0.3);border-radius:12px;'
            'padding:28px;text-align:center;margin-top:12px;">'
            '<div style="font-size:30px;margin-bottom:8px;">📂</div>'
            '<div style="font-size:12px;color:rgba(255,255,255,0.35);">Drop a CSV or Excel file</div>'
            '</div>', unsafe_allow_html=True
        )

    if st.session_state.data_loaded:
        df           = st.session_state.df
        summary      = st.session_state.summary
        col_stats    = st.session_state.col_stats
        missing_report = st.session_state.missing_report
        dt_names     = summary.get("datetime_col_names", [])

        st.markdown(
            f'<div style="background:rgba(99,102,241,0.15);border:1px solid rgba(99,102,241,0.3);'
            f'border-radius:8px;padding:7px 12px;font-size:12px;color:#a5b4fc;margin:12px 0 16px;">'
            f'📄 {st.session_state.filename}</div>', unsafe_allow_html=True
        )

        st.markdown('<div style="font-size:10px;text-transform:uppercase;letter-spacing:0.07em;'
                    'color:rgba(255,255,255,0.38);margin-bottom:8px;">Overview</div>',
                    unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        c1.metric("Rows",    summary["rows"])
        c2.metric("Columns", summary["columns"])
        c3, c4 = st.columns(2)
        c3.metric("Missing", f"{summary['missing_pct']}%")
        c4.metric("Numeric", summary["numeric_cols"])

        st.markdown('<div style="font-size:10px;text-transform:uppercase;letter-spacing:0.07em;'
                    'color:rgba(255,255,255,0.38);margin:16px 0 8px;">Columns</div>',
                    unsafe_allow_html=True)
        for col in df.columns:
            badge = col_badge(col, col_stats, dt_names, missing_report)
            st.markdown(
                f'<div style="display:flex;justify-content:space-between;align-items:center;'
                f'padding:5px 8px;border-radius:6px;margin-bottom:3px;'
                f'background:rgba(255,255,255,0.04);font-size:12px;">'
                f'<span style="color:rgba(255,255,255,0.72);overflow:hidden;text-overflow:ellipsis;'
                f'white-space:nowrap;max-width:68%;">{col}</span>'
                f'{badge}</div>', unsafe_allow_html=True
            )


# ══════════════════════════════════════════════════════════════════════════════
# LOAD NEW FILE
# ══════════════════════════════════════════════════════════════════════════════
if uploaded_file is not None:
    file_key = uploaded_file.name + str(uploaded_file.size)
    if st.session_state.get("file_key") != file_key:
        with st.spinner("Loading dataset..."):
            df = load_data(uploaded_file)
        if df is None:
            st.error("Could not load file. Please check the format.")
            st.stop()

        summary        = get_summary(df)
        missing_report = get_missing_report(df)
        col_stats      = get_column_stats(df)

        with st.spinner("🤖 Analysing dataset..."):
            raw_narrative = generate_narrative(summary, missing_report, col_stats)

        narrative_html = strip_markdown_headings(raw_narrative)

        st.session_state.df             = df
        st.session_state.summary        = summary
        st.session_state.missing_report = missing_report
        st.session_state.col_stats      = col_stats
        st.session_state.filename       = uploaded_file.name
        st.session_state.file_key       = file_key
        st.session_state.data_loaded    = True
        st.session_state.chat_history   = [{"role": "ai", "content": narrative_html}]
        st.session_state.llm_history    = [{"role": "assistant", "content": raw_narrative}]
        st.session_state.suggestion_used = None


# ══════════════════════════════════════════════════════════════════════════════
# MAIN AREA
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.data_loaded:
    df             = st.session_state.df
    summary        = st.session_state.summary
    missing_report = st.session_state.missing_report
    col_stats      = st.session_state.col_stats
    dt_names       = summary.get("datetime_col_names", [])

    tab_chat, tab_charts, tab_data = st.tabs(["💬  AI Chat", "📈  Charts", "🗂️  Data"])

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 1 — AI CHAT
    # ══════════════════════════════════════════════════════════════════════════
    with tab_chat:
        # White content area
        st.markdown('<div style="background:#ffffff;border-radius:12px;padding:20px 24px 8px;">', unsafe_allow_html=True)

        # Chat messages
        for msg in st.session_state.chat_history:
            render_bubble(msg["role"], msg["content"])

        # Inline missing values chart — shown once after first AI message
        if len(st.session_state.chat_history) == 1:
            missing_fig = plot_missing_inline(missing_report)
            if missing_fig:
                st.markdown(
                    '<div style="margin:4px 0 8px;max-width:520px;">'
                    '<div style="font-size:11px;color:#94a3b8;font-weight:600;'
                    'text-transform:uppercase;letter-spacing:0.07em;margin-bottom:6px;">Data quality</div>',
                    unsafe_allow_html=True
                )
                st.pyplot(missing_fig, use_container_width=False)
                st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # Suggestion chips — shown after first message only
        if len(st.session_state.chat_history) == 1:
            st.markdown('<div style="padding:10px 0 4px;background:#ffffff;border-radius:0 0 12px 12px;padding:8px 24px 12px;">', unsafe_allow_html=True)

            num_cols = [c for c, s in col_stats.items() if s.get("type") == "numeric"]
            txt_cols = [c for c, s in col_stats.items() if s.get("type") == "text"]
            suggestions = []
            if num_cols:
                suggestions.append(f"Show outliers in {num_cols[0]}")
            if txt_cols:
                suggestions.append(f"Break down by {txt_cols[0]}")
            if any(r["flag"] == "HIGH" for r in missing_report):
                suggestions.append("How should I handle missing values?")
            if len(num_cols) >= 2:
                suggestions.append(f"Correlate {num_cols[0]} and {num_cols[1]}")
            if dt_names:
                suggestions.append(f"Time range of {dt_names[0]}?")
            suggestions.append("What should I clean first?")

            btn_cols = st.columns(min(len(suggestions[:3]), 3))
            for i, sug in enumerate(suggestions[:3]):
                with btn_cols[i]:
                    if st.button(sug, key=f"sug_{i}", use_container_width=True):
                        st.session_state.suggestion_used = sug
                        st.rerun()

            if len(suggestions) > 3:
                btn_cols2 = st.columns(min(len(suggestions[3:6]), 3))
                for i, sug in enumerate(suggestions[3:6]):
                    with btn_cols2[i]:
                        if st.button(sug, key=f"sug2_{i}", use_container_width=True):
                            st.session_state.suggestion_used = sug
                            st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)

        # Process suggestion click
        if st.session_state.suggestion_used:
            question = st.session_state.suggestion_used
            st.session_state.suggestion_used = None
            st.session_state.chat_history.append({"role": "user",  "content": question})
            with st.spinner("Thinking..."):
                raw = answer_question(question, summary, col_stats, st.session_state.llm_history)
            html = strip_markdown_headings(raw)
            st.session_state.chat_history.append({"role": "ai", "content": html})
            st.session_state.llm_history += [
                {"role": "user",      "content": question},
                {"role": "assistant", "content": raw},
            ]
            st.rerun()

        # Chat input
        user_input = st.chat_input("Ask anything about your data...")
        if user_input:
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            with st.spinner("Thinking..."):
                raw = answer_question(user_input, summary, col_stats, st.session_state.llm_history)
            html = strip_markdown_headings(raw)
            st.session_state.chat_history.append({"role": "ai", "content": html})
            st.session_state.llm_history += [
                {"role": "user",      "content": user_input},
                {"role": "assistant", "content": raw},
            ]
            st.rerun()

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 2 — CHARTS
    # ══════════════════════════════════════════════════════════════════════════
    with tab_charts:
        st.markdown('<div style="background:#ffffff;border-radius:12px;padding:20px 24px;">', unsafe_allow_html=True)

        true_numeric = [
            c for c in df.select_dtypes(include="number").columns
            if c not in dt_names
        ]
        text_cols = list(df.select_dtypes(include="object").columns)

        # ── Numeric distributions ──────────────────────────────────────────
        if true_numeric:
            st.markdown("#### Numeric distributions")
            cols_per_row = 2
            for i in range(0, len(true_numeric), cols_per_row):
                row_cols = st.columns(cols_per_row)
                for j, col in enumerate(true_numeric[i:i + cols_per_row]):
                    with row_cols[j]:
                        fig = plot_histogram(df, col)
                        if fig:
                            with st.expander(f"**{col}**", expanded=False):
                                st.pyplot(fig, use_container_width=True)
                                with st.expander("📋 Copy code", expanded=False):
                                    st.code(f"""
df["{col}"].hist(bins=30)
plt.xlim(left=df["{col}"].min())
plt.title("Distribution of {col}")
plt.show()
""", language="python")

        # ── Categorical ────────────────────────────────────────────────────
        if text_cols:
            st.markdown("#### Categorical columns")
            cols_per_row = 2
            for i in range(0, len(text_cols), cols_per_row):
                row_cols = st.columns(cols_per_row)
                for j, col in enumerate(text_cols[i:i + cols_per_row]):
                    with row_cols[j]:
                        with st.expander(f"**{col}**", expanded=False):
                            st.pyplot(plot_bar(df, col), use_container_width=True)

        # ── Correlation heatmap ────────────────────────────────────────────
        if len(true_numeric) >= 2:
            st.markdown("#### Correlation heatmap")
            total_num = len(true_numeric)

            if total_num > HEATMAP_COL_LIMIT:
                st.info(
                    f"ℹ️ This dataset has {total_num} numeric columns. "
                    f"Showing the first {HEATMAP_COL_LIMIT} below — pick specific columns to compare."
                )
                selected = st.multiselect(
                    "Select columns for heatmap (2–15 recommended)",
                    options=true_numeric,
                    default=true_numeric[:HEATMAP_COL_LIMIT],
                    key="heatmap_cols"
                )
                if len(selected) >= 2:
                    fig, _, _ = plot_correlation(df[selected], selected_cols=selected)
                    st.pyplot(fig, use_container_width=True)
                else:
                    st.warning("Select at least 2 columns.")
            else:
                fig, _, _ = plot_correlation(df[true_numeric])
                st.pyplot(fig, use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 3 — DATA
    # ══════════════════════════════════════════════════════════════════════════
    with tab_data:
        st.markdown('<div style="background:#ffffff;border-radius:12px;padding:20px 24px;">', unsafe_allow_html=True)

        st.markdown(
            f'<p style="color:#64748b;font-size:13px;margin-bottom:12px;">'
            f'{summary["rows"]:,} rows × {summary["columns"]} columns — showing first 100 rows</p>',
            unsafe_allow_html=True
        )
        st.dataframe(df.head(100), use_container_width=True, hide_index=True)

        st.markdown("#### Column statistics")
        stats_rows = [{"column": k, **v} for k, v in col_stats.items()]
        st.dataframe(pd.DataFrame(stats_rows), use_container_width=True, hide_index=True)

        st.markdown("#### Missing values")
        missing_df    = pd.DataFrame(missing_report)
        missing_only  = missing_df[missing_df["missing"] > 0]
        if missing_only.empty:
            st.success("✅ No missing values found.")
        else:
            def colour_flag(val):
                if val == "HIGH": return "color:#ef4444;font-weight:600"
                if val == "LOW":  return "color:#f59e0b;font-weight:600"
                return "color:#22c55e;font-weight:600"
            st.dataframe(
                missing_only.style.map(colour_flag, subset=["flag"]),
                use_container_width=True, hide_index=True
            )

        st.markdown('</div>', unsafe_allow_html=True)

else:
    # Empty state
    st.markdown("""
    <div style="display:flex;flex-direction:column;align-items:center;
                justify-content:center;height:80vh;text-align:center;">
        <div style="font-size:48px;margin-bottom:16px;">📂</div>
        <div style="font-size:20px;font-weight:600;color:rgba(255,255,255,0.65);margin-bottom:8px;">
            Upload a dataset to get started
        </div>
        <div style="font-size:13px;color:rgba(255,255,255,0.3);">
            Supports .csv and .xlsx — use the panel on the left
        </div>
    </div>
    """, unsafe_allow_html=True)