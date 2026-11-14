"""
duplicate_detector.py  —  Validation Layer
--------------------------------------------
Detects exact duplicate rows in the DataFrame.
"""

import pandas as pd
from src.utils.logger import get_logger

logger = get_logger(__name__)


def detect(df: pd.DataFrame) -> dict:
    """
    Finds exact duplicate rows (all columns match).

    Input:  df (DataFrame)
    Output: dict with keys:
                duplicate_count — int
                duplicate_pct   — float
                duplicate_rows  — DataFrame (the actual duplicate rows)
    """
    dupe_mask  = df.duplicated(keep="first")
    dupe_count = int(dupe_mask.sum())
    dupe_pct   = round(dupe_count / len(df) * 100, 2) if len(df) else 0.0

    logger.info(
        "Duplicate detection: %d duplicate rows (%.2f%%)",
        dupe_count, dupe_pct
    )

    return {
        "duplicate_count": dupe_count,
        "duplicate_pct":   dupe_pct,
        "duplicate_rows":  df[dupe_mask],
    }
