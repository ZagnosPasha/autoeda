import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from analyser import load_data, get_missing_report

def plot_histogram(df,col):
    if df[col].dtype == "object":
        print(f"{col} is a text column - use a bar chart instead")
        return None
    fig, ax = plt.subplots(figsize = (10,5))
    ax.hist(df[col], bins = 30, color= "steelblue",edgecolor="white")
    ax.set_title(f"Distribution of {col}", fontsize = 14)
    ax.set_xlabel(col, fontsize=11)
    ax.set_ylabel("Count", fontsize=11)
    return fig

def plot_bar(df, col):
    total_unique = df[col].nunique()

    if total_unique <= 20:
        counts = df[col].value_counts()
    else:
        counts = df[col].value_counts().head(10)
    
    fig , ax = plt.subplots(figsize = (max(6, len(counts) * 1.5), 5))
    ax.bar(range(len(counts)),counts.values, color = "steelblue", edgecolor="white")
    ax.set_xticks(range(len(counts)))
    ax.set_xticklabels(counts.index, rotation = 45, ha= "right")

    title = f"Value counts of {col}"
    if total_unique > 20:
        title += f" (top 10 of {total_unique})"

    ax.set_title(title, fontsize = 14)
    ax.set_xlabel(col, fontsize=11)
    ax.set_ylabel("Count", fontsize=11)
    return fig

def plot_correlation(df):
    correlation_data = df.corr(numeric_only = True)
    fig, ax = plt.subplots(figsize = (10,5))
    sns.heatmap(correlation_data, annot = True, fmt =".2f", cmap="coolwarm", ax=ax)
    return fig

def plot_missing(missing_report):
    cols = [row["column"] for row in missing_report]
    pcts = [row["pct"] for row in missing_report]
    
    
    fig, ax = plt.subplots(figsize = (10,5))
    ax.barh(range(len(cols)),pcts, color = "steelblue", edgecolor="white")
    ax.set_yticks(range(len(cols)))
    ax.set_yticklabels(cols)
    ax.set_title("Missing values per column", fontsize=14)
    ax.set_xlabel("Missing %", fontsize=11)
    return fig




