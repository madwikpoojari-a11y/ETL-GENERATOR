"""
download_real_data.py
----------------------
Downloads the E-Commerce Sales Dataset from Kaggle and saves it as
data/ecommerce_dataset.csv with intentional dirty-data injections added
so the ETL pipeline has real issues to fix.

Run:  python data/download_real_data.py

Requires:  pip install kagglehub
           Kaggle credentials configured (~/.kaggle/kaggle.json)
           OR set KAGGLE_USERNAME / KAGGLE_KEY env variables.

If Kaggle is unavailable, the script falls back to generating a
realistic e-commerce CSV from scratch (no credentials needed).
"""

import os, random, re
import numpy as np
import pandas as pd

SEED = 42
random.seed(SEED)
np.random.seed(SEED)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ecommerce_dataset.csv")


# ─── Fallback: build realistic e-commerce data locally ────────────────────────
def build_fallback(n: int = 5000) -> pd.DataFrame:
    categories   = ["Electronics","Clothing","Books","Home & Kitchen","Sports",
                     "Beauty","Toys","Automotive","Groceries","Health"]
    cities       = ["Mumbai","Delhi","Bangalore","Chennai","Hyderabad","Kolkata",
                    "Pune","Ahmedabad","Jaipur","Lucknow","New York","London",
                    "Dubai","Singapore","Toronto"]
    states       = ["Maharashtra","Karnataka","Tamil Nadu","Delhi","Telangana",
                    "West Bengal","Gujarat","Rajasthan","California","Ontario"]
    statuses     = ["Delivered","Shipped","Pending","Cancelled","Returned"]
    payments     = ["Credit Card","Debit Card","UPI","Net Banking","Cash","Wallet","EMI"]
    first_names  = ["Aarav","Priya","Rahul","Sneha","Amit","Pooja","Vikram","Anjali",
                    "James","Emily","Michael","Sarah","Omar","Fatima","David","Jessica"]
    last_names   = ["Sharma","Patel","Verma","Singh","Kumar","Smith","Johnson",
                    "Brown","Williams","Jones","Khan","Ahmed","Garcia","Miller"]

    df = pd.DataFrame({
        "order_id":        [f"ORD{str(i).zfill(6)}" for i in range(1, n+1)],
        "customer_name":   [f"{random.choice(first_names)} {random.choice(last_names)}" for _ in range(n)],
        "email":           [f"{random.choice(first_names).lower()}.{random.choice(last_names).lower()}@{random.choice(['gmail.com','yahoo.com','hotmail.com'])}" for _ in range(n)],
        "phone":           [f"9{random.randint(100000000,999999999)}" for _ in range(n)],
        "product_category":[random.choice(categories)  for _ in range(n)],
        "product_name":    [f"Product-{random.randint(100,999)}" for _ in range(n)],
        "quantity":        [random.randint(1, 10) for _ in range(n)],
        "unit_price":      [round(random.uniform(50, 5000), 2) for _ in range(n)],
        "total_amount":    None,  # filled below
        "order_date":      pd.date_range("2022-01-01", periods=n, freq="1h").strftime("%Y-%m-%d").tolist(),
        "delivery_date":   pd.date_range("2022-01-05", periods=n, freq="1h").strftime("%Y-%m-%d").tolist(),
        "city":            [random.choice(cities)   for _ in range(n)],
        "state":           [random.choice(states)   for _ in range(n)],
        "order_status":    [random.choice(statuses) for _ in range(n)],
        "payment_method":  [random.choice(payments) for _ in range(n)],
        "discount_pct":    [round(random.uniform(0, 40), 1) for _ in range(n)],
        "rating":          [round(random.uniform(1, 5), 1) for _ in range(n)],
    })
    df["total_amount"] = (df["quantity"] * df["unit_price"] *
                          (1 - df["discount_pct"] / 100)).round(2)
    return df


def inject_dirt(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n  = len(df)

    # 5% random nulls
    for _ in range(int(n * df.shape[1] * 0.05)):
        df.iat[random.randint(0, n-1), random.randint(0, df.shape[1]-1)] = np.nan

    # 3% duplicates
    n_dup = int(n * 0.03)
    dups  = df.sample(n_dup, random_state=SEED)
    df    = pd.concat([df, dups], ignore_index=True).sample(frac=1, random_state=SEED).reset_index(drop=True)

    # Bad emails
    email_idx = df.sample(frac=0.08, random_state=SEED+1).index
    for i in email_idx:
        if pd.notna(df.at[i, "email"]):
            df.at[i, "email"] = str(df.at[i, "email"]).replace("@", "#")

    # Bad dates
    date_idx = df.sample(frac=0.10, random_state=SEED+2).index
    for i in date_idx:
        if pd.notna(df.at[i, "order_date"]):
            df.at[i, "order_date"] = random.choice(["TBD","N/A","not-a-date","00/00/0000"])

    # Type mismatches in total_amount
    df["total_amount"] = df["total_amount"].astype(object)
    amt_idx = df.sample(frac=0.05, random_state=SEED+3).index
    for i in amt_idx:
        df.at[i, "total_amount"] = random.choice(["N/A","error","free","TBD"])

    # Whitespace
    for col in ["customer_name", "city"]:
        ws_idx = df.sample(frac=0.10, random_state=SEED+4).index
        for i in ws_idx:
            if pd.notna(df.at[i, col]):
                df.at[i, col] = "  " + str(df.at[i, col]) + "  "

    # Casing issues
    for col in ["state", "order_status"]:
        c_idx = df.sample(frac=0.15, random_state=SEED+5).index
        for i in c_idx:
            if pd.notna(df.at[i, col]):
                df.at[i, col] = str(df.at[i, col]).upper()

    # 30 fully empty rows
    empty = pd.DataFrame([[np.nan]*df.shape[1]], columns=df.columns).loc[np.zeros(30, dtype=int)]
    df = pd.concat([df, empty], ignore_index=True).sample(frac=1, random_state=SEED+6).reset_index(drop=True)

    return df


def main():
    kaggle_ok = False

    # Try Kaggle first
    try:
        import kagglehub
        from kagglehub import KaggleDatasetAdapter
        print("Trying Kaggle: abbas829/ecommerce-sales-dataset …")
        df_raw = kagglehub.load_dataset(
            KaggleDatasetAdapter.PANDAS,
            "abbas829/ecommerce-sales-dataset",
            "",
        )
        # Sanitize column names
        df_raw.columns = [re.sub(r'[^a-zA-Z0-9_]', '_', c.strip().lower()) for c in df_raw.columns]
        clean_path = OUT.replace("ecommerce_dataset.csv", "ecommerce_clean_reference.csv")
        df_raw.to_csv(clean_path, index=False)
        dirty = inject_dirt(df_raw)
        dirty.to_csv(OUT, index=False)
        kaggle_ok = True
        print(f"OK Kaggle dataset saved: {OUT}  ({len(dirty):,} rows)")
    except Exception as e:
        print(f"Kaggle unavailable ({e}). Using fallback generator.")

    if not kaggle_ok:
        print("Generating fallback e-commerce dataset …")
        clean = build_fallback(5000)
        clean_path = OUT.replace("ecommerce_dataset.csv", "ecommerce_clean_reference.csv")
        clean.to_csv(clean_path, index=False)
        dirty = inject_dirt(clean)
        dirty.to_csv(OUT, index=False)
        print(f"OK Fallback dataset saved: {OUT}  ({len(dirty):,} rows)")

    print(f"\nColumns: {list(pd.read_csv(OUT, nrows=1).columns)}")
    print(f"Shape:   {pd.read_csv(OUT).shape}")


if __name__ == "__main__":
    main()
