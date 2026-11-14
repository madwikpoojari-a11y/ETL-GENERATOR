"""
rule_date_format.py  —  Self-Healing Agent / Rule 5
-----------------------------------------------------
Triggers when any date column contains values not in ISO YYYY-MM-DD format.
Normalizes all parseable dates; logs unparseable ones.
"""

import pandas as pd
from src.utils.logger import get_logger
from src.utils.config import DATE_COLUMNS, KNOWN_DATE_FORMATS

logger = get_logger(__name__)


def _parse_one(val):
    if pd.isna(val):
        return pd.NaT
    s = str(val).strip()
    # Already ISO format — fast path
    if len(s) == 10 and s[4] == "-" and s[7] == "-":
        try:
            return pd.to_datetime(s, format="%Y-%m-%d")
        except Exception:
            pass
    for fmt in KNOWN_DATE_FORMATS:
        try:
            return pd.to_datetime(s, format=fmt)
        except (ValueError, TypeError):
            continue
    try:
        return pd.to_datetime(s)
    except Exception:
        return pd.NaT


def evaluate(df: pd.DataFrame, context: dict) -> bool:
    """Returns True if any date column contains non-ISO values."""
    for col in DATE_COLUMNS:
        if col not in df.columns:
            continue
        non_null = df[col].dropna().astype(str)
        iso_mask = non_null.str.match(r"^\d{4}-\d{2}-\d{2}$")
        if (~iso_mask).any():
            return True
    return False


def apply(df: pd.DataFrame, context: dict) -> tuple[pd.DataFrame, list]:
    """
    Normalizes date columns to YYYY-MM-DD.

    Output:
        df      — DataFrame with normalized dates
        actions — list of action dicts
    """
    df = df.copy()
    actions = []

    for col in DATE_COLUMNS:
        if col not in df.columns:
            continue

        original_nulls = int(df[col].isna().sum())
        parsed   = df[col].apply(_parse_one)
        new_nulls = int(parsed.isna().sum())
        failed    = max(new_nulls - original_nulls, 0)
        normalized = int(parsed.notna().sum())

        df[col] = parsed.dt.strftime("%Y-%m-%d").where(parsed.notna(), other=None)

        msg = (f"Rule 5 — Date Format: '{col}' normalized {normalized} dates, "
               f"{failed} values could not be parsed.")
        logger.warning(msg)

        actions.append({
            "rule_id":   "RULE-05",
            "trigger":   f"Non-ISO dates found in '{col}'",
            "action":    f"Normalized {normalized} dates to YYYY-MM-DD; {failed} unparseable → NaN",
            "outcome":   "HEALED" if failed == 0 else "PARTIAL",
            "column":    col,
        })

    return df, actions
