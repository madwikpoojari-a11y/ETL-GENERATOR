"""
etl_reporter.py  —  Reporting Layer
--------------------------------------
Assembles the final ETL run summary and saves all reports to disk.
"""

import os
import json
import pandas as pd
from datetime import datetime
from src.utils.logger import get_logger
from src.utils.config import REPORTS_DIR

logger = get_logger(__name__)

os.makedirs(REPORTS_DIR, exist_ok=True)


def save_schema_report(schema_df: pd.DataFrame) -> str:
    """Saves schema report DataFrame to CSV. Returns file path."""
    path = os.path.join(REPORTS_DIR, "schema_report.csv")
    schema_df.to_csv(path, index=False)
    logger.info("Schema report saved: %s", path)
    return path


def save_cleaning_report(cleaning_actions: list) -> str:
    """Saves cleaning actions list to CSV. Returns file path."""
    path = os.path.join(REPORTS_DIR, "cleaning_report.csv")
    df = pd.DataFrame(cleaning_actions) if cleaning_actions else pd.DataFrame()
    df.to_csv(path, index=False)
    logger.info("Cleaning report saved: %s", path)
    return path


def save_healing_report(healing_log: list) -> str:
    """Saves healing log to CSV. Returns file path."""
    path = os.path.join(REPORTS_DIR, "healing_report.csv")
    df = pd.DataFrame(healing_log) if healing_log else pd.DataFrame()
    df.to_csv(path, index=False)
    logger.info("Healing report saved: %s", path)
    return path


def save_etl_summary(summary: dict) -> str:
    """Saves the ETL summary dict to a JSON file. Returns file path."""
    path = os.path.join(REPORTS_DIR, "etl_summary.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, default=str)
    logger.info("ETL summary saved: %s", path)
    return path


def build_summary(
    file_name: str,
    table_name: str,
    rows_input: int,
    rows_after_cleaning: int,
    rows_loaded: int,
    score_before: dict,
    score_after: dict,
    healing_log: list,
    load_result: dict,
    duration_seconds: float,
) -> dict:
    """
    Builds the master ETL summary dict shown on the dashboard and saved to disk.
    """
    return {
        "run_timestamp":       datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "source_file":         file_name,
        "target_table":        table_name,
        "rows_input":          rows_input,
        "rows_after_cleaning": rows_after_cleaning,
        "rows_loaded":         rows_loaded,
        "rows_removed":        rows_input - rows_after_cleaning,
        "quality_score_before": score_before.get("total_score", 0),
        "quality_score_after":  score_after.get("total_score", 0),
        "score_improvement":    round(
            score_after.get("total_score", 0) - score_before.get("total_score", 0), 2
        ),
        "healing_rules_triggered": len(healing_log),
        "load_success":        load_result.get("success", False),
        "load_attempts":       load_result.get("attempts", 0),
        "duration_seconds":    round(duration_seconds, 2),
        "score_before_detail": score_before,
        "score_after_detail":  score_after,
    }
