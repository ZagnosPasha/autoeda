import streamlit as st
import pandas as pd
from analyser import load_data, get_summary, get_missing_report, get_column_stats
from visualiser import plot_histogram, plot_bar, plot_correlation, plot_missing
from narrator import generate_narrative

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Perceiv",
    page_icon="📊",
    layout="wide"
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    .stApp {
        background: linear-gradient(135deg, #1a1f2e 0%, #242938 100%);
    }

    [data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 12px;
        padding: 16px;
        backdrop-filter: blur(10px);
    }

    [data-testid="metric-container"] label {
        color: rgba(255, 255, 255, 0.8) !important;
        font-size: 12px !important;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }

    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 28px !important;
        font-weight: 700 !important;
    }

    .narrative-box {
        background: linear-gradient(135deg,
            rgba(99, 102, 241, 0.2),
            rgba(139, 92, 246, 0.15));
        border: 1px solid rgba(99, 102, 241, 0.4);
        border-radius: 16px;
        padding: 24px 28px;
        margin: 16px 0;
        backdrop-filter: blur(10px);
    }

    .narrative-title {
        color: #818cf8;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 10px;
    }

    .narrative-text {
        color: #e2e8f0;
        font-size: 15px;
        line-height: 1.8;
    }

    h2, h3 {
        color: #ffffff !important;
    }

    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255,255,255,0.05);
        border-radius: 10px;
        padding: 4px;
        gap: 4px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        color: rgba(255,255,255,0.6);
        font-weight: 500;
    }

    .stTabs [aria-selected="true"] {
        background: rgba(99, 102, 241, 0.3) !important;
        color: #ffffff !important;
    }

    [data-testid="stFileUploadDropzone"] {
        background: rgba(255,255,255,0.03);
        border: 2px dashed rgba(99, 102, 241, 0.4);
        border-radius: 16px;
    }

    hr {
        border-color: rgba(255,255,255,0.08);
    }

    p, span, div, label {
        color: rgba(255,255,255,0.85);
    }

    .preview-box {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 16px;
    }

    code {
        background: rgba(99, 102, 241, 0.15) !important;
        color: #a5b4fc !important;
        border-radius: 4px;
        padding: 2px 6px;
    }

    /* Fix expander hover */
    .streamlit-expanderHeader:hover {
        background: rgba(99, 102, 241, 0.2) !important;
        color: #ffffff !important;
    }

    .streamlit-expanderHeader {
        background: rgba(255,255,255,0.05) !important;
        border-radius: 8px !important;
        color: rgba(255,255,255,0.8) !important;
    }

    /* Fix code block */
    .stCodeBlock {
        background: #0d1117 !important;
    }

    .stCodeBlock code {
        background: transparent !important;
        color: #c9d1d9 !important;
    }

    pre {
        background: #0d1117 !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 8px !important;
    }

    pre code {
        color: #c9d1d9 !important;
        background: transparent !important;
    }

    [data-testid="stExpander"] details {
        background: rgba(255,255,255,0.03) !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: 12px !important;
    }

    [data-testid="stExpander"] details summary {
        background: rgba(255,255,255,0.05) !important;
        border-radius: 8px !important;
        color: rgba(255,255,255,0.8) !important;
    }

    [data-testid="stExpander"] details summary:hover {
        background: rgba(99, 102, 241, 0.2) !important;
        color: #ffffff !important;
    }

    [data-testid="stExpander"] details[open] summary {
        background: rgba(99, 102, 241, 0.15) !important;
        color: #ffffff !important;
        border-radius: 8px 8px 0 0 !important;
    }
</style>
""", unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("## 📊 Perceiv")
st.markdown(
    '<p style="color:rgba(255,255,255,0.5);margin-top:-12px;font-size:14px;">'
    'Upload any dataset and get instant AI-powered analysis</p>',
    unsafe_allow_html=True
)
st.markdown("---")

# ── File upload ────────────────────────────────────────────────────────────────
uploaded_file = st.file_uploader(
    "Drop your CSV or Excel file here",
    type=["csv", "xlsx"],
    label_visibility="visible"
)

if uploaded_file is not None:

    # Load data
    df = load_data(uploaded_file)

    if df is None:
        st.error("Could not load file. Please check the format and try again.")
        st.stop()

    summary        = get_summary(df)
    missing_report = get_missing_report(df)
    col_stats      = get_column_stats(df)

    st.markdown("---")

    # ── File preview ──────────────────────────────────────────────────────────
    with st.expander("👁️  Preview uploaded file", expanded=False):
        st.markdown(
            f'<p style="color:rgba(255,255,255,0.5);font-size:13px;">'
            f'Showing first 5 rows of <b>{uploaded_file.name}</b> '
            f'— {summary["rows"]} rows × {summary["columns"]} columns</p>',
            unsafe_allow_html=True
        )
        st.dataframe(df.head(), use_container_width=True, hide_index=True)

    st.markdown("---")

    # ── AI Narrative — FIRST ──────────────────────────────────────────────────
    with st.spinner("🤖 Analysing your dataset..."):
        narrative = generate_narrative(summary, missing_report)

    st.markdown(f"""
    <div class="narrative-box">
        <div class="narrative-title">🤖 AI Analysis</div>
        <div class="narrative-text">{narrative}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Summary metrics ────────────────────────────────────────────────────────
    st.markdown("### Dataset overview")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Rows",         summary["rows"])
    c2.metric("Columns",      summary["columns"])
    c3.metric("Missing %",    f"{summary['missing_pct']}%")
    c4.metric("Numeric cols", summary["numeric_cols"])
    c5.metric("Text cols",    summary["text_cols"])

    st.markdown("---")

    # ── Column statistics ──────────────────────────────────────────────────────
    st.markdown("### Column statistics")
    with st.expander("📋  View detailed column statistics", expanded=False):
        stats_rows = []
        for col_name, values in col_stats.items():
            row = {"column": col_name}
            row.update(values)
            stats_rows.append(row)
        stats_df = pd.DataFrame(stats_rows)
        st.dataframe(stats_df, use_container_width=True, hide_index=True)

    st.markdown("---")

    # ── Missing values table ───────────────────────────────────────────────────
    st.markdown("### Missing values report")

    missing_df = pd.DataFrame(missing_report)

    # Filter to only columns WITH missing values
    missing_only = missing_df[missing_df["missing"] > 0]

    if missing_only.empty:
        st.success("✅ Great news — no missing values found in this dataset.")
    else:
        st.warning(
            f"⚠️ {len(missing_only)} column(s) have missing values "
            f"out of {summary['columns']} total."
        )

        def colour_flag(val):
            if val == "HIGH":
                return "color: #f87171; font-weight: 600"
            elif val == "LOW":
                return "color: #fbbf24; font-weight: 600"
            else:
                return "color: #34d399; font-weight: 600"

        styled = missing_only.style.map(colour_flag, subset=["flag"])
        st.dataframe(styled, use_container_width=True, hide_index=True)

    st.markdown("---")

    # ── Charts in tabs ─────────────────────────────────────────────────────────
    st.markdown("### Visualisations")

    tab1, tab2, tab3 = st.tabs([
        "📈  Distributions",
        "🔥  Correlations",
        "❓  Missing values"
    ])

    with tab1:
        numeric_cols = df.select_dtypes(include="number").columns.tolist()
        text_cols    = df.select_dtypes(include="str").columns.tolist()
        cols_per_row = 2

        if numeric_cols:
            st.markdown("**Numeric columns**")
            for i in range(0, len(numeric_cols), cols_per_row):
                row_cols = st.columns(cols_per_row)
                for j, col in enumerate(numeric_cols[i:i+cols_per_row]):
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
                for j, col in enumerate(text_cols[i:i+cols_per_row]):
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
plt.xlabel("{col}")
plt.ylabel("Count")
plt.tight_layout()
plt.show()
""", language="python")

    with tab2:
        st.pyplot(plot_correlation(df))
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

    with tab3:
        # Only show missing chart if there are missing values
        if missing_only.empty:
            st.success("✅ No missing values — nothing to show here.")
        else:
            st.pyplot(plot_missing(missing_report))
            with st.expander("📋 Copy code"):
                st.code("""
import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv("your_file.csv")
missing = df.isnull().sum()
missing = missing[missing > 0]
missing_pct = (missing / len(df) * 100).round(1)
fig, ax = plt.subplots(figsize=(10, 5))
ax.barh(range(len(missing_pct)), missing_pct.values,
        color="steelblue", edgecolor="white")
ax.set_yticks(range(len(missing_pct)))
ax.set_yticklabels(missing_pct.index)
ax.set_title("Missing values per column")
ax.set_xlabel("Missing %")
plt.tight_layout()
plt.show()
""", language="python")

else:
    # ── Empty state ────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="text-align:center;padding:60px 20px;">
        <div style="font-size:48px;margin-bottom:16px;">📂</div>
        <div style="font-size:18px;font-weight:500;color:rgba(255,255,255,0.6);">
            Upload a CSV or Excel file to get started
        </div>
        <div style="font-size:14px;margin-top:8px;color:rgba(255,255,255,0.3);">
            Supports .csv and .xlsx — up to 200MB
        </div>
    </div>
    """, unsafe_allow_html=True)