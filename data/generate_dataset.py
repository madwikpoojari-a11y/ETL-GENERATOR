"""
generate_dataset.py
--------------------
PURPOSE:
    Generates two synthetic retail CSV datasets:
    1. clean_reference.csv  - 10,000 rows of perfectly clean data (ground truth)
    2. dirty_data.csv       - same data with intentional errors injected for pipeline testing

HOW TO RUN:
    Open a terminal in the project root and run:
        python data/generate_dataset.py

WHAT IT PRODUCES:
    data/clean_reference.csv
    data/dirty_data.csv

COLUMNS:
    customer_id, customer_name, email, phone, city, state,
    product_category, purchase_amount, purchase_date, payment_method

ERRORS INJECTED INTO dirty_data.csv:
    - 5%  missing values  (random NaN across all columns)
    - 3%  duplicate rows  (300 rows repeated)
    - 8%  invalid emails  (malformed format)
    - 10% invalid dates   (wrong format or garbage strings)
    - 5%  datatype mismatches in purchase_amount (text injected)
    - 10% leading/trailing spaces in customer_name and city
    - 15% inconsistent casing in state and payment_method
    - 0.5% fully empty rows (50 rows of all NaN)
"""

import pandas as pd
import numpy as np
import random
import os

# ── Reproducibility ──────────────────────────────────────────────────────────
SEED = 42
random.seed(SEED)
np.random.seed(SEED)

# ── Constants ─────────────────────────────────────────────────────────────────
NUM_ROWS = 10_000
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))


# ═════════════════════════════════════════════════════════════════════════════
# SECTION 1 — DATA POOLS
# These are the realistic values each column will draw from randomly.
# ═════════════════════════════════════════════════════════════════════════════

FIRST_NAMES = [
    "Aarav", "Priya", "Rahul", "Sneha", "Amit", "Pooja", "Vikram", "Anjali",
    "Rohit", "Kavya", "Arjun", "Divya", "Suresh", "Meera", "Nikhil", "Riya",
    "Karthik", "Deepa", "Manoj", "Sunita", "James", "Emily", "Michael", "Sarah",
    "David", "Jessica", "Daniel", "Ashley", "Chris", "Amanda", "Mohammed", "Fatima",
    "Hassan", "Layla", "Omar", "Zara", "Ali", "Nadia", "Yusuf", "Samira"
]

LAST_NAMES = [
    "Sharma", "Patel", "Verma", "Singh", "Kumar", "Mehta", "Joshi", "Gupta",
    "Reddy", "Nair", "Iyer", "Rao", "Pillai", "Menon", "Agarwal", "Bansal",
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Wilson", "Taylor", "Anderson", "Thomas", "Jackson", "White", "Khan", "Ahmed",
    "Ali", "Hassan", "Malik", "Sheikh", "Ansari", "Qureshi", "Siddiqui", "Mirza"
]

CITIES = [
    "Mumbai", "Delhi", "Bangalore", "Chennai", "Hyderabad", "Kolkata", "Pune",
    "Ahmedabad", "Jaipur", "Surat", "Lucknow", "Kanpur", "Nagpur", "Indore",
    "Bhopal", "Visakhapatnam", "Patna", "Vadodara", "Ghaziabad", "Ludhiana",
    "New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia",
    "San Antonio", "San Diego", "Dallas", "San Jose"
]

STATES = [
    "Maharashtra", "Delhi", "Karnataka", "Tamil Nadu", "Telangana",
    "West Bengal", "Gujarat", "Rajasthan", "Uttar Pradesh", "Madhya Pradesh",
    "California", "Texas", "Florida", "New York", "Illinois"
]

PRODUCT_CATEGORIES = [
    "Electronics", "Clothing", "Groceries", "Home & Kitchen",
    "Sports & Outdoors", "Books", "Toys & Games", "Beauty & Personal Care",
    "Automotive", "Health & Wellness"
]

PAYMENT_METHODS = [
    "Credit Card", "Debit Card", "UPI", "Net Banking",
    "Cash on Delivery", "Wallet", "EMI"
]

EMAIL_DOMAINS = [
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com",
    "rediffmail.com", "icloud.com", "protonmail.com"
]


# ═════════════════════════════════════════════════════════════════════════════
# SECTION 2 — BASE DATA GENERATION
# Builds 10,000 clean rows. This becomes clean_reference.csv.
# ═════════════════════════════════════════════════════════════════════════════

def generate_customer_id(n):
    """
    Generates unique customer IDs in format CUST-00001 to CUST-10000.
    Input:  n (int) - number of rows
    Output: list of strings
    """
    return [f"CUST-{str(i).zfill(5)}" for i in range(1, n + 1)]


def generate_customer_name(n):
    """
    Combines random first and last names.
    Input:  n (int)
    Output: list of strings
    """
    return [
        f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        for _ in range(n)
    ]


def generate_email(names):
    """
    Builds email from customer name: firstname.lastname@domain.com
    Input:  names (list of str)
    Output: list of valid email strings
    """
    emails = []
    for name in names:
        parts = name.lower().split()
        local = f"{parts[0]}.{parts[1]}"
        domain = random.choice(EMAIL_DOMAINS)
        emails.append(f"{local}@{domain}")
    return emails


def generate_phone(n):
    """
    Generates 10-digit phone numbers as strings.
    Input:  n (int)
    Output: list of strings
    """
    return [
        f"{random.randint(6, 9)}{random.randint(100000000, 999999999)}"
        for _ in range(n)
    ]


def generate_purchase_date(n):
    """
    Generates random dates between 2020-01-01 and 2024-12-31 in YYYY-MM-DD format.
    Input:  n (int)
    Output: list of date strings
    """
    start = pd.Timestamp("2020-01-01")
    end = pd.Timestamp("2024-12-31")
    date_range = pd.date_range(start, end)
    indices = np.random.randint(0, len(date_range), size=n)
    return [date_range[i].strftime("%Y-%m-%d") for i in indices]


def generate_purchase_amount(n):
    """
    Generates purchase amounts between 50.00 and 50000.00 rounded to 2 decimals.
    Input:  n (int)
    Output: list of floats
    """
    return [round(random.uniform(50.0, 50000.0), 2) for _ in range(n)]


def build_clean_dataframe(n):
    """
    Assembles all columns into a single clean DataFrame.
    Input:  n (int) - number of rows
    Output: pd.DataFrame with 10 columns, no errors
    """
    names = generate_customer_name(n)
    df = pd.DataFrame({
        "customer_id":       generate_customer_id(n),
        "customer_name":     names,
        "email":             generate_email(names),
        "phone":             generate_phone(n),
        "city":              [random.choice(CITIES) for _ in range(n)],
        "state":             [random.choice(STATES) for _ in range(n)],
        "product_category":  [random.choice(PRODUCT_CATEGORIES) for _ in range(n)],
        "purchase_amount":   generate_purchase_amount(n),
        "purchase_date":     generate_purchase_date(n),
        "payment_method":    [random.choice(PAYMENT_METHODS) for _ in range(n)],
    })
    return df


# ═════════════════════════════════════════════════════════════════════════════
# SECTION 3 — ERROR INJECTION FUNCTIONS
# Each function takes a DataFrame, injects one type of error, returns the df.
# The original DataFrame is never modified in place — copies are used.
# ═════════════════════════════════════════════════════════════════════════════

def inject_missing_values(df, rate=0.05):
    """
    Randomly replaces ~5% of all cells with NaN.

    Why: Tests null detection (FR-07) and null imputation (FR-17, FR-18).

    Input:  df (DataFrame), rate (float) - proportion of cells to nullify
    Output: DataFrame with random NaN values scattered across all columns
    """
    df = df.copy()
    total_cells = df.shape[0] * df.shape[1]
    n_nulls = int(total_cells * rate)

    for _ in range(n_nulls):
        row = random.randint(0, df.shape[0] - 1)
        col = random.randint(0, df.shape[1] - 1)
        df.iat[row, col] = np.nan

    return df


def inject_duplicate_rows(df, rate=0.03):
    """
    Duplicates ~3% of rows and appends them to the DataFrame.

    Why: Tests duplicate detection (FR-08) and removal (FR-19).

    Input:  df (DataFrame), rate (float)
    Output: DataFrame with ~300 extra duplicate rows appended and shuffled
    """
    n_dupes = int(len(df) * rate)
    duplicate_rows = df.sample(n=n_dupes, random_state=SEED)
    df = pd.concat([df, duplicate_rows], ignore_index=True)
    df = df.sample(frac=1, random_state=SEED).reset_index(drop=True)
    return df


def inject_invalid_emails(df, rate=0.08):
    """
    Corrupts ~8% of email values with invalid formats.

    Corruption patterns:
        - Replace '@' with '#'       e.g. john.doe#gmail.com
        - Remove domain entirely     e.g. john.doe@
        - Add double '@'             e.g. john@@doe.com
        - Remove '.'  in domain      e.g. john@gmailcom

    Why: Tests email format validation (FR-10) and format detection.

    Input:  df (DataFrame), rate (float)
    Output: DataFrame with corrupted email values in ~8% of rows
    """
    df = df.copy()
    indices = df.sample(frac=rate, random_state=SEED).index

    corruption_patterns = [
        lambda e: e.replace("@", "#"),
        lambda e: e.split("@")[0] + "@",
        lambda e: e.replace("@", "@@"),
        lambda e: e.replace(".", ""),
    ]

    for idx in indices:
        if pd.notna(df.at[idx, "email"]):
            pattern = random.choice(corruption_patterns)
            df.at[idx, "email"] = pattern(str(df.at[idx, "email"]))

    return df


def inject_invalid_dates(df, rate=0.10):
    """
    Replaces ~10% of purchase_date values with invalid or non-standard formats.

    Invalid patterns:
        - DD/MM/YYYY           e.g. 25/06/2022
        - MM-DD-YYYY           e.g. 06-25-2022
        - DD Mon YYYY          e.g. 25 Jun 2022
        - Garbage strings      e.g. "not-a-date", "N/A", "00/00/0000"

    Why: Tests date detection (FR-11) and normalization (FR-20, Rule 5).

    Input:  df (DataFrame), rate (float)
    Output: DataFrame with ~10% bad dates in purchase_date
    """
    df = df.copy()
    indices = df.sample(frac=rate, random_state=SEED + 1).index

    garbage = ["not-a-date", "N/A", "00/00/0000", "TBD", "unknown", "null"]

    for idx in indices:
        if pd.notna(df.at[idx, "purchase_date"]):
            choice = random.randint(0, 3)
            original = str(df.at[idx, "purchase_date"])
            try:
                dt = pd.Timestamp(original)
                if choice == 0:
                    df.at[idx, "purchase_date"] = dt.strftime("%d/%m/%Y")
                elif choice == 1:
                    df.at[idx, "purchase_date"] = dt.strftime("%m-%d-%Y")
                elif choice == 2:
                    df.at[idx, "purchase_date"] = dt.strftime("%d %b %Y")
                else:
                    df.at[idx, "purchase_date"] = random.choice(garbage)
            except Exception:
                df.at[idx, "purchase_date"] = random.choice(garbage)

    return df


def inject_amount_type_mismatches(df, rate=0.05):
    """
    Replaces ~5% of purchase_amount values with text strings.

    Text values used: "N/A", "unknown", "free", "TBD", "error", "--"

    Why: Tests datatype mismatch detection (FR-09) and type coercion (Rule 2).

    Input:  df (DataFrame), rate (float)
    Output: DataFrame with text in ~5% of purchase_amount cells
    """
    df = df.copy()
    # Convert to object dtype first so text can be assigned into the column
    df["purchase_amount"] = df["purchase_amount"].astype(object)
    indices = df.sample(frac=rate, random_state=SEED + 2).index
    bad_values = ["N/A", "unknown", "free", "TBD", "error", "--", "none"]

    for idx in indices:
        df.at[idx, "purchase_amount"] = random.choice(bad_values)

    return df


def inject_whitespace(df, rate=0.10):
    """
    Adds leading and/or trailing spaces to ~10% of customer_name and city values.

    Why: Tests string cleaning (FR-15).

    Input:  df (DataFrame), rate (float)
    Output: DataFrame with padded string values
    """
    df = df.copy()

    for col in ["customer_name", "city"]:
        indices = df.sample(frac=rate, random_state=SEED + 3).index
        for idx in indices:
            if pd.notna(df.at[idx, col]):
                val = str(df.at[idx, col])
                choice = random.randint(0, 2)
                if choice == 0:
                    df.at[idx, col] = "  " + val
                elif choice == 1:
                    df.at[idx, col] = val + "  "
                else:
                    df.at[idx, col] = "  " + val + "  "

    return df


def inject_casing_issues(df, rate=0.15):
    """
    Randomly changes the casing of ~15% of state and payment_method values.

    Patterns: ALL UPPER, all lower, rAnDoM mIxEd

    Why: Tests string standardization and consistency validation.

    Input:  df (DataFrame), rate (float)
    Output: DataFrame with inconsistent casing in state and payment_method
    """
    df = df.copy()

    for col in ["state", "payment_method"]:
        indices = df.sample(frac=rate, random_state=SEED + 4).index
        for idx in indices:
            if pd.notna(df.at[idx, col]):
                val = str(df.at[idx, col])
                choice = random.randint(0, 2)
                if choice == 0:
                    df.at[idx, col] = val.upper()
                elif choice == 1:
                    df.at[idx, col] = val.lower()
                else:
                    # Mixed case: alternate upper/lower per character
                    df.at[idx, col] = "".join(
                        c.upper() if i % 2 == 0 else c.lower()
                        for i, c in enumerate(val)
                    )

    return df


def inject_empty_rows(df, n=50):
    """
    Appends 50 fully empty rows (all NaN) to the DataFrame.

    Why: Tests handling of completely blank records — the pipeline should
         either drop or flag these rows rather than loading them.

    Input:  df (DataFrame), n (int) - number of empty rows to add
    Output: DataFrame with n extra all-NaN rows at random positions
    """
    empty = pd.DataFrame(
        [[np.nan] * len(df.columns)] * n,
        columns=df.columns
    )
    df = pd.concat([df, empty], ignore_index=True)
    df = df.sample(frac=1, random_state=SEED + 5).reset_index(drop=True)
    return df


# ═════════════════════════════════════════════════════════════════════════════
# SECTION 4 — INJECTION SUMMARY REPORTER
# Prints a table showing exactly what was injected, so tests know what to find.
# ═════════════════════════════════════════════════════════════════════════════

def print_injection_summary(clean_df, dirty_df):
    """
    Compares clean and dirty DataFrames and prints a summary of injected errors.
    This is the ground truth used to write test cases in Phase 11.
    """
    print("\n" + "=" * 60)
    print("  DATASET INJECTION SUMMARY")
    print("=" * 60)
    print(f"  Clean rows   : {len(clean_df):,}")
    print(f"  Dirty rows   : {len(dirty_df):,}")
    print(f"  Extra rows   : {len(dirty_df) - len(clean_df):,} (dupes + empty rows)")
    print("-" * 60)

    # Null counts per column
    print("\n  NULL VALUES PER COLUMN (dirty_data.csv):")
    null_counts = dirty_df.isnull().sum()
    null_pcts = (dirty_df.isnull().sum() / len(dirty_df) * 100).round(2)
    for col in dirty_df.columns:
        print(f"    {col:<25} {null_counts[col]:>5} nulls  ({null_pcts[col]}%)")

    # Total nulls
    total_nulls = dirty_df.isnull().sum().sum()
    print(f"\n  Total null cells : {total_nulls:,}")

    # Duplicate rows
    n_dupes = dirty_df.duplicated().sum()
    print(f"  Duplicate rows   : {n_dupes:,}")

    # Invalid emails (rough count - rows where email doesn't match basic pattern)
    if "email" in dirty_df.columns:
        import re
        valid_pattern = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
        invalid_emails = dirty_df["email"].dropna().apply(
            lambda x: not bool(valid_pattern.match(str(x)))
        ).sum()
        print(f"  Invalid emails   : {invalid_emails:,}")

    # Type mismatches in purchase_amount
    if "purchase_amount" in dirty_df.columns:
        def is_not_numeric(val):
            if pd.isna(val):
                return False
            try:
                float(val)
                return False
            except (ValueError, TypeError):
                return True

        type_issues = dirty_df["purchase_amount"].apply(is_not_numeric).sum()
        print(f"  Amount non-numeric: {type_issues:,}")

    print("=" * 60)
    print("  Files saved to data/ directory")
    print("=" * 60 + "\n")


# ═════════════════════════════════════════════════════════════════════════════
# SECTION 5 — MAIN EXECUTION
# ═════════════════════════════════════════════════════════════════════════════

def main():
    print("\nGenerating clean base dataset...")
    clean_df = build_clean_dataframe(NUM_ROWS)

    # Save clean reference BEFORE any error injection
    clean_path = os.path.join(OUTPUT_DIR, "clean_reference.csv")
    clean_df.to_csv(clean_path, index=False)
    print(f"  clean_reference.csv saved ({len(clean_df):,} rows)")

    # Apply errors sequentially
    print("\nInjecting errors into dirty dataset...")
    dirty_df = clean_df.copy()
    dirty_df = inject_missing_values(dirty_df,         rate=0.05)
    dirty_df = inject_invalid_emails(dirty_df,         rate=0.08)
    dirty_df = inject_invalid_dates(dirty_df,          rate=0.10)
    dirty_df = inject_amount_type_mismatches(dirty_df, rate=0.05)
    dirty_df = inject_whitespace(dirty_df,             rate=0.10)
    dirty_df = inject_casing_issues(dirty_df,          rate=0.15)
    dirty_df = inject_duplicate_rows(dirty_df,         rate=0.03)
    dirty_df = inject_empty_rows(dirty_df,             n=50)

    # Save dirty dataset
    dirty_path = os.path.join(OUTPUT_DIR, "dirty_data.csv")
    dirty_df.to_csv(dirty_path, index=False)
    print(f"  dirty_data.csv   saved ({len(dirty_df):,} rows)")

    # Print injection summary
    print_injection_summary(clean_df, dirty_df)


if __name__ == "__main__":
    main()
