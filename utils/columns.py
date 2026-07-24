"""
Column standardization utilities.

Maps inconsistent NSE report column names to a standard schema.
"""

from __future__ import annotations


COLUMN_KEYWORDS = {
    "Sr. No": "rank",
    "Security Symbol": "symbol",
    "Security Name": "company_name",
    "Industry": "industry",
    "Equity": "equity_capital",
    "Market": "free_float_market_cap",
    "Weight": "weight",
    "Beta": "beta",
    "R2": "r2",
    "Volatility": "volatility",
    "Monthly Return": "monthly_return",
    "Impact Cost": "impact_cost",
}


def resolve_column(column: str) -> str:
    """
    Convert an original NSE column name into a standardized name.

    Parameters
    ----------
    column : str

    Returns
    -------
    str
    """

    column = column.strip()

    for keyword, standard in COLUMN_KEYWORDS.items():

        if keyword.lower() in column.lower():
            return standard

    return column.lower().replace(" ", "_")