HEADER_KEYWORDS = [
    "Security Symbol",
    "Beta",
    "R2",
]

MAX_HEADER_SEARCH_ROWS = 20

EXPECTED_CONSTITUENTS = 50

REPORT_DATE_REGEX = r"([a-z]{3})(\d{2})"

NUMERIC_COLUMNS = [
    "rank",
    "equity_capital",
    "free_float_market_cap",
    "weight",
    "beta",
    "r2",
    "volatility",
    "monthly_return",
    "impact_cost",
]

REQUIRED_COLUMNS = [
    "rank",
    "symbol",
    "weight",
    "beta",
    "r2",
]


STANDARD_COLUMNS = [
    "rank",
    "symbol",
    "company_name",
    "industry",
    "equity_capital",
    "free_float_market_cap",
    "weight",
    "beta",
    "r2",
    "volatility",
    "monthly_return",
    "impact_cost",
]

# =============================================================================
# Historical Symbol Renames
#
# Used only for metadata enrichment. Some companies changed their NSE trading
# symbols over time (e.g. VSNL -> TATACOMM). These mappings allow company_name
# and industry to be filled across historical symbol changes while preserving
# the original symbol in the compiled dataset.
# =============================================================================

HISTORICAL_SYMBOL_RENAMES  = {
    "BAJAJAUTO": "BAJAJ-AUTO",
    "REL": "RELINFRA",
    "VSNL": "TATACOMM",
}