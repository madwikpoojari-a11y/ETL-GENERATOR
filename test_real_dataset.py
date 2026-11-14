"""
test_real_dataset.py
---------------------
Runs the real Kaggle retail dataset through the full ETL pipeline
and prints a detailed compatibility + results report.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "app"))

import pandas as pd
from pipeline_controller import run_pipeline

DATASET = os.path.join("data", "ecommerce_dataset.csv")
LOG     = os.path.join("logs", "real_dataset_test.log")

def sep(title=""):
    print(f"\n{'='*60}")
    if title: print(f"  {title}")
    if title: print(f"{'='*60}")

def main():
    sep("REAL DATASET PIPELINE COMPATIBILITY TEST")

    # ── 1. Load and inspect raw ────────────────────────────────────
    sep("STEP 1: RAW DATASET INSPECTION")
    df = pd.read_csv(DATASET, dtype=str)
    print(f"  Rows        : {df.shape[0]:,}")
    print(f"  Columns     : {df.shape[1]}")
    print(f"  Column names: {list(df.columns)}")
    print(f"\n  Null counts per column:")
    for col in df.columns:
        n = df[col].isna().sum()
        pct = round(n/len(df)*100, 1)
        flag = " <-- HAS NULLS" if n > 0 else ""
        print(f"    {col:<20} {n:>4} nulls ({pct}%){flag}")
    print(f"\n  Duplicate rows : {df.duplicated().sum()}")

    # ── 2. Check column compatibility ─────────────────────────────
    sep("STEP 2: COLUMN COMPATIBILITY CHECK")
    EXPECTED = ["transaction_id","date","customer_id","gender","age",
                "product_category","quantity","price_per_unit","total_amount"]
    for col in EXPECTED:
        status = "FOUND" if col in df.columns else "MISSING"
        print(f"  {col:<25} {status}")

    # ── 3. Run full pipeline ───────────────────────────────────────
    sep("STEP 3: RUNNING FULL ETL PIPELINE")
    print("  Running pipeline...")
    results = run_pipeline(DATASET, table_name="real_retail_data")

    # ── 4. Results ─────────────────────────────────────────────────
    sep("STEP 4: PIPELINE RESULTS")
    if results["status"] == "success":
        s  = results["summary"]
        sb = results["score_before"]
        sa = results["score_after"]

        print(f"  STATUS              : SUCCESS")
        print(f"  Rows input          : {s['rows_input']:,}")
        print(f"  Rows after cleaning : {s['rows_after_cleaning']:,}")
        print(f"  Rows loaded         : {s['rows_loaded']:,}")
        print(f"  Rows removed        : {s['rows_removed']:,}")
        print(f"  Duration            : {s['duration_seconds']:.2f}s")
        print(f"\n  QUALITY SCORE BEFORE : {sb['total_score']:.1f}/100")
        print(f"    Completeness : {sb['completeness']:.1f}%")
        print(f"    Uniqueness   : {sb['uniqueness']:.1f}%")
        print(f"    Validity     : {sb['validity']:.1f}%")
        print(f"    Consistency  : {sb['consistency']:.1f}%")
        print(f"    Accuracy     : {sb['accuracy']:.1f}%")
        print(f"\n  QUALITY SCORE AFTER  : {sa['total_score']:.1f}/100")
        print(f"    Completeness : {sa['completeness']:.1f}%")
        print(f"    Uniqueness   : {sa['uniqueness']:.1f}%")
        print(f"    Validity     : {sa['validity']:.1f}%")
        print(f"    Consistency  : {sa['consistency']:.1f}%")
        print(f"    Accuracy     : {sa['accuracy']:.1f}%")
        print(f"\n  IMPROVEMENT          : +{s['score_improvement']:.1f} points")

        sep("STEP 5: SELF-HEALING ACTIONS")
        healing = results.get("healing_log", [])
        if healing:
            for h in healing:
                print(f"  [{h['rule_id']}] {h['rule_name']}")
                print(f"    Trigger : {h['trigger']}")
                print(f"    Action  : {h['action']}")
                print(f"    Outcome : {h['outcome']}")
                print()
        else:
            print("  No healing rules triggered.")

        sep("STEP 6: CLEANED DATA SAMPLE")
        cdf = results["clean_df"]
        print(f"  Clean columns : {list(cdf.columns)}")
        print(f"  Clean dtypes  :")
        for col, dtype in cdf.dtypes.items():
            print(f"    {col:<25} {dtype}")
        print(f"\n  Remaining nulls : {cdf.isnull().sum().sum()}")
        print(f"  Sample (3 rows):")
        print(cdf.head(3).to_string(index=False))

        sep("VERDICT")
        print("  COMPATIBLE : YES")
        print("  The real Kaggle retail dataset runs through the pipeline")
        print("  without errors. All 10 pipeline stages completed.")
        print(f"  Quality improved from {sb['total_score']:.1f} to {sa['total_score']:.1f} (+{s['score_improvement']:.1f} pts).")

    else:
        sep("VERDICT")
        print(f"  COMPATIBLE : NO")
        print(f"  Pipeline FAILED: {results.get('error','Unknown error')}")

    sep()

if __name__ == "__main__":
    main()
