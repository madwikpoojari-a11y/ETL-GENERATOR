<div align="center">

<img src="https://readme-typing-svg.demolab.com?font=Inter&weight=800&size=32&pause=1000&color=6BBAA7&center=true&vCenter=true&width=700&lines=⚡+ETL-GENERATOR+AGENT;Self-Healing+Data+Pipeline;Automated+%7C+Intelligent+%7C+Production-Ready" alt="Typing SVG" />

<br/>

![Python](https://img.shields.io/badge/Python-3.11+-6BBAA7?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-FBA100?style=for-the-badge&logo=streamlit&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-3-6C648B?style=for-the-badge&logo=sqlite&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2.0+-B6A19E?style=for-the-badge&logo=pandas&logoColor=white)
![Tests](https://img.shields.io/badge/Tests-33%2F33_Passing-6BBAA7?style=for-the-badge&logo=pytest&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-FBA100?style=for-the-badge)

<br/>

> **An intelligent data engineering system that automatically ingests dirty CSV data,
> detects quality issues, applies autonomous self-healing rules, cleans and transforms
> the dataset, loads it into SQLite, and provides a full audit trail — zero manual intervention.**

<br/>

---

</div>

## 📌 Table of Contents

- [Overview](#-overview)
- [Live Demo Flow](#-live-demo-flow)
- [Architecture](#-architecture)
- [Self-Healing Agent](#-self-healing-agent)
- [Data Quality Scoring](#-data-quality-scoring)
- [Project Structure](#-project-structure)
- [Tech Stack](#-tech-stack)
- [Quick Start](#-quick-start)
- [Datasets](#-datasets)
- [Test Results](#-test-results)
- [Module Reference](#-module-reference)
- [Future Enhancements](#-future-enhancements)
- [Author](#-author)

---

## 🧠 Overview

The **Auto-ETL Generator Agent** solves a core problem in data engineering — dirty data entering pipelines without detection or correction.

Traditional ETL pipelines require a data engineer to manually inspect every CSV, identify issues, write fix scripts, and re-run. This project eliminates that entirely.

```
Dirty CSV  ──►  Extract  ──►  Validate  ──►  Self-Heal  ──►  Clean  ──►  Load  ──►  Report
                                ↑                 ↑
                         Null Detection      6 Healing Rules
                         Dupe Detection      Auto-triggered
                         Type Mismatch       Fully logged
                         Format Check        Auditable
```

**What makes it different:**

- Rules-based self-healing agent — no LLMs, no black boxes, fully deterministic
- Every action logged with rule ID, trigger condition, and outcome
- Before/after quality score comparison with 5 dimensions
- Works on any CSV — not tied to one schema
- Production-like layered architecture (5 layers, 11 modules)

---

## 🎬 Live Demo Flow

```
1. Open http://localhost:8501
2. Navigate → 📂 Upload & Preview
3. Click "Real E-Commerce Dataset" or upload your own CSV
4. Navigate → 🚀 Run Pipeline → click Execute
5. Navigate → 🏠 Dashboard → see quality jump, healing log, pipeline stages
6. Navigate → 📊 Results & Reports → download cleaned CSV, reports, logs
```

**Expected output on the synthetic dirty dataset:**

| Metric | Value |
|---|---|
| Input rows | 10,350 |
| Rows after cleaning | ~9,850 |
| Quality score before | ~58% |
| Quality score after | ~94% |
| Healing rules triggered | 4–5 |
| Runtime | < 10 seconds |

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────┐
│              LAYER 1 — PRESENTATION                 │
│                   Streamlit UI                      │
│    Dashboard · Upload · Schema · Pipeline · Reports │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│              LAYER 2 — APPLICATION                  │
│              Pipeline Controller                    │
│         Orchestrates all 10 ETL stages              │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│               LAYER 3 — SERVICE                     │
│  Ingestion │ Validation │ Cleaning │ Transformation  │
│            Loading │ Reporting                       │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│               LAYER 4 — AGENT                       │
│          Self-Healing Rules Engine                  │
│   RULE-01 · RULE-02 · RULE-03 · RULE-04 · RULE-05  │
│                   RULE-06                           │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│               LAYER 5 — DATA                        │
│          SQLite · CSV Files · Logs · Reports        │
└─────────────────────────────────────────────────────┘
```

**Pipeline Execution Sequence:**

```
Step 1  → Extract          csv_reader.py reads CSV → raw DataFrame
Step 2  → Schema           schema_inferrer.py detects column types
Step 3  → Validate         null, duplicate, type, format checks
Step 4  → Score (Before)   quality_scorer.py calculates pre-clean score
Step 5  → Heal             healing_agent.py evaluates & fires rules
Step 6  → Clean            string → duplicate → type → date → null
Step 7  → Transform        column_standardizer.py → snake_case
Step 8  → Score (After)    quality_scorer.py recalculates
Step 9  → Load             db_loader.py → SQLite (3 retries)
Step 10 → Report           schema + cleaning + healing + summary reports
```

---

## 🧠 Self-Healing Agent

The agent runs between validation and cleaning. It evaluates 6 deterministic rules in order and applies fixes automatically.

```
┌──────────────────────────────────────────────────────────────────┐
│                    SELF-HEALING AGENT                            │
├─────────┬──────────────────────────┬───────────────────────────-┤
│ Rule ID │ Trigger Condition        │ Action Taken               │
├─────────┼──────────────────────────┼────────────────────────────┤
│ RULE-01 │ Expected column missing  │ Fuzzy-match rename         │
│         │ e.g. cust_id → missing   │ cust_id → customer_id      │
├─────────┼──────────────────────────┼────────────────────────────┤
│ RULE-02 │ Non-numeric in numeric   │ pd.to_numeric(coerce)      │
│         │ col: "N/A", "error"      │ bad values → NaN           │
├─────────┼──────────────────────────┼────────────────────────────┤
│ RULE-03 │ Null % > 20% in column   │ Median (numeric)           │
│         │                          │ Mode (categorical)         │
├─────────┼──────────────────────────┼────────────────────────────┤
│ RULE-04 │ Duplicate % > 5%         │ drop_duplicates(keep=first)│
├─────────┼──────────────────────────┼────────────────────────────┤
│ RULE-05 │ Non-ISO dates detected   │ Normalize → YYYY-MM-DD     │
│         │ DD/MM/YYYY, MM-DD-YYYY   │ 10 format patterns tried   │
├─────────┼──────────────────────────┼────────────────────────────┤
│ RULE-06 │ DB load failure          │ Retry up to 3×             │
│         │                          │ Root cause logged          │
└─────────┴──────────────────────────┴────────────────────────────┘
```

Every triggered rule produces a log entry:
```
2026-11-14 15:52:01 | WARNING  | src.agent.healing_agent | [RULE-04] Duplicate rate 3.2% exceeded threshold 5% → drop_duplicates applied | HEALED
```

---

## 📊 Data Quality Scoring

Score is calculated out of **100** across 5 weighted dimensions:

```
┌────────────────┬────────┬─────────────────────────────────────────┐
│ Dimension      │ Weight │ Measured As                             │
├────────────────┼────────┼─────────────────────────────────────────┤
│ Completeness   │  25%   │ % of non-null cells                     │
│ Uniqueness     │  20%   │ % of non-duplicate rows                 │
│ Validity       │  20%   │ % of valid emails + parseable dates     │
│ Consistency    │  20%   │ % of numeric columns with correct types │
│ Accuracy       │  15%   │ % of amounts in plausible range         │
└────────────────┴────────┴─────────────────────────────────────────┘

Total = Σ (dimension_score × weight / 100)
```

---

## 📁 Project Structure

```
ETL-GENERATOR/
│
├── app.py                          ← Streamlit entry point (5-page UI)
├── requirements.txt                ← All dependencies
├── README.md
├── .gitignore
│
├── app/
│   └── pipeline_controller.py      ← ETL orchestrator (10 stages)
│
├── data/
│   ├── generate_dataset.py         ← Synthetic dirty data generator
│   └── download_real_data.py       ← Real e-commerce dataset downloader
│
├── src/
│   ├── ingestion/
│   │   └── csv_reader.py           ← CSV → DataFrame (path or upload)
│   │
│   ├── validation/
│   │   ├── schema_inferrer.py      ← Auto type detection
│   │   ├── null_detector.py        ← Null counts per column
│   │   ├── duplicate_detector.py   ← Exact duplicate detection
│   │   ├── type_validator.py       ← Type mismatch detection
│   │   └── format_validator.py     ← Email + date format validation
│   │
│   ├── cleaning/
│   │   ├── string_cleaner.py       ← Strip whitespace
│   │   ├── duplicate_handler.py    ← Remove dupes + empty rows
│   │   ├── null_handler.py         ← Median / mode imputation
│   │   ├── type_coercer.py         ← Safe type conversion
│   │   └── date_normalizer.py      ← Normalize to YYYY-MM-DD
│   │
│   ├── transformation/
│   │   └── column_standardizer.py  ← Rename to snake_case
│   │
│   ├── loading/
│   │   └── db_loader.py            ← SQLite loader + 3× retry
│   │
│   ├── agent/
│   │   ├── healing_agent.py        ← Rule orchestrator
│   │   └── rules/
│   │       ├── rule_missing_column.py
│   │       ├── rule_type_mismatch.py
│   │       ├── rule_high_nulls.py
│   │       ├── rule_duplicates.py
│   │       ├── rule_date_format.py
│   │       └── rule_load_failure.py
│   │
│   ├── reporting/
│   │   ├── quality_scorer.py       ← Before/after quality score
│   │   ├── schema_reporter.py      ← Schema report
│   │   ├── cleaning_reporter.py    ← Cleaning actions log
│   │   └── etl_reporter.py         ← Final ETL summary
│   │
│   └── utils/
│       ├── logger.py               ← Rotating file + console logger
│       └── config.py               ← All thresholds and constants
│
├── tests/
│   ├── test_cleaning.py            ← 9 tests
│   ├── test_validation.py          ← 8 tests
│   ├── test_healing_agent.py       ← 9 tests
│   ├── test_db_loader.py           ← 3 tests
│   └── test_quality_scorer.py      ← 4 tests
│
├── database/                       ← SQLite DB (created at runtime)
├── logs/                           ← Pipeline logs (created at runtime)
└── reports/                        ← CSV/JSON reports (created at runtime)
```

---

## 🛠 Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Frontend | Streamlit 1.35+ | 5-page dashboard UI |
| Backend | Python 3.11+ | Pipeline logic |
| Database | SQLite + SQLAlchemy | Clean data storage |
| Data Processing | Pandas 2.0+ / NumPy | ETL transformations |
| Fuzzy Matching | thefuzz + Levenshtein | Column name healing |
| Logging | Python logging (Rotating) | Audit trail |
| Testing | pytest | 33 unit tests |

**Theme:** Aqua `#6BBAA7` · Sunshine `#FBA100` · Lavender `#6C648B` · Dusty Rose `#B6A19E`

---

## ⚡ Quick Start

**Clone and run in 3 commands:**

```bash
git clone https://github.com/madwikpoojari-a11y/ETL-GENERATOR.git
cd ETL-GENERATOR
pip install -r requirements.txt
python data/generate_dataset.py
streamlit run app.py
```

Open **http://localhost:8501**

---

**To use the real e-commerce dataset (5,180 rows, 17 columns):**

```bash
python data/download_real_data.py
```

Then go to Upload & Preview → click **"Real E-Commerce Dataset"**

---

**To run all tests:**

```bash
pip install pytest
python -m pytest tests/ -v
```

Expected output:
```
33 passed in 2.56s
```

---

## 📦 Datasets

### 1. Synthetic Retail Dataset (generated)
- **10,000 base rows** → ~10,350 after dirty injection
- **10 columns:** customer_id, customer_name, email, phone, city, state, product_category, purchase_amount, purchase_date, payment_method
- **Injected errors:** 5% nulls, 3% duplicates, 8% bad emails, 10% bad dates, 5% type mismatches, 10% whitespace, 15% casing issues, 50 empty rows

### 2. Real E-Commerce Dataset (generated/downloaded)
- **5,180 rows · 17 columns**
- **Columns:** order_id, customer_name, email, phone, product_category, product_name, quantity, unit_price, total_amount, order_date, delivery_date, city, state, order_status, payment_method, discount_pct, rating
- Same dirty data injected programmatically for realistic pipeline testing

---

## ✅ Test Results

```
============================= test session starts =============================
platform win32 — Python 3.14.3, pytest-9.2.0

tests/test_cleaning.py::test_string_cleaner_strips_spaces          PASSED
tests/test_cleaning.py::test_string_cleaner_no_change_when_clean   PASSED
tests/test_cleaning.py::test_duplicate_handler_removes_dupes       PASSED
tests/test_cleaning.py::test_duplicate_handler_removes_empty_rows  PASSED
tests/test_cleaning.py::test_null_handler_fills_numeric_with_median PASSED
tests/test_cleaning.py::test_null_handler_fills_categorical_with_mode PASSED
tests/test_cleaning.py::test_type_coercer_converts_purchase_amount PASSED
tests/test_cleaning.py::test_date_normalizer_handles_multiple_formats PASSED
tests/test_cleaning.py::test_date_normalizer_sets_nan_for_garbage  PASSED
tests/test_db_loader.py::test_load_writes_correct_row_count        PASSED
tests/test_db_loader.py::test_load_replaces_existing_table         PASSED
tests/test_db_loader.py::test_query_table_returns_dataframe        PASSED
tests/test_healing_agent.py::test_rule_duplicates_triggers         PASSED
tests/test_healing_agent.py::test_rule_duplicates_removes_them     PASSED
tests/test_healing_agent.py::test_rule_high_nulls_triggers         PASSED
tests/test_healing_agent.py::test_rule_high_nulls_imputes          PASSED
tests/test_healing_agent.py::test_rule_type_mismatch_triggers      PASSED
tests/test_healing_agent.py::test_rule_type_mismatch_coerces       PASSED
tests/test_healing_agent.py::test_rule_date_format_triggers        PASSED
tests/test_healing_agent.py::test_rule_date_format_normalizes      PASSED
tests/test_healing_agent.py::test_healing_agent_runs_full_pipeline PASSED
tests/test_quality_scorer.py::test_perfect_score_on_clean_data     PASSED
tests/test_quality_scorer.py::test_low_completeness_score          PASSED
tests/test_quality_scorer.py::test_low_uniqueness_score            PASSED
tests/test_quality_scorer.py::test_score_improves_after_cleaning   PASSED
tests/test_validation.py::test_null_detector_counts_correctly      PASSED
tests/test_validation.py::test_duplicate_detector_finds_exact_dupes PASSED
tests/test_validation.py::test_email_validator_flags_bad_emails    PASSED
tests/test_validation.py::test_email_validator_ignores_nulls       PASSED
tests/test_validation.py::test_date_validator_flags_garbage        PASSED
tests/test_validation.py::test_schema_inferrer_detects_numeric     PASSED
tests/test_validation.py::test_schema_inferrer_detects_date        PASSED
tests/test_validation.py::test_schema_inferrer_detects_string      PASSED

========================= 33 passed in 2.56s ==========================
```

---

## 📋 Module Reference

| Module | Input | Output | Key Function |
|---|---|---|---|
| `csv_reader` | File path / upload | Raw DataFrame | `read_csv()` |
| `schema_inferrer` | DataFrame | Type dict | `infer_schema()` |
| `null_detector` | DataFrame | Null counts dict | `detect()` |
| `duplicate_detector` | DataFrame | Dupe count dict | `detect()` |
| `type_validator` | DataFrame | Violation rows | `detect()` |
| `format_validator` | DataFrame | Bad email/date rows | `validate_emails()` |
| `quality_scorer` | DataFrame | Score dict (0–100) | `calculate()` |
| `healing_agent` | DataFrame + validation | Healed DF + log | `heal()` |
| `string_cleaner` | DataFrame | Cleaned DF + report | `clean()` |
| `duplicate_handler` | DataFrame | Deduped DF | `clean()` |
| `null_handler` | DataFrame | Imputed DF | `clean()` |
| `type_coercer` | DataFrame | Typed DF | `clean()` |
| `date_normalizer` | DataFrame | ISO-date DF | `clean()` |
| `column_standardizer` | DataFrame | snake_case DF | `standardize()` |
| `db_loader` | DataFrame + table name | Load result dict | `load()` |
| `etl_reporter` | All results | Saved report files | `build_summary()` |

---

## 🔭 Future Enhancements

| Enhancement | Description |
|---|---|
| ☁ Cloud Deployment | Deploy on Streamlit Cloud or AWS EC2 |
| 🤖 LLM Integration | Use an LLM to suggest column mappings and schema fixes |
| 🌊 Apache Airflow | Replace manual trigger with a scheduled DAG |
| ⚡ Apache Spark | Scale to 10M+ rows with PySpark |
| 📡 Real-time Ingestion | Kafka consumer for streaming ETL |
| 🏠 Data Warehouse | Load to PostgreSQL, Snowflake, or BigQuery |
| 📧 Alerts | Email/Slack notifications on pipeline failure |
| 🔄 Schema Drift Detection | Alert when incoming schema changes from baseline |
| 🧪 Great Expectations | Replace custom validator with GX framework |
| 🐳 Docker | Containerize for one-command deployment |

---

## 👨‍💻 Author

<div align="center">

**Built as a college project demonstrating production-grade data engineering practices.**

*Auto-ETL Generator Agent — Self-Healing Data Pipeline*

[![GitHub](https://img.shields.io/badge/GitHub-madwikpoojari--a11y-6BBAA7?style=for-the-badge&logo=github)](https://github.com/madwikpoojari-a11y)

---

*"Messy CSV in. Clean data out. The pipeline fixes itself."*

</div>
