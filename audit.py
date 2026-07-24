from pathlib import Path
import pandas as pd
from tqdm import tqdm

DATA_DIR = Path("data/extracted/nifty50")
OUTPUT = Path("data/metadata/audits/nifty50_audit.csv")

OUTPUT.parent.mkdir(parents=True, exist_ok=True)

HEADER_KEYWORDS = [
    "Security Symbol",
    "Security Name",
    "Weight",
    "Weightage",
    "Beta",
    "R2",
]


def find_header(lines, max_lines=20):
    """
    Locate the header row using reliable column names.
    """

    for i, line in enumerate(lines[:max_lines]):
        matches = sum(keyword in line for keyword in HEADER_KEYWORDS)

        if matches >= 3:
            return i

    return None


records = []

csv_files = sorted(DATA_DIR.glob("*.csv"))

for file in tqdm(csv_files, desc="Auditing"):

    with open(file, encoding="utf-8-sig", errors="replace") as f:
        lines = f.readlines()

    header_row = find_header(lines)

    if header_row is None:

        records.append({
            "filename": file.name,
            "header_row": None
        })

        continue

    header = [x.strip() for x in lines[header_row].strip().split(",")]

    row_after = []
    if header_row + 1 < len(lines):
        row_after = [x.strip() for x in lines[header_row + 1].split(",")]

    first_data = []
    data_start = None

    for i in range(header_row + 1, len(lines)):

        row = [x.strip() for x in lines[i].split(",")]

        if any(cell != "" for cell in row):
            first_data = row
            data_start = i
            break

    last_data = []
    for i in range(len(lines)-1, -1, -1):

        row = [x.strip() for x in lines[i].split(",")]

        if any(cell != "" for cell in row):
            last_data = row
            break

    records.append({

        "filename": file.name,

        "total_lines": len(lines),

        "header_row": header_row,

        "data_start_row": data_start,

        "blank_after_header": (
            data_start is not None
            and data_start > header_row + 1
        ),

        "n_columns": len(header),

        "column_names": " | ".join(header),

        "row_after_header": " | ".join(row_after),

        "first_data_row": " | ".join(first_data),

        "last_data_row": " | ".join(last_data)

    })

audit = pd.DataFrame(records)

audit.to_csv(OUTPUT, index=False)

print(audit.head())