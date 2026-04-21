"""
Template registry for Perceiv.
Each template defines:
- questions: conversational Q&A to map user columns
- required: which mapped fields are needed to render
- render: function that draws the dashboard given df + column_map
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker


# ── Shared chart style ─────────────────────────────────────────────────────
_BG    = "#ffffff"
_PANEL = "#f8f9fa"
_FG    = "#1e293b"
_GRID  = "#e2e8f0"
_C1    = "#6366f1"
_C2    = "#0ea5e9"
_C3    = "#10b981"
_C4    = "#f59e0b"

def _style(fig, ax):
    fig.patch.set_facecolor(_BG)
    ax.set_facecolor(_PANEL)
    ax.tick_params(colors=_FG, labelsize=9)
    ax.xaxis.label.set_color(_FG)
    ax.yaxis.label.set_color(_FG)
    ax.title.set_color(_FG)
    for spine in ax.spines.values():
        spine.set_edgecolor(_GRID)
    ax.set_axisbelow(True)
    ax.grid(axis="y", color=_GRID, linewidth=0.5, linestyle="--", alpha=0.7)


def _fmt_num(n):
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.1f}K"
    return f"{n:,.0f}"


# ── KPI tile HTML ──────────────────────────────────────────────────────────
def kpi_tile(label, value, delta=None, color="#6366f1"):
    delta_html = ""
    if delta is not None:
        arrow = "↑" if delta >= 0 else "↓"
        col   = "#10b981" if delta >= 0 else "#ef4444"
        delta_html = f'<div style="font-size:11px;color:{col};margin-top:2px;">{arrow} {abs(delta):.1f}%</div>'
    return f"""
<div style="background:#ffffff;border:1px solid #e5e3de;border-radius:10px;
            padding:12px 14px;flex:1;min-width:0;">
  <div style="font-size:10px;color:#9ca3af;text-transform:uppercase;
              letter-spacing:0.06em;margin-bottom:4px;">{label}</div>
  <div style="font-size:22px;font-weight:700;color:{color};">{value}</div>
  {delta_html}
</div>"""


# ══════════════════════════════════════════════════════════════════════════════
# SALES TEMPLATE
# ══════════════════════════════════════════════════════════════════════════════

SALES_QUESTIONS = [
    {
        "key":     "revenue_col",
        "message": "Which column contains your **revenue or sales amount**?",
        "filter":  "numeric",
    },
    {
        "key":     "date_col",
        "message": "Which column contains the **date or time** of each transaction?",
        "filter":  "any",
    },
    {
        "key":     "category_col",
        "message": "Which column contains a **category, region, or product**? (type 'skip' to skip)",
        "filter":  "any",
        "optional": True,
    },
]


def render_sales_dashboard(df, col_map):
    """Render the Sales dashboard into the current Streamlit context."""
    rev_col  = col_map.get("revenue_col")
    date_col = col_map.get("date_col")
    cat_col  = col_map.get("category_col")

    if not rev_col or rev_col not in df.columns:
        st.warning("Revenue column not found in dataset.")
        return

    rev = pd.to_numeric(df[rev_col], errors="coerce").dropna()

    # ── KPI row ────────────────────────────────────────────────────────────
    total_rev  = rev.sum()
    avg_order  = rev.mean()
    n_orders   = len(rev)
    median_rev = rev.median()

    st.markdown(
        '<div style="display:flex;gap:8px;margin-bottom:14px;">'
        + kpi_tile("Total revenue",  _fmt_num(total_rev),  color=_C1)
        + kpi_tile("Orders",         _fmt_num(n_orders),   color=_C2)
        + kpi_tile("Avg order",      _fmt_num(avg_order),  color=_C3)
        + kpi_tile("Median order",   _fmt_num(median_rev), color=_C4)
        + '</div>',
        unsafe_allow_html=True
    )

    # ── Revenue over time ──────────────────────────────────────────────────
    if date_col and date_col in df.columns:
        try:
            tmp = df[[date_col, rev_col]].copy()
            tmp[date_col] = pd.to_datetime(tmp[date_col], errors="coerce")
            tmp[rev_col]  = pd.to_numeric(tmp[rev_col], errors="coerce")
            tmp = tmp.dropna()

            # Pick sensible time frequency
            date_range = (tmp[date_col].max() - tmp[date_col].min()).days
            freq = "ME" if date_range > 90 else ("W" if date_range > 14 else "D")
            ts = tmp.set_index(date_col)[rev_col].resample(freq).sum().reset_index()

            if len(ts) >= 2:
                fig, ax = plt.subplots(figsize=(5.5, 2.8))
                ax.bar(range(len(ts)), ts[rev_col], color=_C1, alpha=0.8, edgecolor=_BG)
                step = max(1, len(ts) // 5)
                ax.set_xticks(range(0, len(ts), step))
                ax.set_xticklabels(
                    [str(d)[:10] for d in ts[date_col].iloc[::step]],
                    rotation=30, ha="right", fontsize=8
                )
                ax.yaxis.set_major_formatter(
                    mticker.FuncFormatter(lambda x, _: _fmt_num(x))
                )
                ax.set_title("Revenue over time", fontsize=11, fontweight="600", pad=8)
                _style(fig, ax)
                fig.tight_layout(pad=1.2)
                st.pyplot(fig, use_container_width=True)
                plt.close(fig)
        except Exception:
            st.caption("Could not plot revenue over time.")

    # ── Breakdown by category ──────────────────────────────────────────────
    if cat_col and cat_col in df.columns:
        try:
            tmp2 = df[[cat_col, rev_col]].copy()
            tmp2[rev_col] = pd.to_numeric(tmp2[rev_col], errors="coerce")
            grp = (tmp2.groupby(cat_col)[rev_col]
                      .sum()
                      .sort_values(ascending=False)
                      .head(10))

            fig2, ax2 = plt.subplots(figsize=(5.5, max(2.5, len(grp) * 0.35)))
            colors = [_C1, _C2, _C3, _C4] * 3
            ax2.barh(range(len(grp)), grp.values,
                     color=colors[:len(grp)], alpha=0.85, edgecolor=_BG)
            ax2.set_yticks(range(len(grp)))
            ax2.set_yticklabels(
                [str(v)[:18] + "…" if len(str(v)) > 18 else str(v)
                 for v in grp.index],
                fontsize=9
            )
            ax2.xaxis.set_major_formatter(
                mticker.FuncFormatter(lambda x, _: _fmt_num(x))
            )
            ax2.set_title(f"Revenue by {cat_col}", fontsize=11,
                          fontweight="600", pad=8)
            ax2.invert_yaxis()
            _style(ax2.figure, ax2)
            ax2.grid(axis="x", color=_GRID, linewidth=0.5,
                     linestyle="--", alpha=0.7)
            ax2.grid(axis="y", visible=False)
            fig2.tight_layout(pad=1.2)
            st.pyplot(fig2, use_container_width=True)
            plt.close(fig2)
        except Exception:
            st.caption("Could not plot category breakdown.")

    # ── Top rows table ─────────────────────────────────────────────────────
    st.markdown(
        '<div style="font-size:10px;font-weight:700;color:#9ca3af;'
        'text-transform:uppercase;letter-spacing:0.06em;margin:10px 0 6px;">Top 10 rows by revenue</div>',
        unsafe_allow_html=True
    )
    top_cols = [c for c in [date_col, cat_col, rev_col] if c and c in df.columns]
    top_df = (df[top_cols].copy()
              .assign(**{rev_col: pd.to_numeric(df[rev_col], errors="coerce")})
              .dropna(subset=[rev_col])
              .sort_values(rev_col, ascending=False)
              .head(10)
              .reset_index(drop=True))
    st.dataframe(top_df, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# TEMPLATE REGISTRY — add future templates here
# ══════════════════════════════════════════════════════════════════════════════

TEMPLATES = {
    "sales": {
        "name":      "Sales Dashboard",
        "icon":      "💰",
        "desc":      "Revenue KPIs, trends over time, and category breakdown",
        "questions": SALES_QUESTIONS,
        "render":    render_sales_dashboard,
    },
    # Future:
    # "hr":     { "name": "HR Dashboard",     "icon": "👥", ... },
    # "survey": { "name": "Survey Dashboard", "icon": "📋", ... },
}