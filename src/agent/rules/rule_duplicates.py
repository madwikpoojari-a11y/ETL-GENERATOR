"""
rule_duplicates.py  —  Self-Healing Agent / Rule 4
----------------------------------------------------
Triggers when duplicate row percentage exceeds the configured threshold.
Removes all duplicates, keeping the first occurrence.
"""

import pandas as pd
from src.utils.logger import get_logger
from src.utils.config import DUPLICATE_THRESHOLD_PCT

logger = get_logger(__name__)


def evaluate(df: pd.DataFrame, context: dict) -> bool:
    """Returns True if duplicate % > DUPLICATE_THRESHOLD_PCT."""
    dupe_pct = df.duplicated().sum() / len(df) * 100
    return dupe_pct > DUPLICATE_THRESHOLD_PCT


def apply(df: pd.DataFrame, context: dict) -> tuple[pd.DataFrame, list]:
    """
    Removes duplicate rows.

    Output:
        df      — deduplicated DataFrame
        actions — list of action dicts
    """
    df = df.copy()
    before = len(df)
    dupe_count = int(df.duplicated().sum())
    dupe_pct   = round(dupe_count / before * 100, 2)

    df = df.drop_duplicates(keep="first").reset_index(drop=True)
    after = len(df)

    msg = (f"Rule 4 — Duplicates: removed {dupe_count} duplicate rows "
           f"({dupe_pct}%). Rows: {before} → {after}.")
    logger.warning(msg)

    actions = [{
        "rule_id":   "RULE-04",
        "trigger":   f"Duplicate rate {dupe_pct}% exceeded threshold {DUPLICATE_THRESHOLD_PCT}%",
        "action":    f"drop_duplicates(keep='first') — removed {dupe_count} rows",
        "outcome":   "HEALED",
        "column":    "ALL",
    }]

    return df, actions
