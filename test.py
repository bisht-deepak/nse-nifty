from pathlib import Path

from utils.loader import load_nifty_report


# TEST_FILES = [
#     "data/extracted/nifty50/nifty50_jan08.csv",   # earliest report
#     "data/extracted/nifty50/nifty50_aug12.csv",   # 14-column file
#     "data/extracted/nifty50/nifty50_mar18.csv",   # mid-period
#     "data/extracted/nifty50/nifty50_jun26.csv",   # latest report
# ]


# for file in TEST_FILES:

#     print("=" * 100)
#     print(Path(file).name)

#     df = load_nifty_report(file)

#     print(f"Shape: {df.shape}")
#     print()

#     print("Columns:")
#     print(df.columns.tolist())
#     print()

#     print("Dtypes:")
#     print(df.dtypes)
#     print()

#     print("First 3 rows:")
#     print(df.head(3))
#     print()

#     print("Last 3 rows:")
#     print(df.tail(3))
#     print()

#     print("Summary")
#     print(f"Rank Range : {df['rank'].min()} → {df['rank'].max()}")

#     if "symbol" in df.columns:
#         print(f"Unique Symbols : {df['symbol'].nunique()}")

#     print(f"Report Date : {df['report_date'].iloc[0]}")

input_path= "data/extracted/nifty50/nifty50_jan08.csv"
df = load_nifty_report(input_path)
print(f"input_path: {input_path}")
# print(df.columns.tolist())

print(df["free_float_market_cap"].head(10))