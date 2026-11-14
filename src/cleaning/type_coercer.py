"""
type_coercer.py  —  Cleaning Layer
-------------------------------------
Converts columns to their correct Python/pandas types after cleaning.
Non-convertible values are replaced with NaN (then caught by null_handler).
"""

import pandas as pd
from src.utils.logger import get_logger
from src.utils.config import NUMERIC_COLUMNS, DATE_COLUMNS

logger = get_logger(__name__)


def clean(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Coerces numeric and date columns to their proper types.

    Input:  df (DataFrame)
    Output:
        df     — DataFrame with correct dtypes
        report — dict: column -> {"from": str, "to": str, "coercion_errors": int}
    """
    df = df.copy()
    report = {}

    for col in NUMERIC_COLUMNS:
        if col not in df.columns:
            continue
        original = df[col].copy()
        df[col] = pd.to_numeric(df[col], errors="coerce")
        errors  = int(df[col].isna().sum() - original.isna().sum())
        errors  = max(errors, 0)
        report[col] = {"from": "string", "to": "float64", "coercion_errors": errors}
        logger.info("Coerced '%s' to numeric: %d coercion errors", col, errors)

    for col in DATE_COLUMNS:
        if col not in df.columns:
            continue
        original = df[col].copy()
        df[col] = pd.to_datetime(df[col], errors="coerce")
        errors  = int(df[col].isna().sum() - pd.to_datetime(original, errors="coerce").isna().sum())
        errors  = max(errors, 0)
        report[col] = {"from": "string", "to": "datetime64", "coercion_errors": errors}
        logger.info("Coerced '%s' to datetime: %d coercion errors", col, errors)

    return df, report
