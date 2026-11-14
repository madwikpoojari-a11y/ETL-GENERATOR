"""
null_handler.py  —  Cleaning Layer
-------------------------------------
Imputes missing values:
  - Numeric columns  → median
  - Categorical/text → mode (most frequent value)
  - Remaining nulls  → "Unknown"
"""

import pandas as pd
from src.utils.logger import get_logger
from src.utils.config import NUMERIC_COLUMNS

logger = get_logger(__name__)


def clean(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Fills null values using appropriate strategies per column type.

    Input:  df (DataFrame)
    Output:
        df     — DataFrame with no nulls in imputable columns
        report — dict: column -> {"strategy": str, "filled_count": int}
    """
    df = df.copy()
    report = {}

    for col in df.columns:
        null_count = int(df[col].isna().sum())
        if null_count == 0:
            continue

        if col in NUMERIC_COLUMNS:
            # Convert to numeric first, then fill with median
            df[col] = pd.to_numeric(df[col], errors="coerce")
            median_val = df[col].median()
            df[col] = df[col].fillna(median_val)
            report[col] = {"strategy": f"median ({median_val:.2f})", "filled_count": null_count}
            logger.debug("Filled %d nulls in '%s' with median %.2f", null_count, col, median_val)

        else:
            # Use mode for categorical; fall back to "Unknown"
            mode_series = df[col].mode()
            if not mode_series.empty:
                fill_val = mode_series.iloc[0]
                strategy = f"mode ({fill_val})"
            else:
                fill_val = "Unknown"
                strategy = "constant (Unknown)"

            df[col] = df[col].fillna(fill_val)
            report[col] = {"strategy": strategy, "filled_count": null_count}
            logger.debug("Filled %d nulls in '%s' with %s", null_count, col, strategy)

    total_filled = sum(v["filled_count"] for v in report.values())
    logger.info("Null handler: filled %d null values across %d columns",
                total_filled, len(report))
    return df, report
