"""
type_validator.py  —  Validation Layer
----------------------------------------
Checks whether values in each column match the inferred type.
Flags rows where a numeric column contains text, etc.
"""

import pandas as pd
from src.utils.logger import get_logger
from src.utils.config import NUMERIC_COLUMNS, DATE_COLUMNS, KNOWN_DATE_FORMATS

logger = get_logger(__name__)


def _is_numeric(val) -> bool:
    if pd.isna(val):
        return True  # nulls are not type violations
    try:
        float(str(val).strip())
        return True
    except ValueError:
        return False


def _is_date(val) -> bool:
    if pd.isna(val):
        return True
    for fmt in KNOWN_DATE_FORMATS:
        try:
            pd.to_datetime(str(val).strip(), format=fmt)
            return True
        except (ValueError, TypeError):
            continue
    return False


def detect(df: pd.DataFrame) -> dict:
    """
    Identifies rows with type violations in known numeric and date columns.

    Input:  df (DataFrame)
    Output: dict mapping column_name -> {"invalid_count": int, "invalid_rows": DataFrame}
    """
    results = {}

    for col in NUMERIC_COLUMNS:
        if col not in df.columns:
            continue
        mask = ~df[col].apply(_is_numeric)
        results[col] = {
            "invalid_count": int(mask.sum()),
            "invalid_rows":  df[mask],
            "type":          "numeric",
        }
        logger.info(
            "Type check '%s' (numeric): %d invalid values",
            col, mask.sum()
        )

    for col in DATE_COLUMNS:
        if col not in df.columns:
            continue
        mask = ~df[col].apply(_is_date)
        results[col] = {
            "invalid_count": int(mask.sum()),
            "invalid_rows":  df[mask],
            "type":          "date",
        }
        logger.info(
            "Type check '%s' (date): %d invalid values",
            col, mask.sum()
        )

    return results
