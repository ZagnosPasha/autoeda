import pandas as pd

df = pd.read_csv("titanic.csv")

print(df.head())
print(df.shape())
print(df.columns.tolist())