"""
format_validator.py  —  Validation Layer
------------------------------------------
Validates domain-specific formats: email addresses and date strings.
"""

import re
import pandas as pd
from src.utils.logger import get_logger

logger = get_logger(__name__)

# RFC-5322 simplified email pattern
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_emails(df: pd.DataFrame, col: str = "email") -> dict:
    """
    Checks each non-null email value against a basic valid format pattern.

    Input:  df (DataFrame), col (str) column name
    Output: dict with keys:
                invalid_count — int
                invalid_pct   — float
                invalid_rows  — DataFrame
    """
    if col not in df.columns:
        return {"invalid_count": 0, "invalid_pct": 0.0, "invalid_rows": pd.DataFrame()}

    non_null_mask = df[col].notna()
    non_null = df[non_null_mask]

    invalid_mask = non_null[col].astype(str).apply(
        lambda x: not bool(EMAIL_PATTERN.match(x.strip()))
    )

    invalid_rows  = non_null[invalid_mask]
    invalid_count = len(invalid_rows)
    invalid_pct   = round(invalid_count / len(df) * 100, 2)

    logger.info(
        "Email validation: %d invalid emails (%.2f%%)",
        invalid_count, invalid_pct
    )

    return {
        "invalid_count": invalid_count,
        "invalid_pct":   invalid_pct,
        "invalid_rows":  invalid_rows,
    }


def validate_dates(df: pd.DataFrame, col: str = "purchase_date") -> dict:
    """
    Attempts to parse each non-null date value.
    Values that cannot be parsed are flagged as invalid.

    Input:  df (DataFrame), col (str)
    Output: dict with invalid_count, invalid_pct, invalid_rows
    """
    if col not in df.columns:
        return {"invalid_count": 0, "invalid_pct": 0.0, "invalid_rows": pd.DataFrame()}

    non_null_mask = df[col].notna()
    non_null = df[non_null_mask]

    parsed = pd.to_datetime(
        non_null[col].astype(str),
        errors="coerce",
    )
    invalid_mask  = parsed.isna()
    invalid_rows  = non_null[invalid_mask]
    invalid_count = len(invalid_rows)
    invalid_pct   = round(invalid_count / len(df) * 100, 2)

    logger.info(
        "Date validation '%s': %d unparseable values (%.2f%%)",
        col, invalid_count, invalid_pct
    )

    return {
        "invalid_count": invalid_count,
        "invalid_pct":   invalid_pct,
        "invalid_rows":  invalid_rows,
    }
