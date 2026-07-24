"""
Utilities for loading a single NSE index report.
"""

from __future__ import annotations

import calendar
from pathlib import Path

import pandas as pd

from utils.columns import resolve_column
from utils.constants import (
    EXPECTED_CONSTITUENTS,
    HEADER_KEYWORDS,
    MAX_HEADER_SEARCH_ROWS,
    NUMERIC_COLUMNS,
    STANDARD_COLUMNS,
)


# ============================================================================
# Header Detection
# ============================================================================

def find_header_row(filepath: Path) -> int:
    """
    Locate the header row by searching the first few lines for
    known column names.
    """

    with open(filepath, encoding="utf-8-sig", errors="replace") as f:

        for i in range(MAX_HEADER_SEARCH_ROWS):

            line = f.readline()

            if not line:
                break

            matches = sum(keyword in line for keyword in HEADER_KEYWORDS)

            if matches >= 3:
                return i

    raise ValueError(f"Header not found in {filepath.name}")


# ============================================================================
# Report Date
# ============================================================================

def parse_report_date(filepath: Path) -> pd.Timestamp:
    """
    Extract report date from filename.

    Example
    -------
    nifty50_aug12.csv -> Timestamp('2012-08-01')
    """

    period = filepath.stem.split("_")[-1]

    month = period[:3].title()
    year = 2000 + int(period[3:])

    month_num = list(calendar.month_abbr).index(month)

    return pd.Timestamp(year=year, month=month_num, day=1)


# ============================================================================
# Cleaning Helpers
# ============================================================================

def remove_empty_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove completely empty and unnamed columns.
    """

    df = df.dropna(axis=1, how="all")

    df = df.loc[:, ~df.columns.astype(str).str.contains("^Unnamed")]

    return df


def clean_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize column names.
    """

    rename = {
        col: resolve_column(col)
        for col in df.columns
    }

    return df.rename(columns=rename)


def ensure_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ensure all expected columns exist.
    Missing columns are created and filled with pd.NA.
    """

    for col in STANDARD_COLUMNS:
        if col not in df.columns:
            df[col] = pd.NA

    return df[STANDARD_COLUMNS]


def remove_unit_row(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove the units row.

    The units row contains entries such as
    (In Rs.), (Rs. Crores), %, etc.
    """

    if "rank" not in df.columns:
        raise ValueError("'rank' column not found.")

    df["rank"] = pd.to_numeric(df["rank"], errors="coerce")

    df = df[df["rank"].notna()].copy()

    df["rank"] = df["rank"].astype(int)

    return df


def keep_constituents(df: pd.DataFrame) -> pd.DataFrame:
    """
    Keep only constituent rows (rank 1–50).
    """

    return df[df["rank"].between(1, EXPECTED_CONSTITUENTS)].copy()


def clean_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert numeric columns to appropriate dtypes.
    """

    for col in NUMERIC_COLUMNS:

        if col not in df.columns:
            continue

        df[col] = (
            df[col]
            .astype(str)
            .str.replace(",", "", regex=False)
            .str.strip()
        )

        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


# ============================================================================
# Validation
# ============================================================================

def validate_report(df: pd.DataFrame, filepath: Path) -> None:
    """
    Validate a cleaned report.
    """

    if len(df) != EXPECTED_CONSTITUENTS:
        raise ValueError(
            f"{filepath.name}: Expected "
            f"{EXPECTED_CONSTITUENTS} rows, found {len(df)}."
        )

    if df["rank"].min() != 1:
        raise ValueError(f"{filepath.name}: Rank does not start at 1.")

    if df["rank"].max() != EXPECTED_CONSTITUENTS:
        raise ValueError(
            f"{filepath.name}: Rank does not end at "
            f"{EXPECTED_CONSTITUENTS}."
        )

    if df["rank"].duplicated().any():
        raise ValueError(f"{filepath.name}: Duplicate ranks detected.")

    if "symbol" in df.columns:
        if df["symbol"].duplicated().any():
            raise ValueError(
                f"{filepath.name}: Duplicate security symbols detected."
            )


# ============================================================================
# Public Loader
# ============================================================================

def load_nifty_report(filepath: str | Path) -> pd.DataFrame:
    """
    Load a single NSE constituent report.

    Parameters
    ----------
    filepath : str | Path

    Returns
    -------
    pandas.DataFrame
    """

    filepath = Path(filepath)

    header_row = find_header_row(filepath)

    df = pd.read_csv(
        filepath,
        skiprows=header_row,
        encoding="utf-8-sig",
    )

    df = remove_empty_columns(df)

    df = clean_columns(df)

    df = ensure_columns(df)  

    df = remove_unit_row(df)

    df = keep_constituents(df)

    df = clean_dtypes(df)

    df["report_date"] = parse_report_date(filepath)

    df["source_file"] = filepath.name

    validate_report(df, filepath)

    return df.reset_index(drop=True)