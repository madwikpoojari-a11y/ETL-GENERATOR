"""
test_cleaning.py
-----------------
Unit tests for all cleaning modules.
Run with: pytest tests/
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import pandas as pd
import numpy as np

from src.cleaning.string_cleaner    import clean as clean_strings
from src.cleaning.duplicate_handler import clean as remove_duplicates
from src.cleaning.null_handler      import clean as handle_nulls
from src.cleaning.type_coercer      import clean as coerce_types
from src.cleaning.date_normalizer   import clean as normalize_dates


# ── String Cleaner ─────────────────────────────────────────────────────────

def test_string_cleaner_strips_spaces():
    df = pd.DataFrame({"name": ["  Alice  ", "Bob", "  Carol"]})
    cleaned, report = clean_strings(df)
    assert cleaned["name"].tolist() == ["Alice", "Bob", "Carol"]
    assert report["name"] == 2


def test_string_cleaner_no_change_when_clean():
    df = pd.DataFrame({"name": ["Alice", "Bob"]})
    cleaned, report = clean_strings(df)
    assert report == {}


# ── Duplicate Handler ──────────────────────────────────────────────────────

def test_duplicate_handler_removes_dupes():
    df = pd.DataFrame({"a": [1, 2, 2, 3], "b": ["x", "y", "y", "z"]})
    cleaned, report = remove_duplicates(df)
    assert len(cleaned) == 3
    assert report["rows_removed_duplicates"] == 1


def test_duplicate_handler_removes_empty_rows():
    df = pd.DataFrame({
        "a": [1, np.nan, 3],
        "b": ["x", np.nan, "z"]
    })
    cleaned, report = remove_duplicates(df)
    assert len(cleaned) == 2
    assert report["rows_removed_empty"] == 1


# ── Null Handler ───────────────────────────────────────────────────────────

def test_null_handler_fills_numeric_with_median():
    df = pd.DataFrame({"purchase_amount": ["100", "200", None, "300"]})
    cleaned, report = handle_nulls(df)
    assert cleaned["purchase_amount"].isna().sum() == 0
    assert "purchase_amount" in report


def test_null_handler_fills_categorical_with_mode():
    df = pd.DataFrame({"city": ["Delhi", "Delhi", None, "Mumbai"]})
    cleaned, report = handle_nulls(df)
    assert cleaned["city"].isna().sum() == 0
    assert cleaned["city"].iloc[2] == "Delhi"  # mode is Delhi


# ── Type Coercer ───────────────────────────────────────────────────────────

def test_type_coercer_converts_purchase_amount():
    df = pd.DataFrame({"purchase_amount": ["100.50", "N/A", "200.00"]})
    cleaned, report = coerce_types(df)
    assert pd.api.types.is_float_dtype(cleaned["purchase_amount"])
    assert report["purchase_amount"]["coercion_errors"] == 1


# ── Date Normalizer ────────────────────────────────────────────────────────

def test_date_normalizer_handles_multiple_formats():
    df = pd.DataFrame({
        "purchase_date": ["2023-06-15", "15/06/2023", "06-15-2023", "15 Jun 2023"]
    })
    cleaned, report = normalize_dates(df)
    assert all(cleaned["purchase_date"].dropna().str.match(r"^\d{4}-\d{2}-\d{2}$"))


def test_date_normalizer_sets_nan_for_garbage():
    df = pd.DataFrame({"purchase_date": ["not-a-date", "2023-01-01"]})
    cleaned, report = normalize_dates(df)
    assert cleaned["purchase_date"].iloc[0] is None or pd.isna(cleaned["purchase_date"].iloc[0])
    assert cleaned["purchase_date"].iloc[1] == "2023-01-01"
