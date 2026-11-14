"""
schema_inferrer.py  —  Validation Layer
-----------------------------------------
Infers the data type of each column by attempting type conversions
on the actual values. Does NOT modify the DataFrame.

Returns a schema dict used by the cleaning modules and the self-healing agent.
"""

import pandas as pd
from src.utils.logger import get_logger
from src.utils.config import KNOWN_DATE_FORMATS

logger = get_logger(__name__)


def _try_numeric(series: pd.Series) -> bool:
    """Returns True if >80% of non-null values convert to float."""
    non_null = series.dropna()
    if len(non_null) == 0:
        return False
    converted = pd.to_numeric(non_null, errors="coerce")
    return (converted.notna().sum() / len(non_null)) >= 0.80


def _try_date(series: pd.Series) -> bool:
    """Returns True if >80% of non-null values parse as a known date format."""
    non_null = series.dropna().astype(str)
    if len(non_null) == 0:
        return False
    for fmt in KNOWN_DATE_FORMATS:
        try:
            parsed = pd.to_datetime(non_null, format=fmt, errors="coerce")
            if (parsed.notna().sum() / len(non_null)) >= 0.80:
                return True
        except Exception:
            continue
    # Try pandas generic parser as fallback
    try:
        parsed = pd.to_datetime(non_null, errors="coerce", format="mixed")
        return (parsed.notna().sum() / len(non_null)) >= 0.80
    except Exception:
        return False


def _try_boolean(series: pd.Series) -> bool:
    """Returns True if the column's unique non-null values are a boolean set."""
    bool_sets = [
        {"true", "false"},
        {"yes", "no"},
        {"1", "0"},
        {"y", "n"},
    ]
    non_null = series.dropna().astype(str).str.strip().str.lower().unique()
    unique_set = set(non_null)
    return any(unique_set <= bs for bs in bool_sets)


def infer_schema(df: pd.DataFrame) -> dict:
    """
    Infers the type of each column.

    Input:  df (DataFrame) — raw data, all columns as strings
    Output: dict mapping column_name -> inferred type string
            Types: "numeric", "date", "boolean", "string"

    Example output:
        {
            "customer_id":     "string",
            "purchase_amount": "numeric",
            "purchase_date":   "date",
            ...
        }
    """
    schema = {}
    for col in df.columns:
        series = df[col]
        if _try_boolean(series):
            schema[col] = "boolean"
        elif _try_numeric(series):
            schema[col] = "numeric"
        elif _try_date(series):
            schema[col] = "date"
        else:
            schema[col] = "string"
        logger.debug("Column '%s' inferred as: %s", col, schema[col])

    logger.info("Schema inference complete: %d columns typed", len(schema))
    return schema


def get_schema_report(df: pd.DataFrame) -> pd.DataFrame:
    """
    Builds a human-readable schema report DataFrame.

    Input:  df (DataFrame)
    Output: DataFrame with columns:
                column_name, inferred_type, null_count,
                null_pct, unique_count, sample_values
    """
    schema = infer_schema(df)
    rows = []
    for col in df.columns:
        null_count = int(df[col].isna().sum())
        null_pct   = round(null_count / len(df) * 100, 2)
        unique_count = int(df[col].nunique(dropna=True))
        samples = df[col].dropna().astype(str).unique()[:3].tolist()

        rows.append({
            "column_name":   col,
            "inferred_type": schema[col],
            "null_count":    null_count,
            "null_pct":      null_pct,
            "unique_count":  unique_count,
            "sample_values": " | ".join(samples),
        })

    report_df = pd.DataFrame(rows)
    logger.info("Schema report generated for %d columns", len(rows))
    return report_df
