
import pandas as pd

def load_data(file_path):
    try:
        filename = file_path.name if hasattr(file_path, "name") else file_path

        if filename.endswith(".csv"):          # ← filename not file_path
            try:
                df = pd.read_csv(file_path, encoding="utf-8")
            except UnicodeDecodeError:
                df = pd.read_csv(file_path, encoding="latin1")
            rows, cols = df.shape
            print(f"Loaded {filename} - {rows} rows and {cols} columns")
            return df
        elif filename.endswith(".xlsx"):       # ← filename not file_path
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
    x , y = df.shape
    sumry = {}
    sumry["rows"] = x
    sumry["columns"] = y
    total_cels = x * y
    missing = df.isnull().sum().sum()
    sumry["missing_pct"] = float(round((missing/total_cels)*100,1))
    sumry["numeric_cols"] = df.select_dtypes(include="number").shape[1]
    sumry["text_cols"] = df.select_dtypes(include="str").shape[1]
    return sumry

def get_missing_report(df):
    misng_rpt = []
    cols = df.columns
    totl_row = len(df)
    for column in cols:
        misng_cols = {}
        col_misng = int(df[column].isnull().sum())
        col_misng_pct = float(round((col_misng/totl_row)*100,1))
        misng_cols["column"] = column
        misng_cols["missing"] = col_misng
        misng_cols["pct"] = col_misng_pct
        if col_misng_pct == 0.0:
            misng_cols["flag"] = "CLEAN"
        elif 0 < col_misng_pct < 10:
            misng_cols["flag"] = "LOW"
        else:
            misng_cols["flag"] = "HIGH"
        misng_rpt.append(misng_cols)
       
    return misng_rpt


def get_column_stats(df):
    cols = df.columns
    num_cols = df.select_dtypes(include="number").columns
    text_cols = df.select_dtypes(include="str").columns
    
    stats ={}
    for column in cols:
        col_stats = {}
        if column in num_cols:
            col_stats["type"] = "numeric"
            col_stats["mean"] = float(round(df[column].mean(),2))
            col_stats["median"] = float(round(df[column].median(),2))
            col_stats["std"] = float(round(df[column].std(),2))
            col_stats["min"] = float(df[column].min())
            col_stats["max"] = float(df[column].max())
        elif column in text_cols:
            col_stats["type"] = "text"
            col_stats["unique_values"] = df[column].nunique()
            col_stats["most_common"] = df[column].mode()[0]
        else:
            print("not a column been checked currently")
        stats[column] = col_stats
    return stats


