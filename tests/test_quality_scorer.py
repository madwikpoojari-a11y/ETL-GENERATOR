"""
test_quality_scorer.py
-----------------------
Unit tests for the data quality scoring module.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from src.reporting.quality_scorer import calculate as score


def test_perfect_score_on_clean_data():
    df = pd.DataFrame({
        "customer_id":      ["C001", "C002"],
        "customer_name":    ["Alice", "Bob"],
        "email":            ["alice@example.com", "bob@example.com"],
        "phone":            ["9999999999", "8888888888"],
        "city":             ["Delhi", "Mumbai"],
        "state":            ["Delhi", "Maharashtra"],
        "product_category": ["Electronics", "Books"],
        "purchase_amount":  [500.0, 1500.0],
        "purchase_date":    ["2023-01-01", "2023-06-15"],
        "payment_method":   ["UPI", "Credit Card"],
    })
    result = score(df)
    assert result["total_score"] > 90
    assert result["completeness"] == 100.0
    assert result["uniqueness"] == 100.0


def test_low_completeness_score():
    df = pd.DataFrame({
        "purchase_amount": [None, None, None, None, 100.0],
        "purchase_date":   [None, None, None, None, "2023-01-01"],
    })
    result = score(df)
    assert result["completeness"] < 50


def test_low_uniqueness_score():
    row = {"customer_id": "C1", "email": "a@b.com", "purchase_amount": 100.0}
    df = pd.DataFrame([row] * 10)
    result = score(df)
    assert result["uniqueness"] < 20


def test_score_improves_after_cleaning():
    dirty = pd.DataFrame({
        "email":           ["bad#email", "also#bad", "good@test.com"],
        "purchase_amount": ["N/A", "100", "200"],
        "purchase_date":   ["not-a-date", "2023-01-01", "2022-06-15"],
    })
    clean = pd.DataFrame({
        "email":           ["good@test.com", "other@test.com", "third@test.com"],
        "purchase_amount": [100.0, 200.0, 300.0],
        "purchase_date":   ["2023-01-01", "2022-06-15", "2021-12-31"],
    })
    dirty_score = score(dirty)
    clean_score = score(clean)
    assert clean_score["total_score"] > dirty_score["total_score"]
