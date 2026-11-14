"""
config.py
---------
Central configuration file. All thresholds, paths, and constants live here.
To change a threshold (e.g. null tolerance), change it once here — every
module that imports it picks up the new value automatically.
"""

import os

# ── Project root (two levels up from this file) ───────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ── Directory paths ────────────────────────────────────────────────────────
DATA_DIR     = os.path.join(BASE_DIR, "data")
DATABASE_DIR = os.path.join(BASE_DIR, "database")
LOGS_DIR     = os.path.join(BASE_DIR, "logs")
REPORTS_DIR  = os.path.join(BASE_DIR, "reports")

# ── File paths ─────────────────────────────────────────────────────────────
DATABASE_PATH = os.path.join(DATABASE_DIR, "etl_database.db")
LOG_FILE_PATH = os.path.join(LOGS_DIR,     "etl_pipeline.log")

# ── Self-healing thresholds ────────────────────────────────────────────────
# Rule 3: trigger imputation when null % in a column exceeds this value
NULL_THRESHOLD_PCT = 20.0

# Rule 4: trigger dedup when duplicate % exceeds this value
DUPLICATE_THRESHOLD_PCT = 5.0

# Rule 6: number of DB load retry attempts before fatal error
DB_LOAD_MAX_RETRIES = 3

# Rule 6: seconds to wait between retry attempts
DB_LOAD_RETRY_DELAY = 2

# ── Quality score weights (must sum to 100) ────────────────────────────────
QUALITY_WEIGHTS = {
    "completeness": 25,   # % of non-null values
    "uniqueness":   20,   # % of non-duplicate rows
    "validity":     20,   # % of valid emails + dates
    "consistency":  20,   # % of correctly typed values
    "accuracy":     15,   # % of values in expected range/format
}

# ── Expected columns for the retail dataset ────────────────────────────────
EXPECTED_COLUMNS = [
    "customer_id",
    "customer_name",
    "email",
    "phone",
    "city",
    "state",
    "product_category",
    "purchase_amount",
    "purchase_date",
    "payment_method",
]

# ── Date formats the normalizer will attempt to parse ─────────────────────
KNOWN_DATE_FORMATS = [
    "%Y-%m-%d",   # 2023-06-15  (ISO standard — target format)
    "%d/%m/%Y",   # 15/06/2023
    "%m/%d/%Y",   # 06/15/2023
    "%m-%d-%Y",   # 06-15-2023
    "%d-%m-%Y",   # 15-06-2023
    "%d %b %Y",   # 15 Jun 2023
    "%d %B %Y",   # 15 June 2023
    "%b %d, %Y",  # Jun 15, 2023
    "%B %d, %Y",  # June 15, 2023
    "%Y/%m/%d",   # 2023/06/15
]

# ── Numeric columns (used by type validator and coercer) ──────────────────
NUMERIC_COLUMNS = ["purchase_amount"]

# ── Date columns ──────────────────────────────────────────────────────────
DATE_COLUMNS = ["purchase_date"]

# ── Categorical columns (use mode for imputation) ─────────────────────────
CATEGORICAL_COLUMNS = [
    "customer_name", "email", "phone", "city", "state",
    "product_category", "payment_method", "customer_id"
]
