# Auto-ETL Generator Agent with Self-Healing Data Pipeline

An intelligent ETL system that automatically ingests dirty CSV data, detects and fixes data quality issues, loads clean data into SQLite, and provides a full dashboard and audit trail.

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Generate the synthetic dataset
python data/generate_dataset.py

# 3. Run the app
streamlit run app.py
```

---

## Project Structure

```
ETL Gen/
├── app.py                      ← Streamlit UI entry point
├── requirements.txt
├── data/
│   ├── generate_dataset.py     ← Synthetic data generator
│   ├── dirty_data.csv          ← Generated dirty dataset
│   └── clean_reference.csv     ← Ground truth
├── database/
│   └── etl_database.db         ← SQLite (created at runtime)
├── logs/
│   └── etl_pipeline.log
├── reports/
│   ├── schema_report.csv
│   ├── cleaning_report.csv
│   ├── healing_report.csv
│   └── etl_summary.json
├── app/
│   └── pipeline_controller.py  ← ETL orchestrator
├── src/
│   ├── ingestion/              ← CSV reader
│   ├── validation/             ← Schema, nulls, dupes, types, formats
│   ├── cleaning/               ← String, null, dupe, type, date cleaning
│   ├── transformation/         ← Column standardization
│   ├── loading/                ← SQLite loader with retry
│   ├── agent/                  ← Self-healing rules engine
│   │   └── rules/              ← 6 individual healing rules
│   ├── reporting/              ← Quality scorer, report generators
│   └── utils/                  ← Logger, config
└── tests/                      ← pytest test suite
```

---

## Self-Healing Rules

| Rule | Trigger | Action |
|------|---------|--------|
| RULE-01 | Expected column missing | Fuzzy-match rename |
| RULE-02 | Non-numeric values in numeric column | Safe type coercion |
| RULE-03 | Null % > 20% in any column | Median/mode imputation |
| RULE-04 | Duplicate % > 5% | drop_duplicates |
| RULE-05 | Non-ISO dates detected | Normalize to YYYY-MM-DD |
| RULE-06 | DB load failure | Retry up to 3 times |

---

## Running Tests

```bash
pytest tests/ -v
```

---

## Technology Stack

- Python 3.11+
- Streamlit
- Pandas / NumPy
- SQLAlchemy + SQLite
- thefuzz (fuzzy column matching)
- pytest
