"""
rule_missing_column.py  —  Self-Healing Agent / Rule 1
--------------------------------------------------------
Triggers when an expected column is absent from the DataFrame.
Attempts to find the closest matching column using fuzzy string matching
and renames it. If no close match exists, logs a warning.
"""

import pandas as pd
from src.utils.logger import get_logger
from src.utils.config import EXPECTED_COLUMNS

logger = get_logger(__name__)

# Minimum similarity score (0-100) to accept a fuzzy match
FUZZY_THRESHOLD = 70


def _fuzzy_match(target: str, candidates: list) -> tuple[str | None, int]:
    """
    Finds the closest match for `target` in `candidates` using
    Levenshtein ratio from thefuzz library.

    Returns (best_match, score) or (None, 0) if no match exceeds threshold.
    """
    try:
        from thefuzz import fuzz
        best_match = None
        best_score = 0
        for candidate in candidates:
            score = fuzz.ratio(target.lower(), candidate.lower())
            if score > best_score:
                best_score = score
                best_match = candidate
        if best_score >= FUZZY_THRESHOLD:
            return best_match, best_score
        return None, best_score
    except ImportError:
        # thefuzz not installed — fall back to simple substring check
        for candidate in candidates:
            if target.lower() in candidate.lower() or candidate.lower() in target.lower():
                return candidate, 80
        return None, 0


def evaluate(df: pd.DataFrame, context: dict) -> bool:
    """
    Returns True if any expected column is missing from the DataFrame.
    """
    missing = [col for col in EXPECTED_COLUMNS if col not in df.columns]
    return len(missing) > 0


def apply(df: pd.DataFrame, context: dict) -> tuple[pd.DataFrame, list]:
    """
    For each missing expected column, searches for a fuzzy match in the
    actual columns and renames it.

    Input:
        df      — DataFrame
        context — dict (unused here, reserved for future context passing)

    Output:
        df      — DataFrame with renamed columns where matches were found
        actions — list of action dicts logged by the healing agent
    """
    df = df.copy()
    actions = []
    actual_columns = list(df.columns)

    for expected in EXPECTED_COLUMNS:
        if expected in df.columns:
            continue

        match, score = _fuzzy_match(expected, actual_columns)

        if match:
            df = df.rename(columns={match: expected})
            actual_columns = list(df.columns)
            msg = (f"Rule 1 — Missing Column: '{match}' → renamed to "
                   f"'{expected}' (similarity {score}%)")
            logger.warning(msg)
            actions.append({
                "rule_id":   "RULE-01",
                "trigger":   f"Column '{expected}' missing; found '{match}' (score {score})",
                "action":    f"Renamed '{match}' to '{expected}'",
                "outcome":   "HEALED",
                "column":    expected,
            })
        else:
            msg = (f"Rule 1 — Missing Column: '{expected}' not found and "
                   f"no fuzzy match above threshold {FUZZY_THRESHOLD}.")
            logger.warning(msg)
            actions.append({
                "rule_id":   "RULE-01",
                "trigger":   f"Column '{expected}' missing; no match found",
                "action":    "No action — column absent",
                "outcome":   "UNRESOLVED",
                "column":    expected,
            })

    return df, actions
