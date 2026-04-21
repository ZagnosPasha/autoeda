import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# ── Shared light theme ─────────────────────────────────────────────────────────
_BG      = "#ffffff"
_PANEL   = "#f8f9fa"
_FG      = "#1e293b"
_GRID    = "#e2e8f0"
_ACCENT  = "#6366f1"
_ACCENT2 = "#0ea5e9"

def _apply_light(fig, ax):
    fig.patch.set_facecolor(_BG)
    ax.set_facecolor(_PANEL)
    ax.tick_params(colors=_FG, labelsize=10)
    ax.xaxis.label.set_color(_FG)
    ax.yaxis.label.set_color(_FG)
    ax.title.set_color(_FG)
    for spine in ax.spines.values():
        spine.set_edgecolor(_GRID)
    ax.grid(axis="y", color=_GRID, linewidth=0.6, linestyle="--", alpha=0.8)
    ax.set_axisbelow(True)


def plot_histogram(df, col):
    if df[col].dtype == "object":
        return None
    fig, ax = plt.subplots(figsize=(6, 3.5))
    ax.hist(df[col].dropna(), bins=30, color=_ACCENT,
            edgecolor=_BG, linewidth=0.4, alpha=0.85)
    ax.set_xlim(left=df[col].min())
    ax.set_title(f"Distribution — {col}", fontsize=12, pad=10, fontweight="600")
    ax.set_xlabel(col, fontsize=10)
    ax.set_ylabel("Count", fontsize=10)
    _apply_light(fig, ax)
    ax.grid(axis="x", visible=False)
    fig.tight_layout(pad=1.2)
    return fig


def plot_bar(df, col):
    total_unique = df[col].nunique()
    counts = df[col].value_counts().head(10 if total_unique > 20 else total_unique)

    fig, ax = plt.subplots(figsize=(6, 3.5))
    ax.bar(range(len(counts)), counts.values, color=_ACCENT2,
           edgecolor=_BG, linewidth=0.4, alpha=0.85)
    ax.set_xticks(range(len(counts)))
    ax.set_xticklabels(
        [str(v)[:18] + "…" if len(str(v)) > 18 else str(v) for v in counts.index],
        rotation=40, ha="right", fontsize=9
    )
    title = f"Value counts — {col}"
    if total_unique > 20:
        title += f"  (top 10 of {total_unique})"
    ax.set_title(title, fontsize=12, pad=10, fontweight="600")
    ax.set_ylabel("Count", fontsize=10)
    _apply_light(fig, ax)
    fig.tight_layout(pad=1.2)
    return fig


HEATMAP_COL_LIMIT = 15

def plot_correlation(df, selected_cols=None):
    """Returns (fig, was_capped: bool, total_numeric: int)."""
    num_df = df.select_dtypes(include="number")
    total  = num_df.shape[1]

    if selected_cols:
        num_df = num_df[selected_cols]
    elif total > HEATMAP_COL_LIMIT:
        num_df = num_df.iloc[:, :HEATMAP_COL_LIMIT]

    was_capped = (selected_cols is None) and (total > HEATMAP_COL_LIMIT)
    n = num_df.shape[1]

    corr = num_df.corr()
    size = max(5, min(n * 0.75, 11))
    fig, ax = plt.subplots(figsize=(size, size * 0.8))

    sns.heatmap(
        corr, annot=(n <= 12), fmt=".2f", cmap="RdYlBu_r",
        ax=ax, linewidths=0.4, linecolor=_GRID,
        annot_kws={"size": 8} if n <= 12 else {},
        cbar_kws={"shrink": 0.75}
    )
    ax.set_title("Correlation heatmap", fontsize=12, pad=12,
                 color=_FG, fontweight="600")
    ax.tick_params(colors=_FG, labelsize=9)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")
    fig.patch.set_facecolor(_BG)
    fig.tight_layout(pad=1.5)
    return fig, was_capped, total


def plot_missing_inline(missing_report):
    """Compact horizontal bar — only columns with missing values."""
    missing_only = sorted(
        [r for r in missing_report if r["missing"] > 0],
        key=lambda r: r["pct"], reverse=True
    )
    if not missing_only:
        return None

    cols   = [r["column"] for r in missing_only]
    pcts   = [r["pct"]    for r in missing_only]
    colors = ["#ef4444" if p >= 10 else "#f59e0b" for p in pcts]

    n = len(cols)
    h = max(2.0, n * 0.38)
    fig, ax = plt.subplots(figsize=(6, h))

    bars = ax.barh(range(n), pcts, color=colors,
                   edgecolor=_BG, linewidth=0.3, alpha=0.9)
    ax.set_yticks(range(n))
    ax.set_yticklabels(
        [c[:28] + "…" if len(c) > 28 else c for c in cols],
        fontsize=9, color=_FG
    )
    ax.set_xlabel("Missing %", fontsize=9)
    ax.set_title("Missing values by column", fontsize=11, pad=8, fontweight="600")
    ax.set_xlim(0, max(pcts) * 1.18)

    for i, (bar, pct) in enumerate(zip(bars, pcts)):
        ax.text(pct + 0.4, i, f"{pct}%", va="center", fontsize=8, color=_FG)

    _apply_light(fig, ax)
    ax.grid(axis="x", color=_GRID, linewidth=0.5, linestyle="--", alpha=0.7)
    ax.grid(axis="y", visible=False)
    ax.invert_yaxis()
    fig.tight_layout(pad=1.2)
    return fig


def plot_missing(missing_report):
    return plot_missing_inline(missing_report)