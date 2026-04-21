import re
import streamlit as st
import pandas as pd
from analyser import load_data, get_summary, get_missing_report, get_column_stats
from visualiser import (plot_histogram, plot_bar, plot_correlation,
                        plot_missing_inline, HEATMAP_COL_LIMIT)
from narrator import generate_narrative, answer_question

st.set_page_config(page_title="Perceiv", page_icon="✦", layout="wide")

# ══════════════════════════════════════════════════════════════════════════════
# CSS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
  #MainMenu, footer, header { visibility: hidden; }
  .block-container { padding: 0 !important; max-width: 100% !important; }

  /* ── Root background ── */
  .stApp { background: #f5f4f0; }

  /* ── Hide default Streamlit sidebar toggle ── */
  [data-testid="stSidebarCollapseButton"] { display: none !important; }
  [data-testid="stSidebar"] {
      width: 52px !important;
      min-width: 52px !important;
      background: #ffffff !important;
      border-right: 1px solid #e5e3de !important;
  }
  [data-testid="stSidebar"] > div:first-child {
      width: 52px !important;
      padding: 0 !important;
  }

  /* ── Upload dropzone — home screen ── */
  [data-testid="stFileUploadDropzone"] {
      background: #ffffff !important;
      border: 2px dashed #d1d5db !important;
      border-radius: 16px !important;
      padding: 32px !important;
  }
  [data-testid="stFileUploadDropzone"]:hover {
      border-color: #6366f1 !important;
  }
  [data-testid="stFileUploaderDropzoneInstructions"] {
      color: #6b7280 !important;
  }

  /* ── Home screen ── */
  .home-wrap {
      display: flex; flex-direction: column;
      align-items: center; justify-content: center;
      min-height: 100vh; background: #f5f4f0;
  }
  .home-logo {
      font-size: 42px; font-weight: 700; color: #1a1a1a;
      letter-spacing: -1px; margin-bottom: 6px;
  }
  .home-logo span { color: #6366f1; }
  .home-sub {
      font-size: 15px; color: #9ca3af; margin-bottom: 40px;
  }
  .home-upload-box {
      background: #ffffff; border: 1.5px dashed #d1d5db;
      border-radius: 20px; padding: 40px 60px;
      text-align: center; cursor: pointer;
      transition: border-color 0.2s;
      max-width: 480px; width: 100%;
  }
  .home-upload-box:hover { border-color: #6366f1; }
  .home-upload-icon { font-size: 36px; margin-bottom: 12px; }
  .home-upload-title {
      font-size: 16px; font-weight: 600; color: #1a1a1a; margin-bottom: 6px;
  }
  .home-upload-hint { font-size: 13px; color: #9ca3af; }

  /* ── Main app layout (after upload) ── */
  .app-shell {
      display: flex; height: 100vh; overflow: hidden;
      background: #f5f4f0;
  }

  /* Left icon rail */
  .icon-rail {
      width: 52px; flex-shrink: 0;
      background: #ffffff; border-right: 1px solid #e5e3de;
      display: flex; flex-direction: column;
      align-items: center; padding: 14px 0; gap: 4px;
      z-index: 10;
  }
  .rail-logo {
      font-size: 18px; font-weight: 800; color: #6366f1;
      margin-bottom: 16px; letter-spacing: -1px;
  }
  .rail-btn {
      width: 36px; height: 36px; border-radius: 10px;
      display: flex; align-items: center; justify-content: center;
      cursor: pointer; transition: background 0.15s;
      font-size: 16px; color: #9ca3af; border: none;
      background: transparent; position: relative;
  }
  .rail-btn:hover { background: #f3f4f6; color: #374151; }
  .rail-btn.active { background: #eef2ff; color: #6366f1; }
  .rail-btn .tooltip {
      display: none; position: absolute; left: 48px;
      background: #1f2937; color: #fff; font-size: 11px;
      padding: 4px 8px; border-radius: 6px; white-space: nowrap; z-index: 100;
  }
  .rail-btn:hover .tooltip { display: block; }

  /* Center chat column */
  .chat-col {
      flex: 1; display: flex; flex-direction: column;
      min-width: 0; overflow: hidden;
  }
  .chat-messages {
      flex: 1; overflow-y: auto; padding: 32px 10% 16px;
      display: flex; flex-direction: column; gap: 20px;
  }

  /* Bubbles */
  .bubble-ai {
      background: #ffffff; border: 1px solid #e5e3de;
      border-radius: 18px 18px 18px 4px;
      padding: 16px 20px; max-width: 720px;
      font-size: 14px; line-height: 1.7; color: #1a1a1a;
      box-shadow: 0 1px 3px rgba(0,0,0,0.04);
  }
  .bubble-user {
      background: #eef2ff; border: 1px solid #c7d2fe;
      border-radius: 18px 18px 4px 18px;
      padding: 12px 18px; max-width: 560px;
      align-self: flex-end;
      font-size: 14px; line-height: 1.65; color: #3730a3;
  }
  .msg-label {
      font-size: 10px; font-weight: 700; letter-spacing: 0.09em;
      text-transform: uppercase; margin-bottom: 6px;
  }
  .label-ai   { color: #6366f1; }
  .label-user { color: #9ca3af; text-align: right; }

  /* Bubble markdown formatting */
  .bubble-ai strong { color: #111827; font-weight: 600; }
  .bubble-ai ul { margin: 4px 0; padding-left: 0; list-style: none; }
  .bubble-ai li {
      padding: 3px 0 3px 16px; position: relative; color: #374151;
  }
  .bubble-ai li::before {
      content: "–"; position: absolute; left: 0; color: #6366f1;
  }
  .bubble-ai p { margin: 4px 0; }
  .bubble-ai h3, .bubble-ai h4 {
      font-size: 13px; font-weight: 700; color: #111827;
      margin: 12px 0 4px; text-transform: uppercase;
      letter-spacing: 0.05em;
  }

  /* Suggestion chips */
  .chips-wrap {
      display: flex; flex-wrap: wrap; gap: 8px;
      padding: 4px 10% 0;
  }

  /* Chat input row */
  .input-row {
      padding: 12px 10% 20px;
      background: #f5f4f0;
  }
  /* Chat input — force light background on all inner elements */
  [data-testid="stChatInput"],
  [data-testid="stChatInput"] > div,
  [data-testid="stChatInput"] > div > div,
  [data-testid="stChatInput"] > div > div > div {
      background: #ffffff !important;
      border-radius: 16px !important;
  }
  [data-testid="stChatInput"] > div {
      border: 1.5px solid #e5e3de !important;
      box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important;
  }
  [data-testid="stChatInput"] textarea {
      background: #ffffff !important;
      color: #1a1a1a !important;
      font-size: 14px !important;
      caret-color: #6366f1 !important;
  }
  [data-testid="stChatInput"] textarea::placeholder {
      color: #9ca3af !important;
  }

  /* Right panel */
  .right-panel {
      width: 300px; flex-shrink: 0;
      background: #ffffff; border-left: 1px solid #e5e3de;
      display: flex; flex-direction: column;
      overflow: hidden; transition: width 0.2s ease;
  }
  .right-panel.collapsed { width: 0 !important; border: none !important; }
  .panel-header {
      display: flex; align-items: center; justify-content: space-between;
      padding: 14px 16px 10px;
      border-bottom: 1px solid #f0ede8;
      font-size: 11px; font-weight: 700; color: #9ca3af;
      text-transform: uppercase; letter-spacing: 0.08em;
  }
  .panel-close {
      cursor: pointer; color: #9ca3af; font-size: 14px;
      background: none; border: none; padding: 2px 4px;
      border-radius: 4px;
  }
  .panel-close:hover { background: #f3f4f6; color: #374151; }
  .panel-body { flex: 1; overflow-y: auto; padding: 14px 14px 20px; }

  /* Stats tiles */
  .stat-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 16px; }
  .stat-tile {
      background: #f9f8f6; border: 1px solid #e5e3de;
      border-radius: 10px; padding: 10px 12px;
  }
  .stat-val { font-size: 20px; font-weight: 700; color: #111827; }
  .stat-val.warn { color: #d97706; }
  .stat-val.ok   { color: #059669; }
  .stat-key { font-size: 10px; color: #9ca3af; margin-top: 1px; text-transform: uppercase; letter-spacing: 0.05em; }

  /* Column rows in panel */
  .col-section-label {
      font-size: 10px; font-weight: 700; color: #9ca3af;
      text-transform: uppercase; letter-spacing: 0.08em;
      margin: 12px 0 6px;
  }
  .col-row {
      display: flex; justify-content: space-between; align-items: center;
      padding: 5px 8px; border-radius: 7px; margin-bottom: 3px;
      font-size: 12px; color: #374151;
      background: #f9f8f6;
  }
  .col-name { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 68%; }
  .col-chip {
      font-size: 9px; font-weight: 700; padding: 2px 6px;
      border-radius: 8px; text-transform: uppercase; letter-spacing: 0.04em;
      flex-shrink: 0;
  }
  .chip-num  { background: #eef2ff; color: #4f46e5; }
  .chip-text { background: #f0fdf4; color: #15803d; }
  .chip-dt   { background: #fffbeb; color: #b45309; }
  .chip-miss { background: #fff7ed; color: #c2410c; }

  /* Charts in panel */
  .panel-chart-wrap { margin-bottom: 12px; }
  .panel-chart-label {
      font-size: 11px; font-weight: 600; color: #6b7280;
      margin-bottom: 6px;
  }

  /* Suggestion buttons */
  div[data-testid="stHorizontalBlock"] > div > div > button {
      background: #ffffff !important;
      border: 1px solid #d1d5db !important;
      border-radius: 20px !important;
      color: #4f46e5 !important;
      font-size: 12px !important;
      padding: 5px 14px !important;
      font-weight: 500 !important;
  }
  div[data-testid="stHorizontalBlock"] > div > div > button:hover {
      background: #eef2ff !important;
      border-color: #6366f1 !important;
  }

  /* Expanders in charts panel */
  [data-testid="stExpander"] details {
      background: #f9f8f6 !important;
      border: 1px solid #e5e3de !important;
      border-radius: 8px !important;
      margin-bottom: 8px !important;
  }
  [data-testid="stExpander"] details summary {
      color: #374151 !important; font-size: 13px !important;
  }

  /* Multiselect */
  [data-testid="stMultiSelect"] { background: transparent; }

  /* Scrollbar */
  ::-webkit-scrollbar { width: 4px; height: 4px; }
  ::-webkit-scrollbar-track { background: transparent; }
  ::-webkit-scrollbar-thumb { background: #d1d5db; border-radius: 4px; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def md_to_html(text: str) -> str:
    """Convert LLM markdown to safe HTML for bubble rendering."""
    # Section headers with emoji (### or **Header**)
    text = re.sub(r'^#{1,4}\s*(.+)$', r'<h4>\1</h4>', text, flags=re.MULTILINE)
    # Bold
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    # Italic
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    # Bullet lines
    lines = text.split('\n')
    out, in_list = [], False
    for line in lines:
        s = line.strip()
        if s.startswith('- ') or s.startswith('• '):
            if not in_list:
                out.append('<ul>')
                in_list = True
            out.append(f'<li>{s[2:]}</li>')
        else:
            if in_list:
                out.append('</ul>')
                in_list = False
            if s:
                # If it's already an h4 tag, don't wrap in <p>
                if s.startswith('<h4>'):
                    out.append(s)
                else:
                    out.append(f'<p>{s}</p>')
    if in_list:
        out.append('</ul>')
    return '\n'.join(out)


def render_bubble(role, content):
    if role == "ai":
        st.markdown(f"""
        <div style="display:flex;flex-direction:column;align-items:flex-start;">
          <div class="msg-label label-ai">PERCEIV</div>
          <div class="bubble-ai">{content}</div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="display:flex;flex-direction:column;align-items:flex-end;">
          <div class="msg-label label-user">YOU</div>
          <div class="bubble-user">{content}</div>
        </div>""", unsafe_allow_html=True)


def col_chip_html(col_name, col_stats, dt_names, missing_report):
    for r in missing_report:
        if r["column"] == col_name and r["flag"] == "HIGH":
            return f'<span class="col-chip chip-miss">{r["pct"]}% miss</span>'
    if col_name in dt_names:
        return '<span class="col-chip chip-dt">date</span>'
    t = col_stats.get(col_name, {}).get("type", "other")
    if t == "numeric": return '<span class="col-chip chip-num">num</span>'
    if t == "text":    return '<span class="col-chip chip-text">text</span>'
    return ''


# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════
for k, v in [
    ("chat_history",       []),
    ("llm_history",        []),
    ("data_loaded",        False),
    ("suggestion_used",    None),
    ("panel_view",         "stats"),
    ("panel_open",         False),
    ("heatmap_cols",       None),
    ("show_missing_chart", True),
]:
    if k not in st.session_state:
        st.session_state[k] = v


# ══════════════════════════════════════════════════════════════════════════════
# HOME SCREEN (before upload)
# ══════════════════════════════════════════════════════════════════════════════
if not st.session_state.data_loaded:
    # Hide sidebar on home screen
    st.markdown("""
    <style>
      [data-testid="stSidebar"] { display: none !important; }
      .block-container { padding: 0 !important; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="display:flex;flex-direction:column;align-items:center;
                padding-top:18vh;text-align:center;">
      <div style="font-size:44px;font-weight:700;color:#1a1a1a;
                  letter-spacing:-1.5px;margin-bottom:8px;">✦ Perceiv</div>
      <div style="font-size:15px;color:#9ca3af;margin-bottom:48px;">
        Upload a dataset — get instant AI analysis
      </div>
    </div>
    """, unsafe_allow_html=True)

    _, center, _ = st.columns([1, 1.4, 1])
    with center:
        uploaded = st.file_uploader(
            "Drop a CSV or Excel file here, or click to browse",
            type=["csv", "xlsx"],
            label_visibility="visible"
        )

    if uploaded is not None:
        with st.spinner("Loading…"):
            df = load_data(uploaded)
        if df is None:
            st.error("Could not load file.")
            st.stop()

        summary        = get_summary(df)
        missing_report = get_missing_report(df)
        col_stats      = get_column_stats(df)

        with st.spinner("Analysing…"):
            raw = generate_narrative(summary, missing_report, col_stats)

        st.session_state.df             = df
        st.session_state.summary        = summary
        st.session_state.missing_report = missing_report
        st.session_state.col_stats      = col_stats
        st.session_state.filename       = uploaded.name
        st.session_state.file_key       = uploaded.name + str(uploaded.size)
        st.session_state.data_loaded    = True
        st.session_state.chat_history   = [{"role": "ai", "content": md_to_html(raw)}]
        st.session_state.llm_history    = [{"role": "assistant", "content": raw}]
        st.session_state.panel_open     = True
        st.session_state.panel_view     = "stats"
        st.rerun()

    st.stop()


# ══════════════════════════════════════════════════════════════════════════════
# MAIN APP SHELL (after upload)
# ══════════════════════════════════════════════════════════════════════════════
df             = st.session_state.df
summary        = st.session_state.summary
missing_report = st.session_state.missing_report
col_stats      = st.session_state.col_stats
dt_names       = summary.get("datetime_col_names", [])

# ── Hidden file uploader (triggered by rail button) ────────────────────────
with st.sidebar:
    new_file = st.file_uploader("new", type=["csv","xlsx"], label_visibility="collapsed", key="rail_upload")
    if new_file is not None:
        fkey = new_file.name + str(new_file.size)
        if fkey != st.session_state.get("file_key"):
            with st.spinner("Loading…"):
                df2 = load_data(new_file)
            if df2 is not None:
                s2  = get_summary(df2)
                mr2 = get_missing_report(df2)
                cs2 = get_column_stats(df2)
                with st.spinner("Analysing…"):
                    raw2 = generate_narrative(s2, mr2, cs2)
                st.session_state.df             = df2
                st.session_state.summary        = s2
                st.session_state.missing_report = mr2
                st.session_state.col_stats      = cs2
                st.session_state.filename       = new_file.name
                st.session_state.file_key       = fkey
                st.session_state.chat_history   = [{"role": "ai", "content": md_to_html(raw2)}]
                st.session_state.llm_history    = [{"role": "assistant", "content": raw2}]
                st.session_state.panel_open     = True
                st.session_state.panel_view     = "stats"
                st.session_state.suggestion_used = None
                st.rerun()

# ── Three-column layout: rail | chat | panel ───────────────────────────────
# Always render all 3 columns — hide panel content via conditional, never width=0
# Wider chat when panel closed, narrower when open
_chat_w = 0.58 if st.session_state.panel_open else 0.92
rail_col, chat_col, panel_col = st.columns([0.04, _chat_w, 0.38 if st.session_state.panel_open else 0.04])

# ════════════════════════════════════════════════════
# LEFT ICON RAIL
# ════════════════════════════════════════════════════
with rail_col:
    st.markdown(
        '<div style="display:flex;flex-direction:column;align-items:center;'
        'padding:12px 0 0;gap:8px;">'
        '<div style="font-size:17px;font-weight:800;color:#6366f1;margin-bottom:8px;">✦</div>'
        '</div>',
        unsafe_allow_html=True
    )


# ════════════════════════════════════════════════════
# CENTER CHAT
# ════════════════════════════════════════════════════
with chat_col:
    # File name header
    st.markdown(
        f'<div style="padding:14px 0 0 16px;font-size:12px;color:#9ca3af;font-weight:500;">'
        f'✦ Perceiv &nbsp;·&nbsp; <span style="color:#6366f1;">{st.session_state.filename}</span></div>',
        unsafe_allow_html=True
    )

    # Messages — rendered in a centered max-width container via CSS
    for msg in st.session_state.chat_history:
        render_bubble(msg["role"], msg["content"])

    # Inline missing chart — always show when there are missing values (not just msg==1)
    if st.session_state.get("show_missing_chart", True):
        missing_fig = plot_missing_inline(missing_report)
        if missing_fig:
            _, mc, _ = st.columns([0.05, 0.85, 0.1])
            with mc:
                st.pyplot(missing_fig, use_container_width=True)
            st.session_state.show_missing_chart = False

    # Suggestion chips — only on first message
    if len(st.session_state.chat_history) == 1:
        st.markdown('<div style="height:8px;"></div>', unsafe_allow_html=True)
        num_cols = [c for c, s in col_stats.items() if s.get("type") == "numeric"]
        txt_cols = [c for c, s in col_stats.items() if s.get("type") == "text"]
        suggestions = []
        if num_cols:                    suggestions.append(f"Outliers in {num_cols[0]}?")
        if txt_cols:                    suggestions.append(f"Break down by {txt_cols[0]}")
        if any(r["flag"]=="HIGH" for r in missing_report):
            suggestions.append("Fix missing values?")
        if len(num_cols) >= 2:          suggestions.append(f"Correlate {num_cols[0]} & {num_cols[1]}")
        if dt_names:                    suggestions.append(f"Time range of {dt_names[0]}?")
        suggestions.append("What to clean first?")

        _, sc, _ = st.columns([0.05, 0.9, 0.05])
        with sc:
            btns = st.columns(min(3, len(suggestions)))
            for i, sug in enumerate(suggestions[:3]):
                with btns[i]:
                    if st.button(sug, key=f"sug_{i}", use_container_width=True):
                        st.session_state.suggestion_used = sug
                        st.rerun()
            if len(suggestions) > 3:
                btns2 = st.columns(min(3, len(suggestions)-3))
                for i, sug in enumerate(suggestions[3:6]):
                    with btns2[i]:
                        if st.button(sug, key=f"sug2_{i}", use_container_width=True):
                            st.session_state.suggestion_used = sug
                            st.rerun()

    # Process suggestion
    if st.session_state.suggestion_used:
        q = st.session_state.suggestion_used
        st.session_state.suggestion_used = None
        st.session_state.chat_history.append({"role": "user", "content": q})
        with st.spinner("Thinking…"):
            raw = answer_question(q, summary, col_stats, st.session_state.llm_history)
        html = md_to_html(raw)
        st.session_state.chat_history.append({"role": "ai", "content": html})
        st.session_state.llm_history += [
            {"role": "user", "content": q},
            {"role": "assistant", "content": raw},
        ]
        st.rerun()

    # Chat input
    st.markdown('<div style="padding-top:12px;"></div>', unsafe_allow_html=True)
    user_input = st.chat_input("Ask anything about your data…")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.spinner("Thinking…"):
            raw = answer_question(user_input, summary, col_stats, st.session_state.llm_history)
        html = md_to_html(raw)
        st.session_state.chat_history.append({"role": "ai", "content": html})
        st.session_state.llm_history += [
            {"role": "user", "content": user_input},
            {"role": "assistant", "content": raw},
        ]
        st.rerun()


# ════════════════════════════════════════════════════
# RIGHT PANEL
# ════════════════════════════════════════════════════
with panel_col:
    if st.session_state.panel_open:
        view = st.session_state.panel_view

        # Panel header with view toggle buttons
        st.markdown(
            '<div style="padding:10px 8px 8px;border-bottom:1px solid #f0ede8;">'
            '</div>',
            unsafe_allow_html=True
        )
        ph1, ph2, ph3, ph4 = st.columns([1,1,1,0.5])
        with ph1:
            if st.button("📊 Stats",   key="pv_stats",  use_container_width=True,
                         type="primary" if view=="stats" else "secondary"):
                st.session_state.panel_view = "stats"; st.rerun()
        with ph2:
            if st.button("📈 Charts",  key="pv_charts", use_container_width=True,
                         type="primary" if view=="charts" else "secondary"):
                st.session_state.panel_view = "charts"; st.rerun()
        with ph3:
            if st.button("🗂️ Data",   key="pv_data",   use_container_width=True,
                         type="primary" if view=="data" else "secondary"):
                st.session_state.panel_view = "data"; st.rerun()
        with ph4:
            if st.button("✕", key="close_panel", use_container_width=True):
                st.session_state.panel_open = False; st.rerun()

        # ── STATS VIEW ────────────────────────────────
        if view == "stats":
            missing_pct = summary["missing_pct"]
            miss_color  = "warn" if missing_pct > 5 else "ok"

            st.markdown(f"""
            <div class="stat-grid">
              <div class="stat-tile">
                <div class="stat-val">{summary['rows']:,}</div>
                <div class="stat-key">Rows</div>
              </div>
              <div class="stat-tile">
                <div class="stat-val">{summary['columns']}</div>
                <div class="stat-key">Columns</div>
              </div>
              <div class="stat-tile">
                <div class="stat-val {miss_color}">{missing_pct}%</div>
                <div class="stat-key">Missing</div>
              </div>
              <div class="stat-tile">
                <div class="stat-val">{summary['numeric_cols']}</div>
                <div class="stat-key">Numeric</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown('<div class="col-section-label">Columns</div>', unsafe_allow_html=True)
            for col in df.columns:
                chip = col_chip_html(col, col_stats, dt_names, missing_report)
                st.markdown(
                    f'<div class="col-row">'
                    f'<span class="col-name">{col}</span>'
                    f'{chip}</div>',
                    unsafe_allow_html=True
                )

        # ── CHARTS VIEW ───────────────────────────────
        elif view == "charts":
            true_num = [c for c in df.select_dtypes(include="number").columns
                        if c not in dt_names]
            txt_cols_list = list(df.select_dtypes(include="object").columns)

            chart_type = st.selectbox(
                "Chart type",
                ["Distributions (numeric)", "Categorical", "Correlation heatmap"],
                key="chart_type_sel",
                label_visibility="collapsed"
            )

            if chart_type == "Distributions (numeric)":
                if not true_num:
                    st.caption("No numeric columns found.")
                else:
                    col_sel = st.selectbox("Column", true_num, key="hist_col_sel",
                                           label_visibility="collapsed")
                    fig = plot_histogram(df, col_sel)
                    if fig:
                        st.pyplot(fig, use_container_width=True)

            elif chart_type == "Categorical":
                if not txt_cols_list:
                    st.caption("No categorical columns found.")
                else:
                    col_sel = st.selectbox("Column", txt_cols_list, key="bar_col_sel",
                                           label_visibility="collapsed")
                    st.pyplot(plot_bar(df, col_sel), use_container_width=True)

            elif chart_type == "Correlation heatmap":
                if len(true_num) < 2:
                    st.caption("Need at least 2 numeric columns.")
                else:
                    total_num = len(true_num)
                    if total_num > HEATMAP_COL_LIMIT:
                        st.caption(f"{total_num} numeric cols — select up to 15:")
                        selected = st.multiselect(
                            "Columns", options=true_num,
                            default=true_num[:HEATMAP_COL_LIMIT],
                            key="heatmap_sel", label_visibility="collapsed"
                        )
                        if len(selected) >= 2:
                            fig, _, _ = plot_correlation(df[selected], selected_cols=selected)
                            st.pyplot(fig, use_container_width=True)
                        else:
                            st.caption("Select at least 2 columns.")
                    else:
                        fig, _, _ = plot_correlation(df[true_num])
                        st.pyplot(fig, use_container_width=True)

        # ── DATA VIEW ─────────────────────────────────
        elif view == "data":
            st.caption(f"{summary['rows']:,} rows × {summary['columns']} cols")
            st.dataframe(df.head(200), use_container_width=True, hide_index=True, height=400)

            st.markdown("**Missing values**")
            mdf = pd.DataFrame(missing_report)
            monly = mdf[mdf["missing"] > 0]
            if monly.empty:
                st.success("All clean ✓")
            else:
                def cflag(v):
                    if v=="HIGH": return "color:#ef4444;font-weight:600"
                    if v=="LOW":  return "color:#f59e0b;font-weight:600"
                    return ""
                st.dataframe(monly.style.map(cflag, subset=["flag"]),
                             use_container_width=True, hide_index=True)