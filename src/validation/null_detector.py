"""
null_detector.py  —  Validation Layer
---------------------------------------
Detects and reports null values across the entire DataFrame.
Returns structured results consumed by the self-healing agent and dashboard.
"""

import pandas as pd
from src.utils.logger import get_logger

logger = get_logger(__name__)


def detect(df: pd.DataFrame) -> dict:
    """
    Counts null values per column and overall.

    Input:  df (DataFrame)
    Output: dict with keys:
                per_column  — dict: column -> {"count": int, "pct": float}
                total_nulls — int
                total_cells — int
                overall_pct — float
    """
    total_cells = df.shape[0] * df.shape[1]
    per_column = {}

    for col in df.columns:
        count = int(df[col].isna().sum())
        pct   = round(count / len(df) * 100, 2)
        per_column[col] = {"count": count, "pct": pct}

    total_nulls = sum(v["count"] for v in per_column.values())
    overall_pct = round(total_nulls / total_cells * 100, 2) if total_cells else 0.0

    logger.info(
        "Null detection: %d null cells out of %d total (%.2f%%)",
        total_nulls, total_cells, overall_pct
    )

    return {
        "per_column":  per_column,
        "total_nulls": total_nulls,
        "total_cells": total_cells,
        "overall_pct": overall_pct,
    }


def get_null_report(df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns a DataFrame report of null counts, suitable for display and export.

    Output columns: column_name, null_count, null_pct, has_nulls
    """
    result = detect(df)
    rows = [
        {
            "column_name": col,
            "null_count":  v["count"],
            "null_pct":    v["pct"],
            "has_nulls":   v["count"] > 0,
        }
        for col, v in result["per_column"].items()
    ]
    return pd.DataFrame(rows)
