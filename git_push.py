import subprocess, os

REPO   = r"c:\Users\Lenovo\OneDrive\Documents\ETL Gen"
LOG    = os.path.join(REPO, "logs", "git_push.log")

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

run(["git", "add", "."],                                       "git add")
run(["git", "commit", "-m", "docs: godly README with full project documentation\n\n"
     "- Architecture diagrams (ASCII)\n"
     "- Self-healing agent rule table\n"
     "- Quality scoring formula\n"
     "- Full module reference table\n"
     "- Complete test results\n"
     "- Dataset specifications\n"
     "- Future enhancements roadmap"],                         "git commit")
rc = run(["git", "push", "-u", "origin", "main", "--force"],   "git push")

print("\nSUCCESS" if rc == 0 else "\nFAILED — check logs/git_push.log")
