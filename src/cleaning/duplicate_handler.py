"""
duplicate_handler.py  —  Cleaning Layer
-----------------------------------------
Removes exact duplicate rows, keeping the first occurrence.
Also drops rows that are entirely null (empty records).
"""

import pandas as pd
from src.utils.logger import get_logger

logger = get_logger(__name__)


def clean(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Removes duplicate rows and fully-empty rows.

    Input:  df (DataFrame)
    Output:
        df     — deduplicated DataFrame
        report — dict with rows_removed_duplicates, rows_removed_empty
    """
    df = df.copy()
    original_len = len(df)

    # Drop fully empty rows first
    df_no_empty = df.dropna(how="all")
    empty_removed = original_len - len(df_no_empty)

    # Drop duplicate rows
    df_deduped = df_no_empty.drop_duplicates(keep="first")
    dupes_removed = len(df_no_empty) - len(df_deduped)

    df_deduped = df_deduped.reset_index(drop=True)

    report = {
        "rows_removed_duplicates": dupes_removed,
        "rows_removed_empty":      empty_removed,
        "rows_before":             original_len,
        "rows_after":              len(df_deduped),
    }

    logger.info(
        "Duplicate handler: removed %d duplicates + %d empty rows. %d -> %d rows.",
        dupes_removed, empty_removed, original_len, len(df_deduped)
    )

    return df_deduped, report
