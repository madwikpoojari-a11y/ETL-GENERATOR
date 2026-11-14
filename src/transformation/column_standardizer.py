"""
column_standardizer.py  —  Transformation Layer
--------------------------------------------------
Standardizes column names to snake_case (lowercase, spaces → underscores).
Also trims whitespace from column names themselves.
"""

import re
import pandas as pd
from src.utils.logger import get_logger

logger = get_logger(__name__)


def _to_snake_case(name: str) -> str:
    """Converts any column name string to clean snake_case."""
    name = name.strip()
    name = re.sub(r"[\s\-]+", "_", name)       # spaces/hyphens → underscore
    name = re.sub(r"[^a-zA-Z0-9_]", "", name)  # remove special chars
    name = re.sub(r"_+", "_", name)             # collapse multiple underscores
    return name.lower().strip("_")


def standardize(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Renames all columns to snake_case.

    Input:  df (DataFrame)
    Output:
        df     — DataFrame with renamed columns
        report — dict: old_name -> new_name (only for columns that changed)
    """
    df = df.copy()
    rename_map = {}

    for col in df.columns:
        new_col = _to_snake_case(col)
        if new_col != col:
            rename_map[col] = new_col

    if rename_map:
        df = df.rename(columns=rename_map)
        logger.info("Column standardizer renamed %d columns: %s", len(rename_map), rename_map)
    else:
        logger.info("Column standardizer: all column names already clean")

    return df, rename_map
