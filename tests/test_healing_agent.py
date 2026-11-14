"""
test_healing_agent.py
----------------------
Unit tests for self-healing rules and the healing agent orchestrator.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import pandas as pd
import numpy as np

from src.agent.rules.rule_duplicates    import evaluate as eval_dupes,    apply as apply_dupes
from src.agent.rules.rule_high_nulls    import evaluate as eval_nulls,    apply as apply_nulls
from src.agent.rules.rule_type_mismatch import evaluate as eval_types,    apply as apply_types
from src.agent.rules.rule_date_format   import evaluate as eval_dates,    apply as apply_dates
from src.agent.rules.rule_missing_column import evaluate as eval_missing, apply as apply_missing
from src.agent.healing_agent            import heal


def test_rule_duplicates_triggers_above_threshold():
    # 4 out of 5 rows are duplicates — well above 5% threshold
    df = pd.DataFrame({"a": [1, 1, 1, 1, 2], "b": ["x", "x", "x", "x", "y"]})
    assert bool(eval_dupes(df, {})) is True


def test_rule_duplicates_removes_them():
    df = pd.DataFrame({"a": [1, 1, 2], "b": ["x", "x", "y"]})
    healed, actions = apply_dupes(df, {})
    assert len(healed) == 2
    assert actions[0]["outcome"] == "HEALED"


def test_rule_high_nulls_triggers():
    # col 'b' is 100% null — above 20% threshold
    df = pd.DataFrame({"a": [1, 2, 3], "b": [None, None, None]})
    assert eval_nulls(df, {}) is True


def test_rule_high_nulls_imputes():
    df = pd.DataFrame({"city": ["Delhi", None, None, None, "Mumbai"]})
    healed, actions = apply_nulls(df, {})
    assert healed["city"].isna().sum() == 0


def test_rule_type_mismatch_triggers():
    df = pd.DataFrame({"purchase_amount": ["100", "N/A", "200"]})
    assert eval_types(df, {}) is True


def test_rule_type_mismatch_coerces():
    df = pd.DataFrame({"purchase_amount": ["100", "N/A", "200"]})
    healed, actions = apply_types(df, {})
    assert pd.to_numeric(healed["purchase_amount"], errors="coerce").notna().sum() == 2


def test_rule_date_format_triggers_on_non_iso():
    df = pd.DataFrame({"purchase_date": ["15/06/2023", "2023-01-01"]})
    assert eval_dates(df, {}) is True


def test_rule_date_format_normalizes():
    df = pd.DataFrame({"purchase_date": ["15/06/2023", "06-15-2023", "2023-01-01"]})
    healed, actions = apply_dates(df, {})
    valid = healed["purchase_date"].dropna().str.match(r"^\d{4}-\d{2}-\d{2}$")
    assert valid.all()


def test_healing_agent_runs_full_pipeline():
    df = pd.DataFrame({
        "customer_id":      ["C1", "C1", "C3"],
        "customer_name":    ["  Alice  ", "Alice", "Bob"],
        "email":            ["a@b.com", "a@b.com", "bad#email"],
        "phone":            ["9999999999", "9999999999", "8888888888"],
        "city":             ["Delhi", "Delhi", None],
        "state":            ["MH", "MH", "DL"],
        "product_category": ["Electronics", "Electronics", "Books"],
        "purchase_amount":  ["500", "500", "N/A"],
        "purchase_date":    ["2023-01-01", "2023-01-01", "15/06/2023"],
        "payment_method":   ["UPI", "UPI", "Cash on Delivery"],
    })
    healed_df, healing_log = heal(df, {})
    assert isinstance(healed_df, pd.DataFrame)
    assert isinstance(healing_log, list)
    assert len(healed_df) > 0
