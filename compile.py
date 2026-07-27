"""
Compile all Nifty 50 monthly constituent reports into a single dataset.
"""

from pathlib import Path

import pandas as pd
from tqdm import tqdm

from utils.loader import load_nifty_report
from utils.constants import (
    EXPECTED_CONSTITUENTS, 
    REQUIRED_COLUMNS,
    HISTORICAL_SYMBOL_RENAMES 
)

# =============================================================================
# Configuration
# =============================================================================

INPUT_DIR = Path("data/extracted/nifty50")

OUTPUT_DIR = Path("data/processed")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_PARQUET = OUTPUT_DIR / "nifty50_history.parquet"
OUTPUT_CSV = OUTPUT_DIR / "nifty50_history.csv"

ERROR_LOG = Path("data/metadata/audits/compile_errors.csv")
ERROR_LOG.parent.mkdir(parents=True, exist_ok=True)


# =============================================================================
# Fill Missing Metadata
# =============================================================================

def fill_metadata(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fill missing company names and industries using
    values available for the same company in other reports.
    """

    df = df.copy()

    # Normalize historical symbols
    df["lookup_symbol"] = df["symbol"].replace(HISTORICAL_SYMBOL_RENAMES )

    df = df.sort_values(["lookup_symbol", "report_date"])

    df["company_name"] = (
        df.groupby("lookup_symbol")["company_name"]
          .transform(lambda x: x.ffill().bfill())
    )

    df["industry"] = (
        df.groupby("lookup_symbol")["industry"]
          .transform(lambda x: x.ffill().bfill())
    )

    df = (
        df.drop(columns="lookup_symbol")
          .sort_values(["report_date", "rank"])
          .reset_index(drop=True)
    )

    df.loc[df["symbol"] == "GLAXO", "company_name"] = (
        "GlaxoSmithKline Pharmaceuticals Ltd."
    )
    
    return df

# =============================================================================
# Validation
# =============================================================================

def validate_dataset(df: pd.DataFrame) -> None:
    """
    Validate the compiled dataset before saving.
    """

    print("\nRunning dataset validation...\n")

    # -------------------------------------------------------------------------
    # Required columns
    # -------------------------------------------------------------------------

    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]

    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    print("✓ Required columns present")

    # -------------------------------------------------------------------------
    # Missing report dates
    # -------------------------------------------------------------------------

    if df["report_date"].isna().any():
        raise ValueError("Missing report_date values detected.")

    print("✓ No missing report dates")

    # -------------------------------------------------------------------------
    # Constituents per report
    # -------------------------------------------------------------------------

    counts = df.groupby("report_date").size()

    bad = counts[counts != EXPECTED_CONSTITUENTS]

    if not bad.empty:
        raise ValueError(
            f"Some reports do not contain {EXPECTED_CONSTITUENTS} constituents:\n\n{bad}"
        )

    print(f"✓ Every report contains {EXPECTED_CONSTITUENTS} constituents")

    # -------------------------------------------------------------------------
    # Duplicate symbols
    # -------------------------------------------------------------------------

    dup = df.duplicated(["report_date", "symbol"])

    if dup.any():
        raise ValueError(
            "Duplicate (report_date, symbol) combinations detected."
        )

    print("✓ No duplicate symbols within a report")

    # -------------------------------------------------------------------------
    # Duplicate ranks
    # -------------------------------------------------------------------------

    dup = df.duplicated(["report_date", "rank"])

    if dup.any():
        raise ValueError(
            "Duplicate (report_date, rank) combinations detected."
        )

    print("✓ No duplicate ranks within a report")

    # -------------------------------------------------------------------------
    # Rank range
    # -------------------------------------------------------------------------

    rank_check = (
        df.groupby("report_date")["rank"]
        .agg(["min", "max"])
    )

    if (
        (rank_check["min"] != 1).any()
        or
        (rank_check["max"] != EXPECTED_CONSTITUENTS).any()
    ):
        raise ValueError("Invalid rank range detected.")

    print(f"✓ Rank range is 1–{EXPECTED_CONSTITUENTS} for every report")

    # -------------------------------------------------------------------------
    # Missing metadata
    # -------------------------------------------------------------------------

    missing_company = df["company_name"].isna().sum()
    missing_industry = df["industry"].isna().sum()

    if missing_company:
        print(f"⚠ Missing company_name: {missing_company}")

    if missing_industry:
        print(f"⚠ Missing industry: {missing_industry}")

    print("\n" + "=" * 60)
    print("DATASET VALIDATION PASSED")
    print("=" * 60)


# =============================================================================
# Main
# =============================================================================

def main():

    csv_files = sorted(INPUT_DIR.glob("*.csv"))

    print(f"Found {len(csv_files)} reports.\n")

    reports = []
    errors = []

    for file in tqdm(csv_files, desc="Loading Reports"):

        try:
            reports.append(load_nifty_report(file))

        except Exception as e:

            errors.append(
                {
                    "file": file.name,
                    "error": str(e),
                }
            )

    print()

    print(f"Successfully loaded : {len(reports)}")
    print(f"Failed              : {len(errors)}")

    if not reports:
        raise RuntimeError("No reports were successfully loaded.")

    master = (
        pd.concat(reports, ignore_index=True)
        .sort_values(["report_date", "rank"])
        .reset_index(drop=True)
    )

    master = fill_metadata(master)

    # -------------------------------------------------------------------------
    # Validate
    # -------------------------------------------------------------------------

    validate_dataset(master)

    # -------------------------------------------------------------------------
    # Save
    # -------------------------------------------------------------------------

    master.to_parquet(OUTPUT_PARQUET, index=False)
    master.to_csv(OUTPUT_CSV, index=False)

    print("\nSaved files")
    print("-" * 60)
    print(f"Parquet : {OUTPUT_PARQUET}")
    print(f"CSV      : {OUTPUT_CSV}")

    # -------------------------------------------------------------------------
    # Save errors
    # -------------------------------------------------------------------------

    if errors:

        pd.DataFrame(errors).to_csv(ERROR_LOG, index=False)

        print(f"\nError log : {ERROR_LOG}")

    # -------------------------------------------------------------------------
    # Summary
    # -------------------------------------------------------------------------

    print("\nDataset Summary")
    print("-" * 60)

    print(f"Reports               : {master['report_date'].nunique()}")
    print(f"Rows                  : {len(master):,}")
    print(f"Columns               : {len(master.columns)}")
    print(f"Unique Companies      : {master['symbol'].nunique()}")
    print(f"Date Range            : {master['report_date'].min().date()} → {master['report_date'].max().date()}")


if __name__ == "__main__":
    main()