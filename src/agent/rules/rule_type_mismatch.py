"""
rule_type_mismatch.py  —  Self-Healing Agent / Rule 2
-------------------------------------------------------
Triggers when a numeric column contains non-numeric values.
Attempts safe conversion; non-convertible values become NaN.
"""

import pandas as pd
from src.utils.logger import get_logger
from src.utils.config import NUMERIC_COLUMNS

logger = get_logger(__name__)


def evaluate(df: pd.DataFrame, context: dict) -> bool:
    """Returns True if any numeric column contains non-numeric text."""
    for col in NUMERIC_COLUMNS:
        if col not in df.columns:
            continue
        converted = pd.to_numeric(df[col], errors="coerce")
        if converted.isna().sum() > df[col].isna().sum():
            return True
    return False


def apply(df: pd.DataFrame, context: dict) -> tuple[pd.DataFrame, list]:
    """
    Converts numeric columns to float, coercing bad values to NaN.

    Output:
        df      — DataFrame with numeric columns converted
        actions — list of action dicts
    """
    df = df.copy()
    actions = []

    for col in NUMERIC_COLUMNS:
        if col not in df.columns:
            continue

        before_nulls = int(df[col].isna().sum())
        df[col] = pd.to_numeric(df[col], errors="coerce")
        after_nulls  = int(df[col].isna().sum())
        coerced      = after_nulls - before_nulls

        if coerced > 0:
            msg = f"Rule 2 — Type Mismatch: coerced {coerced} non-numeric values in '{col}' to NaN"
            logger.warning(msg)
            actions.append({
                "rule_id":   "RULE-02",
                "trigger":   f"{coerced} non-numeric values in '{col}'",
                "action":    f"pd.to_numeric(errors='coerce') applied to '{col}'",
                "outcome":   "HEALED",
                "column":    col,
            })

    return df, actions
