from pathlib import Path
import calendar

DATA_DIR = Path("data/extracted/nifty50")

# Expected files
expected = []

for year in range(2008, 2027):
    for month in range(1, 13):

        if year == 2026 and month > 6:
            break

        mon = calendar.month_abbr[month].lower()
        expected.append(f"nifty50_{mon}{str(year)[2:]}.csv")

# Actual files
actual = {f.name for f in DATA_DIR.glob("*.csv")}

# Find missing
missing = sorted(set(expected) - actual)

print(f"Expected : {len(expected)}")
print(f"Found    : {len(actual)}")
print(f"Missing  : {len(missing)}")

if missing:
    print("\nMissing files:")
    for f in missing:
        print(f)