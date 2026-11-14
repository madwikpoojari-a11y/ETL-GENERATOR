"""
download_real_data.py
----------------------
Downloads real datasets from Kaggle using kagglehub.
Tries multiple datasets — uses the first one that succeeds.
Falls back to built-in generator if all Kaggle downloads fail.

Run: python data/download_real_data.py
"""

import os, sys, re, random, shutil
import numpy as np
import pandas as pd

SEED = 42
random.seed(SEED)
np.random.seed(SEED)

BASE = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.join(BASE, "ecommerce_dataset.csv")
REF  = os.path.join(BASE, "ecommerce_clean_reference.csv")

KAGGLE_DATASETS = [
    # Only the retail sales dataset — confirmed working, no auth needed
    ("mohammadtalib786/retail-sales-dataset", "retail_sales_dataset.csv"),
]


# ── Inject dirt into any real DataFrame ───────────────────────────────────────
def inject_dirt(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n  = len(df)

    # Sanitize column names first
    df.columns = [re.sub(r'[^a-zA-Z0-9_]', '_', c.strip().lower()) for c in df.columns]

    # 5% random nulls
    for _ in range(int(n * df.shape[1] * 0.05)):
        df.iat[random.randint(0, n-1), random.randint(0, df.shape[1]-1)] = np.nan

    # 3% duplicates
    n_dup = max(1, int(n * 0.03))
    dups  = df.sample(n=n_dup, random_state=SEED)
    df    = pd.concat([df, dups], ignore_index=True).sample(frac=1, random_state=SEED).reset_index(drop=True)

    # Bad emails in any email-like column
    email_cols = [c for c in df.columns if 'email' in c.lower() or 'mail' in c.lower()]
    for col in email_cols:
        idx = df.sample(frac=0.08, random_state=SEED+1).index
        for i in idx:
            if pd.notna(df.at[i, col]):
                df.at[i, col] = str(df.at[i, col]).replace("@", "#")

    # Bad dates in any date-like column
    date_cols = [c for c in df.columns if any(x in c.lower() for x in ['date','time','day'])]
    for col in date_cols[:2]:
        idx = df.sample(frac=0.10, random_state=SEED+2).index
        for i in idx:
            if pd.notna(df.at[i, col]):
                df.at[i, col] = random.choice(["TBD","N/A","not-a-date","00/00/0000"])

    # Type mismatches in any price/amount column
    num_cols = [c for c in df.columns if any(x in c.lower() for x in
                ['price','amount','cost','salary','total','revenue','value'])]
    for col in num_cols[:2]:
        df[col] = df[col].astype(object)
        idx = df.sample(frac=0.05, random_state=SEED+3).index
        for i in idx:
            df.at[i, col] = random.choice(["N/A","error","free","TBD"])

    # Whitespace in string columns
    str_cols = [c for c in df.columns if df[c].dtype == object][:3]
    for col in str_cols:
        idx = df.sample(frac=0.10, random_state=SEED+4).index
        for i in idx:
            if pd.notna(df.at[i, col]):
                df.at[i, col] = "  " + str(df.at[i, col]) + "  "

    # Casing issues
    for col in str_cols[1:3]:
        idx = df.sample(frac=0.15, random_state=SEED+5).index
        for i in idx:
            if pd.notna(df.at[i, col]):
                df.at[i, col] = str(df.at[i, col]).upper()

    # 20 fully empty rows
    empty = pd.DataFrame([[np.nan]*df.shape[1]]*20, columns=df.columns)
    df = pd.concat([df, empty], ignore_index=True).sample(frac=1, random_state=SEED+6).reset_index(drop=True)

    return df


# ── Fallback: build realistic e-commerce data ─────────────────────────────────
def build_fallback(n: int = 5000) -> pd.DataFrame:
    cats     = ["Electronics","Clothing","Books","Home & Kitchen","Sports",
                "Beauty","Toys","Automotive","Groceries","Health"]
    cities   = ["Mumbai","Delhi","Bangalore","Chennai","Hyderabad","Kolkata",
                "Pune","Ahmedabad","Jaipur","Lucknow","New York","London","Dubai"]
    states   = ["Maharashtra","Karnataka","Tamil Nadu","Delhi","Telangana",
                "West Bengal","Gujarat","Rajasthan","California","Ontario"]
    statuses = ["Delivered","Shipped","Pending","Cancelled","Returned"]
    pays     = ["Credit Card","Debit Card","UPI","Net Banking","Cash","Wallet","EMI"]
    fnames   = ["Aarav","Priya","Rahul","Sneha","Amit","Pooja","Vikram","Anjali",
                "James","Emily","Michael","Sarah","Omar","Fatima","David","Jessica"]
    lnames   = ["Sharma","Patel","Verma","Singh","Kumar","Smith","Johnson",
                "Brown","Williams","Jones","Khan","Ahmed","Garcia","Miller"]

    names = [f"{random.choice(fnames)} {random.choice(lnames)}" for _ in range(n)]
    qty   = [random.randint(1, 10) for _ in range(n)]
    price = [round(random.uniform(50, 5000), 2) for _ in range(n)]
    disc  = [round(random.uniform(0, 40), 1) for _ in range(n)]

    df = pd.DataFrame({
        "order_id":         [f"ORD{str(i).zfill(6)}" for i in range(1, n+1)],
        "customer_name":    names,
        "email":            [f"{nm.split()[0].lower()}.{nm.split()[1].lower()}@{random.choice(['gmail.com','yahoo.com','hotmail.com'])}" for nm in names],
        "phone":            [f"9{random.randint(100000000,999999999)}" for _ in range(n)],
        "product_category": [random.choice(cats)     for _ in range(n)],
        "product_name":     [f"Product-{random.randint(100,999)}" for _ in range(n)],
        "quantity":         qty,
        "unit_price":       price,
        "total_amount":     [round(q*p*(1-d/100), 2) for q,p,d in zip(qty,price,disc)],
        "order_date":       pd.date_range("2022-01-01", periods=n, freq="1h").strftime("%Y-%m-%d").tolist(),
        "delivery_date":    pd.date_range("2022-01-05", periods=n, freq="1h").strftime("%Y-%m-%d").tolist(),
        "city":             [random.choice(cities)   for _ in range(n)],
        "state":            [random.choice(states)   for _ in range(n)],
        "order_status":     [random.choice(statuses) for _ in range(n)],
        "payment_method":   [random.choice(pays)     for _ in range(n)],
        "discount_pct":     disc,
        "rating":           [round(random.uniform(1, 5), 1) for _ in range(n)],
    })
    return df


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    success = False

    try:
        import kagglehub
        from kagglehub import KaggleDatasetAdapter

        for slug, file_path in KAGGLE_DATASETS:
            try:
                print(f"Trying Kaggle: {slug} ...")

                # Try new API first (kagglehub >= 1.0)
                try:
                    df_raw = kagglehub.dataset_load(
                        KaggleDatasetAdapter.PANDAS,
                        slug,
                        path=file_path if file_path else None
                    )
                except AttributeError:
                    # Older API
                    df_raw = kagglehub.load_dataset(
                        KaggleDatasetAdapter.PANDAS, slug, file_path
                    )
                if df_raw is None or len(df_raw) == 0:
                    print(f"  Empty result, skipping.")
                    continue

                # Sanitize columns
                df_raw.columns = [re.sub(r'[^a-zA-Z0-9_]', '_', c.strip().lower())
                                  for c in df_raw.columns]

                # Keep only first 10000 rows if huge
                df_raw = df_raw.head(10000).reset_index(drop=True)

                # Save clean reference
                df_raw.to_csv(REF, index=False)

                # Inject dirt and save
                dirty = inject_dirt(df_raw)
                dirty.to_csv(OUT, index=False)

                print(f"  OK: {slug}")
                print(f"  Rows: {len(dirty):,}  Columns: {list(df_raw.columns)[:6]}...")
                success = True
                break

            except Exception as e:
                print(f"  Failed: {e}")
                continue

    except ImportError:
        print("kagglehub not installed.")

    if not success:
        print("\nAll Kaggle sources failed. Using built-in fallback generator...")
        clean = build_fallback(5000)
        clean.to_csv(REF, index=False)
        dirty = inject_dirt(clean)
        dirty.to_csv(OUT, index=False)
        print(f"Fallback dataset saved: {len(dirty):,} rows, {dirty.shape[1]} columns")

    # Final check
    result = pd.read_csv(OUT)
    print(f"\nFinal dataset: {result.shape[0]:,} rows x {result.shape[1]} columns")
    print(f"Columns: {list(result.columns)}")
    print(f"Saved: {OUT}")


if __name__ == "__main__":
    main()
