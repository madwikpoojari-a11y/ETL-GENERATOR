"""
date_normalizer.py  —  Cleaning Layer
----------------------------------------
Normalizes all date columns to ISO format: YYYY-MM-DD.
Unparseable values become NaN (handled by null_handler).
"""

import pandas as pd
from src.utils.logger import get_logger
from src.utils.config import DATE_COLUMNS, KNOWN_DATE_FORMATS

logger = get_logger(__name__)


def _parse_date(val):
    """
    Tries every known format in order, then pandas generic parser.
    Returns a pd.Timestamp or pd.NaT.
    """
    if pd.isna(val):
        return pd.NaT
    s = str(val).strip()
    for fmt in KNOWN_DATE_FORMATS:
        try:
            return pd.to_datetime(s, format=fmt)
        except (ValueError, TypeError):
            continue
    # Generic fallback
    try:
        return pd.to_datetime(s)
    except Exception:
        return pd.NaT


def clean(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Parses and normalizes all DATE_COLUMNS to YYYY-MM-DD string format.

    Input:  df (DataFrame)
    Output:
        df     — DataFrame with normalized date strings
        report — dict: column -> {"normalized": int, "failed": int}
    """
    df = df.copy()
    report = {}

    for col in DATE_COLUMNS:
        if col not in df.columns:
            continue

        original_nulls = int(df[col].isna().sum())
        parsed = df[col].apply(_parse_date)
        new_nulls = int(parsed.isna().sum())
        failed = max(new_nulls - original_nulls, 0)

        # Store back as YYYY-MM-DD strings (NaT becomes NaN naturally)
        df[col] = parsed.dt.strftime("%Y-%m-%d").where(parsed.notna(), other=None)

        normalized = int(df[col].notna().sum())
        report[col] = {"normalized": normalized, "failed": failed}

        logger.info(
            "Date normalizer '%s': %d normalized, %d unparseable",
            col, normalized, failed
        )

    return df, report
