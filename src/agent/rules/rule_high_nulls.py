"""
rule_high_nulls.py  —  Self-Healing Agent / Rule 3
----------------------------------------------------
Triggers when any column's null percentage exceeds the configured threshold.
Applies imputation: median for numeric, mode for categorical.
"""

import pandas as pd
from src.utils.logger import get_logger
from src.utils.config import NULL_THRESHOLD_PCT, NUMERIC_COLUMNS

logger = get_logger(__name__)


def evaluate(df: pd.DataFrame, context: dict) -> bool:
    """Returns True if any column has null % > NULL_THRESHOLD_PCT."""
    for col in df.columns:
        pct = df[col].isna().sum() / len(df) * 100
        if pct > NULL_THRESHOLD_PCT:
            return True
    return False


def apply(df: pd.DataFrame, context: dict) -> tuple[pd.DataFrame, list]:
    """
    Imputes columns that exceed the null threshold.

    Output:
        df      — DataFrame with high-null columns imputed
        actions — list of action dicts
    """
    df = df.copy()
    actions = []

    for col in df.columns:
        null_count = int(df[col].isna().sum())
        pct = null_count / len(df) * 100

        if pct <= NULL_THRESHOLD_PCT:
            continue

        if col in NUMERIC_COLUMNS:
            numeric_col = pd.to_numeric(df[col], errors="coerce")
            fill_val = numeric_col.median()
            df[col] = numeric_col.fillna(fill_val)
            strategy = f"median ({fill_val:.2f})"
        else:
            mode_series = df[col].mode()
            fill_val = mode_series.iloc[0] if not mode_series.empty else "Unknown"
            df[col] = df[col].fillna(fill_val)
            strategy = f"mode ({fill_val})"

        msg = (f"Rule 3 — High Nulls: '{col}' had {pct:.1f}% nulls "
               f"(threshold {NULL_THRESHOLD_PCT}%). Applied {strategy}.")
        logger.warning(msg)
        actions.append({
            "rule_id":   "RULE-03",
            "trigger":   f"'{col}' null rate {pct:.1f}% > threshold {NULL_THRESHOLD_PCT}%",
            "action":    f"Imputed {null_count} values with {strategy}",
            "outcome":   "HEALED",
            "column":    col,
        })

    return df, actions
