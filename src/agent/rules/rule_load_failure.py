"""
rule_load_failure.py  —  Self-Healing Agent / Rule 6
------------------------------------------------------
This rule is invoked by db_loader.py directly (not by the healing agent loop)
because it wraps the load operation itself.

It is kept here as a named rule so it appears in the healing log and dashboard
like every other rule, maintaining a consistent audit trail.
"""

from src.utils.logger import get_logger

logger = get_logger(__name__)


def log_retry(attempt: int, max_retries: int, error: str):
    """
    Logs a retry attempt. Called by db_loader on each failed attempt.

    Input:
        attempt     — current attempt number (1-based)
        max_retries — maximum allowed attempts
        error       — error message string
    """
    logger.warning(
        "Rule 6 — Load Failure: attempt %d/%d failed. Error: %s",
        attempt, max_retries, error
    )


def log_fatal(max_retries: int, error: str):
    """
    Logs a fatal load failure after all retries are exhausted.
    """
    logger.error(
        "Rule 6 — Load Failure: FATAL. All %d attempts failed. Root cause: %s",
        max_retries, error
    )


def build_action(attempts: int, success: bool, error: str | None) -> dict:
    """
    Returns a standardized action dict for the healing log.
    """
    return {
        "rule_id":   "RULE-06",
        "trigger":   "Database load failure",
        "action":    f"Retried load up to {attempts} times",
        "outcome":   "HEALED" if success else "FATAL",
        "column":    "N/A",
        "error":     error or "",
    }
