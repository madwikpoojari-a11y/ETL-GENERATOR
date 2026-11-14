"""
quality_scorer.py  —  Reporting Layer
----------------------------------------
Calculates a data quality score out of 100 across five dimensions:
  Completeness (25): how many cells are non-null
  Uniqueness   (20): how many rows are non-duplicate
  Validity     (20): how many emails and dates are valid
  Consistency  (20): how many numeric columns have correct types
  Accuracy     (15): how many purchase amounts are in a sensible range

Returns both the total score and a per-dimension breakdown.
"""

import re
import pandas as pd
from src.utils.logger import get_logger
from src.utils.config import QUALITY_WEIGHTS, NUMERIC_COLUMNS, DATE_COLUMNS

logger = get_logger(__name__)

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _completeness(df: pd.DataFrame) -> float:
    """% of non-null cells."""
    total = df.shape[0] * df.shape[1]
    if total == 0:
        return 100.0
    non_null = df.notna().sum().sum()
    return round(non_null / total * 100, 2)


def _uniqueness(df: pd.DataFrame) -> float:
    """% of non-duplicate rows."""
    if len(df) == 0:
        return 100.0
    unique_rows = len(df) - df.duplicated().sum()
    return round(unique_rows / len(df) * 100, 2)


def _validity(df: pd.DataFrame) -> float:
    """% of valid emails + parseable dates (averaged)."""
    scores = []

    if "email" in df.columns:
        non_null = df["email"].dropna().astype(str)
        if len(non_null) > 0:
            valid = non_null.apply(lambda x: bool(EMAIL_PATTERN.match(x.strip()))).sum()
            scores.append(round(valid / len(non_null) * 100, 2))

    for col in DATE_COLUMNS:
        if col in df.columns:
            non_null = df[col].dropna().astype(str)
            if len(non_null) > 0:
                parsed = pd.to_datetime(non_null, errors="coerce", format="mixed")
                valid = parsed.notna().sum()
                scores.append(round(valid / len(non_null) * 100, 2))

    return round(sum(scores) / len(scores), 2) if scores else 100.0


def _consistency(df: pd.DataFrame) -> float:
    """% of numeric column values that are actually numeric."""
    scores = []
    for col in NUMERIC_COLUMNS:
        if col not in df.columns:
            continue
        non_null = df[col].dropna()
        if len(non_null) == 0:
            continue
        converted = pd.to_numeric(non_null, errors="coerce")
        valid = converted.notna().sum()
        scores.append(round(valid / len(non_null) * 100, 2))

    return round(sum(scores) / len(scores), 2) if scores else 100.0


def _accuracy(df: pd.DataFrame) -> float:
    """% of purchase_amount values in plausible range (0 < amount < 1,000,000)."""
    col = "purchase_amount"
    if col not in df.columns:
        return 100.0
    numeric = pd.to_numeric(df[col], errors="coerce").dropna()
    if len(numeric) == 0:
        return 100.0
    in_range = ((numeric > 0) & (numeric < 1_000_000)).sum()
    return round(in_range / len(numeric) * 100, 2)


def calculate(df: pd.DataFrame) -> dict:
    """
    Calculates the full quality score.

    Input:  df (DataFrame)
    Output: dict with keys:
                total_score     (float, 0–100)
                completeness    (float)
                uniqueness      (float)
                validity        (float)
                consistency     (float)
                accuracy        (float)
    """
    dimensions = {
        "completeness": _completeness(df),
        "uniqueness":   _uniqueness(df),
        "validity":     _validity(df),
        "consistency":  _consistency(df),
        "accuracy":     _accuracy(df),
    }

    total = sum(
        dimensions[dim] * QUALITY_WEIGHTS[dim] / 100
        for dim in QUALITY_WEIGHTS
    )

    result = {"total_score": round(total, 2), **dimensions}
    logger.info("Quality score calculated: %.2f/100  %s", total, dimensions)
    return result
