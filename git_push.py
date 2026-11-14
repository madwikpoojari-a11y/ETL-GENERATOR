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
     "fix: correct real dataset stats in README\n\n"
     "- Dataset 2: 1050 rows x 9 cols (not 5180 x 17)\n"
     "- Columns: transaction_id, date, customer_id, gender, age,\n"
     "  product_category, quantity, price_per_unit, total_amount\n"
     "- Pipeline verified result: 1006 rows loaded, 97.5->100.0 score, 0.77s\n"
     "- Quick start note updated to reflect real Kaggle dataset"], "git commit")
rc = run(["git", "push", "-u", "origin", "main"], "git push")
print("\nSUCCESS" if rc == 0 else "\nFAILED")
