import streamlit as st
import pandas as pd
from analyser import load_data, get_summary, get_missing_report, get_column_stats
from visualiser import plot_histogram, plot_bar, plot_correlation, plot_missing
from narrator import generate_narrative

st.set_page_config(page_title="AutoEDA", page_icon="📊", layout="wide")

st.title("📊 AutoEDA")
st.write("Upload a dataset and get instant AI-powered analysis")

uploaded_file = st.file_uploader("Upload your CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file is not None:

    df = load_data(uploaded_file)

    # ── Summary metrics ──────────────────────────────────────────
    st.subheader("Dataset Summary")
    summary = get_summary(df)
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Rows", summary["rows"])
    col2.metric("Columns", summary["columns"])
    col3.metric("Missing %", f"{summary['missing_pct']}%")
    col4.metric("Numeric Cols", summary["numeric_cols"])
    col5.metric("Text Cols", summary["text_cols"])

    # ── Missing values table ──────────────────────────────────────
    st.subheader("Missing Values Report")
    missing_report = get_missing_report(df)
    st.dataframe(pd.DataFrame(missing_report), use_container_width=True)

    # ── Correlation heatmap ───────────────────────────────────────
    st.subheader("Correlation Heatmap")
    st.pyplot(plot_correlation(df))

    # ── Missing values chart ──────────────────────────────────────
    st.subheader("Missing Values Chart")
    st.pyplot(plot_missing(missing_report))

    # ── Histograms for numeric columns ────────────────────────────
    st.subheader("Numeric Column Distributions")
    numeric_cols = df.select_dtypes(include="number").columns
    for col in numeric_cols:
        st.pyplot(plot_histogram(df, col))

    # ── Bar charts for text columns ───────────────────────────────
    st.subheader("Categorical Column Distributions")
    text_cols = df.select_dtypes(include="str").columns
    for col in text_cols:
        st.pyplot(plot_bar(df, col))

    # ── AI Narrative ──────────────────────────────────────────────
    st.subheader("🤖 AI Analysis")
    with st.spinner("Generating AI narrative..."):
        narrative = generate_narrative(summary, missing_report)
    st.info(narrative)

else:
    st.info("👆 Upload a CSV or Excel file above to get started")