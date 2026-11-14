"""
string_cleaner.py  —  Cleaning Layer
--------------------------------------
Strips leading/trailing whitespace from all string-like columns.
Works with both object dtype and pandas StringDtype (pandas 2+).
"""

import pandas as pd
from src.utils.logger import get_logger

logger = get_logger(__name__)


def _is_string_col(series: pd.Series) -> bool:
    """Returns True for object, string, or StringDtype columns."""
    return (
        series.dtype == object
        or pd.api.types.is_string_dtype(series)
        or hasattr(series, "str")
    )


def clean(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Strips whitespace from every string column.

    Input:  df (DataFrame)
    Output:
        df     — cleaned DataFrame
        report — dict: column -> cells_changed (int)
    """
    df = df.copy()
    report = {}

    for col in df.columns:
        if not _is_string_col(df[col]):
            continue
        try:
            original = df[col].copy()
            stripped = df[col].str.strip()
            df[col]  = stripped
            # Count cells that actually changed (ignoring nulls)
            mask    = df[col].notna() & original.notna()
            changed = int((original[mask] != df[col][mask]).sum())
            if changed > 0:
                report[col] = changed
                logger.debug("Stripped whitespace in '%s': %d cells", col, changed)
        except Exception:
            pass  # Non-string column slipped through — skip safely

    total = sum(report.values())
    logger.info("String cleaning complete: %d cells stripped across %d columns",
                total, len(report))
    return df, report
