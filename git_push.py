import subprocess, os

REPO = r"c:\Users\Lenovo\OneDrive\Documents\ETL Gen"
LOG  = os.path.join(REPO, "logs", "git_push.log")

def run(cmd, label):
    print(f">>> {label}")
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(f"\n{'='*50}\n{label}\n{r.stdout}\n{r.stderr}\n")
    if r.stdout.strip(): print(r.stdout.strip())
    errs = [l for l in (r.stderr or "").splitlines()
            if "Permission denied" not in l and "could not open" not in l
            and "LF will be" not in l and l.strip()]
    if errs: print("STDERR:", "\n".join(errs))
    return r.returncode

run(["git", "add", "."], "git add")
run(["git", "commit", "-m",
     "data: add real Kaggle retail dataset + updated downloader\n\n"
     "- Downloaded mohammadtalib786/retail-sales-dataset (1050 rows, 9 cols)\n"
     "- Real columns: transaction_id, date, customer_id, gender, age,\n"
     "  product_category, quantity, price_per_unit, total_amount\n"
     "- Dirty data injected: nulls, dupes, bad dates, type mismatches\n"
     "- Updated download_real_data.py to target only confirmed dataset\n"
     "- Updated .gitignore to include small real dataset in repo"],
    "git commit")
rc = run(["git", "push", "-u", "origin", "main", "--force"], "git push")
print("\nSUCCESS" if rc == 0 else "\nFAILED — check logs/git_push.log")
