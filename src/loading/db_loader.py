"""
db_loader.py  —  Loading Layer
--------------------------------
Loads a cleaned DataFrame into SQLite using SQLAlchemy.
Implements retry logic (Rule 6 of the self-healing agent).

The table is created if it does not exist; existing data is replaced
each pipeline run (use if_exists="append" if incremental loads are needed).
"""

import time
import os
import pandas as pd
from sqlalchemy import create_engine, text
from src.utils.logger import get_logger
from src.utils.config import DATABASE_PATH, DATABASE_DIR, DB_LOAD_MAX_RETRIES, DB_LOAD_RETRY_DELAY

logger = get_logger(__name__)


def get_engine():
    """Creates and returns a SQLAlchemy engine connected to the SQLite database."""
    os.makedirs(DATABASE_DIR, exist_ok=True)
    engine = create_engine(f"sqlite:///{DATABASE_PATH}", echo=False)
    return engine


def load(df: pd.DataFrame, table_name: str, if_exists: str = "replace") -> dict:
    """
    Loads a DataFrame into the SQLite database with retry logic.

    Input:
        df         — cleaned DataFrame to load
        table_name — target SQLite table name (sanitized by caller)
        if_exists  — "replace" (default) or "append"

    Output:
        dict with keys:
            success       (bool)
            rows_loaded   (int)
            attempts      (int)
            error         (str or None)
    
    Security: table_name must be validated by caller. This function does not
    allow parameterized table names in SQLAlchemy, so the caller must ensure
    table_name matches ^[a-zA-Z_][a-zA-Z0-9_]*$ before calling.
    """
    import re
    # Security: double-check table name format
    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', table_name):
        logger.error("Invalid table name rejected: %s", table_name)
        return {
            "success":     False,
            "rows_loaded": 0,
            "attempts":    0,
            "error":       f"Invalid table name: {table_name}",
        }
    
    engine  = get_engine()
    attempt = 0
    last_error = None

    while attempt < DB_LOAD_MAX_RETRIES:
        attempt += 1
        try:
            logger.info(
                "DB load attempt %d/%d → table '%s' (%d rows)",
                attempt, DB_LOAD_MAX_RETRIES, table_name, len(df)
            )

            df.to_sql(
                name=table_name,
                con=engine,
                if_exists=if_exists,
                index=False,
                chunksize=500,
            )

            # Verify row count using text() for safe parameterization
            with engine.connect() as conn:
                # Security: table_name is validated above, but still use quoted identifier
                result = conn.execute(text(f'SELECT COUNT(*) FROM "{table_name}"'))
                loaded_count = result.scalar()

            logger.info(
                "DB load SUCCESS: %d rows written to table '%s'",
                loaded_count, table_name
            )

            return {
                "success":     True,
                "rows_loaded": loaded_count,
                "attempts":    attempt,
                "error":       None,
            }

        except Exception as e:
            last_error = str(e)
            logger.warning(
                "DB load attempt %d failed: %s", attempt, last_error
            )
            if attempt < DB_LOAD_MAX_RETRIES:
                logger.info("Retrying in %d seconds...", DB_LOAD_RETRY_DELAY)
                time.sleep(DB_LOAD_RETRY_DELAY)

    # All retries exhausted
    logger.error(
        "DB load FAILED after %d attempts. Last error: %s",
        DB_LOAD_MAX_RETRIES, last_error
    )
    return {
        "success":     False,
        "rows_loaded": 0,
        "attempts":    attempt,
        "error":       last_error,
    }


def list_tables() -> list:
    """Returns a list of all table names in the SQLite database."""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            return [row[0] for row in result]
    except Exception:
        return []


def query_table(table_name: str, limit: int = 100) -> pd.DataFrame:
    """
    Returns up to `limit` rows from a loaded table for preview.

    Input:  table_name (str), limit (int)
    Output: pd.DataFrame
    
    Security: Validates table name before querying.
    """
    import re
    # Security: validate table name
    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', table_name):
        logger.error("Invalid table name rejected in query: %s", table_name)
        return pd.DataFrame()
    
    # Security: validate limit is positive integer
    if not isinstance(limit, int) or limit < 1 or limit > 10000:
        limit = 100
    
    try:
        engine = get_engine()
        with engine.connect() as conn:
            # Use quoted identifier for table name
            df = pd.read_sql(
                f'SELECT * FROM "{table_name}" LIMIT {limit}',
                conn
            )
        return df
    except Exception as e:
        logger.error("Query failed for table '%s': %s", table_name, str(e))
        return pd.DataFrame()
