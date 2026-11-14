"""
test_db_loader.py
------------------
Unit tests for the database loading module.
Uses an in-memory SQLite database to avoid creating test files on disk.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import pandas as pd
from sqlalchemy import create_engine, text

# Patch the engine to use in-memory SQLite for tests
import src.loading.db_loader as db_loader

@pytest.fixture
def in_memory_engine():
    return create_engine("sqlite:///:memory:")


@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "customer_id":      ["C001", "C002", "C003"],
        "customer_name":    ["Alice", "Bob", "Carol"],
        "purchase_amount":  [100.0, 200.0, 300.0],
        "purchase_date":    ["2023-01-01", "2023-02-01", "2023-03-01"],
    })


def test_load_writes_correct_row_count(sample_df, in_memory_engine, monkeypatch):
    monkeypatch.setattr(db_loader, "get_engine", lambda: in_memory_engine)
    result = db_loader.load(sample_df, "test_table")
    assert result["success"] is True
    assert result["rows_loaded"] == 3


def test_load_replaces_existing_table(sample_df, in_memory_engine, monkeypatch):
    monkeypatch.setattr(db_loader, "get_engine", lambda: in_memory_engine)
    db_loader.load(sample_df, "test_table")
    result = db_loader.load(sample_df, "test_table", if_exists="replace")
    assert result["rows_loaded"] == 3  # not 6


def test_query_table_returns_dataframe(sample_df, in_memory_engine, monkeypatch):
    monkeypatch.setattr(db_loader, "get_engine", lambda: in_memory_engine)
    db_loader.load(sample_df, "query_test")
    df = db_loader.query_table("query_test", limit=10)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 3
