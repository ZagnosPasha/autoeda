import pandas as pd
 
# ── Datetime detection helpers ─────────────────────────────────────────────────
 
_DATE_KEYWORDS = [
    "date", "time", "year", "month", "day", "dt", "timestamp",
    "created", "updated", "opened", "closed", "period", "week"
]
 
def _looks_like_year_col(series: pd.Series) -> bool:
    """Integer column whose values all fall in 1900–2100 and name hints at a year."""
    if not pd.api.types.is_integer_dtype(series):
        return False
    non_null = series.dropna()
    if non_null.empty:
        return False
    return bool((non_null >= 1900).all() and (non_null <= 2100).all())
 
def _col_name_is_temporal(col_name: str) -> bool:
    return any(kw in col_name.lower() for kw in _DATE_KEYWORDS)
 
def _try_parse_datetime(series: pd.Series) -> bool:
    """Try parsing an object/string column as dates. Returns True if >80% parse."""
    if series.dtype != object:
        return False
    sample = series.dropna().head(100)
    if sample.empty:
        return False
    try:
        parsed = pd.to_datetime(sample, infer_datetime_format=True, errors="coerce")
        return parsed.notna().mean() > 0.8
    except Exception:
        return False
 
def detect_datetime_columns(df: pd.DataFrame) -> set:
    """Return a set of column names that should be treated as datetime."""
    dt_cols = set()
 
    # 1. Columns pandas already parsed as datetime
    for col in df.select_dtypes(include=["datetime", "datetimetz"]).columns:
        dt_cols.add(col)
 
    # 2. Numeric columns that look like year columns
    for col in df.select_dtypes(include="number").columns:
        if _col_name_is_temporal(col) and _looks_like_year_col(df[col]):
            dt_cols.add(col)
 
    # 3. Object/string columns that parse cleanly as dates
    for col in df.select_dtypes(include="object").columns:
        if _try_parse_datetime(df[col]):
            dt_cols.add(col)
 
    return dt_cols
 
 
# ── Core functions ─────────────────────────────────────────────────────────────
 
def load_data(file_path):
    try:
        filename = file_path.name if hasattr(file_path, "name") else file_path
 
        if filename.endswith(".csv"):
            try:
                file_path.seek(0)
                df = pd.read_csv(file_path, encoding="utf-8")
            except UnicodeDecodeError:
                file_path.seek(0)
                df = pd.read_csv(file_path, encoding="latin1")
            rows, cols = df.shape
            print(f"Loaded {filename} - {rows} rows and {cols} columns")
            return df
        elif filename.endswith(".xlsx"):
            file_path.seek(0)
            df = pd.read_excel(file_path)
            rows, cols = df.shape
            print(f"Loaded {filename} - {rows} rows and {cols} columns")
            return df
        else:
            print("Sorry unsupported file type")
            return None
    except FileNotFoundError:
        print(f"File not found in: {file_path}")
        return None
 
 
def get_summary(df):
    dt_cols = detect_datetime_columns(df)
 
    x, y = df.shape
    sumry = {}
    sumry["rows"] = x
    sumry["columns"] = y
    total_cels = x * y
    missing = df.isnull().sum().sum()
    sumry["missing_pct"] = float(round((missing / total_cels) * 100, 1))
 
    # Exclude datetime cols from the numeric count
    true_numeric = [
        c for c in df.select_dtypes(include="number").columns
        if c not in dt_cols
    ]
    sumry["numeric_cols"] = len(true_numeric)
    sumry["text_cols"] = df.select_dtypes(include="object").shape[1]
    sumry["datetime_cols"] = len(dt_cols)
    sumry["datetime_col_names"] = list(dt_cols)
    return sumry
 
 
def get_missing_report(df):
    misng_rpt = []
    totl_row = len(df)
    for column in df.columns:
        col_misng = int(df[column].isnull().sum())
        col_misng_pct = float(round((col_misng / totl_row) * 100, 1))
        if col_misng_pct == 0.0:
            flag = "CLEAN"
        elif col_misng_pct < 10:
            flag = "LOW"
        else:
            flag = "HIGH"
        misng_rpt.append({
            "column": column,
            "missing": col_misng,
            "pct": col_misng_pct,
            "flag": flag
        })
    return misng_rpt
 
 
def get_column_stats(df):
    dt_cols = detect_datetime_columns(df)
    num_cols = [c for c in df.select_dtypes(include="number").columns if c not in dt_cols]
    text_cols = list(df.select_dtypes(include="object").columns)
 
    stats = {}
    for column in df.columns:
        col_stats = {}
        if column in dt_cols:
            col_stats["type"] = "datetime"
            non_null = df[column].dropna()
            col_stats["unique_values"] = int(df[column].nunique())
            col_stats["missing_pct"] = float(round(df[column].isnull().mean() * 100, 1))
            # Try to show min/max as readable dates
            try:
                parsed = pd.to_datetime(non_null, errors="coerce").dropna()
                if not parsed.empty:
                    col_stats["min"] = str(parsed.min().date())
                    col_stats["max"] = str(parsed.max().date())
            except Exception:
                pass
        elif column in num_cols:
            col_stats["type"] = "numeric"
            col_stats["mean"] = float(round(df[column].mean(), 2))
            col_stats["median"] = float(round(df[column].median(), 2))
            col_stats["std"] = float(round(df[column].std(), 2))
            col_stats["min"] = float(df[column].min())
            col_stats["max"] = float(df[column].max())
            # Skewness flag
            skew = df[column].skew()
            if skew > 1:
                col_stats["skew"] = "right-skewed"
            elif skew < -1:
                col_stats["skew"] = "left-skewed"
            else:
                col_stats["skew"] = "roughly symmetric"
        elif column in text_cols:
            col_stats["type"] = "text"
            col_stats["unique_values"] = int(df[column].nunique())
            col_stats["most_common"] = str(df[column].mode()[0]) if not df[column].mode().empty else "N/A"
            col_stats["top_pct"] = float(round(
                df[column].value_counts(normalize=True).iloc[0] * 100, 1
            )) if not df[column].empty else 0.0
        else:
            col_stats["type"] = "other"
        stats[column] = col_stats
    return stats