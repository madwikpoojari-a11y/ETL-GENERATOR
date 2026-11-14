"""
pipeline_controller.py  —  Application Layer
----------------------------------------------
Orchestrates the full ETL pipeline in strict sequence.
Called by the Streamlit UI. Returns a results dict that
the UI renders — the controller never touches Streamlit directly.

Pipeline sequence:
  1. Extract      — read CSV
  2. Schema       — infer types, build schema report
  3. Validate     — nulls, duplicates, type issues, format issues
  4. Score Before — quality score on raw data
  5. Heal         — self-healing agent
  6. Clean        — string, duplicate, null, type, date cleaning
  7. Transform    — column standardization
  8. Score After  — quality score on clean data
  9. Load         — write to SQLite
  10. Report      — save all report files, build summary
"""

import time
import os
import pandas as pd
from datetime import datetime
from src.utils.logger import get_logger

from src.ingestion.csv_reader          import read_csv, get_metadata
from src.validation.schema_inferrer    import infer_schema, get_schema_report
from src.validation.null_detector      import detect as detect_nulls
from src.validation.duplicate_detector import detect as detect_duplicates
from src.validation.type_validator     import detect as detect_types
from src.validation.format_validator   import validate_emails, validate_dates
from src.reporting.quality_scorer      import calculate as score
from src.agent.healing_agent           import heal, get_healing_summary
from src.cleaning.string_cleaner       import clean as clean_strings
from src.cleaning.duplicate_handler    import clean as remove_duplicates
from src.cleaning.null_handler         import clean as handle_nulls
from src.cleaning.type_coercer         import clean as coerce_types
from src.cleaning.date_normalizer      import clean as normalize_dates
from src.transformation.column_standardizer import standardize
from src.loading.db_loader             import load
from src.reporting.etl_reporter        import (
    build_summary, save_schema_report, save_cleaning_report,
    save_healing_report, save_etl_summary
)

logger = get_logger(__name__)


def run_pipeline(source, table_name: str = "cleaned_data") -> dict:
    """
    Runs the complete ETL pipeline from CSV source to SQLite.

    Input:
        source     — file path string or Streamlit UploadedFile
        table_name — target SQLite table name

    Output:
        results dict with keys:
            status           ("success" | "failed")
            metadata         (dict)
            schema_report    (DataFrame)
            null_report      (dict)
            duplicate_report (dict)
            type_report      (dict)
            email_report     (dict)
            date_report      (dict)
            score_before     (dict)
            score_after      (dict)
            healing_log      (list)
            healing_summary  (DataFrame)
            cleaning_actions (list)
            clean_df         (DataFrame)
            load_result      (dict)
            summary          (dict)
            error            (str or None)
    """
    start_time = time.time()
    cleaning_actions = []
    logger.info("=" * 60)
    logger.info("Pipeline started — table: '%s'", table_name)
    logger.info("=" * 60)

    try:
        # ── Step 1: Extract ───────────────────────────────────────────────
        logger.info("STEP 1: Extract")
        metadata = get_metadata(source)
        # Re-read for the DataFrame (get_metadata internally reads too,
        # but we need the df object explicitly)
        if isinstance(source, str):
            raw_df = read_csv(source)
        else:
            source.seek(0)
            raw_df = read_csv(source)

        rows_input = len(raw_df)

        # ── Step 2: Schema Inference ──────────────────────────────────────
        logger.info("STEP 2: Schema Inference")
        schema_report = get_schema_report(raw_df)

        # ── Step 3: Validation ────────────────────────────────────────────
        logger.info("STEP 3: Validation")
        null_report      = detect_nulls(raw_df)
        duplicate_report = detect_duplicates(raw_df)
        type_report      = detect_types(raw_df)
        email_report     = validate_emails(raw_df)
        date_report      = validate_dates(raw_df)

        validation_results = {
            "nulls":      null_report,
            "duplicates": duplicate_report,
            "types":      type_report,
            "emails":     email_report,
            "dates":      date_report,
        }

        # ── Step 4: Quality Score — BEFORE ────────────────────────────────
        logger.info("STEP 4: Quality Score (before)")
        score_before = score(raw_df)

        # ── Step 5: Self-Healing Agent ────────────────────────────────────
        logger.info("STEP 5: Self-Healing Agent")
        healed_df, healing_log = heal(raw_df, validation_results)

        # ── Step 6: Cleaning ──────────────────────────────────────────────
        logger.info("STEP 6: Cleaning")

        df, report = clean_strings(healed_df)
        if report:
            cleaning_actions.append({"step": "string_cleaner", "detail": str(report)})

        df, report = remove_duplicates(df)
        cleaning_actions.append({"step": "duplicate_handler", "detail": str(report)})

        df, report = coerce_types(df)
        if report:
            cleaning_actions.append({"step": "type_coercer", "detail": str(report)})

        df, report = normalize_dates(df)
        if report:
            cleaning_actions.append({"step": "date_normalizer", "detail": str(report)})

        df, report = handle_nulls(df)
        if report:
            cleaning_actions.append({"step": "null_handler", "detail": str(report)})

        # ── Step 7: Transform ─────────────────────────────────────────────
        logger.info("STEP 7: Transform")
        df, rename_map = standardize(df)
        if rename_map:
            cleaning_actions.append({"step": "column_standardizer", "detail": str(rename_map)})

        clean_df = df

        # ── Step 8: Quality Score — AFTER ─────────────────────────────────
        logger.info("STEP 8: Quality Score (after)")
        score_after = score(clean_df)

        # ── Step 9: Load ──────────────────────────────────────────────────
        logger.info("STEP 9: Load → SQLite table '%s'", table_name)
        load_result = load(clean_df, table_name)

        # ── Step 10: Report ───────────────────────────────────────────────
        logger.info("STEP 10: Reporting")
        duration = time.time() - start_time

        summary = build_summary(
            file_name           = metadata["file_name"],
            table_name          = table_name,
            rows_input          = rows_input,
            rows_after_cleaning = len(clean_df),
            rows_loaded         = load_result.get("rows_loaded", 0),
            score_before        = score_before,
            score_after         = score_after,
            healing_log         = healing_log,
            load_result         = load_result,
            duration_seconds    = duration,
        )

        save_schema_report(schema_report)
        save_cleaning_report(cleaning_actions)
        save_healing_report(healing_log)
        save_etl_summary(summary)

        logger.info(
            "Pipeline COMPLETE in %.2fs | Score: %.1f → %.1f | Rows: %d → %d loaded",
            duration,
            score_before["total_score"],
            score_after["total_score"],
            rows_input,
            load_result.get("rows_loaded", 0),
        )

        return {
            "status":           "success",
            "metadata":         metadata,
            "schema_report":    schema_report,
            "null_report":      null_report,
            "duplicate_report": duplicate_report,
            "type_report":      type_report,
            "email_report":     email_report,
            "date_report":      date_report,
            "score_before":     score_before,
            "score_after":      score_after,
            "healing_log":      healing_log,
            "healing_summary":  get_healing_summary(healing_log),
            "cleaning_actions": cleaning_actions,
            "clean_df":         clean_df,
            "load_result":      load_result,
            "summary":          summary,
            "error":            None,
        }

    except Exception as e:
        duration = time.time() - start_time
        logger.error("Pipeline FAILED after %.2fs: %s", duration, str(e), exc_info=True)
        return {
            "status": "failed",
            "error":  str(e),
            "summary": {"duration_seconds": round(duration, 2)},
        }
