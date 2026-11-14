"""
test_validation.py
-------------------
Unit tests for all validation modules.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import pandas as pd
import numpy as np

from src.validation.null_detector      import detect as detect_nulls
from src.validation.duplicate_detector import detect as detect_dupes
from src.validation.format_validator   import validate_emails, validate_dates
from src.validation.schema_inferrer    import infer_schema
from src.validation.type_validator     import detect as detect_types


def test_null_detector_counts_correctly():
    df = pd.DataFrame({"a": [1, None, 3], "b": [None, None, "x"]})
    result = detect_nulls(df)
    assert result["per_column"]["a"]["count"] == 1
    assert result["per_column"]["b"]["count"] == 2
    assert result["total_nulls"] == 3


def test_duplicate_detector_finds_exact_dupes():
    df = pd.DataFrame({"a": [1, 2, 2], "b": ["x", "y", "y"]})
    result = detect_dupes(df)
    assert result["duplicate_count"] == 1


def test_email_validator_flags_bad_emails():
    df = pd.DataFrame({"email": [
        "valid@example.com", "bademail#domain.com", "also@bad", "good@test.org"
    ]})
    result = validate_emails(df)
    assert result["invalid_count"] == 2


def test_email_validator_ignores_nulls():
    df = pd.DataFrame({"email": ["valid@example.com", None, "bad#email"]})
    result = validate_emails(df)
    assert result["invalid_count"] == 1


def test_date_validator_flags_garbage():
    df = pd.DataFrame({"purchase_date": ["2023-01-15", "not-a-date", "TBD", "2022-12-31"]})
    result = validate_dates(df)
    assert result["invalid_count"] >= 2


def test_schema_inferrer_detects_numeric():
    df = pd.DataFrame({"purchase_amount": ["100.50", "200", "350.00"]})
    schema = infer_schema(df)
    assert schema["purchase_amount"] == "numeric"


def test_schema_inferrer_detects_date():
    df = pd.DataFrame({"purchase_date": ["2023-01-01", "2022-06-15", "2021-12-31"]})
    schema = infer_schema(df)
    assert schema["purchase_date"] == "date"


def test_schema_inferrer_detects_string():
    df = pd.DataFrame({"city": ["Delhi", "Mumbai", "Pune"]})
    schema = infer_schema(df)
    assert schema["city"] == "string"
